from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class UserManager(models.Manager):
    def create_user(self, username, email, password, first_name, last_name):
        username = username.strip().lower()
        if not username:
            raise ValueError("Username is required.")

        email = email.strip()
        if not email:
            raise ValueError("Email is required.")

        if not password:
            raise ValueError("Password is required.")

        first_name = first_name.strip()
        if not first_name:
            raise ValueError("First name is required.")
        
        last_name = last_name.strip()
        if not last_name:
            raise ValueError("Last name is required.")

        user = self.model(
            username = username,
            email = email,
            first_name = first_name,
            last_name = last_name
        )
        
        user.set_password(password)
        user.save(using = self._db)

        return user
            
        
    def create_superuser(self, username, email, password, first_name, last_name):
        user = self.create_user(
            username = username,
            email = email,
            first_name = first_name,
            last_name = last_name,
        )

        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        
        return user

        


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length = 255, unique = True)
    email = models.EmailField(max_length = 255, unique = True)
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True) 
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default = False)
            

    USERNAME_FIELD = "username"

    objects = UserManager()