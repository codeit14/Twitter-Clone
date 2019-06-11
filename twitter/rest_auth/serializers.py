from django.contrib.auth.hashers import make_password
from django.db.models import Q
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import TwitterUser


class TwitterUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=25, required=True)
    last_name = serializers.CharField(max_length=25, required=True)
    username = serializers.CharField(max_length=25, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'}, required=True)
    contact_number = PhoneNumberField(required=True)
    country_code = serializers.CharField(max_length=15, default="91")

    def validate(self, attrs):
        if not (attrs.get('email') and attrs.get('password') and attrs.get('first_name') and attrs.get('last_name')
                and attrs.get('contact_number')):
            msg = 'Field should not be empty'
            raise ValidationError(msg)
        users = TwitterUser.objects.filter(Q(email=attrs.get('email')) | Q(contact_number=attrs.get('contact_number')) |
                                           Q(username=attrs.get('username'))).count()
        if users:
            msg = 'Account already taken'
            raise ValidationError(msg)

        return attrs

    def create(self, validated_data):
            first_name = validated_data.pop("first_name")
            last_name = validated_data.pop("last_name")
            username = validated_data.pop("username")
            email = validated_data.pop("email")
            password = validated_data.pop("password")
            contact_number = validated_data.pop("contact_number")

            data = {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email": email,
                "password": make_password(password),
                "contact_number": contact_number
            }
            instance = TwitterUser.objects.create(**data)
            return instance

    class Meta:
        model = TwitterUser
        fields = "__all__"


class TwitterUserDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=25, required=True)
    email = serializers.EmailField(required=True)
    contact_number = PhoneNumberField(required=True)
    country_code = serializers.CharField(max_length=15, default="91")
    no_of_users_following = serializers.SerializerMethodField()
    no_of_users_followed = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    no_of_tweets = serializers.SerializerMethodField()

    @staticmethod
    def get_no_of_users_following(object):
        return object.following_users.all().count()

    @staticmethod
    def get_no_of_users_followed(object):
        return object.followed_users.all().count()

    @staticmethod
    def get_full_name(object):
        return object.first_name + " " + object.last_name

    @staticmethod
    def get_no_of_tweets(object):
        return object.tweets.all().count() + object.retweets.all().count()

    class Meta:
        model = TwitterUser
        fields = ("username", "email", "contact_number", "country_code", "no_of_users_following",
                  "no_of_users_followed", "full_name", "followed_users", "following_users",)
