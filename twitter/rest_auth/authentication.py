import jwt
from django.conf import settings
from rest_framework import status, exceptions
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from rest_framework.response import Response

from .models import TwitterUser


class TwitterTokenAuthentication(BaseAuthentication):
    model = None

    def get_model(self):
        return TwitterUser

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'tweet' or auth is None or len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1]
            if token == "null":
                msg = 'Null token not allowed'
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        model = self.get_model()
        payload = jwt.decode(token, settings.ENCRYPTION_SECRET_KEY)
        email = payload['email']
        username = payload['username']
        msg = {'Error': "Token mismatch", 'status': "401"}
        try:
            user = model.objects.filter(
                email=email,
                username=username,
                is_active=True
            )
            if user:
                user = user.first()
            else:
                msg = 'Invalid Token'
                raise exceptions.AuthenticationFailed(msg)

            if not str(user.user_token.token) == str(token) or user.user_token.is_expired:
                raise exceptions.AuthenticationFailed(msg)

        except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
            return Response({'details': "Token is invalid"}, status=status.HTTP_403_FORBIDDEN)

        return user, token

    def authenticate_header(self, request):
        return 'TWEET'
