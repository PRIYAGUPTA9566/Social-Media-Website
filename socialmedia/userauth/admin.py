from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Followers)
admin.site.register(Follow)
admin.site.register(FollowRequest)
admin.site.register(Chat)
admin.site.register(Message) 
admin.site.register(LikePost)