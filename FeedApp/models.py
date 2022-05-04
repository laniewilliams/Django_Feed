from django.db import models #this file describes how our database is setup
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model): #user profile whenever a new user is created
    first_name = models.CharField(max_length=200,blank=True)
    last_name = models.CharField(max_length=200,blank=True)
    email = models.EmailField(max_length=300,blank=True)
    dob = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE) #1:1 field with the user entity that comes with Django. We're associating each profile to a user.
    friends = models.ManyToManyField(User,blank=True, related_name='friends') #a profile can have many friends (M:M field)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)


    def __str__(self): #will return the username from the user
        return f"{self.user.username}"

STATUS_CHOICES = (
    ('sent','sent'),
    ('accepted','accepted')
)

class Relationship(models.Model): #allows us to establish a relationship between 2 profiles
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender') #sender is a FK to the profile class
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver') #receiver is a FK to the profile class
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="send") #once they accepted, the status would be changed to accepted
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    

class Post(models.Model): #allows the user to make posts
    description = models.CharField(max_length=255, blank=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE) #want to know who is making this post
    image = models.ImageField(upload_to='images',blank=True) #will not work if you don't have pillow installed, images is the images folder. all uploaded images will be saved there
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self): #return the description of the post
        return self.description

class Comment(models.Model): #allows the user to comment on a post
    post = models.ForeignKey(Post, on_delete=models.CASCADE) #want to know which post was commented on
    username = models.ForeignKey(User, related_name='details', on_delete=models.CASCADE) #who is commenting on the post
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True,blank=True)

    def __str__(self):
        return self.text
    
    
class Like(models.Model): #allows user to like posts
	username = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE) #who liked it
	post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE) #what post did they like


