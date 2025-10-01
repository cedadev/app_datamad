"""
Resets selected grants (former Siebel "/1" grants) back to their value prior to the update to DataMAD which occurred
on 9th September, when Facilities information began to be properly extracted from the Databank database (TFS).

This ended up unintentionally overwriting the previous Siebel grants facilties information, hence the need for the reset.
"""

from django.core.management.base import BaseCommand
from datamad2.models import ImportedGrant, Grant
import datetime
import sys

class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        input_group = parser.add_mutually_exclusive_group()
        input_group.add_argument('--rollback', help='Rollback to change on this date')

    @staticmethod
    def roundDownDateTime(dt):
        delta_min = dt.minute % 1
        return datetime.datetime(dt.year, dt.month, dt.day,
                                dt.hour, dt.minute - delta_min)

    def handle(self, *args, **options):
        if options["rollback"] is None:
            # Default rollback option
            # options["rollback"] = datetime.datetime(2025, 9, 10, 9, 9)
            options["rollback"] = datetime.datetime(2025, 9, 10, 9, 7, tzinfo=datetime.timezone.utc)

            # (2025, 9, 10, 9, 7, 4, 856784, tzinfo=datetime.timezone.utc)
        else:
            # Change rollback into a datetime
            options["rollback"] = datetime.datetime.strptime(options['rollback'], '%Y%m%d').date()

        if options.get('rollback'):
           siebel_grants = Grant.objects.filter(grant_ref__contains='/1')
           
           for siebel_grant in siebel_grants:
                grant_ref = siebel_grant.grant_ref
                current_ig = ImportedGrant()
                limes = siebel_grant.importedgrant_set.filter(creation_date__lt=options["rollback"]).order_by('creation_date').reverse()
                counter = 0
                for lime in limes:
                    print(lime.creation_date)
                    if counter==0:
                        ...
                        #current_ig.facility = lime.facility
                        #lime.creation_date
                        #current_ig.save()
