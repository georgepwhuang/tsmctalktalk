from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from markdown import markdown
from django.utils.html import mark_safe
from django.conf import settings

# Create your models here.

class Board(models.Model):
	name = models.CharField(max_length=30, unique=True)
	description = models.CharField(max_length=50)
	creation_time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

class Topic(models.Model):
	subject = models.CharField(max_length=255, unique=True)
	board = models.ForeignKey(Board, on_delete=models.SET_NULL, related_name='topics', null=True)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='topics', null=True)
	anonymous = models.BooleanField(default=False)
	created_on = models.DateTimeField(auto_now_add=True)	
	views = models.PositiveIntegerField(default=0)
	is_closed = models.BooleanField(default=False)

	def __str__(self):
		return self.subject

	def get_last_posts_pageno(self):
		rem = self.posts.count() % settings.POST_PAGINATE_BY
		quo = self.posts.count() // settings.POST_PAGINATE_BY
		if rem == 0:
			pageno = quo
		else:
			pageno = quo + 1
		return pageno

	def get_pageno_of_post(self,post):
		#first get index of post in queryset, since queryset doesnot gives index, we will eumerate it
		queryset = self.posts.all().order_by('id')	#RELATED to boards.views.TopicPage_View - if needed, change at both
		post_index = None
		for index,value in enumerate(queryset, start=1):
			if value.id == post.id:
				post_index = index 
				break
		#get page location
		rem = post_index % settings.POST_PAGINATE_BY
		quo = post_index // settings.POST_PAGINATE_BY
		if rem == 0:
			pageno = quo
		else:
			pageno = quo + 1
		return pageno

class Post(models.Model):
	message = models.CharField(max_length=5000)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='posts', null=True)
	anonymous = models.BooleanField(default=False)
	created_on = models.DateTimeField(auto_now_add=True)
	topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, related_name='posts', null=True)
	updated_on = models.DateTimeField(default=timezone.now)	#if you use timezone.now in save the use () because then callable is not passed but value is
	#updated_on is default means 1st time it will be now then while updating post we will update this as well

	def __str__(self):
		#return first 30 characters of message only
		return (self.message[:30] if len(self.message)>30 else self.message)

	def get_message_as_markdown(self):
		return mark_safe(markdown(self.message))
		
