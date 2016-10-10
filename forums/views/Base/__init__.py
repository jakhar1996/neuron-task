class BaseView():
	'''
	Simple Wrapper for accessing request inside the inherting class
	'''
	def fromRequest(self,*args , type = "POST"):
		t = getattr(self.request,type)
		return [t.get(e) for e in args ] if isinstance(args,tuple) else t.get(*args)
