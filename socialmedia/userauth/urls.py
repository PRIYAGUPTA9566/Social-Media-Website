from django.contrib import admin
from django.urls import path
from socialmedia import settings
from userauth import views
from django.conf.urls.static import static 

urlpatterns = [
    path('home/',views.home), 
    path('',views.signup),
    path('loginn/',views.loginn),
    path('logoutt/', views.logoutt),
    path('home/upload', views.upload, name='upload'),
    path('like-post/<str:id>', views.likes, name='like-post'),
    path('home<str:id>', views.home_posts),
    path('explore',views.explore), 
    path('profile/<str:id_user>', views.profile, name='profile'), 
    path('followers/<str:username>/', views.followers_list, name='followers_list'), 
    path('following/', views.following_list, name='following_list'),
    path('follow/<str:username>/', views.follow_profile, name='follow_profile'),
    path('follow',views.follow, name='follow'),
    path('delete/<str:id>', views.delete),
    path('search-results/',views.search_results,name='search_results'),
    path('show_requests/', views.show_requests, name='show_requests'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('decline_request/<int:request_id>/', views.decline_request, name='decline_request'), 
    path('chat/<str:username>/', views.chat_page, name='chat_page'),
    path('fetch_messages/<int:chat_id>/', views.fetch_messages, name='fetch_messages'),
    path('post_message/<int:chat_id>/', views.post_message, name='post_message'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'), 
]

admin.site.site_header = "Social Media"
admin.site.site_title = "Social Media" 

