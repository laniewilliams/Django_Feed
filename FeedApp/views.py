from django.shortcuts import render, redirect
from .forms import PostForm,ProfileForm, RelationshipForm #we have imported the forms we're going to use
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined, 
# Django looks for a function called index() in the views.py file. 

def index(request):
    """The home page for Learning Log."""
    return render(request, 'FeedApp/index.html')



@login_required #this is a decorator. It prevents unauthorized access to pages that follow
def profile(request):
    profile = Profile.objects.filter(user=request.user) #request.user refers to the person using the system. user= is used because it is one of the attributes of the Profile model
    #used filter isntead of get because get does not work with filter, only filter does
    if not profile.exists():
        Profile.objects.create(user=request.user) #create a profile for them
    profile = Profile.objects.get(user=request.user) #after we've created it we can get the actual profile of the user

    if request.method != 'POST': #means the method is get
        form = ProfileForm(instance=profile)
    else:
        form = ProfileForm(instance=profile, data=request.POST) #we're saving the profile data to the database
        if form.is_valid(): #performs data verification
            form.save()
            return redirect('FeedApp:index')


    context = {'form':form} #sending the form
    return render(request, 'FeedApp/profile.html',context)

@login_required #this is a decorator. It prevents unauthorized access to pages that follow
def myfeed(request):
    comment_count_list = [] #we're making lists to keep track of the NUMBER of comments and likes
    like_count_list = []
    posts = Post.objects.filter(username=request.user).order_by('-date_posted') #gets all the post by a certain user and puts the newest posts at the top using the "-" in front of data_posted
    for p in posts:
        c_count = Comment.objects.filter(post=p).count() #get the count of comments linked to each post
        l_count = Like.objects.filter(post=p).count() #get the count of likes linked to each post
        comment_count_list.append(c_count)
        like_count_list.append(l_count)

    zipped_list = zip(posts,comment_count_list,like_count_list) #gives you the comments and likes for each post and you can iterate through all at once

    context = {'posts':posts,'zipped_list':zipped_list} #we want the actual post to show up and the number of likes and comments
    return render(request, 'FeedApp/myfeed.html', context)

@login_required #this is a decorator. It prevents unauthorized access to pages that follow
def new_post(request):
    if request.method != 'POST':
        form = PostForm() #blank form if it's a get request
    else:
        form = PostForm(request.POST,request.FILES) #if it's a post request we save the post to the database. We get the post and the files.
        if form.is_valid():
            new_post = form.save(commit=False) #creating an instance but not writing it to the database yet, because we're missing information
            new_post.username = request.user
            new_post.save() #write to database
            return redirect('FeedApp:myfeed') #keep them at the feed page
    
    context = {'form':form}
    return render(request, 'FeedApp/new_post.html', context)


