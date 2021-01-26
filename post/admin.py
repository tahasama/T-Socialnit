from django.contrib import admin
from .models import Post, Comment

# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User

# from nested_inline.admin import NestedStackedInline, NestedModelAdmin



# class CommentbyAdmin(NestedStackedInline):
#     model = Comment
   

# class PostbyAdmin(NestedStackedInline):
#     model = Post
#     inlines =[CommentbyAdmin,]
  

# class UserAdmin(NestedModelAdmin):
#     list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')
#     inlines =[PostbyAdmin,]
    

# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created')
    list_filter = ('user', 'created')
    search_fields = ('user',)
    raw_id_fields = ('user',)
    ordering = ('created',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('commenter', 'post', 'created',)
    list_filter = ('created', 'updated')
    search_fields = ('commenter', 'body')

