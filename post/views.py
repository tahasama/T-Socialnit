from django.shortcuts import redirect, render, get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Post, Comment

from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login


# ContactForm, SearchForm, UserEditForm
from .forms import UserCreationEmailForm, PostForm, CommentForm
# from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


# from django.db.models import Count

# from django.core.mail import send_mail, EmailMessage

from django.contrib.auth.decorators import login_required, permission_required

# from django.contrib import messages

from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
def create_post(request):

    posts = Post.objects.all()

    if request.method == 'POST':
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            posts = form.save(commit=False)
            posts.user = request.user
            posts.save()
            return redirect('post:wall', posts.user.id)
    else:
        form = PostForm()
    if "text" in request.GET:
        return render(request, 'post/content/text.html', {'posts': posts, 'form': form})
    if "image" in request.GET:
        return render(request, 'post/content/image.html', {'posts': posts, 'form': form})
    if "video" in request.GET:
        return render(request, 'post/content/video.html', {'posts': posts, 'form': form})

# def update_post(request,post_slug):
#     post = Post.objects.get(slug=post_slug)
#     users_in_group = Group.objects.get(name="writer").user_set.all()
#     if request.method == 'POST' and  request.user in users_in_group and post.author == request.user:
#         form = PostForm(request.POST, instance=post)
#         if form.is_valid():


#             post.published = False
#             post.save()
#             messages.success(request, 'Post has been updated, and will be published after revsion')

#         return redirect('blog:post_list_author')
#     else:
#         form = PostForm(instance=post)
#     return render(request,'blog/create.html',{'post': post,'form':form})

# def delete_post(request,post_slug):
#     users_in_group = Group.objects.get(name="writer").user_set.all()
#     if request.method == 'POST'and  request.user in users_in_group:
#         post = Post.objects.get(slug=post_slug)
#         post.delete()
#         messages.success(request, 'Post has been updated, and will be published after revsion')
#     return redirect('blog:post_list_author')


def post_list(request, user_id=None):
    posts = Post.objects.all().order_by('-created')
    # print(posts.values())

    if user_id:
        user = User.objects.get(id=user_id)
        posts = Post.objects.filter(user=user).order_by('-created')
        print(posts.values())

    return render(request, 'post/list.html', {'posts': posts})


def post_detail(request, post_id=None, user_id=None):

    post = get_object_or_404(Post, id=post_id)
    print(post)
    comments = Comment.objects.filter(post=post)

    users_like = post.users_like.all()
    #print(users_like)

    if "like" in request.GET:
        x = post.users_like.add(request.user)
        print(x)
    
    if "unlike" in request.GET:
        post.users_like.remove(request.user)

    if request.method == 'POST' and request.user.is_authenticated:

        form = CommentForm(data=request.POST)
        if form.is_valid():
            comments = form.save(commit=False)
            comments.post = post
            comments.commenter = request.user
            comments.save()
            print(comments.id)
            return redirect('post:post_detail', post.user.id, post.id)
    else:
        form = CommentForm()
    return render(request, 'post/detail.html', {'post': post, 'form': form, 'comments': comments, 'users_like': users_like})


def update_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, post=post, id=comment_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
        return redirect('post:post_detail', post.user.id, post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'post/detail.html', {'form': form, 'comment': comment, 'post': post})


def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, post=post, id=comment_id)

    comment.delete()
    return redirect('post:post_detail', post.user.id, post.id)


def register(request):
    if request.method == 'POST':
        form = UserCreationEmailForm(data=request.POST)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            #register_user = User.objects.get(username=cd['username'])
            # if 'writer' in request.GET:
            #     customer_group = Group.objects.get(name='writer')
            #     customer_group.user_set.add(register_user)
            # else:
            # customer_group = Group.objects.get(name='reader')
            # customer_group.user_set.add(register_user)
            user = authenticate(
                username=cd['username'], password=cd['password1'])
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('post:home')
    else:
        form = UserCreationEmailForm()
    return render(request, 'users/registration.html', {'form': form})

# @login_required
# def edit(request):
#     if request.method == 'POST':
#         form = UserEditForm(instance=request.user, data=request.POST)
#         if form.is_valid():
#             form.save()
#         return redirect('home')
#     else:
#         form = UserEditForm(instance=request.user)
#     return render(request,'bloggers/edit.html',{'form': form})

# def contact(request):
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             subject = form.cleaned_data.get('subject')
#             from_email = form.cleaned_data.get('from_email')
#             message = form.cleaned_data.get('message')
#             name = form.cleaned_data.get('name')

#             message_format = f"client :{name} \n\n with e-mail: {from_email} has sent you a new message:\n\n{message}"
#             msg = EmailMessage(
#                 subject,
#                 message_format,
#                 to=['serertei@gmail.com'],
#                 from_email=from_email
#             )
#             msg.send()
#             return render(request, 'blog/contact_success.html')
#     else:
#         form = ContactForm()
#     return render(request, 'blog/contact.html', {'form': form})

# def search(request):
#     query = None
#     results = []
#     if request.method == "GET":
#         query = request.GET.get("query")
#         search_vector = SearchVector('user')
#         search_query = SearchQuery(query)
#         results = Post.objects.annotate(search=search_vector,
#                     rank=SearchRank(search_vector, search_query)).filter(
#                                         search=search_query).order_by('-rank')
#         return render(request,'blog/search.html',{'query': query,'results': results})


# @ login_required
# def like(request):
#     if request.POST.get('action') == 'post':
#         result = ''
#         id = int(request.POST.get('postid'))
#         post = get_object_or_404(Post, id=id)
#         if post.likes.filter(id=request.user.id).exists():
#             post.likes.remove(request.user)
#             post.like_count -= 1
#             result = post.like_count
#             post.save()
#         else:
#             post.likes.add(request.user)
#             post.like_count += 1
#             result = post.like_count
#             post.save()

#         return JsonResponse({'result': result, })
