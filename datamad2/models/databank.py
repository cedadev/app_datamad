# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BridgeApplicationClassificationArea(models.Model):
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    classificationareaskey = models.IntegerField(db_column='ClassificationAreaSKey')  # Field name made lowercase.
    weighting = models.DecimalField(db_column='Weighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    weightingtype = models.CharField(db_column='WeightingType', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bridge_application_classification_area'


class BridgeApplicationClassificationQualifier(models.Model):
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    classificationqualifierskey = models.IntegerField(db_column='ClassificationQualifierSKey')  # Field name made lowercase.
    derivedweighting = models.DecimalField(db_column='DerivedWeighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bridge_application_classification_qualifier'


class BridgeApplicationClassificationReportingRcuk(models.Model):
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    classificationreportingrcukskey = models.IntegerField(db_column='ClassificationReportingRCUKSKey')  # Field name made lowercase.
    weighting = models.DecimalField(db_column='Weighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bridge_application_classification_reporting_RCUK'


class BridgeApplicationClassificationReportingCouncil(models.Model):
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    classificationreportingcouncilskey = models.IntegerField(db_column='ClassificationReportingCouncilSKey')  # Field name made lowercase.
    weighting = models.DecimalField(db_column='Weighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bridge_application_classification_reporting_council'


class DimApplicationDate(models.Model):
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    firstreceiveddate = models.DateField(db_column='FirstReceivedDate', blank=True, null=True)  # Field name made lowercase.
    lastreceived = models.DateField(db_column='LastReceived', blank=True, null=True)  # Field name made lowercase.
    councildecisiondate = models.DateTimeField(db_column='CouncilDecisionDate', blank=True, null=True)  # Field name made lowercase.
    proposedstartdate = models.DateField(db_column='ProposedStartDate', blank=True, null=True)  # Field name made lowercase.
    proposedenddate = models.DateField(db_column='ProposedEndDate', blank=True, null=True)  # Field name made lowercase.
    announcedstartdate = models.DateField(db_column='AnnouncedStartDate', blank=True, null=True)  # Field name made lowercase.
    announcedenddate = models.DateField(db_column='AnnouncedEndDate', blank=True, null=True)  # Field name made lowercase.
    earlieststartdate = models.DateField(db_column='EarliestStartDate', blank=True, null=True)  # Field name made lowercase.
    lateststartdate = models.DateField(db_column='LatestStartDate', blank=True, null=True)  # Field name made lowercase.
    actualstartdate = models.DateField(db_column='ActualStartDate', blank=True, null=True)  # Field name made lowercase.
    actualenddate = models.DateField(db_column='ActualEndDate', blank=True, null=True)  # Field name made lowercase.
    authoriseddate = models.DateField(db_column='AuthorisedDate', blank=True, null=True)  # Field name made lowercase.
    rejecteddate = models.DateField(db_column='RejectedDate', blank=True, null=True)  # Field name made lowercase.
    terminateddate = models.DateField(db_column='TerminatedDate', blank=True, null=True)  # Field name made lowercase.
    transferreddate = models.DateField(db_column='TransferredDate', blank=True, null=True)  # Field name made lowercase.
    activedate = models.DateField(db_column='ActiveDate', blank=True, null=True)  # Field name made lowercase.
    estimatedstartdate = models.DateField(db_column='EstimatedStartDate', blank=True, null=True)  # Field name made lowercase.
    communicationdecisiondate = models.DateField(db_column='CommunicationDecisionDate', blank=True, null=True)  # Field name made lowercase.
    peerrevieweddate = models.DateField(db_column='PeerReviewedDate', blank=True, null=True)  # Field name made lowercase.
    harmoniseddecisiondate = models.DateTimeField(db_column='HarmonisedDecisionDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_application_date'


class DimApplicationExt(models.Model):
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    applicationsummary = models.TextField(db_column='ApplicationSummary', blank=True, null=True)  # Field name made lowercase.
    applicationtechnicalsummary = models.TextField(db_column='ApplicationTechnicalSummary', blank=True, null=True)  # Field name made lowercase.
    organisationapplicationproposalid = models.CharField(db_column='OrganisationApplicationProposalID', max_length=160, blank=True, null=True)  # Field name made lowercase.
    organisationapplicationid = models.CharField(db_column='OrganisationApplicationID', max_length=120, blank=True, null=True)  # Field name made lowercase.
    routingclassification = models.CharField(db_column='RoutingClassification', max_length=120, blank=True, null=True)  # Field name made lowercase.
    panukriclassification_ahrc = models.CharField(db_column='PanUKRIClassification_AHRC', max_length=255, blank=True, null=True)  # Field name made lowercase.
    covid19classification_ahrc = models.CharField(db_column='Covid19Classification_AHRC', max_length=255, blank=True, null=True)  # Field name made lowercase.
    earlycareercategory_ahrc = models.CharField(db_column='EarlyCareerCategory_AHRC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    interdisciplinaryind_ahrc = models.TextField(db_column='InterdisciplinaryInd_AHRC', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    councillongname = models.CharField(db_column='CouncilLongName', max_length=250, blank=True, null=True)  # Field name made lowercase.
    insiebelind = models.TextField(db_column='InSiebelInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    inoffsystemind = models.TextField(db_column='InOffSystemInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    intfsind = models.TextField(db_column='InTFSInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    iniukind = models.TextField(db_column='InIUKInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    inreind = models.TextField(db_column='InREInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = False
        db_table = 'dim_application_ext'


class DimClassificationArea(models.Model):
    classificationareaskey = models.IntegerField(db_column='ClassificationAreaSKey')  # Field name made lowercase.
    classificationareaid = models.CharField(db_column='ClassificationAreaID', max_length=80, blank=True, null=True)  # Field name made lowercase.
    subresearchtopicid = models.CharField(db_column='SubResearchTopicID', max_length=80, blank=True, null=True)  # Field name made lowercase.
    subresearchtopic = models.CharField(db_column='SubResearchTopic', max_length=255, blank=True, null=True)  # Field name made lowercase.
    researchtopicid = models.CharField(db_column='ResearchTopicID', max_length=80, blank=True, null=True)  # Field name made lowercase.
    researchtopic = models.CharField(db_column='ResearchTopic', max_length=255, blank=True, null=True)  # Field name made lowercase.
    subjectareaid = models.CharField(db_column='SubjectAreaID', max_length=80, blank=True, null=True)  # Field name made lowercase.
    subjectarea = models.CharField(db_column='SubjectArea', max_length=255, blank=True, null=True)  # Field name made lowercase.
    remit_ahrc = models.CharField(db_column='Remit_AHRC', max_length=15, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_area'


class DimClassificationForCurrent(models.Model):
    classificationforcurrentskey = models.IntegerField(db_column='ClassificationFoRCurrentSKey')  # Field name made lowercase.
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    studentshipskey = models.IntegerField(db_column='StudentshipSKey')  # Field name made lowercase.
    forgroupid = models.CharField(db_column='FoRGroupID', max_length=20)  # Field name made lowercase.
    forgroupname = models.CharField(db_column='FoRGroupName', max_length=300)  # Field name made lowercase.
    forgroup = models.CharField(db_column='FoRGroup', max_length=300, blank=True, null=True)  # Field name made lowercase.
    fordivisionid = models.CharField(db_column='FoRDivisionID', max_length=20)  # Field name made lowercase.
    fordivisionname = models.CharField(db_column='FoRDivisionName', max_length=300)  # Field name made lowercase.
    fordivision = models.CharField(db_column='FoRDivision', max_length=300, blank=True, null=True)  # Field name made lowercase.
    weighting = models.DecimalField(db_column='Weighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    classificationpercentagesource = models.CharField(db_column='ClassificationPercentageSource', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_for_current'


class DimClassificationHrcsHcCurrent(models.Model):
    classificationhrcshccurrentskey = models.IntegerField(db_column='ClassificationHRCSHCCurrentSKey')  # Field name made lowercase.
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    studentshipskey = models.IntegerField(db_column='StudentshipSKey')  # Field name made lowercase.
    hrcshcid = models.CharField(db_column='HRCSHCID', max_length=20)  # Field name made lowercase.
    hrcshcname = models.CharField(db_column='HRCSHCName', max_length=300)  # Field name made lowercase.
    hrcshc = models.CharField(db_column='HRCSHC', max_length=300, blank=True, null=True)  # Field name made lowercase.
    weighting = models.DecimalField(db_column='Weighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    classificationpercentagesource = models.CharField(db_column='ClassificationPercentageSource', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_hrcs_hc_current'


class DimClassificationHrcsRacCurrent(models.Model):
    classificationhrcsraccurrentskey = models.IntegerField(db_column='ClassificationHRCSRACCurrentSKey')  # Field name made lowercase.
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    studentshipskey = models.IntegerField(db_column='StudentshipSKey')  # Field name made lowercase.
    hrcsraccodeid = models.CharField(db_column='HRCSRACCodeID', max_length=20)  # Field name made lowercase.
    hrcsraccodename = models.CharField(db_column='HRCSRACCodeName', max_length=300)  # Field name made lowercase.
    hrcsraccode = models.CharField(db_column='HRCSRACCode', max_length=300, blank=True, null=True)  # Field name made lowercase.
    hrcsracsubcode = models.CharField(db_column='HRCSRACSubCode', max_length=300, blank=True, null=True)  # Field name made lowercase.
    hrcsracsubcodeid = models.CharField(db_column='HRCSRACSubCodeID', max_length=20)  # Field name made lowercase.
    hrcsracsubcodename = models.CharField(db_column='HRCSRACSubCodeName', max_length=300)  # Field name made lowercase.
    weighting = models.DecimalField(db_column='Weighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    classificationpercentagesource = models.CharField(db_column='ClassificationPercentageSource', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_hrcs_rac_current'


class DimClassificationQualifier(models.Model):
    classificationqualifierskey = models.IntegerField(db_column='ClassificationQualifierSKey')  # Field name made lowercase.
    qualifierclassificationid = models.CharField(db_column='QualifierClassificationID', max_length=100)  # Field name made lowercase.
    qualifierclassification = models.CharField(db_column='QualifierClassification', max_length=255)  # Field name made lowercase.
    qualifierclassificationgroupid = models.CharField(db_column='QualifierClassificationGroupID', max_length=100)  # Field name made lowercase.
    qualifierclassificationgroup = models.CharField(db_column='QualifierClassificationGroup', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_qualifier'


class DimClassificationRcdcCurrent(models.Model):
    classificationrcdccurrentskey = models.IntegerField(db_column='ClassificationRCDCCurrentSKey')  # Field name made lowercase.
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    rcdcid = models.CharField(db_column='RCDCID', max_length=20)  # Field name made lowercase.
    rcdcname = models.CharField(db_column='RCDCName', max_length=300)  # Field name made lowercase.
    rcdc = models.CharField(db_column='RCDC', max_length=300, blank=True, null=True)  # Field name made lowercase.
    weighting = models.DecimalField(db_column='Weighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    classificationpercentagesource = models.CharField(db_column='ClassificationPercentageSource', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_rcdc_current'


class DimClassificationReportingCouncil(models.Model):
    classificationreportingcouncilskey = models.IntegerField(db_column='ClassificationReportingCouncilSKey')  # Field name made lowercase.
    reportingcouncilclassificationid = models.CharField(db_column='ReportingCouncilClassificationID', max_length=100)  # Field name made lowercase.
    reportingcouncilclassification = models.CharField(db_column='ReportingCouncilClassification', max_length=255)  # Field name made lowercase.
    reportingcouncilclassificationgroupid = models.CharField(db_column='ReportingCouncilClassificationGroupID', max_length=100)  # Field name made lowercase.
    reportingcouncilclassificationgroup = models.CharField(db_column='ReportingCouncilClassificationGroup', max_length=255)  # Field name made lowercase.
    reportingcouncilclassificationcouncilid = models.CharField(db_column='ReportingCouncilClassificationCouncilID', max_length=100)  # Field name made lowercase.
    reportingcouncilclassificationcouncil = models.CharField(db_column='ReportingCouncilClassificationCouncil', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_reporting_council'


class DimClassificationReportingRcuk(models.Model):
    classificationreportingrcukskey = models.IntegerField(db_column='ClassificationReportingRCUKSKey')  # Field name made lowercase.
    reportingrcukclassificationid = models.CharField(db_column='ReportingRCUKClassificationID', max_length=100)  # Field name made lowercase.
    reportingrcukclassification = models.CharField(db_column='ReportingRCUKClassification', max_length=255)  # Field name made lowercase.
    reportingrcuksubgroupid = models.CharField(db_column='ReportingRCUKSubGroupID', max_length=100)  # Field name made lowercase.
    reportingrcuksubgroup = models.CharField(db_column='ReportingRCUKSubGroup', max_length=255)  # Field name made lowercase.
    reportingrcukgroupid = models.CharField(db_column='ReportingRCUKGroupID', max_length=100)  # Field name made lowercase.
    reportingrcukgroup = models.CharField(db_column='ReportingRCUKGroup', max_length=255)  # Field name made lowercase.
    reportingrcukhierarchylevel = models.CharField(db_column='ReportingRCUKHierarchyLevel', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_reporting_rcuk'


class DimClassificationSdgCurrent(models.Model):
    classificationsdgcurrentskey = models.IntegerField(db_column='ClassificationSDGCurrentSKey')  # Field name made lowercase.
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    studentshipskey = models.IntegerField(db_column='StudentshipSKey')  # Field name made lowercase.
    sdgid = models.CharField(db_column='SDGID', max_length=20)  # Field name made lowercase.
    sdgname = models.CharField(db_column='SDGName', max_length=300)  # Field name made lowercase.
    sdg = models.CharField(db_column='SDG', max_length=300, blank=True, null=True)  # Field name made lowercase.
    weighting = models.DecimalField(db_column='Weighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    classificationpercentagesource = models.CharField(db_column='ClassificationPercentageSource', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_sdg_current'


class DimClassificationStudentshipThematic(models.Model):
    classificationstudentshipthematicskey = models.IntegerField(db_column='ClassificationStudentshipThematicSKey')  # Field name made lowercase.
    studentshipskey = models.IntegerField(db_column='StudentshipSKey')  # Field name made lowercase.
    classificationid = models.CharField(db_column='ClassificationId', max_length=100)  # Field name made lowercase.
    classificationname = models.CharField(db_column='ClassificationName', max_length=150)  # Field name made lowercase.
    themedescription = models.TextField(db_column='ThemeDescription', blank=True, null=True)  # Field name made lowercase.
    classificationmethodologydescription = models.CharField(db_column='ClassificationMethodologyDescription', max_length=250, blank=True, null=True)  # Field name made lowercase.
    classificationmethodologylink = models.CharField(db_column='ClassificationMethodologyLink', max_length=250)  # Field name made lowercase.
    obsolescence = models.CharField(db_column='Obsolescence', max_length=100, blank=True, null=True)  # Field name made lowercase.
    measureofsimilarity = models.DecimalField(db_column='MeasureOfSimilarity', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    isbelongstoclass = models.TextField(db_column='IsBelongsToClass', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    classifieddate = models.DateTimeField(db_column='ClassifiedDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_studentship_thematic'


class DimClassificationUoaCurrent(models.Model):
    classificationuoacurrentskey = models.IntegerField(db_column='ClassificationUoACurrentSKey')  # Field name made lowercase.
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    uoacodeid = models.CharField(db_column='UoACodeID', max_length=20)  # Field name made lowercase.
    uoarefpanel = models.CharField(db_column='UoAREFPanel', max_length=300)  # Field name made lowercase.
    uoacode = models.CharField(db_column='UoACode', max_length=300, blank=True, null=True)  # Field name made lowercase.
    uoasubcode = models.CharField(db_column='UoASubCode', max_length=300, blank=True, null=True)  # Field name made lowercase.
    unitofassessmentid = models.CharField(db_column='UnitOfAssessmentID', max_length=20)  # Field name made lowercase.
    unitofassessmentname = models.CharField(db_column='UnitOfAssessmentName', max_length=300)  # Field name made lowercase.
    weighting = models.DecimalField(db_column='Weighting', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    classificationpercentagesource = models.CharField(db_column='ClassificationPercentageSource', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_classification_uoa_current'


class DimDepartment(models.Model):
    organisationdepartmentskey = models.IntegerField(db_column='OrganisationDepartmentSKey')  # Field name made lowercase.
    departmentid = models.CharField(db_column='DepartmentID', max_length=30, blank=True, null=True)  # Field name made lowercase.
    departmentname = models.CharField(db_column='DepartmentName', max_length=250, blank=True, null=True)  # Field name made lowercase.
    departmentstatus = models.CharField(db_column='DepartmentStatus', max_length=50, blank=True, null=True)  # Field name made lowercase.
    departmenttype = models.CharField(db_column='DepartmentType', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_department'


class DimOpportunity(models.Model):
    opportunityskey = models.IntegerField(db_column='OpportunitySKey')  # Field name made lowercase.
    opportunityname = models.CharField(db_column='OpportunityName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    opportunitynumber = models.CharField(db_column='OpportunityNumber', max_length=100, blank=True, null=True)  # Field name made lowercase.
    opportunitystartdate = models.DateTimeField(db_column='OpportunityStartDate', blank=True, null=True)  # Field name made lowercase.
    opportunityenddate = models.DateTimeField(db_column='OpportunityEndDate', blank=True, null=True)  # Field name made lowercase.
    opportunityclosedate = models.DateTimeField(db_column='OpportunityCloseDate', blank=True, null=True)  # Field name made lowercase.
    opportunitymode_ahrc = models.CharField(db_column='OpportunityMode_AHRC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    opportunityoriginsource = models.CharField(db_column='OpportunityOriginSource', max_length=9, blank=True, null=True)  # Field name made lowercase.
    opportunitycomments = models.TextField(db_column='OpportunityComments', blank=True, null=True)  # Field name made lowercase.
    applicantledortargeted = models.CharField(db_column='ApplicantLedOrTargeted', max_length=15, blank=True, null=True)  # Field name made lowercase.
    isresponsive = models.CharField(db_column='IsResponsive', max_length=15, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_opportunity'


class DimOrganisation(models.Model):
    organisationskey = models.IntegerField(db_column='OrganisationSKey')  # Field name made lowercase.
    organisationid = models.CharField(db_column='OrganisationID', max_length=30, blank=True, null=True)  # Field name made lowercase.
    organisationname = models.CharField(db_column='OrganisationName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    companyregistrationnumber = models.CharField(db_column='CompanyRegistrationNumber', max_length=50, blank=True, null=True)  # Field name made lowercase.
    organisationtype = models.CharField(db_column='OrganisationType', max_length=100, blank=True, null=True)  # Field name made lowercase.
    organisationsubtype = models.CharField(db_column='OrganisationSubType', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cofunderind = models.TextField(db_column='CoFunderInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    canholdrcgrantsind = models.TextField(db_column='CanHoldRCGrantsInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    siebelstatus = models.CharField(db_column='SiebelStatus', max_length=80, blank=True, null=True)  # Field name made lowercase.
    organisationurl = models.CharField(db_column='OrganisationURL', max_length=800, blank=True, null=True)  # Field name made lowercase.
    rdmid = models.CharField(db_column='RDMID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    gridid = models.CharField(db_column='GRIDID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    organisationcdrid = models.CharField(db_column='OrganisationCDRID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rorid = models.CharField(db_column='RORID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    isni = models.CharField(db_column='ISNI', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ukprn = models.CharField(db_column='UKPRN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    addressline1 = models.CharField(db_column='AddressLine1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    townorcity = models.CharField(db_column='TownOrCity', max_length=100, blank=True, null=True)  # Field name made lowercase.
    county = models.CharField(db_column='County', max_length=100, blank=True, null=True)  # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=100, blank=True, null=True)  # Field name made lowercase.
    postcode = models.CharField(db_column='PostCode', max_length=75, blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=100, blank=True, null=True)  # Field name made lowercase.
    latitude = models.CharField(db_column='Latitude', max_length=30, blank=True, null=True)  # Field name made lowercase.
    longitude = models.CharField(db_column='Longitude', max_length=30, blank=True, null=True)  # Field name made lowercase.
    localauthority = models.CharField(db_column='LocalAuthority', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ward = models.CharField(db_column='Ward', max_length=255, blank=True, null=True)  # Field name made lowercase.
    lep1code = models.CharField(db_column='LEP1Code', max_length=255, blank=True, null=True)  # Field name made lowercase.
    lep1name = models.CharField(db_column='LEP1Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    lep2code = models.CharField(db_column='LEP2Code', max_length=255, blank=True, null=True)  # Field name made lowercase.
    parliamentaryconstituency = models.CharField(db_column='ParliamentaryConstituency', max_length=150, blank=True, null=True)  # Field name made lowercase.
    parliamentaryconstituencycode = models.CharField(db_column='ParliamentaryConstituencyCode', max_length=150, blank=True, null=True)  # Field name made lowercase.
    itl3code = models.CharField(db_column='ITL3Code', max_length=255, blank=True, null=True)  # Field name made lowercase.
    itl3name = models.CharField(db_column='ITL3Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    itl2code = models.CharField(db_column='ITL2Code', max_length=150, blank=True, null=True)  # Field name made lowercase.
    itl2name = models.CharField(db_column='ITL2Name', max_length=150, blank=True, null=True)  # Field name made lowercase.
    itl1code = models.CharField(db_column='ITL1Code', max_length=150, blank=True, null=True)  # Field name made lowercase.
    itl1name = models.CharField(db_column='ITL1Name', max_length=150, blank=True, null=True)  # Field name made lowercase.
    nuts3code = models.CharField(db_column='NUTS3Code', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nuts2code = models.CharField(db_column='NUTS2Code', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nuts1code = models.CharField(db_column='NUTS1Code', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_organisation'


class DimPanel(models.Model):
    panelskey = models.IntegerField(db_column='PanelSKey')  # Field name made lowercase.
    panelreference = models.CharField(db_column='PanelReference', max_length=400, blank=True, null=True)  # Field name made lowercase.
    meetingname = models.CharField(db_column='MeetingName', max_length=400, blank=True, null=True)  # Field name made lowercase.
    panelname = models.CharField(db_column='PanelName', max_length=400, blank=True, null=True)  # Field name made lowercase.
    paneldescription = models.TextField(db_column='PanelDescription', blank=True, null=True)  # Field name made lowercase.
    datepanelupdated = models.DateTimeField(db_column='DatePanelUpdated', blank=True, null=True)  # Field name made lowercase.
    panelstartdate = models.DateTimeField(db_column='PanelStartDate', blank=True, null=True)  # Field name made lowercase.
    panelenddate = models.DateTimeField(db_column='PanelEndDate', blank=True, null=True)  # Field name made lowercase.
    panelstatus = models.CharField(db_column='PanelStatus', max_length=100, blank=True, null=True)  # Field name made lowercase.
    paneltype = models.CharField(db_column='PanelType', max_length=400, blank=True, null=True)  # Field name made lowercase.
    panellocation = models.CharField(db_column='PanelLocation', max_length=400, blank=True, null=True)  # Field name made lowercase.
    plannedduration = models.CharField(db_column='PlannedDuration', max_length=15, blank=True, null=True)  # Field name made lowercase.
    actualduration = models.CharField(db_column='ActualDuration', max_length=15, blank=True, null=True)  # Field name made lowercase.
    panelpublishind = models.TextField(db_column='PanelPublishInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    panelprivateind = models.TextField(db_column='PanelPrivateInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    isintfsind = models.TextField(db_column='IsInTFSInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    isinsiebelind = models.TextField(db_column='IsInSiebelInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = False
        db_table = 'dim_panel'


class DimPerson(models.Model):
    personskey = models.IntegerField(db_column='PersonSKey')  # Field name made lowercase.
    personid = models.CharField(db_column='PersonID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tfsid = models.CharField(db_column='TFSID', max_length=30, blank=True, null=True)  # Field name made lowercase.
    pid = models.CharField(db_column='PID', max_length=60, blank=True, null=True)  # Field name made lowercase.
    personcdrid = models.CharField(db_column='PersonCDRID', max_length=30, blank=True, null=True)  # Field name made lowercase.
    orcid = models.CharField(db_column='ORCID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=100, blank=True, null=True)  # Field name made lowercase.
    forename = models.CharField(db_column='Forename', max_length=100, blank=True, null=True)  # Field name made lowercase.
    surname = models.CharField(db_column='Surname', max_length=100, blank=True, null=True)  # Field name made lowercase.
    forenameandsurname = models.CharField(db_column='ForenameAndSurname', max_length=200, blank=True, null=True)  # Field name made lowercase.
    initials = models.CharField(db_column='Initials', max_length=48, blank=True, null=True)  # Field name made lowercase.
    fullname = models.CharField(db_column='FullName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    preferredname = models.CharField(db_column='PreferredName', max_length=280, blank=True, null=True)  # Field name made lowercase.
    salutation = models.CharField(db_column='Salutation', max_length=300, blank=True, null=True)  # Field name made lowercase.
    preferredcontactmethod = models.CharField(db_column='PreferredContactMethod', max_length=30, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)  # Field name made lowercase.
    goneawayind = models.CharField(db_column='GoneAwayInd', max_length=50, blank=True, null=True)  # Field name made lowercase.
    persondeletedind = models.CharField(db_column='PersonDeletedInd', max_length=50, blank=True, null=True)  # Field name made lowercase.
    deceasedind = models.CharField(db_column='DeceasedInd', max_length=50, blank=True, null=True)  # Field name made lowercase.
    meetingfeespayableind = models.TextField(db_column='MeetingFeesPayableInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    panelorcollegefeespayableind = models.CharField(db_column='PanelOrCollegeFeesPayableInd', max_length=1, blank=True, null=True)  # Field name made lowercase.
    bodymemberind = models.CharField(db_column='BodyMemberInd', max_length=1, blank=True, null=True)  # Field name made lowercase.
    sanctionedind = models.CharField(db_column='SanctionedInd', max_length=1, blank=True, null=True)  # Field name made lowercase.
    nationality = models.CharField(db_column='Nationality', max_length=100, blank=True, null=True)  # Field name made lowercase.
    currentpost = models.CharField(db_column='CurrentPost', max_length=255, blank=True, null=True)  # Field name made lowercase.
    jesaccountstatus = models.CharField(db_column='JeSAccountStatus', max_length=120, blank=True, null=True)  # Field name made lowercase.
    personsiebelstatus = models.CharField(db_column='PersonSiebelStatus', max_length=30, blank=True, null=True)  # Field name made lowercase.
    personurl = models.CharField(db_column='PersonURL', max_length=800, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_person'


class DimScheme(models.Model):
    schemeskey = models.IntegerField(db_column='SchemeSKey')  # Field name made lowercase.
    schemeid = models.CharField(db_column='SchemeID', max_length=100, blank=True, null=True)  # Field name made lowercase.
    schemename = models.CharField(db_column='SchemeName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    schemetype = models.CharField(db_column='SchemeType', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dim_scheme'


class FactApplication(models.Model):
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    applicationid = models.CharField(db_column='ApplicationID', max_length=50)  # Field name made lowercase.
    awardid = models.CharField(db_column='AwardID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    financeawardid = models.CharField(db_column='FinanceAwardID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicationtitle = models.CharField(db_column='ApplicationTitle', max_length=255, blank=True, null=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=255, blank=True, null=True)  # Field name made lowercase.
    categoryeoi = models.CharField(db_column='CategoryEOI', max_length=255, blank=True, null=True)  # Field name made lowercase.
    categoryharmonised = models.CharField(db_column='CategoryHarmonised', max_length=255, blank=True, null=True)  # Field name made lowercase.
    leadfundingarea = models.CharField(db_column='LeadFundingArea', max_length=250, blank=True, null=True)  # Field name made lowercase.
    applicationstatus = models.CharField(db_column='ApplicationStatus', max_length=255, blank=True, null=True)  # Field name made lowercase.
    stage = models.CharField(db_column='Stage', max_length=255, blank=True, null=True)  # Field name made lowercase.
    stagestatus = models.CharField(db_column='StageStatus', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fundingdecision = models.CharField(db_column='FundingDecision', max_length=255, blank=True, null=True)  # Field name made lowercase.
    closurecategory = models.CharField(db_column='ClosureCategory', max_length=30, blank=True, null=True)  # Field name made lowercase.
    rejectionreason = models.CharField(db_column='RejectionReason', max_length=255, blank=True, null=True)  # Field name made lowercase.
    administratingcouncil = models.CharField(db_column='AdministratingCouncil', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicationfunder = models.CharField(db_column='ApplicationFunder', max_length=50, blank=True, null=True)  # Field name made lowercase.
    opportunityowner = models.CharField(db_column='OpportunityOwner', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicationownertype = models.CharField(db_column='ApplicationOwnerType', max_length=15, blank=True, null=True)  # Field name made lowercase.
    applicationreceiveddate = models.DateField(db_column='ApplicationReceivedDate', blank=True, null=True)  # Field name made lowercase.
    applicationreceivedfy = models.CharField(db_column='ApplicationReceivedFY', max_length=15, blank=True, null=True)  # Field name made lowercase.
    decisiondate = models.DateTimeField(db_column='DecisionDate', blank=True, null=True)  # Field name made lowercase.
    decisionfy = models.CharField(db_column='DecisionFY', max_length=15, blank=True, null=True)  # Field name made lowercase.
    applicationstartdate = models.DateTimeField(db_column='ApplicationStartDate', blank=True, null=True)  # Field name made lowercase.
    applicationenddate = models.DateTimeField(db_column='ApplicationEndDate', blank=True, null=True)  # Field name made lowercase.
    applicationduration = models.IntegerField(db_column='ApplicationDuration', blank=True, null=True)  # Field name made lowercase.
    announcedduration = models.DecimalField(db_column='AnnouncedDuration', max_digits=22, decimal_places=7, blank=True, null=True)  # Field name made lowercase.
    proposedduration = models.DecimalField(db_column='ProposedDuration', max_digits=22, decimal_places=7, blank=True, null=True)  # Field name made lowercase.
    fectype = models.CharField(db_column='FECType', max_length=30, blank=True, null=True)  # Field name made lowercase.
    transferredind = models.TextField(db_column='TransferredInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    applicationispublicind = models.IntegerField(db_column='ApplicationIsPublicInd', blank=True, null=True)  # Field name made lowercase.
    applicationoriginsource = models.CharField(db_column='ApplicationOriginSource', max_length=30, blank=True, null=True)  # Field name made lowercase.
    primaryuoa = models.CharField(db_column='PrimaryUoA', max_length=300, blank=True, null=True)  # Field name made lowercase.
    secondaryuoa = models.CharField(db_column='SecondaryUoA', max_length=300, blank=True, null=True)  # Field name made lowercase.
    opportunityskey = models.IntegerField(db_column='OpportunitySKey')  # Field name made lowercase.
    schemeskey = models.IntegerField(db_column='SchemeSKey')  # Field name made lowercase.
    organisationdepartmentskey = models.IntegerField(db_column='OrganisationDepartmentSKey')  # Field name made lowercase.
    leadorganisationskey = models.IntegerField(db_column='LeadOrganisationSKey')  # Field name made lowercase.
    applicantpersonskey = models.IntegerField(db_column='ApplicantPersonSKey')  # Field name made lowercase.
    applicantpersonediskey = models.IntegerField(db_column='ApplicantPersonEDISKey')  # Field name made lowercase.
    primaryclassificationareaskey = models.IntegerField(db_column='PrimaryClassificationAreaSKey')  # Field name made lowercase.
    numberofapplications = models.IntegerField(db_column='NumberOfApplications')  # Field name made lowercase.
    numberofsuccessfulapplications = models.IntegerField(db_column='NumberOfSuccessfulApplications')  # Field name made lowercase.
    numberofrejectedapplications = models.IntegerField(db_column='NumberOfRejectedApplications')  # Field name made lowercase.
    appliedforfecamount = models.DecimalField(db_column='AppliedForFECAmount', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    appliedforamount = models.DecimalField(db_column='AppliedForAmount', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    fecpercentage = models.DecimalField(db_column='FECPercentage', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    awardedfecamount = models.DecimalField(db_column='AwardedFECAmount', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    awardedamount = models.DecimalField(db_column='AwardedAmount', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    recordupdatedindatabank = models.DateTimeField(db_column='RecordUpdatedInDataBank', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'fact_application'


class FactApplicationPeerReview(models.Model):
    peerreviewskey = models.IntegerField(db_column='PeerReviewSKey')  # Field name made lowercase.
    reviewsystemid = models.CharField(db_column='ReviewSystemID', max_length=255)  # Field name made lowercase.
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    applicationid = models.CharField(db_column='ApplicationID', max_length=50)  # Field name made lowercase.
    awardid = models.CharField(db_column='AwardID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    financeawardid = models.CharField(db_column='FinanceAwardID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicationtitle = models.CharField(db_column='ApplicationTitle', max_length=255, blank=True, null=True)  # Field name made lowercase.
    applicationstatus = models.CharField(db_column='ApplicationStatus', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fundingdecision = models.CharField(db_column='FundingDecision', max_length=255, blank=True, null=True)  # Field name made lowercase.
    applicationispublicind = models.IntegerField(db_column='ApplicationIsPublicInd', blank=True, null=True)  # Field name made lowercase.
    applicationoriginsource = models.CharField(db_column='ApplicationOriginSource', max_length=30, blank=True, null=True)  # Field name made lowercase.
    primaryuoa = models.CharField(db_column='PrimaryUoA', max_length=300, blank=True, null=True)  # Field name made lowercase.
    secondaryuoa = models.CharField(db_column='SecondaryUoA', max_length=300, blank=True, null=True)  # Field name made lowercase.
    opportunityskey = models.IntegerField(db_column='OpportunitySKey')  # Field name made lowercase.
    schemeskey = models.IntegerField(db_column='SchemeSKey')  # Field name made lowercase.
    administratingcouncil = models.CharField(db_column='AdministratingCouncil', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicationfunder = models.CharField(db_column='ApplicationFunder', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicantpersonskey = models.IntegerField(db_column='ApplicantPersonSKey')  # Field name made lowercase.
    applicantpersonediskey = models.IntegerField(db_column='ApplicantPersonEDISKey')  # Field name made lowercase.
    leadorganisationskey = models.IntegerField(db_column='LeadOrganisationSKey')  # Field name made lowercase.
    leadorganisationdepartmentskey = models.IntegerField(db_column='LeadOrganisationDepartmentSKey')  # Field name made lowercase.
    primaryclassificationareaskey = models.IntegerField(db_column='PrimaryClassificationAreaSKey')  # Field name made lowercase.
    reviewerpersonskey = models.IntegerField(db_column='ReviewerPersonSKey')  # Field name made lowercase.
    reviewerpersonediskey = models.IntegerField(db_column='ReviewerPersonEDISKey')  # Field name made lowercase.
    latestreviewstatus = models.CharField(db_column='LatestReviewStatus', max_length=255, blank=True, null=True)  # Field name made lowercase.
    reviewstatusgroup = models.CharField(db_column='ReviewStatusGroup', max_length=255, blank=True, null=True)  # Field name made lowercase.
    reviewstage = models.CharField(db_column='ReviewStage', max_length=255, blank=True, null=True)  # Field name made lowercase.
    datefirstinviteissue = models.DateTimeField(db_column='DateFirstInviteIssue', blank=True, null=True)  # Field name made lowercase.
    dateinvitereminder = models.DateTimeField(db_column='DateInviteReminder', blank=True, null=True)  # Field name made lowercase.
    datelatestinvitereplyreceived = models.DateTimeField(db_column='DateLatestInviteReplyReceived', blank=True, null=True)  # Field name made lowercase.
    datefirstsubmitted = models.DateTimeField(db_column='DateFirstSubmitted', blank=True, null=True)  # Field name made lowercase.
    datefirstreceived = models.DateTimeField(db_column='DateFirstReceived', blank=True, null=True)  # Field name made lowercase.
    datereview = models.DateTimeField(db_column='DateReview', blank=True, null=True)  # Field name made lowercase.
    reviewerconflictind = models.TextField(db_column='ReviewerConflictInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    conflictsoftind = models.TextField(db_column='ConflictSoftInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    conflicthardind = models.TextField(db_column='ConflictHardInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    responsestage = models.CharField(db_column='ResponseStage', max_length=30, blank=True, null=True)  # Field name made lowercase.
    responsestatus = models.CharField(db_column='ResponseStatus', max_length=50, blank=True, null=True)  # Field name made lowercase.
    respondedapplicantpersonskey = models.IntegerField(db_column='RespondedApplicantPersonSKey', blank=True, null=True)  # Field name made lowercase.
    respondedapplicantpersonediskey = models.IntegerField(db_column='RespondedApplicantPersonEDISKey', blank=True, null=True)  # Field name made lowercase.
    dateresponseinviteissue = models.DateTimeField(db_column='DateResponseInviteIssue', blank=True, null=True)  # Field name made lowercase.
    dateresponsedue = models.DateTimeField(db_column='DateResponseDue', blank=True, null=True)  # Field name made lowercase.
    dateresponsereceived = models.DateTimeField(db_column='DateResponseReceived', blank=True, null=True)  # Field name made lowercase.
    reviewperiodduration = models.IntegerField(db_column='ReviewPeriodDuration', blank=True, null=True)  # Field name made lowercase.
    score = models.DecimalField(db_column='Score', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    numberofresponses = models.IntegerField(db_column='NumberOfResponses', blank=True, null=True)  # Field name made lowercase.
    datelatestreviewinviteaccepted = models.DateTimeField(db_column='DateLatestReviewInviteAccepted', blank=True, null=True)  # Field name made lowercase.
    datelatestreviewinvitedeclined = models.DateTimeField(db_column='DateLatestReviewInviteDeclined', blank=True, null=True)  # Field name made lowercase.
    datelatestreviewinvitecancelled = models.DateTimeField(db_column='DateLatestReviewInviteCancelled', blank=True, null=True)  # Field name made lowercase.
    reviewersource = models.CharField(db_column='ReviewerSource', max_length=255, blank=True, null=True)  # Field name made lowercase.
    reviewerexpertisetype = models.CharField(db_column='ReviewerExpertiseType', max_length=255, blank=True, null=True)  # Field name made lowercase.
    reviewerleveltype = models.CharField(db_column='ReviewerLevelType', max_length=255, blank=True, null=True)  # Field name made lowercase.
    anonymousreference = models.CharField(db_column='AnonymousReference', max_length=255, blank=True, null=True)  # Field name made lowercase.
    anonymisedind = models.TextField(db_column='AnonymisedInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    recordupdatedindatabank = models.DateTimeField(db_column='RecordUpdatedInDataBank', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'fact_application_peer_review'


class FactApplicationTeam(models.Model):
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    teammemberrole = models.CharField(db_column='TeamMemberRole', max_length=50)  # Field name made lowercase.
    teammemberpersonskey = models.IntegerField(db_column='TeamMemberPersonSKey')  # Field name made lowercase.
    teammemberpersonediskey = models.IntegerField(db_column='TeamMemberPersonEDISKey')  # Field name made lowercase.
    teammemberorganisationskey = models.IntegerField(db_column='TeamMemberOrganisationSKey')  # Field name made lowercase.
    leadapplicantpersonskey = models.IntegerField(db_column='LeadApplicantPersonSKey')  # Field name made lowercase.
    leadapplicantpersonediskey = models.IntegerField(db_column='LeadApplicantPersonEDISKey')  # Field name made lowercase.
    leadorganisationskey = models.IntegerField(db_column='LeadOrganisationSKey')  # Field name made lowercase.
    isprimaryind = models.TextField(db_column='IsPrimaryInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    applicationid = models.CharField(db_column='ApplicationID', max_length=50)  # Field name made lowercase.
    awardid = models.CharField(db_column='AwardID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    applicationtitle = models.CharField(db_column='ApplicationTitle', max_length=255, blank=True, null=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fundingarea = models.CharField(db_column='FundingArea', max_length=250, blank=True, null=True)  # Field name made lowercase.
    applicationstatus = models.CharField(db_column='ApplicationStatus', max_length=255, blank=True, null=True)  # Field name made lowercase.
    stage = models.CharField(db_column='Stage', max_length=255, blank=True, null=True)  # Field name made lowercase.
    stagestatus = models.CharField(db_column='StageStatus', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fundingdecision = models.CharField(db_column='FundingDecision', max_length=255, blank=True, null=True)  # Field name made lowercase.
    closurecategory = models.CharField(db_column='ClosureCategory', max_length=30, blank=True, null=True)  # Field name made lowercase.
    rejectionreason = models.CharField(db_column='RejectionReason', max_length=255, blank=True, null=True)  # Field name made lowercase.
    administratingcouncil = models.CharField(db_column='AdministratingCouncil', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicationowner = models.CharField(db_column='ApplicationOwner', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicationownertype = models.CharField(db_column='ApplicationOwnerType', max_length=15, blank=True, null=True)  # Field name made lowercase.
    applicationreceiveddate = models.DateField(db_column='ApplicationReceivedDate', blank=True, null=True)  # Field name made lowercase.
    applicationreceivedfy = models.CharField(db_column='ApplicationReceivedFY', max_length=15, blank=True, null=True)  # Field name made lowercase.
    decisiondate = models.DateTimeField(db_column='DecisionDate', blank=True, null=True)  # Field name made lowercase.
    decisionfy = models.CharField(db_column='DecisionFY', max_length=15, blank=True, null=True)  # Field name made lowercase.
    applicationstartdate = models.DateTimeField(db_column='ApplicationStartDate', blank=True, null=True)  # Field name made lowercase.
    applicationenddate = models.DateTimeField(db_column='ApplicationEndDate', blank=True, null=True)  # Field name made lowercase.
    applicationduration = models.IntegerField(db_column='ApplicationDuration', blank=True, null=True)  # Field name made lowercase.
    announcedduration = models.DecimalField(db_column='AnnouncedDuration', max_digits=22, decimal_places=7, blank=True, null=True)  # Field name made lowercase.
    proposedduration = models.DecimalField(db_column='ProposedDuration', max_digits=22, decimal_places=7, blank=True, null=True)  # Field name made lowercase.
    fectype = models.CharField(db_column='FECType', max_length=30, blank=True, null=True)  # Field name made lowercase.
    transferredind = models.TextField(db_column='TransferredInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    resubmissioninvitedind = models.TextField(db_column='ResubmissionInvitedInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    revisionreturnedind = models.TextField(db_column='RevisionReturnedInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    applicationispublicind = models.IntegerField(db_column='ApplicationIsPublicInd', blank=True, null=True)  # Field name made lowercase.
    applicationoriginsource = models.CharField(db_column='ApplicationOriginSource', max_length=30, blank=True, null=True)  # Field name made lowercase.
    primaryuoa = models.CharField(db_column='PrimaryUoA', max_length=300, blank=True, null=True)  # Field name made lowercase.
    secondaryuoa = models.CharField(db_column='SecondaryUoA', max_length=300, blank=True, null=True)  # Field name made lowercase.
    opportunityskey = models.IntegerField(db_column='OpportunitySKey')  # Field name made lowercase.
    schemeskey = models.IntegerField(db_column='SchemeSKey')  # Field name made lowercase.
    teammemberstartdate = models.DateTimeField(db_column='TeamMemberStartDate', blank=True, null=True)  # Field name made lowercase.
    teammemberenddate = models.DateTimeField(db_column='TeamMemberEndDate', blank=True, null=True)  # Field name made lowercase.
    teammemberduration = models.IntegerField(db_column='TeamMemberDuration', blank=True, null=True)  # Field name made lowercase.
    teammembertotalhours = models.IntegerField(db_column='TeamMemberTotalHours', blank=True, null=True)  # Field name made lowercase.
    applicationappliedforamount = models.DecimalField(db_column='ApplicationAppliedForAmount', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    applicationawardedamount = models.DecimalField(db_column='ApplicationAwardedAmount', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    recordupdatedindatabank = models.DateTimeField(db_column='RecordUpdatedInDataBank')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'fact_application_team'


class FactPanelApplicationMember(models.Model):
    panelapplicationmemberskey = models.IntegerField(db_column='PanelApplicationMemberSKey')  # Field name made lowercase.
    panelskey = models.IntegerField(db_column='PanelSKey')  # Field name made lowercase.
    applicationskey = models.IntegerField(db_column='ApplicationSKey')  # Field name made lowercase.
    applicationid = models.CharField(db_column='ApplicationID', max_length=50)  # Field name made lowercase.
    awardid = models.CharField(db_column='AwardID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    financeawardid = models.CharField(db_column='FinanceAwardID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicationtitle = models.CharField(db_column='ApplicationTitle', max_length=255, blank=True, null=True)  # Field name made lowercase.
    applicationstatus = models.CharField(db_column='ApplicationStatus', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fundingdecision = models.CharField(db_column='FundingDecision', max_length=255, blank=True, null=True)  # Field name made lowercase.
    applicationispublicind = models.IntegerField(db_column='ApplicationIsPublicInd', blank=True, null=True)  # Field name made lowercase.
    applicationoriginsource = models.CharField(db_column='ApplicationOriginSource', max_length=30, blank=True, null=True)  # Field name made lowercase.
    primaryuoa = models.CharField(db_column='PrimaryUoA', max_length=300, blank=True, null=True)  # Field name made lowercase.
    secondaryuoa = models.CharField(db_column='SecondaryUoA', max_length=300, blank=True, null=True)  # Field name made lowercase.
    opportunityskey = models.IntegerField(db_column='OpportunitySKey', blank=True, null=True)  # Field name made lowercase.
    schemeskey = models.IntegerField(db_column='SchemeSKey', blank=True, null=True)  # Field name made lowercase.
    administratingcouncil = models.CharField(db_column='AdministratingCouncil', max_length=50, blank=True, null=True)  # Field name made lowercase.
    applicationfunder = models.CharField(db_column='ApplicationFunder', max_length=50, blank=True, null=True)  # Field name made lowercase.
    panelmemberorganisationskey = models.IntegerField(db_column='PanelMemberOrganisationSKey', blank=True, null=True)  # Field name made lowercase.
    panelmemberpersonskey = models.IntegerField(db_column='PanelMemberPersonSKey')  # Field name made lowercase.
    datepanelapplicationupdated = models.DateTimeField(db_column='DatePanelApplicationUpdated', blank=True, null=True)  # Field name made lowercase.
    panelrole = models.CharField(db_column='PanelRole', max_length=50, blank=True, null=True)  # Field name made lowercase.
    datepanelmemberupdated = models.DateTimeField(db_column='DatePanelMemberUpdated', blank=True, null=True)  # Field name made lowercase.
    panelmemberapplicationrole = models.CharField(db_column='PanelMemberApplicationRole', max_length=50, blank=True, null=True)  # Field name made lowercase.
    datepanelapplicationmemberupdated = models.DateTimeField(db_column='DatePanelApplicationMemberUpdated', blank=True, null=True)  # Field name made lowercase.
    panelparticipantstatus = models.CharField(db_column='PanelParticipantStatus', max_length=50, blank=True, null=True)  # Field name made lowercase.
    panelmemberattendedduration = models.CharField(db_column='PanelMemberAttendedDuration', max_length=50, blank=True, null=True)  # Field name made lowercase.
    panelmemberfeepayable = models.DecimalField(db_column='PanelMemberFeePayable', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    panelmemberexpensesallowedind = models.TextField(db_column='PanelMemberExpensesAllowedInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    panelmemberpaymenteligibleind = models.TextField(db_column='PanelMemberPaymentEligibleInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    panelmemberconflictrecordsexistind = models.TextField(db_column='PanelMemberConflictRecordsExistInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    panelmemberconfictedind = models.TextField(db_column='PanelMemberConfictedInd', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    dateconflictpanelmemberupdated = models.DateTimeField(db_column='DateConflictPanelMemberUpdated', blank=True, null=True)  # Field name made lowercase.
    prescore = models.DecimalField(db_column='PreScore', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dateprescoreupdated = models.DateTimeField(db_column='DatePreScoreUpdated', blank=True, null=True)  # Field name made lowercase.
    overallscore = models.DecimalField(db_column='OverallScore', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    overallmeetingoutcome = models.CharField(db_column='OverallMeetingOutcome', max_length=100, blank=True, null=True)  # Field name made lowercase.
    overallrank = models.DecimalField(db_column='OverallRank', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    recordupdatedindatabank = models.DateTimeField(db_column='RecordUpdatedInDataBank', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'fact_panel_application_member'
