# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '11 Jun 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import django_tables2 as tables
from .models import Grant, DataProduct, User, Subtask
from .models.data_management_plans import PreservationPlan, DataFormat, DocumentTemplate
from django_tables2.utils import A


class GrantTable(tables.Table):
    visibility = tables.TemplateColumn(
        accessor='visible',
        template_name='datamad2/fields/visibility_field.html',
        verbose_name=''
    )

    grant_ref = tables.LinkColumn(
        viewname='grant_detail',
        args=[A('pk')],
        verbose_name='Grant Reference'
    )

    labels = tables.TemplateColumn(
        template_name='datamad2/fields/top_categories_field.html'
    )

    date_added = tables.DateTimeColumn(
        accessor='date_added',
        format='d M Y'
    )

    actual_start_date = tables.DateColumn(
        accessor='importedgrant__actual_start_date',
        format='d M Y'
    )

    actual_end_date = tables.DateColumn(
        accessor='importedgrant__actual_end_date',
        format='d M Y'
    )

    assigned_datacentre = tables.TemplateColumn(
        accessor='assigned_data_centre',
        template_name='datamad2/fields/assigned_datacentre_field.html',
        attrs={'td':{'class': 'align-middle text-center'}}
    )

    associated_grants = tables.TemplateColumn(
        template_name='datamad2/fields/associated_grants_field.html'
    )

    grant_title = tables.TemplateColumn(
        template_name='datamad2/fields/grant_title_field.html'
    )

    class Meta:
        model = Grant
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {
            'td': {
                'class': 'align-middle'
            }
        }
        fields = (
            'importedgrant__nerc_id',
            'importedgrant__grant_holder',
            'importedgrant__call',
        )
        sequence = (
            'visibility',
            'grant_ref',
            'importedgrant__nerc_id',
            'grant_title',
            'importedgrant__grant_holder',
            'importedgrant__call',
            'labels',
            'date_added',
            'actual_start_date',
            'actual_end_date',
            'assigned_datacentre',
            '...'
        )


class DataProductTableMixin(tables.Table):
    actions = tables.TemplateColumn(
        template_name='datamad2/fields/data_product_action_field.html'
    )
    added = tables.DateColumn(format='d/m/Y')
    modified = tables.DateTimeColumn(format('d/m/y H:i a'))


class DataProductMeta:
    model = DataProduct
    template_name = 'django_tables2/bootstrap-responsive.html'
    orderable = False
    empty_text = "No data products in this category"

    fields = [
        'added',
        'modified',
        'actions'
    ]

    sequence = [
        '...',
        'added',
        'modified',
        'actions'
    ]


class DigitalDataProductTable(DataProductTableMixin, tables.Table):

    delivery_date = tables.DateColumn(format='d/m/Y')
    embargo_date = tables.DateColumn(format='d/m/Y')
    data_volume = tables.TemplateColumn(
        template_name='datamad2/fields/data_product_volume_field.html'
    )


    class Meta(DataProductMeta):
        fields = [
            'description',
            'contact',
            'data_volume',
            'delivery_date',
            'embargo_date',
            'doi',
            'preservation_plan',
            'additional_comments',
            'data_product_type',
        ] + DataProductMeta.fields


class ModelSourceDataProductTable(DataProductTableMixin):
    class Meta(DataProductMeta):
        fields = [
            'name',
            'contact',
            'description',
            'sample_destination',
            'additional_comments',
        ] + DataProductMeta.fields


class PhysicalDataProductTable(DataProductTableMixin):

    delivery_date = tables.DateColumn(format='d/m/Y')

    class Meta(DataProductMeta):
        fields = [
            'name',
            'contact',
            'data_format',
            'issues',
            'delivery_date',
            'additional_comments',
        ] + DataProductMeta.fields


class HardcopyDataProductTable(DataProductTableMixin):

    delivery_date = tables.DateColumn(format='d/m/Y')

    class Meta(DataProductMeta):
        fields = [
            'name',
            'contact',
            'data_format',
            'issues',
            'delivery_date',
            'additional_comments',
        ] + DataProductMeta.fields


class ThirdPartyDataProductTable(DataProductTableMixin):

    data_volume = tables.TemplateColumn(
        template_name='datamad2/fields/data_product_volume_field.html'
    )

    class Meta(DataProductMeta):
        fields = [
            'name',
            'contact',
            'data_location',
            'description',
            'data_volume',
            'responsibility',
            'issues',
            'additional_comments',
            'added',
            'modified',
            'actions'
        ]


class PreservationPlanTable(tables.Table):

    actions = tables.TemplateColumn(
        template_name='datamad2/fields/preservation_plan_action_field.html'
    )

    class Meta:
        model= PreservationPlan
        template_name = 'django_tables2/bootstrap-responsive.html'
        orderable = False
        empty_text = "No preservations plans to display"

        fields = [
            'short_name',
            'description'
        ]

        sequence = (
            '...',
            'actions'
        )

class DataFormatTable(tables.Table):

    actions = tables.TemplateColumn(
        template_name='datamad2/fields/data_format_action_field.html'
    )

    class Meta:
        model= DataFormat
        template_name = 'django_tables2/bootstrap-responsive.html'
        orderable = False
        empty_text = "No data formats to display"

        fields = [
            'format',
        ]

        sequence = (
            '...',
            'actions'
        )

class DocumentTemplateTable(tables.Table):

    actions = tables.TemplateColumn(
        template_name='datamad2/fields/document_template_action_field.html'
    )

    class Meta:
        model= DocumentTemplate
        template_name = 'django_tables2/bootstrap-responsive.html'
        orderable = False
        empty_text = "No data formats to display"

        fields = [
            'name',
            'description',
            'type'
        ]

        sequence = (
            '...',
            'actions'
        )


class UserTable(tables.Table):

    actions = tables.TemplateColumn(
        template_name='datamad2/fields/user_action_field.html',
        attrs={
            'td': {},
            'th': {}
        }
    )

    admin_status = tables.TemplateColumn(
        accessor=A('is_admin'),
        template_name='datamad2/fields/boolean_field.html',
        attrs={
            'td': {
                'class': 'text-center'
            },
            'th': {
                'class': 'text-center'
            }
        }
    )

    class Meta:
        model = User
        orderable = False
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {
            'td': {
                'class': 'text-center'
            },
            'th': {
                'class': 'text-center'
            }
        }
        sequence = ("...", "actions")
        fields = [
            'first_name',
            'last_name',
            'email',
        ]


class SubtaskTable(tables.Table):

    actions = tables.TemplateColumn(
        template_name='datamad2/fields/subtask_action_field.html',
        attrs={
            'td': {},
            'th': {}
        }
    )

    class Meta:
        model = Subtask
        orderable = False
        template_name = 'django_tables2/bootstrap-responsive.html'
        empty_text = "No subtasks to display"
        attrs = {
            'td': {
                'class': 'text-center'
            },
            'th': {
                'class': 'text-center'
            }
        }
        sequence = ("...", "actions")
        fields = [
            'name',
            'schedule_time',
            'ref_time',
        ]