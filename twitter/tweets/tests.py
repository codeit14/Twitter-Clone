import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password

from rest_auth.models import TwitterUser, TwitterUserToken
from tweets.models import TweetFeed
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from tweets.views import FollowUser, LikeTweetView, TweetFeeds, ReTweetCreateView


class TestTweets(APITestCase):
    user1 = None
    user2 = None
    tweet = None

    def generate_token(self):
        payload = {
            'username': self.user1.username,
            'email': self.user1.email,
        }
        jwt_token = jwt.encode(payload, settings.ENCRYPTION_SECRET_KEY)
        TwitterUserToken.objects.create(token=jwt_token, user=self.user1)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user1 = TwitterUser.objects.create(email='151031vaibha@gmail.com', username='tidu11313',
                                                password=make_password('14141141'), contact_number='+918010222222',
                                                first_name='vaibhav', last_name='jain')
        self.user2 = TwitterUser.objects.create(email='15103vaibha@gmail.com', username='tidu1313',
                                                password=make_password('14141141'), contact_number='+918010222232',
                                                first_name='vai', last_name='jai')
        self.tweet = TweetFeed.objects.create(description='Test tweets', user=self.user1)
        self.generate_token()

    def test_follow_unfollow(self):
        request = self.factory.put('/tweets/follow/{}/'.format(self.user2.user_id),
                                   HTTP_AUTHORIZATION='TWEET {}'.format(self.user1.user_token.token.decode()))
        request.user = self.user1
        view = FollowUser.as_view()
        response = view(request, self.user2.user_id)
        self.assertTrue(response.status_code, 200)

    def test_like_unlike(self):
        request = self.factory.put('/tweets/tweet/like/{}/'.format(self.tweet.tweet_id),
                                   HTTP_AUTHORIZATION='TWEET {}'.format(self.user1.user_token.token.decode()))
        request.user = self.user1
        view = LikeTweetView.as_view()
        response = view(request, self.tweet.tweet_id)
        self.assertTrue(response.status_code, 200)

    def test_post_tweet(self):
        request = self.factory.post('/tweets/tweet/', {'description': 'Testing creation of tweets'},
                                    HTTP_AUTHORIZATION='TWEET {}'.format(self.user1.user_token.token.decode()))
        request.user = self.user1
        view = TweetFeeds.as_view()
        response = view(request)
        self.assertTrue(response.status_code, 201)

    def test_create_retweet(self):
        request = self.factory.post('/tweets/tweet/retweet/post/{}/'.format(self.tweet.tweet_id),
                                    {'comment': 'Testing creation of retweet'},
                                    HTTP_AUTHORIZATION='TWEET {}'.format(self.user1.user_token.token.decode()))
        request.user = self.user1
        view = ReTweetCreateView.as_view()
        response = view(request, {"pk": self.tweet.tweet_id})
        self.assertTrue(response.status_code, 201)
