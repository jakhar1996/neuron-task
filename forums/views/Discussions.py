from django.views import generic,View
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from forums.models import Question,Comment
from forums.Algorithms import voteCount
from .Forms import QuestionForm
from django.urls import reverse
from django.shortcuts import render,redirect
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from forums.views.Base import BaseView
import json,datetime

class Redirect(View):
	def dispatch(self,request,*args,**kwargs):
		return redirect("/discussions/")
class Index(View):
	'''
	Rendering the Forums index page
	'''
	template_name = "discussions/index.html"

	#class attribute to determine the sorting to be used
	sortMapper = {
		"" : Question.featured,
		"featured" : Question.featured,
		"latest" : Question.latest,
		"unanswered" : Question.unanswered
	}

	def dispatch(self,request,*args,**kwargs):
		_sort = self.sortMapper.get(kwargs.get("sort"))
		return render(request , self.template_name , {"question_list" : _sort()})


class Thread(generic.DetailView):
	'''
	View to manage a thread
	'''
	model = Question
	template_name = "discussions/thread.html"

	def getContext(self,request,**kwargs):
		q = Question.forUrl(kwargs.get("key"))
		if not q:
			raise Http404("Thread Does not exist")
		return q

	def get(self,request,*args,**kwargs):
		q = self.getContext(request,**kwargs)
		return render(request,self.template_name,{"question" : q , "user" : request.user})

class PostView(LoginRequiredMixin ,generic.edit.FormView):
	'''
	Saving the incoming form for adding a question
	'''
	template_name = "discussions/ask.html"
	form_class = QuestionForm

	def form_valid(self,form):
		q = Question(pub_date = datetime.datetime.now())
		for i,e in form.cleaned_data.items():
			setattr(q,i,e)
		try:
			q.setURL()
			print("URL ",q.url)
			q.save()
		except Exception as e:
			print(e)
		else:
			return HttpResponseRedirect("/discussions/%s"%q.url)

		return super().form_valid(form)

	

class QuestionView(BaseView,SingleObjectMixin,View):
	'''
	View to manage actions on a question:
	1. Voting
	'''
	def post(self,request,*args,**kwargs):
		if request.user.id is not None:
			self.request = request
			qid,vote = self.fromRequest("qid","vote")
			v = {
				"uid" : request.user.id,
				"vote" : vote
			}
			q = Question.setVote(qid,v).serialize()
			return HttpResponse(q , content_type = "application/json")
		return HttpResponse(status  =403)

class CommentView(BaseView,SingleObjectMixin,View):
	'''
	Wrapper for managing Actions on a comment:
	1. Voting
	2. Comment on Post
	3. Reply to a comment
	'''
	objMapper = {
		"comment" : Comment,
		"question" : Question
	}

	def vote(self,request,*args,**kwargs):
		self.request = request
		uid , cid,vote = self.fromRequest("uid","cid" , "vote")
		v = {
			"uid" : uid,
			"vote" : vote 
		}
		c = Comment.setVote(cid,v).to_json()
		return HttpResponse(c, content_type = "application/json")

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		'''
		Exempting csrf check for testing
		'''
		self.request = request
		return super().dispatch(request, *args, **kwargs)

	def post(self,request,*args,**kwargs):
		if request.user.id is not None:
			if "action" in kwargs:
				#action kwarg is passed through url. Voting is performed in this block
				#similarly more functionality can be added by defining appropriate actions-method pairs
				return getattr(self,kwargs.get("action"))(request,*args,**kwargs)

			#Adding Comment to question or Replying to Comment works through this block	
			#method kwarg is passed through url definition
			
			obj = self.objMapper.get(kwargs.get("method"))
			if request.user.id is not None:
				qid,comment = self.fromRequest("qid","comment")
				c = obj.setComment(qid,comment,request.user.id)
				return HttpResponse(c.to_json(), content_type = "application/json")
		return HttpResponse(status = 403)