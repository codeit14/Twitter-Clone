import base64
import io

import magic
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.renderers import MultiPartRenderer, JSONRenderer
from rest_framework.response import Response

from rest_auth.authentication import TwitterTokenAuthentication
from rest_auth.models import TwitterUser
from tweets.models import TweetFeed, Attachment, ReTweetFeed
from tweets.serializers import TweetFeedsSerializer, AttachmentSerializer, ReTweetSerializer


class TweetFeeds(CreateAPIView, DestroyAPIView, RetrieveAPIView):
    authentication_classes = (TwitterTokenAuthentication,)
    queryset = TweetFeed.objects.all()
    serializer_class = TweetFeedsSerializer
    parser_classes = (MultiPartParser,)
    renderer_classes = (MultiPartRenderer, JSONRenderer,)

    def destroy(self, request, *args, **kwargs):
        tweet = self.get_object()
        self.perform_destroy(tweet)
        return Response({'details': 'Tweet deleted'}, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, tweet):
        tweet.attachments.all().delete()
        tweet.delete()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        files = request.FILES
        files_list = list()
        for file in files:
            files_list.append({"file_data": base64.b64encode(files[file].read()).decode(),
                               "file_name": files[file].name})

        data = {
            'description': request.data.get('description')
        }

        serializer = TweetFeedsSerializer(data=data, context={'user': request.user, 'attachments': files_list})
        if serializer.is_valid():
            serializer.save()
            return Response({"details": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"details": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


class FollowUser(GenericAPIView):
    authentication_classes = (TwitterTokenAuthentication,)

    def put(self, request, pk):
        is_follow = request.data.get('is_follow')
        user_id = pk
        current_user = request.user
        user = TwitterUser.objects.filter(user_id=user_id)
        if user:
            user = user.first()
        else:
            return Response({'details': 'Invalid User id'}, status=status.HTTP_400_BAD_REQUEST)

        if is_follow:
            current_user.following_users.add(user)
            current_user.save()
            user.followed_users.add(current_user)
            user.save()
        else:
            current_user.following_users.remove(user)
            current_user.save()
            user.followed_users.remove(current_user)
            user.save()

        return Response({'details': 'Success'}, status=status.HTTP_200_OK)


class UserTweetFeeds(ListAPIView):
    serializer_class = TweetFeedsSerializer
    ordering = ('-created',)
    authentication_classes = (TwitterTokenAuthentication,)

    def get_queryset(self, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = TwitterUser.objects.filter(user_id=user_id)
        if not user:
            return None

        return user.first().tweets

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(*args, **kwargs)
        if not queryset:
            return Response({'details': 'Invalid User id'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'details': serializer.data}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AttachmentView(RetrieveAPIView):
    serializer_class = AttachmentSerializer
    authentication_classes = (TwitterTokenAuthentication,)
    queryset = Attachment.objects.all()

    @staticmethod
    def hasattr(dictionary, key):
        if key in dictionary and dictionary[key]:
            return True
        return False

    def retrieve(self, request, *args, **kwargs):
        attachment = self.get_object()
        serializer = self.get_serializer(attachment)
        if self.hasattr(serializer.data, 'data'):
            data = serializer.data['data']
            image = base64.b64decode(data)
            mime_type = magic.Magic(mime=True).from_buffer(io.BytesIO(image).read())
            return Response({"details": image}, content_type=mime_type, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Error in retrieving data"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class LikeTweetView(GenericAPIView):
    authentication_classes = (TwitterTokenAuthentication,)

    def put(self, request, pk):
        is_like = request.data.get('is_like')
        tweet_id = pk
        current_user = request.user
        tweet = TweetFeed.objects.filter(tweet_id=tweet_id)
        if tweet:
            tweet = tweet.first()
        else:
            return Response({'details': 'Invalid Tweet id'}, status=status.HTTP_400_BAD_REQUEST)

        if is_like:
            tweet.liked_by.add(current_user)
            tweet.save()
        else:
            tweet.liked_by.remove(current_user)
            tweet.save()

        return Response({'details': 'Success'}, status=status.HTTP_200_OK)


class ReTweetCreateView(CreateAPIView):
    serializer_class = ReTweetSerializer
    authentication_classes = (TwitterTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        comment = request.data.get('comment', "")
        tweet_id = kwargs.get('pk')
        current_user = request.user
        tweet = TweetFeed.objects.filter(tweet_id=tweet_id)
        if tweet:
            tweet = tweet.first()
        else:
            return Response({'details': 'Invalid Tweet id'}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            'comment': comment,
        }

        serializer = ReTweetSerializer(data=data, context={'user': current_user, 'tweet': tweet})
        if serializer.is_valid():
            serializer.save()
            retweet_id = serializer.data['retweet_id']
            return Response({'details': {'message': 'Retweeted Successfully', 'retweet_id': retweet_id}},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'details': 'Validation Error'}, status=status.HTTP_400_BAD_REQUEST)


class UserReTweetFeeds(ListAPIView):
    serializer_class = ReTweetSerializer
    ordering = ('-created',)
    authentication_classes = (TwitterTokenAuthentication,)

    def get_queryset(self, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = TwitterUser.objects.filter(user_id=user_id)
        if not user:
            return None

        return user.first().retweets

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(*args, **kwargs)
        if not queryset:
            return Response({'details': 'Invalid User id'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'details': serializer.data}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ReTweetDeleteRetrieveView(RetrieveAPIView, DestroyAPIView):
    queryset = ReTweetFeed.objects.all()
    serializer_class = ReTweetSerializer
    authentication_classes = (TwitterTokenAuthentication,)


