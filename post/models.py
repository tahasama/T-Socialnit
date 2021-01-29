from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.enums import Choices
from django.shortcuts import redirect, reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True,blank=True)
    photo = models.ImageField(null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)

    def get_all_friends(self):
        return self.friends.all()
    
    def get_count_friends(self):
        return self.friends.all().count()

    def __str__(self):
        return str(self.user)

STATUS_CHOICES = (
            ('send','send'),
            ('accepted','accepted')
        )

class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"

class Post(models.Model):
    user = models.ForeignKey(User, related_name='post_created', on_delete=models.CASCADE)
    url = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/%Y/%m/%d/', blank=True, null=True)
    video = models.FileField(upload_to="video/%Y%m/%d/",blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    users_like = models.ManyToManyField(User,related_name='posts_liked',blank=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f"post by {self.user}"
    
    def get_absolute_url(self):
        return reverse('post:post_detail', args=[self.id])



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return self.commenter

    def get_absolute_url(self):
        return reverse('post:comment',args=[self.post.id, self.id])


