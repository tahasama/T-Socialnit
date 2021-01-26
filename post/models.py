from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, reverse





class Post(models.Model):
    user = models.ForeignKey(User, related_name='post_created', on_delete=models.CASCADE)
    url = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/%Y/%m/%d/', blank=True, null=True)
    video = models.FileField(upload_to="video/%Y%m/%d/",blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    users_like = models.ManyToManyField(User,related_name='images_liked',blank=True)

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
        return f" by {self.commenter}"

    def get_absolute_url(self):
        return reverse('post:comment',args=[self.post.id, self.id])

