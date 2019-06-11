import jwt

from django.conf import settings
from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_auth.authentication import TwitterTokenAuthentication
from rest_auth.models import TwitterUser, TwitterUserToken
from rest_auth.serializers import TwitterUserSerializer, TwitterUserDetailSerializer


class SignupView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TwitterUserSerializer
    user = None

    def generate_token(self):
        payload = {
            'username': self.user.username,
            'email': self.user.email,
        }
        jwt_token = jwt.encode(payload, settings.ENCRYPTION_SECRET_KEY)
        TwitterUserToken.objects.create(token=jwt_token, user=self.user)
        return jwt_token

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            self.user = TwitterUser.objects.get(username=serializer.validated_data['username'])
            return Response({"details": {"token": self.generate_token()}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"details": "Invalid Details"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    user = None

    def generate_token(self):
        payload = {
            'username': self.user.username,
            'email': self.user.email,
        }
        jwt_token = jwt.encode(payload, settings.ENCRYPTION_SECRET_KEY)
        self.user.user_token.token = jwt_token
        self.user.user_token.is_expired = False
        self.user.user_token.save()
        self.user.save()

        return jwt_token

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not (username and password):
            return Response({"details": "Invalid Username or Password"}, status=status.HTTP_400_BAD_REQUEST)

        user = TwitterUser.objects.filter(username=username)
        if user and check_password(password, user.first().password):
            self.user = user.first()
            self.user.is_active = True
            self.user.save()
            return Response({"details": {"token": self.generate_token()}}, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Invalid Username or Password"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    authentication_classes = (TwitterTokenAuthentication,)

    def get(self, request):
        user = request.user
        user.is_active = False
        user.user_token.is_expired = True
        user.user_token.save()
        user.save()

        return Response({"details": "Logout Successfully"}, status=status.HTTP_200_OK)


class UserDetailsAPIView(RetrieveAPIView):
    queryset = TwitterUser.objects.all()
    serializer_class = TwitterUserDetailSerializer
    authentication_classes = (TwitterTokenAuthentication,)
