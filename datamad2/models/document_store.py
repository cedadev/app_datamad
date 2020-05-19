# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '22 Apr 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
import hashlib
import os


class MediaFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        return name

    def _save(self, name, content):
        if self.exists(name):
            raise ValidationError('File already exists: %s' % name)

        return super(MediaFileSystemStorage, self)._save(name, content)


def file_name(instance, filename):
    # h = instance.checksum
    grant_ref = (instance.grant.grant_ref).replace('/', '_')
    # basename, ext = os.path.splitext(filename)
    return os.path.join('documents', grant_ref, filename)


class Document(models.Model):
    # ordering by creation date
    class Meta:
        ordering = ['-last_modified']

    title = models.CharField(max_length=100, blank=True, help_text='If left blank the title will be the name of the file.')
    type = models.CharField(choices=(("support", "Support"), ("dmp", "DMP")), max_length=100)
    upload = models.FileField(upload_to=file_name, storage=MediaFileSystemStorage())
    last_modified = models.DateTimeField(auto_now=True)
    grant = models.ForeignKey('Grant', on_delete=models.CASCADE)
    checksum = models.CharField(max_length=100, blank=True)

    def set_title(self):
        """
        Default the title to be the file name if nothing set on upload
        """
        if not self.title:
            self.title = self.upload.name

    def generate_checksum(self):
        """
        Generate an MD5 checksum to check for file changes
        """
        if not self.pk:
            md5 = hashlib.md5()
            for chunk in self.upload.chunks():
                md5.update(chunk)
            self.checksum = md5.hexdigest()

    def save(self, *args, **kwargs):
        self.set_title()
        self.generate_checksum()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"
