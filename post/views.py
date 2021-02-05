from django.dispatch.dispatcher import receiver
from django.shortcuts import redirect, render, get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Post, Comment, Profile, Relationship

from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login


# ContactForm, SearchForm
from .forms import UserCreationEmailForm, PostForm, CommentForm, UserEditForm
# from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


# from django.db.models import Count

# from django.core.mail import send_mail, EmailMessage

from django.contrib.auth.decorators import login_required, permission_required

# from django.contrib import messages

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.db.models import Q



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

def update_post(request,post_id):
    post = Post.objects.get(id=post_id)
    if request.method == 'POST' and post.author == request.user:
        form = PostForm(request.POST,files=request.FILES, instance=post)
        if form.is_valid():
            post.save()
            messages.success(request, 'Post has been updated')

        return redirect('post:wall')
    else:
        form = PostForm(instance=post)
    if "text" in request.GET:
        return render(request, 'post/content/text.html', {'posts': post, 'form': form})
    if "image" in request.GET:
        return render(request, 'post/content/image.html', {'posts': post, 'form': form})
    if "video" in request.GET:
        return render(request, 'post/content/video.html', {'posts': post, 'form': form})

def delete_post(request,post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    messages.success(request, 'Post has been deleted')
    return redirect('post:home')


def post_list(request, user_id=None):
    profile = get_object_or_404(Profile, user=request.user)
    friends = profile.friends.all()
    posts = Post.objects.filter(Q(user__in=friends) | Q(user=request.user))
    # print(posts.values())

    if user_id:
        user = User.objects.get(id=user_id)
        posts = Post.objects.filter(user=user).order_by('-created')
        #print(posts.values())
 
   
    all_profiles = Profile.objects.all().exclude(user=profile.user)
    profiles = profile.get_all_friends()
    rel_r = Relationship.objects.filter(sender=profile)
    rel_s = Relationship.objects.filter(receiver=profile)
    rel_receiver = []
    rel_sender = []
    for r in rel_r:
        rel_receiver.append(r.receiver.user)
 
    for s in rel_s:
        rel_sender.append(s.sender.user)
   
    nb_invitation = len(rel_sender)

    # print(nb_invitation)
    # print(rel_sender)
    # print(rel_receiver)
    # print(rel_s)
    # print(rel_r)
    return render(request,'post/list.html',{
        'profile':profile,'profiles':profiles,'all_profiles':all_profiles,'posts': posts,
        'rel_sender':rel_sender,'rel_receiver':rel_receiver,'nb_invitation':nb_invitation})



def post_detail(request, post_id=None):
    post = None
    post = get_object_or_404(Post, id=post_id)
    #print(post)
    comments = Comment.objects.filter(post=post)

    users_like = post.users_like.all()
    #print(users_like)

    if "like" in request.GET : 
        post.users_like.add(request.user)
        return redirect(request.META.get('HTTP_REFERER'))

    
    if "unlike" in request.GET:
        post.users_like.remove(request.user)
        return redirect(request.META.get('HTTP_REFERER'))

    if request.method == 'POST' and request.user.is_authenticated:

        form = CommentForm(data=request.POST)
        if form.is_valid():
            comments = form.save(commit=False)
            comments.post = post
            comments.commenter = request.user
            comments.save()
            #print(comments.id)
            return redirect('post:post_detail', post.id)
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
        return redirect('post:post_detail', post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'post/detail.html', {'form': form, 'comment': comment, 'post': post})


def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, post=post, id=comment_id)
    comment.delete()
    return redirect('post:post_detail', post.id)


def register(request):
    if request.method == 'POST':
        form = UserCreationEmailForm(data=request.POST)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password1'])
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('post:home')
    else:
        form = UserCreationEmailForm()
    return render(request, 'users/registration.html', {'form': form})

@login_required
def edit(request):
    if request.method == 'POST':
        form = UserEditForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
        return redirect('home')
    else:
        form = UserEditForm(instance=request.user)
    return render(request,'bloggers/edit.html',{'form': form})


def search(request):
    user = User.objects.filter(username__contains=request.GET['name'])
    print
    return render(request, 'post/search.html', {'user': user})

    
@login_required
def send_invitation(request):
    if request.method=='POST':
        id = request.POST.get('profile_id')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(id=id)
        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')
        return redirect(request.META.get('HTTP_REFERER'))  # to stay on the same page
    return redirect('post:home')

@login_required
def cancel(request):
    if request.method=="POST":
        id = request.POST.get('profile_id')
        sender = Profile.objects.get(user=request.user)
        receiver = Profile.objects.get(id=id)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('post:home')

@login_required
def reject(request):
    if request.method=="POST":
        id = request.POST.get('profile_id')
        receiver = Profile.objects.get(user=request.user)
        sender = Profile.objects.get(id=id)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('post:home')

@login_required
def accept(request):
    if request.method=="POST":
        id = request.POST.get('profile_id')
        sender = Profile.objects.get(id=id)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            sender.friends.add(receiver.user)
            receiver.friends.add(sender.user)
            rel.save()
    return redirect('post:home')

@login_required
def unfriend(request):
    if request.method=='POST':
        id = request.POST.get('profile_id')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(id=id)

        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
        )
        sender.friends.remove(receiver.user)
        receiver.friends.remove(sender.user)
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('post:home')