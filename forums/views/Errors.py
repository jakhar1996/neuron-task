from django.views import View
from django.shortcuts import render

class View404(View):
	def get(self,request,*args,**kwargs):
		return render(request,"404.html")