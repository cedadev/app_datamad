# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '22 Apr 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class DataCentre(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    # name = models.CharField(max_length=200, blank=True, null=True,
    #                                          choices=(
    #                                              ("BODC", "BODC"),
    #                                              ("CEDA", "CEDA"),
    #                                              ("EIDC", "EIDC"),
    #                                              ("NGDC", "NGDC"),
    #                                              ("PDC", "PDC"),
    #                                              ("ADS", "ADS"),
    #                                          ))
    jira_project = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name}"


class UserManager(BaseUserManager):
    def _create_user(self, email, data_centre, password, **extra_fields):
        """
        Creates and saves a user with given email and password
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email), **extra_fields)

        # Set the username to match the email
        user.username = self.normalize_email(email)
        user.set_password(password)
        user.data_centre = DataCentre.objects.get(name=data_centre)
        user.save(using=self._db)
        return user

    def create_user(self, email, data_centre, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, data_centre, password, **extra_fields)

    def create_superuser(self, email, data_centre, password=None, **extra_fields):

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, data_centre, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.EmailField(max_length=255)
    data_centre = models.ForeignKey('DataCentre', on_delete=models.SET_NULL, null=True, blank=True, to_field='name')

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'data_centre']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin