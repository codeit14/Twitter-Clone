import base64
import io

import magic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from tweets.models import Attachment, TweetFeed, ReTweetFeed


class AttachmentSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        data = validated_data.pop("data")
        mime_type = validated_data.pop("mime_type")
        file_size = validated_data.pop("file_size")
        attachment_data = {
            'data': data,
            'mime_type': mime_type,
            'file_size': file_size,
        }
        instance = Attachment.objects.create(**attachment_data)

        return instance

    class Meta:
        model = Attachment
        fields = '__all__'


class TweetFeedsSerializer(serializers.ModelSerializer):
    attachments = serializers.SlugRelatedField(queryset=Attachment.objects.all(), slug_field='attachment_id', many=True,
                                               required=False)
    no_of_likes = serializers.SerializerMethodField()
    no_of_retweets = serializers.SerializerMethodField()

    @staticmethod
    def process_attachment(attachment):
        attachment_data = {
            "data": attachment["file_data"],
            "file_name": attachment["file_name"],
            "mime_type": magic.Magic(mime=True).from_buffer(io.BytesIO(base64.b64decode(attachment["file_data"])).
                                                            read()),
            "file_size": io.BytesIO(base64.b64decode(attachment["file_data"])).__sizeof__()
        }
        return attachment_data

    @staticmethod
    def get_no_of_likes(object):
        return object.liked_by.all().count()

    @staticmethod
    def get_no_of_retweets(object):
        return object.retweets.all().count()

    def validate(self, attrs):
        if not attrs.get('description') or len(attrs.get('description')) > 500:
            msg = 'Invalid value'
            raise ValidationError(msg)
        return attrs

    def create(self, validated_data):
        description = validated_data.pop('description')
        attachments = self.context.get('attachments', [])
        user = self.context.get("user")
        tweet = TweetFeed.objects.create(description=description, user=user)
        tweet_attachments = list()
        for attachment in attachments:
            attachment_data = self.process_attachment(attachment)
            tweet_attachments.append(AttachmentSerializer().create(attachment_data))

        if tweet_attachments:
            tweet.attachments.add(*tweet_attachments)

        return tweet

    class Meta:
        model = TweetFeed
        fields = ('tweet_id', 'description', 'attachments', "no_of_likes", "no_of_retweets",)


class ReTweetSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(max_length=500)

    def validate(self, attrs):
        if attrs.get('comment') and len(attrs.get('comment')) > 500:
            msg = 'Invalid value'
            raise ValidationError(msg)

        return attrs

    def create(self, validated_data):
        comment = validated_data.pop("comment", "")
        user = self.context.get("user")
        tweet = self.context.get("tweet")
        print(user, tweet)
        data = {
            "comment": comment,
            "user": user,
            "tweet": tweet
        }
        instance = ReTweetFeed.objects.create(**data)
        return instance

    class Meta:
        model = ReTweetFeed
        exclude = ('modified',)
