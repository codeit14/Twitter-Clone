from django.urls import path
from tweets.views import FollowUser, TweetFeeds, UserTweetFeeds, AttachmentView, LikeTweetView, ReTweetCreateView, \
    UserReTweetFeeds, ReTweetDeleteRetrieveView

urlpatterns = [
    path('follow/<uuid:pk>/', FollowUser.as_view()),
    path('tweet/', TweetFeeds.as_view()),
    path('tweet/<uuid:pk>/', TweetFeeds.as_view()),
    path('tweet/user/<uuid:pk>/', UserTweetFeeds.as_view()),
    path('attachment/<uuid:pk>/', AttachmentView.as_view()),
    path('tweet/like/<uuid:pk>/', LikeTweetView.as_view()),
    path('tweet/retweet/post/<uuid:pk>/', ReTweetCreateView.as_view()),
    path('tweet/retweet/user/<uuid:pk>/', UserReTweetFeeds.as_view()),
    path('tweet/retweet/read/<uuid:pk>/', ReTweetDeleteRetrieveView.as_view()),
    path('tweet/retweet/delete/<uuid:pk>/', ReTweetDeleteRetrieveView.as_view()),
]
