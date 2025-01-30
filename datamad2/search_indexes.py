# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '14 May 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from datamad2.models.grants import Grant, ImportedGrant
from haystack import indexes
from datamad2.utils import call_strip_date


class GrantIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    grant_ref = indexes.CharField(model_attr='grant_ref', faceted=True)
    assigned_datacentre = indexes.CharField(model_attr='assigned_data_centre', null=True, faceted=True, default='Unassigned')
    other_datacentre = indexes.CharField(model_attr='other_data_centre', null=True, faceted=True, default='Unassigned')
    labels = indexes.CharField(model_attr='importedgrant__labels', null=True, faceted=True, default='Unassigned')
    secondary_classification = indexes.CharField(model_attr='importedgrant__secondary_classification', null=True, faceted=True, default='Unassigned')
    grant_status = indexes.CharField(model_attr='importedgrant__grant_status', null=True, faceted=True, default='Unassigned')
    grant_type = indexes.CharField(model_attr='importedgrant__grant_type', null=True, faceted=True, default='Unassigned')
    scheme = indexes.CharField(model_attr='importedgrant__scheme', null=True, faceted=True, default='Unassigned')
    call = indexes.CharField(model_attr='importedgrant__call', null=True, faceted=True, default='Unassigned')
    facility = indexes.CharField(model_attr='importedgrant__facility', null=True, faceted=True, default='Unassigned')
    lead = indexes.CharField(model_attr='importedgrant__lead_grant', null=True, faceted=True)
    ncas = indexes.CharField(model_attr='importedgrant__ncas', null=True, faceted=True)
    nceo = indexes.CharField(model_attr='importedgrant__nceo', null=True, faceted=True)
    overall_score = indexes.IntegerField(model_attr='importedgrant__overall_score', null=True)
    date_added = indexes.DateTimeField(model_attr='date_added', null=True)
    actual_start_date = indexes.DateField(model_attr='importedgrant__actual_start_date', null=True)
    dmp_agreed = indexes.CharField(model_attr='dmp_agreed', null=True, faceted=True)
    grant_title = indexes.CharField(model_attr='importedgrant__title', faceted=True)
    grant_holder = indexes.CharField(model_attr='importedgrant__grant_holder', faceted=True)
    documents_attached = indexes.CharField(faceted=True)
    visible = indexes.CharField(faceted=True)

    def get_model(self):
        return Grant

    def prepare_secondary_classification(self, obj):
        if not obj.importedgrant:
            return None
        
        secondary_classification = obj.importedgrant.secondary_classification
        if secondary_classification:
            return secondary_classification.split(':')[0]
        return secondary_classification

    def prepare_labels(self, obj):
        if not obj.importedgrant:
            return None
        
        all_labels = obj.importedgrant.labels
        labels = {area.split()[0] for area in all_labels['science_areas']}
        labels.update(
            set(
                all_labels.get('routing_classification',[])
            )
        )

        return list(labels)

    def prepare_facility(self, obj):
        if not obj.importedgrant:
            return None

        facility = obj.importedgrant.facility

        # Facilities can be \n separated but want to index them
        # individually
        facilities = []
        for f in facility.split('\n'):
            facilities.append(f.strip())

        if facilities:
            return facilities

    def prepare_call(self, obj):
        if not obj.importedgrant:
            return None

        call = obj.importedgrant.call

        return call_strip_date(call)

    def prepare_documents_attached(self, obj):
        return str(bool(obj.document_set.count()))

    def prepare_visible(self, obj):
        return str(obj.visible)