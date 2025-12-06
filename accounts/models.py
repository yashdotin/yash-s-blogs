from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	is_editor = models.BooleanField(default=False)
	is_author = models.BooleanField(default=False)
	profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
	name = models.CharField(max_length=255, blank=True, default='')
	location = models.CharField(max_length=255, blank=True, default='')
	about = models.TextField(blank=True, default='')

	def promote_to_author(self):
		self.is_author = True
		self.save()

	def __str__(self):
		return self.get_full_name() or self.username