from django.conf.urls import *

from forums.views import Discussions, User,Errors

app_name = "forums"

urlpatterns = [
	url(r'^(?P<sort>(|featured|latest|unanswered))$' , Discussions.Index.as_view() , name = "index"), #for discussions index
	url(r'^ask$' , Discussions.PostView.as_view() , name="ask_question"), #for posting new question
	url(r'^vote$',Discussions.QuestionView.as_view() , name="vote"), #for voting a question
	url(r'^comment$' , Discussions.CommentView.as_view(),name="comment" , kwargs = {"method" : "question"}), #For Commenting on a question
	url(r'^comment/reply$' , Discussions.CommentView.as_view() , kwargs = {"method" : "comment"}), #For replying on a comment
	url(r'^comment/vote$' , Discussions.CommentView.as_view() , kwargs = {"action" : "vote"}), #For voting on a comment
	url(r'^comment/favourite$' , User.ProfileView.as_view() , kwargs = {"action" : "favourite" , "method" : "comment"}), #For Adding a favourite
	url(r'^post/favourite$' , User.ProfileView.as_view() , kwargs = {"action" : "favourite" , "method" : "question"}), #For Adding a favourite
	url(r'^message$',User.AccountView.as_view()), #For sending a message
	url(r'^(?P<key>.+)$' , Discussions.Thread.as_view() , name = "thread"), #For visiting a thread
]
