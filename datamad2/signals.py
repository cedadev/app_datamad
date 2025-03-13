# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '08 Dec 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'
from haystack.signals import RealtimeSignalProcessor

from django.db.models.signals import post_save
from django.dispatch import receiver
from datamad2.models import Document
from datamad2.search_indexes import GrantIndex

@receiver(post_save, sender=Document)
def update_haystack_index(sender, **kwargs):
    """
    Signal processor to update the grant in the haystack index when a document is
    uploaded to a grant.
    :param sender:
    :param kwargs:
    """
    GrantIndex().update_object(kwargs['instance'].grant)