from django.db import models
from model_utils.models import TimeStampedModel
import uuid
from rest_auth.models import TwitterUser


class TweetFeed(TimeStampedModel):
    tweet_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    description = models.TextField()
    user = models.ForeignKey(TwitterUser, related_name='tweets', on_delete=models.CASCADE, null=True)
    liked_by = models.ManyToManyField(TwitterUser, related_name='liked_tweets', null=True)
    retweeted_by = models.ManyToManyField(TwitterUser, related_name='retweeted_tweets', null=True,
                                          through='ReTweetFeed')


class Attachment(TimeStampedModel):
    attachment_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    file_name = models.TextField(null=True)
    data = models.TextField(null=True)
    file_size = models.IntegerField(null=True)
    mime_type = models.CharField(max_length=200, null=True)
    tweet = models.ForeignKey(TweetFeed, on_delete=models.CASCADE, related_name='attachments', null=True)


class ReTweetFeed(TimeStampedModel):
    retweet_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    tweet = models.ForeignKey(TweetFeed, on_delete=models.CASCADE, related_name='retweets', null=True)
    user = models.ForeignKey(TwitterUser, on_delete=models.CASCADE, related_name='retweets', null=True)
    comment = models.TextField(null=True)

