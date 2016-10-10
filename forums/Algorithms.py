'''
Algorithms for calculating score of Posts, Comments and Voting
reference : 
1. https://github.com/reddit/reddit/blob/master/r2/r2/lib/db/_sorts.pyx
2. https://medium.com/hacking-and-gonzo/how-reddit-ranking-algorithms-work-ef111e33d0d9
'''
from math import *
import datetime


epoch = datetime.datetime(1970,1,1)
def sign(a):
	if a == 0 : return 0
	return a/abs(a)

def voteCount(p,n):
	#Used in initial implementation for vote counting
	p = int(p)
	n = int(n)
	return abs(p)*(n-p) + (1-abs(p))*n

def epoch_seconds(date):
	td = date-epoch
	return td.days * 86400 + td.seconds + (float(td.microseconds)/1000000)

def hot(score,date):
	#Algorithm for sorting featured posts
	order = log(max(abs(score),1),10)
	sign = 1 if score > 0 else -1 if score < 0 else 0
	seconds = epoch_seconds(date) - 1134028003
	a = round(sign * order + seconds/45000,7)
	return a

def zeero(a):
	a.score = 0
	a.vote_count = 0
	return a


def confidence(ups,downs):
	'''
	Algorithm for sorting comments
	'''
	n = ups + downs

	if n == 0:
		return 0
	z = 1.281551565545
	p = float(ups) / n

	left = p + 1/(2*n)*z*z
	right = z*sqrt(p*(1-p)/n + z*z/(4*n*n))
	under = 1 + 1/n*z*z

	return (left - right) / under
