# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '08 Dec 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'
import sys
from haystack.signals import RealtimeSignalProcessor

from django.db.models.signals import post_save
from django.dispatch import receiver
from datamad2.models import Document
from datamad2.search_indexes import GrantIndex

class HaystackSignalProcessor(RealtimeSignalProcessor):
    """
    Handle signals to update search index when models are saved or deleted.

    This is just a wrapper around the default haystack signal processor that
    does nothing when run during tests or importing a fixture.

    It has been "borrowed" from the ceda_moles_django app
    """
    def allow(self):
        # Hack to avoid re-indexing whilst a fixture is being imported (outside
        # the tests). Otherwise this seems to lead to problems where objects
        # cannot be found
        if "loaddata" in sys.argv:
            return False

        return True

    def handle_save(self, *args, **kwargs):
        if self.allow():
            super(HaystackSignalProcessor, self).handle_save(*args, **kwargs)

    def handle_delete(self, *args, **kwargs):
        if self.allow():
            super(HaystackSignalProcessor, self).handle_delete(*args, **kwargs)


@receiver(post_save, sender=Document)
def update_haystack_index(sender, **kwargs):
    """
    Signal processor to update the grant in the haystack index when a document is
    uploaded to a grant.
    :param sender:
    :param kwargs:
    """
    GrantIndex().update_object(kwargs['instance'].grant)