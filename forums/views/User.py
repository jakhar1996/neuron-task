from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from forums.models import Question, Comment , Messages , Favourites
from django.urls import reverse
from django.shortcuts import render , get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from forums.views.Base import BaseView
import json

class UserData():
	'''
	Simple Wrapper for extending accessibility of user object inside templates 
	'''
	def __init__(self,user):
		self.user = user

	@property
	def questions(self):
		'''Return the Posts by the user'''
		return Question.objects.filter(user_id = self.user.id)
	@property
	def comments(self):
		'''Return the comments by the user'''
		return Comment.objects.filter(user_id = self.user.id)
	@property
	def username(self):
		'''Return the username'''
		return self.user.username
	@property
	def first_name(self):
		'''Return the first_name'''
		return self.user.first_name
	@property
	def last_name(self):
		'''Return the last_name'''
		return self.user.last_name
	@property
	def inbox(self):
		'''Return the messages in inbox of the user'''
		return Messages.objects.filter(receiver_id = self.id)
	@property
	def sentbox(self):
		'''Return the messages in the sentbox of the user'''
		return Messages.objects.filter(sender_id = self.id)
	@property
	def favourites(self):
		'''Returns the favourites'''
		return Favourites.objects.filter(user_id = self.id)
	@property
	def id(self):
		'''Return the id of the user'''
		return self.user.id



class ProfileView( BaseView,View):
	'''
	Wrapper for the actions directly related to the user profile like:
		1. Viewing profile page
		2. Marking Favourites
	View can only be accessed if user is logged in   
	'''
	class Mapper():
		objMapper = {
			"comment" : Comment,
			"question" : Question
		}
		'''Depending on the functionality many more classmethods can be added to extend functionality'''
		@classmethod
		def favourite(self,request,**kwargs):
			obj = self.objMapper.get(kwargs.get("method"))
			oid  = self.fromRequest("id")
			f = Favourites(kind = kwargs.get("method") , obj_id = oid , user_id = request.user.id )
			f.save()
			return HttpResponse(f.to_json() , content_type = "application/json")

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		'''Bypassing the csrf check'''
		self.request = request
		return super().dispatch(request, *args, **kwargs)

	def get(self,request,*args,**kwargs):
		'''Rendering the profile view'''
		user = UserData(request.user)
		return render(request , "user/profile.html" , {"user" : user } )
	
	def post(self,request,*args,**kwargs):
		if request.user.id is not None:
			return getattr(self.Mapper,kwargs.get("action"))(request,**kwargs) 
		return HttpResponse(status = 403)

class AccountView(View):
	'''
	Wrapper for account related functionalities like:
		1. Sending Message
		2. View Public Account Page
	'''
	http_method_names = ["get","post"]
	def get(self,request,*args,**kwargs):
		key = kwargs.get("username")
		user = get_object_or_404(User,username = key)
		return render(request , "user/account.html" , {"user" : UserData(user)})

	def post(self,request,*args,**kwargs):
		'''
		Manages the messaging
		'''
		if request.user.id is not None:
			sender_id = request.user.id
			receiver_id = request.POST.get("to")
			message = request.POST.get("m")
			m = Messages(sender_id = int(sender_id) , receiver_id = int(receiver_id) , message= message ).save()
			return HttpResponse(m.to_json() , content_type = "application/json")
		return HttpResponse(status = 403)


	