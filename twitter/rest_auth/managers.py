from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):

        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        handle = extra_fields.pop('handle', "na")
        is_active = extra_fields.pop("is_active", True)
        user = self.model(email=email, is_staff=is_staff, is_active=is_active,
                          is_superuser=is_superuser, last_login=now, **extra_fields)
        user.set_password(password)
        user.date_joined = now
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        is_staff = extra_fields.pop("is_staff", False)
        return self._create_user(email, password, is_staff, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)
