"""neuron URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url , include
from django.contrib import admin
from forums.views.User import ProfileView,AccountView
from forums.views.Discussions import Index,Redirect

urlpatterns = [
    url(r'^$',Redirect.as_view()),  
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/profile[/]$' , ProfileView.as_view() , name="profile"),
    url(r'^accounts/',include("allauth.urls")),
    url(r'^discussions/' , include("forums.urls")),
    url(r'^user/(?P<username>.+)$',AccountView.as_view() , name= "account")
]
