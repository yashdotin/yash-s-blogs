from django.conf import settings
from django.conf import settings
from django.db import models
from django.utils.text import slugify


User = settings.AUTH_USER_MODEL


class Category(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=220, unique=True)

	def __str__(self):
		return self.name


class Tag(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(max_length=120, unique=True)

	def __str__(self):
		return self.name


class Post(models.Model):
	STATUS = [
		("DRAFT", "Draft"),
		("REVIEW", "Review Requested"),
		("PUBLISHED", "Published"),
		("REJECTED", "Rejected"),
	]

	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
	title = models.CharField(max_length=300)
	slug = models.SlugField(max_length=320, unique=True, blank=True)
	excerpt = models.TextField(blank=True)
	story = models.TextField(blank=True, help_text="A narrative story or introduction to your post")
	body = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS, default="DRAFT")
	categories = models.ManyToManyField(Category, blank=True, related_name="posts")
	tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
	featured_image = models.ImageField(upload_to="featured_images/", blank=True, null=True)
	reading_time = models.IntegerField(null=True, blank=True)
	published_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	views = models.BigIntegerField(default=0, editable=False)

	class Meta:
		ordering = ["-published_at", "-created_at"]
		indexes = [models.Index(fields=["-published_at"]) ]

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.slug:
			base = slugify(self.title)[:300]
			slug = base
			i = 1
			while Post.objects.filter(slug=slug).exists():
				slug = f"{base}-{i}"
				i += 1
			self.slug = slug

		if self.body:
			words = len(self.body.split())
			self.reading_time = max(1, words // 200)

		super().save(*args, **kwargs)


class Revision(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="revisions")
	title = models.CharField(max_length=300)
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return f"Revision of {self.post_id} @ {self.created_at}"


class DraftAutosave(models.Model):
	# lightweight autosave store per user & post (post can be null for new drafts)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="autosaves")
	post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="autosaves")
	title = models.CharField(max_length=300, blank=True)
	body = models.TextField(blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ("user", "post")

	def __str__(self):
		return f"Autosave user={self.user_id} post={self.post_id} at {self.updated_at}"


class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
	parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	body = models.TextField()
	is_spam = models.BooleanField(default=False)
	approved = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Comment by {self.author_id} on {self.post_id}"