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
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail


class DataCentre(models.Model):

    name = models.CharField(max_length=100, null=True, unique=True, verbose_name='Datacentre Name')
    jira_project = models.CharField(max_length=100, blank=True, verbose_name='Data Management JIRA Project')

    def __str__(self):
        return f"{self.name}"

    @property
    def jiraissuetype(self):
        return self.jiraissuetype_set.first()


class UserManager(BaseUserManager):
    def _create_user(self, email, password, data_centre=None, **extra_fields):
        """
        Creates and saves a user with given email and password
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email), 
            **extra_fields)

        # Set the username to match the email
        user.username = self.normalize_email(email)
        user.set_password(password)
        # causing create superuser to fail, so data centre only included for non superusers
        if not user.is_superuser:
            user.data_centre = DataCentre.objects.get(name=data_centre)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, datacentre=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, datacentre, **extra_fields)

    def create_superuser(self, email, password=None, datacentre=None, **extra_fields):
        DataCentre.objects.get_or_create(name=None)

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, password, datacentre, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=255,
        unique=True,
    )
    username = models.EmailField(max_length=255)
    data_centre = models.ForeignKey('DataCentre', on_delete=models.SET_NULL, null=True, blank=True, to_field='name')
    preferred_facets = models.TextField(null=True)
    preferred_sorting = models.TextField(null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False, verbose_name="Admin Status")
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    @property
    def preferences(self):
        preferred_facets = []
        preferred_sorting = None

        if self.preferred_facets:
            preferred_facets = self.preferred_facets.split(',')
        if self.preferred_sorting:
            preferred_sorting = self.preferred_sorting

        return {
            'preferred_facets': preferred_facets,
            'preferred_sorting': preferred_sorting
        }

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()