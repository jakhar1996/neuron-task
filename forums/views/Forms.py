from django.views import generic
from forums.models import Question , Comment
from django import forms

class QuestionForm(forms.Form):
	'''
	Form For Posting Question
	'''
	question = forms.CharField(label = "Title" , required = True , max_length = 200)
	description = forms.CharField( label = "Description" , required = True , max_length = 1000)
