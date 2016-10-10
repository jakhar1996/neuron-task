import re
from django.db import models
from django.contrib.auth.models import User
from mongoengine import *
from forums.Algorithms import voteCount , hot , confidence
import json

class _BaseForUser():
	'''
	
	'''
	@property
	def user(self):
		'''Returns the user which posted the Post/Comment'''
		return User.objects.get(pk = self.user_id)

	@user.setter
	def user(self,user):
		'''
		Simple way to set user.
		Instead of Model.user_id = request.user.id we can do Model.user = request.user	
		'''
		self.user_id = user.id

class Base(_BaseForUser):
	'''Base Class from which wraps some basic functionality associated with Questions and Comments'''

	parent = None #Helper Attribute 
	'''
	Following methods have been wrapped in @classmethods so that some operations can be encapsulated in the Model
	'''

	@classmethod
	def featured(self , page = 1):
		'''
		Returns Featured Posts/Comments. Sorted by Descending score
		Pagination achieved through array slicing
		'''
		first = (page-1)*10 + 1
		last = page*10
		return self.objects.order_by("-score")[first:last]
	
	@classmethod
	def latest(self , page = 1):
		'''Returns Latest Posts/Comments. Latest post/comment first'''
		first = (page-1)*10 + 1
		last = page*10
		return self.objects.order_by("-pub_date")[first:last]
	
	@classmethod
	def unanswered(self , page = 1):
		'''Returns Posts/Comments with zero comments'''
		first = (page-1)*10 + 1
		last = page*10		
		return self.objects.filter(comments__size = 0)[first:last]
	
	@classmethod
	def getById(self,pk):
		'''Quick Lookup using the primary key'''
		return self.objects.get(id = pk)

	@classmethod
	def setVote(self,qid,vote):
		'''Adds a vote to the Model instance'''
		q = self.getById(qid)
		q._vote(vote)
		return q

	@property
	def voteCount(self):
		'''Iterates through the votes and adds each vote'''
		return sum([int(e.vote) for e in self.votes])

	@classmethod
	def setComment(self,qid,comment,uid):
		'''
		Add a comment to a post
		Add a reply to a comment
		'''
		q = self.getById(qid)
		c = self.comment(comment_text = comment)
		if self.comment.parent is not None:
			setattr(c,self.comment.parent,q)
		q.addComment(c)
		return c

	def addComment(self,comment):
		'''
		Method to add comment if direct instance of comment is available
		'''
		if isinstance(comment,self.comment):
			comment.save()
			print("adding Comment")
			self.comments.append(comment)
			self.save()
		else:
			raise TypeError

	def calcScore(self):
		'''
		Method to calculate Score for featured posts. Default implementation is for Questions/Posts
		'''
		self.score = hot(self.voteCount , self.pub_date)
		self.save()

	def _vote(self,vote):
		'''
		Internal implementation for vote setting
		'''
		try:
			past = self.votes.get(user_id = vote.get("uid"))
		except Exception as e:
			past = self.votes.create(user_id = vote.get("uid"))
		past.vote = int(vote.get("vote"))
		self.save()
		if self.scorable:
			self.calcScore()
		return self

class Vote(EmbeddedDocument):
	'''
	Model for Votes
	'''
	user_id = IntField(default = 1)
	vote = IntField(default = 0)

class CommentReplies(Document,_BaseForUser):
	'''
	Model for Comment Replies
	'''
	parent = "comment"
	comment_text = StringField(max_length = 1000)
	user_id = IntField(default = 1)
	pub_date = DateTimeField(help_text = "date published")
	comment = ReferenceField("Comment")

class Comment(Base,Document):
	'''
	Model for Comments
	'''
	scorable = True #Helper attribute which decides whether score should be calculated if this model is voted. calcScore() method should be defined if set to True


	comment = CommentReplies
	parent = "question_id"
	comment_text = StringField(max_length = 100)
	votes = EmbeddedDocumentListField(Vote)
	user_id = IntField(default = 1)
	pub_date = DateTimeField(help_text = "date published")
	question_id = ReferenceField("Question")
	comments = ListField(ReferenceField(CommentReplies))
	score = FloatField(default = 0)

	def calcScore(self):
		self.score = confidence(len([e for e in self.votes if e.vote == 1]) , len([e for e in self.votes if e.vote == -1]))
		self.save()

class Question(Base,Document):
	'''Model for Comments'''
	comment = Comment
	scorable = True

	question = StringField(max_length = 200)
	description = StringField(max_length = 1000)
	pub_date = DateTimeField(help_text = "date published")
	comments = ListField(ReferenceField(Comment))
	url = StringField(max_length = 100)
	votes = EmbeddedDocumentListField(Vote)
	user_id = IntField(default = 1)
	score = FloatField(default  =0)

	meta = {
		'indexes': [
			'question', 
			('pub_date', '+question')
		],
		"strict" : False
	}

	def joinTitle(self):
		'''Helper method for joining title'''
		return '-'.join([e.lower() for e in self.question.split()])

	def setURL(self):
		'''Make a url for the Question Instance'''
		pattern = '[^a-zA-Z0-9-]'
		self.url  = re.sub(pattern,'', self.joinTitle()).lower()

	@property
	def qid(self):
		return str(self.id)

	@classmethod
	def forUrl(self,url):
		'''Find a Question using url'''
		return self.objects.get(url = url)

	def serialize(self):
		'''Extending to_json() of Mongoengine'''
		data = json.loads(self.to_json())
		data["voteCount"] = self.voteCount
		return json.dumps(data)

class Messages(Document):
	'''
	Model for Messages
	'''
	sender_id = IntField(default = 1)
	receiver_id = IntField(default = 1)
	message = StringField(max_length  =1000)
	time = DateTimeField(help_text = "time sent")

	def _getUser(self,user_id):
		return User.objects.get(pk = user_id)
		
	@property
	def sender(self):
		'''Return User object of the message sender'''
		return self._getUser(self.sender_id)

	@property
	def receiver(self):
		'''Return User object of the message receiver'''
		return self._getUser(self.receiver_id)


class Favourites(Document):
	user_id = IntField(default = 1)
	kind = StringField()
	obj_id = StringField()