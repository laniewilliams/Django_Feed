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
    return render(request, 'FeedApp/profile.html')
    



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


@login_required
def comments(request, post_id): #creating our own button and processing it manually
    if request.method == 'POST' and request.POST.get('btn1'): #checking to see if the request method was post and if the button was clicked. naming the button in the html as btn1
        comment = request.POST.get('comment') #getting whatever text is in the box
        Comment.objects.create(post_id=post_id,username=request.user,text=comment,date_added=date.today()) #this is creating a new row in the comment model

    comments = Comment.objects.filter(post=post_id)
    post = Post.objects.get(id=post_id)

    context = {'post':post,'comments':comments}
    return render(request, 'FeedApp/comments.html',context)


@login_required #this is a decorator. It prevents unauthorized access to pages that follow
def friendsfeed(request):
    comment_count_list = [] #we're making lists to keep track of the NUMBER of comments and likes
    like_count_list = []
    friends = Profile.objects.filter(user=request.user).values('friends')
    posts = Post.objects.filter(username__in=friends).order_by('-date_posted') #gets all the post by a certain user and puts the newest posts at the top using the "-" in front of data_posted
    for p in posts:
        c_count = Comment.objects.filter(post=p).count() #get the count of comments linked to each post
        l_count = Like.objects.filter(post=p).count() #get the count of likes linked to each post
        comment_count_list.append(c_count)
        like_count_list.append(l_count)

    zipped_list = zip(posts,comment_count_list,like_count_list) #gives you the comments and likes for each post and you can iterate through all at once

    if request.method == 'POST' and request.POST.get('like'): #if the form was submitted and the button was pressed
        post_to_like = request.POST.get('like') #get the value
        print(post_to_like)
        like_already_exists = Like.objects.filter(post_id=post_to_like,username=request.user) #checking to see if a person has already liked it
        if not like_already_exists.exists(): #if the user dhasn't liked it, create a new like object
            Like.objects.create(post_id=post_to_like, username=request.user)
            return redirect('FeedApp:friendsfeed')

    context = {'posts':posts,'zipped_list':zipped_list} #we want the actual post to show up and the number of likes and comments
    return render(request, 'FeedApp/friendsfeed.html', context)

@login_required
def friends(request): #handles friend requests
    #get the admin_profile and user profile to create the first relationship
    admin_profile = Profile.objects.get(user=1) #the first person created is the admin
    user_profile = Profile.objects.get(user=request.user) 

    #to get my friends and their corresponding profiles
    user_friends = user_profile.friends.all()
    user_friends_profiles = Profile.objects.filter(user__in=user_friends) #this will be a list

    #to get Friend Requests sent
    user_relationships = Relationship.objects.filter(sender=user_profile) #all the people the user has sent requests to
    request_sent_profiles = user_relationships.values('receiver') #receiver is an attribute from the Relationship model, getting the profile of everyone we sent a request to

    # to get eligible profiles - exclude the user, their existing friends, and friend request sent already
    all_profiles = Profile.objects.exclude(user=request.user).exclude(id__in=user_friends_profiles).exclude(id__in=request_sent_profiles) #keep applying the exlude to each one

    # to get friend request received by the user
    request_received_profiles = Relationship.objects.filter(receiver=user_profile,status='sent') #friend requests that I have received

    #we need one row in the relationship model to perform the code above
    # if this is the first time to access the friend reqests page, create the first relationship
    # with the admin of the website so the admin is friends with everyone

    if not user_relationships.exists():  #'filter' works with exists but 'get' does not
        Relationship.objects.create(sender=user_profile,receiver=admin_profile,status='sent')
        
    # check to see WHICH submit button was pressed (sending a friend request or accepting a friend request)

    # this is to process alls send requests
    if request.method == 'POST' and request.POST.get('send_requests'):
        receivers = request.POST.getlist('send_requests') #we're getting a list because send_requests is going to be checkboxes in the html
                                                            # the value of the checkbox will be the id of the profile
        for receiver in receivers:
            receiver_profile = Profile.objects.get(id=receiver) #get the receiver profile and then create the relationship object
            Relationship.objects.create(sender=user_profile,receiver=receiver_profile,status='sent')
        return redirect('FeedApp:friends')

    # this is to process all receive requests
    
    if request.method == 'POST' and request.POST.get('receive_requests'): #how we know which button was pressed
        senders = request.POST.getlist('receive_requests') #list of all the senders (maybe you have many friend requests)
        for sender in senders:
            # update the relationship model for the sender to status 'accepted'
            Relationship.objects.filter(id=sender).update(status='accepted')

            #create a relationship object to access the sender's user id
            # to add to the friends list of the user
            relationship_obj = Relationship.objects.get(id=sender)
            user_profile.friends.add(relationship_obj.sender.user) #get the user id of the person that sent to request. Then we're adding that user to the friends of the current user

            # add the user to the friends list of the sender's profile
            relationship_obj.sender.friends.add(request.user)

    context = {'user_friends_profiles': user_friends_profiles, 'user_relationships':user_relationships,
                    'all_profiles':all_profiles, 'request_received_profiles':request_received_profiles}

    return render(request, 'FeedApp/friends.html', context)
