from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from PIL import Image


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=128)
    verification_token = models.CharField(
        max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='profile_pictures', blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.profile_picture:
            image = Image.open(self.profile_picture.path)

            # Redimensiona la imagen si es necesario
            max_size = (300, 300)
            if image.width > max_size[0] or image.height > max_size[1]:
                image.thumbnail(max_size)
                image.save(self.profile_picture.path)

    def image_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return ""

    def has_perm(self, perm, obj=None):
        "¿El usuario tiene un permiso específico?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "¿El usuario tiene permisos para ver la aplicación `app_label`?"
        # Simplest possible answer: Yes, always
        return True
