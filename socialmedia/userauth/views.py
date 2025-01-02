 
from  django.shortcuts  import  render, redirect , get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from . models import Profile , Post , Followers, Follow , LikePost
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import FollowRequest,Chat, Message
from django.db.models import Q
import json
from django.contrib.auth.decorators import login_required 
from django.http import HttpResponseForbidden
 
def signup(request):
    innvalid = None 
    try:
        if request.method == 'POST':
            fnm=request.POST.get('fnm')
            emailid=request.POST.get('emailid') 
            pwd=request.POST.get('pwd')
            print(fnm,emailid,pwd)
            my_user=User.objects.create_user(fnm,emailid,pwd)
            my_user.save()
            user_model = User.objects.get(username=fnm)
            new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
            new_profile.save()
            if my_user is not None:
                login(request,my_user)
                # return redirect('/')
            return redirect('/loginn')   
    except:
        innvalid="User already exists"
    return render(request, 'signup.html',{'innvalid':innvalid})


def loginn(request):
    try:
        if request.method == 'POST':
            fnm = request.POST.get('fnm')
            pwd = request.POST.get('pwd')
            userr = authenticate(request,username=fnm,password=pwd)
            if userr is not None:
                login(request,userr)
                
            return redirect('/home')
    except:
        innvalid = "Invalid Credentials"
        return render(request, 'loginn.html',{'innvalid':innvalid})
    return render(request, 'loginn.html')
 
@login_required(login_url='/loginn')
def logoutt(request):
    logout(request)
    return redirect('/loginn')

@login_required(login_url='/loginn')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/home')
    else:
        return redirect('/home')
    

  
@login_required(login_url='/loginn')
def profile(request, id_user): 
    user_object = User.objects.get(username=id_user) 
    profile = Profile.objects.get(user=request.user) 
    user_profile = Profile.objects.get(user=user_object) 
    user_posts = Post.objects.filter(user=id_user).order_by('-created_at') 
    user_post_length = user_posts.count()

    follower = request.user.username
    user = id_user
    if Followers.objects.filter(follower=follower, user=user).first():
        follow_unfollow = 'Unfollow'
    else:
        follow_unfollow='Follow'
    
    user_followers = len(Followers.objects.filter(user=id_user))
    # print(Followers.objects.filter(user=id_user), "user_followers ++++++++++++++++++++++")
    user_following = len(Followers.objects.filter(follower=id_user))

    # Context for the template
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'profile': profile,
        'follow_unfollow' : follow_unfollow,
        'user_followers': user_followers,
        'user_following' : user_following,
    }

    if request.user.username == id_user:
        if request.method == 'POST':
            if request.FILES.get('image')==None:
                image=user_profile.profileimg
                bio=request.POST['bio']
                location = request.POST['location']

                user_profile.profileimg=image
                user_profile.bio=bio
                user_profile.location=location
                user_profile.save()

            if request.FILES.get('image')!=None:
                image=request.FILES.get('image')
                bio=request.POST['bio']
                location = request.POST['location']

                user_profile.profileimg=image
                user_profile.bio=bio
                user_profile.location=location
                user_profile.save()
            return redirect('/profile/'+id_user)
        else:
            return render(request, 'profile.html', context)
        
    # Handle follow/unfollow logic
    if request.method == 'POST' and 'follow_button' in request.POST:
        if follow_unfollow == 'Follow':
            # Create a new follow relationship
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()
        elif follow_unfollow == 'Follow':
            # Delete the follow relationship
            unfollow = Followers.objects.get(follower=follower, user=user)
            unfollow.delete()
        
        return redirect('/profile/' + id_user)
            

    return render(request, 'profile.html', context)

   
@login_required(login_url='/loginn')
def home(request): 
    following_users = Followers.objects.filter(follower=request.user.username).values_list('user',flat=True) 
    post = Post.objects.filter(Q(user=request.user.username) | Q(user__in=following_users)).order_by('-created_at')
    profile = Profile.objects.get(user=request.user)
    context = {
        'post':post,
        'profile':profile, 
    }

    return render(request, 'main.html', context)

@login_required(login_url='/loginn')  
def explore(request):
    post = Post.objects.all().order_by('-created_at')
    context = {
        'post':post
    }
    return render(request, 'explore.html', context )


def likes(request, id):
    if request.method == 'GET':
        username = request.user.username
        post = get_object_or_404(Post, id=id)

        like_filter = LikePost.objects.filter(post_id = id, username=username).first()
        if like_filter is None:
            new_like = LikePost.objects.create(post_id=id, username=username)
            post.no_of_likes = post.no_of_likes + 1
            # return redirect('/home')
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes + 1
            # return redirect('/home')
        post.save()
        return redirect('/home')

def home_posts(request, id):
    post = Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context = {
        'post':post,
        'profile':profile
    }
    return render(request, 'main.html', context)




@login_required(login_url='/loginn')
def follow(request ):
    if request.method == 'POST':
        follower = request.user  # The logged-in user
        user_username = request.POST.get('user')  # Get the target username from the request

        if not user_username:
            return JsonResponse({'message': 'Target user not specified'}, status=400)

        user = get_object_or_404(User, username=user_username)  # Get the target user

        # Check if the user is already being followed
        if Followers.objects.filter(follower=follower.username, user=user.username).exists():
            # Unfollow: Delete the follower relationship
            Followers.objects.filter(follower=follower.username, user=user.username).delete()
            # Optionally, delete any pending follow request
            FollowRequest.objects.filter(sender=follower, receiver=user).delete()
            # return JsonResponse({'message': 'Unfollowed successfully', 'action': 'Follow'}, status=200)
            return redirect('profile', id_user=user.username)  # Use `username` for `id_user`
 
             

        # Check if a follow request already exists
        if FollowRequest.objects.filter(sender=follower, receiver=user).exists():
            # return JsonResponse({'message': 'Follow request already sent'}, status=400)
            return redirect('profile', id_user=user.username)  # Use `username` for `id_user`
  
          

        # Create a follow request
        FollowRequest.objects.create(sender=follower, receiver=user)
        # return JsonResponse({'message': 'Follow request sent successfully', 'action': 'Unfollow'}, status=200)
        return redirect('profile', id_user=user.username)  # Use `username` for `id_user`
 
        

    return JsonResponse({'message': 'Invalid request method'}, status=400)
 
@login_required(login_url='/loginn')
def followers_list(request, username):
    # Get the user profile by username
    user_profile = get_object_or_404(Profile, user__username=username)
    # print(user_profile, "+++++++")
    
    # Get all followers for this user
    followers = Followers.objects.filter(user=user_profile.user)
    # print(followers,"++++++++")

    # Get the actual follower users
    follower_users = [follower.follower for follower in followers]
    # print(follower_users,"++++++++")

    return render(request, 'followers_list.html', {
        'user_profile': user_profile,
        'followers': follower_users,  # Pass the list of user objects instead of Followerss objects
    }) 

 

@login_required(login_url='/loginn')
def following_list(request):
    # Get the logged-in user
    current_user = request.user

    # Fetch the users this user is following
    following_relationships = Followers.objects.filter(follower=current_user.username)

    # Extract the usernames of the users being followed
    following_users = [User.objects.get(username=follow.user) for follow in following_relationships]

    return render(request, 'following_list.html', {
        'following_users': following_users,
    })




@login_required(login_url='/loginn')
def follow_profile(request, username):
    # Get the user object for the username
    profile_to_follow = get_object_or_404(User, username=username)
    current_user = request.user

    # Check if the current user is already following the user
    follow, created = Followers.objects.get_or_create(user=profile_to_follow, follower=current_user)

    if not created:
        # If the follow relationship already exists, unfollow
        follow.delete()

    return redirect('followers_list', username=profile_to_follow.username)

 
@login_required(login_url='/loginn')
def show_requests(request):
    # Fetch the follow requests where the logged-in user is the receiver
    follow_requests = FollowRequest.objects.filter(receiver=request.user)

    # Return the follow requests to the template
    return render(request, 'show_requests.html', {'follow_requests': follow_requests})
 
@login_required(login_url='/loginn') 
def accept_request(request, request_id):
    # Get the follow request object, ensuring the receiver is the current user
    follow_request = get_object_or_404(FollowRequest, id=request_id, receiver=request.user)

    # Add the sender to the receiver's followers
    # Using the actual User objects instead of usernames
    Followers.objects.create(follower=follow_request.sender, user=follow_request.receiver)
    
    # Delete the follow request after acceptance
    follow_request.delete()

    # Redirect to the page showing the current follow requests (or any other page)
    return redirect('show_requests')

@login_required(login_url='/loginn') 
def decline_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, id=request_id, receiver=request.user)

    # Delete the follow request after decline
    follow_request.delete()

    # Redirect back to the follow requests page
    return redirect('show_requests')

@login_required(login_url='/loginn')   
def delete(request, id):
    post = Post.objects.get(id=id)
    post.delete()
    return redirect('/profile/' +request.user.username)

@login_required(login_url='/loginn')
def search_results(request):
    query = request.GET.get('q', '').strip()  # Default to an empty string if 'q' is None
    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)

    if query:  # Only perform the search if a query exists
        users = Profile.objects.filter(user__username__icontains=query)
        posts = Post.objects.filter(caption__icontains=query)

    context = {
        'query': query,
        'users': users,
        'posts': posts
    }

    return render(request, 'search_user.html', context)
@login_required(login_url='/loginn')
def chat_page(request, username):
    user = request.user
    other_user = get_object_or_404(User, username=username)

    # Get or create the chat between the two users
    chat = Chat.objects.filter(
        (Q(user1=user) & Q(user2=other_user)) | (Q(user1=other_user) & Q(user2=user))
    ).first()

    if not chat:
        chat = Chat.objects.create(user1=user, user2=other_user)

    # Debugging print statement to check fields being queried
    print(chat.messages.order_by('timestamp').query)

    # Fetch messages for the chat, ordered by timestamp
    messages = chat.messages.order_by('timestamp').values(
        'sender__username', 'content', 'timestamp'
    )

    # Format messages for display
    formatted_messages = [
        {
            'sender': 'You' if msg['sender__username'] == user.username else msg['sender__username'],
            'content': msg['content'],
            'timestamp': msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
        }
        for msg in messages
    ]

    return render(request, 'chat.html', {
        'chat': chat,
        'other_user': other_user,
        'messages': formatted_messages,
    })



@login_required(login_url='/loginn')
def fetch_messages(request, chat_id):
    if request.method == 'GET':
        chat = get_object_or_404(Chat, id=chat_id)

        # Verify the user is part of the chat
        if request.user not in [chat.user1, chat.user2]:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        # Fetch and format messages
        messages = chat.messages.order_by('timestamp').values('sender__username', 'content', 'timestamp')
        return JsonResponse({'messages': list(messages)})



@login_required(login_url='/loginn')
def post_message(request, chat_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()

        if not message_content:
            return JsonResponse({'error': 'Message content is required'}, status=400)

        chat = get_object_or_404(Chat, id=chat_id)

        # Verify the user is part of the chat
        if request.user not in [chat.user1, chat.user2]:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        # Create and save the message
        message = Message.objects.create(chat=chat, sender=request.user, content=message_content)

        # Respond with the new message details
        return JsonResponse({
            'sender': message.sender.username,
            'message': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        })

@login_required(login_url='/loginn')    
def follow_user(request):
    if request.method == 'POST':
        # Get the user to follow and the current user (follower)
        user_to_follow = get_object_or_404(User, username=request.POST['user'])
        follower = get_object_or_404(User, username=request.POST['follower'])

        # Check if the user is already following this user
        existing_follow = Follow.objects.filter(user=user_to_follow, follower=follower).first()

        if existing_follow:
            # If the follow already exists, unfollow
            existing_follow.delete()
        else:
            # Otherwise, create a new follow relationship
            Follow.objects.create(user=user_to_follow, follower=follower)

        # Redirect to the user's profile page after following/unfollowing
        return redirect('profile', username=user_to_follow.username)