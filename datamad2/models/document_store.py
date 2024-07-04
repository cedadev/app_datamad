# encoding: utf-8
"""
Django models relating to the document store. File uploads attached to grant objects.
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
from django.conf import settings

DOCUMENT_TYPES = (
    ("support", "Support"),
    ("dmp", "DMP")
)

def file_name(instance, filename):
    h = instance.checksum
    grant_ref = (instance.grant.grant_ref).replace('/', '_')
    basename, ext = os.path.splitext(filename)
    return os.path.join('documents', grant_ref, f'{h}{ext}')


class MediaFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        return name

    def _save(self, name, content):
        if self.exists(name):
            raise ValidationError('File already uploaded')

        return super(MediaFileSystemStorage, self)._save(name, content)


class Document(models.Model):
    # ordering by creation date
    class Meta:
        ordering = ['-last_modified']

    title = models.CharField(max_length=100, blank=True)
    download_title = models.CharField(max_length=100, blank=True)
    type = models.CharField(choices=DOCUMENT_TYPES, max_length=100)
    upload = models.FileField(upload_to=file_name, storage=MediaFileSystemStorage())
    last_modified = models.DateTimeField(auto_now=True)
    grant = models.ForeignKey('Grant', on_delete=models.CASCADE)
    checksum = models.CharField(max_length=100, blank=True)
    tags = models.CharField(
        max_length=100,
        blank=True,
        help_text='Comma separated list of tags to be displayed with the file'
    )

    def set_title(self):
        """
        Set the title to be the file name
        """
        self.title = self.upload.name.split('.')[0]
        self.file_ext = self.upload.name.split('.')[1]

    def generate_checksum(self):
        """
        Generate an MD5 checksum to check for file changes
        """
        if not self.pk:
            md5 = hashlib.md5()
            for chunk in self.upload.chunks():
                md5.update(chunk)
            self.checksum = md5.hexdigest()

    def get_tags(self):
        return self.tags.split(',')

    def save(self, *args, **kwargs):
        self.set_title()
        self.generate_checksum()

        version = 1
        exists = Document.objects.filter(title=self.title).exists()

        if exists:
            while exists:
                version += 1
                exists = Document.objects.filter(title=(self.title + f' v{version}')).exists()

            title = self.title + f' v{version}'

        else:
            title = self.title

        self.title = title
        self.download_title = self.title + f'.{self.file_ext}'

        super().save(*args, **kwargs)

    def delete_file(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.upload.name))
        super(Document, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"
