# encoding: utf-8
"""
Django models relating to the NERC Grants

The Grant object holds customisable metadata edited by the DataMAD application,
the ImportedGrant object holds metadata which comes in from the NERC Siebel csv
import. This data is not edited by the DataMAD application.
"""
__author__ = 'Richard Smith'
__date__ = '22 Apr 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from django.db import models
from django.utils import timezone
import re
from model_utils.fields import MonitorField
import logging

SCIENCE_AREA_PATTERN = re.compile(r'(?P<area>\w+):\s?(?P<percentage>\d{1,3})%', re.M)
UNFUNDED_GRANT_TYPES = ['Strategy & Partnerships (KE)','Public Engagement Grants','NERC Strategic Capital Grants']

LOGGER = logging.getLogger(__name__)


class Grant(models.Model):

    # objects = GrantManager()

    # Grant Reference	Siebel	Unique identifier for the grant			GRANTREFERENCE
    grant_ref = models.CharField(max_length=50, default='', blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    # alt data contact email
    alt_data_contact = models.CharField(max_length=256, null=True, blank=True)
    # Alt Data Contact Email	Sharepoint	PI may not always be the contact for data related issues (although responsible for ensuring delivery of the data)
    alt_data_contact_email = models.EmailField(null=True, blank=True)
    # Alt Data Contact Phone No	Sharepoint	PI may not always be the contact for data related issues (although responsible for ensuring delivery of the data)
    alt_data_contact_phone = models.CharField(max_length=256, null=True, blank=True)
    # Assigned Data Centre	Sharepoint	E.g. NGDC
    assigned_data_centre = models.ForeignKey('DataCentre', null=True, on_delete=models.SET_NULL, related_name='assigned_data_centre', blank=True)
    # Other DC's Expecting Datasets	Sharepoint	E.g. PDC
    other_data_centre = models.ForeignKey('DataCentre', null=True, on_delete=models.SET_NULL, related_name='other_data_centre', blank=True)
    # Parent Grant	Siebel	Cross reference record to a lead grant record if the grant is covered by an
    # overarching DMP			PARENT_GRANT
    parent_grant = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_grant')
    # Hide Record	Sharepoint
    hide_record = models.BooleanField(null=True, blank=True)
    # DateContact with PI	Sharepoint	Date or Null
    date_contacted_pi = models.DateField(null=True, blank=True, verbose_name='Date contacted PI')
    # Will Grant Produce Data	Sharepoint	Y/N
    will_grant_produce_data = models.BooleanField(null=True, blank=True)
    # Datasets Delivered as per DMP?	Sharepoint	Yes, No or Null
    datasets_delivered = models.BooleanField(null=True, blank=True,
                                             help_text="Datasets Delivered as per DMP?")
    # Sanctions Recommended	Sharepoint	Yes, No or Null
    sanctions_recommended = models.BooleanField(null=True, blank=True)
    # C for S found?	Sharepoint	Yes/No/Grant not found
    case_for_support_found = models.BooleanField(null=True, blank=True)
    # claim status
    claimed = models.BooleanField(null=True, blank=True)
    # checks for updated imported grant (more than one version)
    updated_imported_grant = models.BooleanField(null=True, blank=True, editable=False, verbose_name='Grant updated')

    # programme - one programme can have many grants
    # programme = models.ForeignKey(to='dmp.Programme', blank=True, null=True, on_delete=models.PROTECT)

    science_area = models.CharField(max_length=256, null=True, blank=True)

    dmp_agreed = models.BooleanField(default=False)
    dmp_agreed_date = MonitorField(monitor='dmp_agreed', when=[True])

    @property
    def update_linked_grants(self):
        editable_grant_info = {"alt_data_contact": self.alt_data_contact, 
        "alt_data_contact_email": self.alt_data_contact_email, 
        "alt_data_contact_phone": self.alt_data_contact_phone, 
        "other_data_centre": self.other_data_centre, 
        "date_contacted_pi": self.date_contacted_pi, 
        "will_grant_produce_data": self.will_grant_produce_data, 
        "datasets_delivered": self.datasets_delivered, 
        "sanctions_recommended": self.sanctions_recommended, 
        "dmp_agreed": self.dmp_agreed}

        if self.parent_grant:
            # if there is a parent grant, I am a child grant. Update parent.
            Grant.objects.filter(pk=self.parent_grant.pk).update(**editable_grant_info)
            
            # Get and update siblings
            Grant.objects.filter(parent_grant=self.parent_grant).update(**editable_grant_info)

        # I might be a parent grant - get any child grants and update
        child_grants = self.child_grant.get_queryset()
        child_grants.update(**editable_grant_info)
        

    @property
    def importedgrant(self):
        """
        Return the most recent imported grant version for this grant
        :return:
        """
        return self.importedgrant_set.first()

    @property
    def funded_grant(self):
        """
        Determines whether a grant falls under the funded grants as defined by NERC
        datacentres
        :return: bool
        """
        ig = self.importedgrant
        if ig:
            return ig.grant_type not in UNFUNDED_GRANT_TYPES
        else:
            return True

    @property
    def visible(self):
        """
        Allows grants to be hidden. By default, only funded grants are visible
        but this can be overridden in special circumstances.
        :return: bool
        """

        # Default to use funding status for visibility
        if self.hide_record is None:
            return self.funded_grant

        return not self.hide_record

    @property
    def digital_data_products(self):
        """
        Return a set of digtial data products
        :return:
        """
        return self.dataproduct_set.filter(data_product_type='digital')

    @property
    def model_source_data_products(self):
        """
        Return a set of model source data products
        :return:
        """
        return self.dataproduct_set.filter(data_product_type='model_source')

    @property
    def physical_data_products(self):
        """
        Return a set of pysical data products
        :return:
        """
        return self.dataproduct_set.filter(data_product_type='physical')

    @property
    def hardcopy_data_products(self):
        """
        Return a set of hardcopy data products
        :return:
        """
        return self.dataproduct_set.filter(data_product_type='hardcopy')

    @property
    def third_party_data_products(self):
        """
        Return a set of third party data products
        :return:
        """
        return self.dataproduct_set.filter(data_product_type='third_party')

    @property
    def updated_date(self):
        return self.importedgrant.creation_date

    def save(self, *args, **kwargs):
        if self.assigned_data_centre is None:
            self.claimed = False
        else:
            self.claimed = True
        return super(Grant, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.grant_ref}: {self.importedgrant.title}"


class ImportedGrant(models.Model):
    # ordering by creation date
    class Meta:
        ordering = ['-creation_date']

    # Title	Siebel	Name of the grant			PROJECT_TITLE
    title = models.CharField(max_length=1024, default='')
    # Grant Reference	Siebel	Unique identifier for the grant			GRANTREFERENCE
    grant_ref = models.CharField(max_length=50, default='', blank=True)
    # UKRI Databank reference
    ukri_id = models.CharField(max_length=20, default='', blank=True)
    # NERC ID
    nerc_id = models.CharField(max_length=20, default='', blank=True)
    # grant to imported grant relationship
    grant = models.ForeignKey(to=Grant, on_delete=models.PROTECT, null=True, blank=True)
    # Grant Status	Siebel	Active/Closed			GRANT_STATUS
    grant_status = models.CharField(max_length=50, default="Active",
                                    choices=(("Active", "Active"), ("Closed", "Closed")))
    # date imported grant was created
    # creation_date = models.DateTimeField(auto_now_add=True)
    creation_date = models.DateTimeField(editable=False)
    # AmountAwarded	Siebel	Amount in pounds stirling			AMOUNT
    amount_awarded = models.FloatField(null=True, blank=True)
    # Call	Siebel	E.g. Standard Grant DEC06			CALL
    # ignore call for now
    call = models.CharField(max_length=1024, default='', blank=True)
    # grade / overall score
    overall_score = models.FloatField(null=True, blank=True)
    # Grant Type	Siebel	E.g. RM grants & fees			GRANT_TYPE
    facility = models.TextField(default='', blank=True)
    # The xls file run by RTS also contains Abstract and Objectives I presume these are from the GRANT
    grant_type = models.CharField(max_length=1024, default='', blank=True)
    # Scheme	Siebel	E.g. Standard Grant			SCHEME
    scheme = models.CharField(max_length=1024, default='', blank=True)
    # Lead Grant (Yes / No)	Siebel	Y/N			LEAD_GRANT
    lead_grant = models.BooleanField(null=True, blank=True)
    # Grant Holder	Siebel	Principal investigator (title, first name, surname)			GRANT_HOLDER
    grant_holder = models.CharField(max_length=256, default='', blank=True)
    # Department	Siebel	e.g. School of Geography, Earth and Environmental Sciences			DEPARTMENT
    department = models.CharField(max_length=256, default='', blank=True)
    # Research Organisation	Siebel	E.g. University of Birmingham			RESEARCH_ORG
    research_org = models.CharField(max_length=256, default='', blank=True)
    # Address 1	Siebel				ADDRESS1
    address1 = models.CharField(max_length=256, default='', blank=True)
    # Address 2	Siebel				ADDRESS2
    address2 = models.CharField(max_length=256, default='', blank=True)
    # City	Siebel				CITY
    city = models.CharField(max_length=256, default='', blank=True)
    # Post Code	Siebel				POSTCODE
    post_code = models.CharField(max_length=256, default='', blank=True)
    # E-Mail	Siebel	Email address			EMAIL
    email = models.EmailField(null=True, blank=True)
    # Work Number	Siebel	Work telephone number			WORK_NUMBER
    work_number = models.CharField(max_length=256, null=True, blank=True, default='')
    # data contact name
    data_contact = models.CharField(max_length=256, null=True, blank=True)
    # Data Contact Email	Siebel	PI may not always be the contact for data related issues
    # (although responsible for ensuring delivery of the data)			MISSING
    data_contact_email = models.EmailField(null=True, blank=True)
    # Data Contact Phone	Siebel	PI may not always be the contact for data related issues
    # (although responsible for ensuring delivery of the data)			MISSING
    data_contact_phone = models.CharField(max_length=256, null=True, blank=True, default='')
    # Routing Classification	Siebel	E.g. Earth, Freshwater			ROUTING_CLASSIFICATION
    routing_classification = models.CharField(max_length=200, blank=True, null=True,
                                              choices=(("Marine", "Marine"),
                                                       ("Earth", "Earth"),
                                                       ("Atmospheric", "Atmospheric"),
                                                       ("Freshwater", "Freshwater"),
                                                       ("Terrestrial", "Terrestrial"),
                                                       ("Earth Observation", "Earth Observation"),
                                                       ("Panel A", "Panel A"),
                                                       ("Panel B", "Panel B"),
                                                       ("Panel C", "Panel C"),
                                                       ("BODC", "BODC"),
                                                       ("CEDA", "CEDA"),
                                                       ("EIDC", "EIDC"),
                                                       ("NGDC", "NGDC"),
                                                       ("PDC", "PDC"),
                                                       ))
    # Secondary Classifications	Siebel	E.g. Co-funded 40%; Cross-Research Council: 100%			MISSING
    secondary_classification = models.TextField(null=True, blank=True)
    # Science Area	Siebel	E.g. Earth: 70% Marine:30%			MISSING
    science_area = models.CharField(max_length=256, null=True, blank=True)
    # NCAS (Yes/No)	Siebel	Y/N			NCAS
    ncas = models.BooleanField(blank=True, null=True)
    # NCEO (yes/No)	Siebel	Y/N			NCEO
    nceo = models.BooleanField(blank=True, null=True)
    # Comments	Siebel	Currently not in use			MISSING
    comments = models.TextField(default='', blank=True)
    # # Original Proposed Start Date Siebel Date field set to the same as Proposed
    # # Start Date when record first added to the list	MISSING
    # original_proposed_start_date = models.DateField(null=True, blank=True)
    # # Original Proposed End Date	Siebel	Date field  set to the same as Proposed End Date when record first
    # # added to the list			MISSING
    # original_proposed_end_date = models.DateField(null=True, blank=True)
    # Proposed Start date	Siebel				PROPOSED_ST_DT
    proposed_start_date = models.DateField(null=True, blank=True)
    # Proposed End date	Siebel				PROPOSED_END_DT
    proposed_end_date = models.DateField(null=True, blank=True)
    # Actual Start Date	Siebel				ACTUAL_START_DATE
    actual_start_date = models.DateField(null=True, blank=True)
    # Actual End Date	Siebel				ACTUAL_END_DATE
    actual_end_date = models.DateField(null=True, blank=True)
    # End Date Changed?	Siebel				MISSING
    # end_date_changed = models.BooleanField(null=True, blank=True)
    # # Start Date Changed?	Siebel				MISSING
    # start_date_changed = models.BooleanField(null=True, blank=True)
    # Abstract	Siebel		Truncated
    abstract = models.TextField(default='', blank=True)
    # Objectives	Siebel		Truncated
    objectives = models.TextField(default='', blank=True)

    # ordered by newest imported grant first

    # def compare(self, obj):
    #     # excluded_keys =  # tuple containing names of attributes to exclude
    #     return self._compare(self, obj) #, excluded_keys)

    # def get_previous(self):
    #     previous = self.get_previous_by_creation_date()
    #     if previous.exists():
    #         return self._compare(self, previous)
    #
    #
    # def _compare(self, obj1, obj2): #, excluded_keys):
    #     d1, d2 = obj1.__dict__, obj2.__dict__
    #     old, new = {}, {}
    #     for k, v in d1.items():
    #     #    if k in excluded_keys:
    #     #     continue
    #         try:
    #             if v != d2[k]:
    #                 old.update({k: v})
    #                 new.update({k: d2[k]})
    #         except KeyError:
    #             old.update({k: v})
    #
    #     return old, new

    def get_diff_fields(self):
        model_fields = [field.name for field in self._meta.get_fields() if field.name != 'id']
        #imported_grants = self.grant.importedgrant_set.all()
        date = self.creation_date
        passed = self.grant.importedgrant_set.filter(creation_date__lt=date).order_by('creation_date')
        if len(list(passed)) > 0:
            previous = list(passed)[-1]
            if previous:
                changed_fields = list(filter(
                    lambda field: getattr(previous, field, None) != getattr(self, field, None), model_fields))
                return changed_fields

    @property
    def science_areas(self):
        science_areas = {}
        if self.science_area:
            for match in SCIENCE_AREA_PATTERN.finditer(self.science_area):
                science_areas[match.group('area')] = int(match.group('percentage'))

            science_areas = sorted(science_areas.items(), key=lambda x: x[1], reverse=True)

        return [f'{k} {v}%' for k,v in science_areas]

    @property
    def labels(self):
        routing_labels = {'science_areas': self.science_areas}
        if self.routing_classification:
            routing_labels['routing_classification'] = [self.routing_classification]

        return routing_labels

    def save(self, *args, **kwargs):
        # On save, update timestamps
        exists = Grant.objects.filter(grant_ref=self.grant_ref).exists()
        self.creation_date = timezone.now()

        if exists:
            existing_grant = Grant.objects.get(grant_ref=self.grant_ref)
            self.grant = existing_grant
            existing_grant.updated_imported_grant = True
            existing_grant.save()
        else:
            new_grant = Grant.objects.create(grant_ref=self.grant_ref, claimed=False, updated_imported_grant=False)
            self.grant = new_grant

        return super(ImportedGrant, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.grant_ref}: {self.title[:50]}: [{self.grant_holder}]"




"""
NGDC Grants Round Category	NGDC	NGDC internal category
NGDC Correspondence	NGDC	Linked to NGDC Correspondence Document Library (will show the number of emails/items for the particular grant)
NGDC DMP Documents	NGDC	Linked to NGDC DMP Document Library (will show the number of DMP items for the particular grant)
BGS contact	NGDC	Name of BGS/NGDC primary contact for this grant
Large data expected (in TB)	NGDC	Number in terabytes
Date large data expected	NGDC	Yes, No or Null
Detailed Accession Item ID	NGDC	Detailed accession number where applicable
NGDC Notes	NGDC
Metadata - citation_id	NGDC
DOI	NGDC
NGDC date to contact	NGDC	Date for next contact
Reason to contact	NGDC	Reason for next contact
"""