import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from .managers import CustomUserManager


class TwitterUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=250, db_index=True, unique=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=200)
    contact_number = PhoneNumberField()
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = CustomUserManager()
    following_users = models.ManyToManyField('self', symmetrical=False, related_name='user1', null=True)
    followed_users = models.ManyToManyField('self', symmetrical=False, related_name='user2', null=True)

    USERNAME_FIELD = 'username'

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        ordering = ('-date_joined',)

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email

    def get_full_name(self):
        if not self.last_name:
            return self.first_name
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        return self.email


class TwitterUserToken(TimeStampedModel):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True)
    token = models.TextField(null=True)
    is_expired = models.BooleanField(default=False)
    user = models.OneToOneField(TwitterUser, related_name="user_token", on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.token)


class UserNotifications(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    message = models.TextField()
    user = models.ForeignKey(TwitterUser, on_delete=models.CASCADE)
    is_delivered = models.BooleanField(default=False)
