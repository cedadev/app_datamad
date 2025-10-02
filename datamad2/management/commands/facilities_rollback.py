"""
Resets selected grants (former Siebel "/1" grants) back to their value prior to the update to DataMAD which occurred
on 9th September, when Facilities information began to be properly extracted from the Databank database (TFS).

This ended up unintentionally overwriting the previous Siebel grants facilties information, hence the need for the reset.
"""

from django.core.management.base import BaseCommand
from datamad2.models import ImportedGrant, Grant
import datetime
from django.forms.models import model_to_dict

class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        input_group = parser.add_mutually_exclusive_group()
        input_group.add_argument('--rollback_date', help='Rollback to last change prior to this date')
        input_group.add_argument('--rollback_field', help='Field(s) to amend to version prior to given date')

    @staticmethod
    def roundDownDateTime(dt):
        delta_min = dt.minute % 1
        return datetime.datetime(dt.year, dt.month, dt.day,
                                dt.hour, dt.minute - delta_min)

    def handle(self, *args, **options):
        if options["rollback_date"] is None:
            # Default rollback option
            # options["rollback"] = datetime.datetime(2025, 9, 10, 9, 9)
            options["rollback_date"] = datetime.datetime(2025, 9, 10, 9, 7, tzinfo=datetime.timezone.utc)

            # (2025, 9, 10, 9, 7, 4, 856784, tzinfo=datetime.timezone.utc)
        else:
            # Change rollback into a datetime
            options["rollback_date"] = datetime.datetime.strptime(options['rollback_date'], '%Y%m%d').date()

        if options["rollback_field"] is None:
            # Default field to rollback
            options["rollback_field"] = ["facility"]
            
        siebel_grants = Grant.objects.filter(grant_ref__contains='/1')
        siebel_grants = siebel_grants.objects.imported_grant_set.first().filter(actual_end_date__gt=datetime.datetime(2024, 5, 31, tzinfo=datetime.timezone.utc))
        
        for siebel_grant in siebel_grants:
            current_ig = siebel_grant.importedgrant
            ig_history = siebel_grant.importedgrant_set.filter(creation_date__lt=options["rollback_date"]).order_by('creation_date').reverse()

            previous_ig = ig_history[0]

            for field in options["rollback_field"]:
                current_ig.facility = getattr(previous_ig, field)
            
            data = model_to_dict(current_ig)

            # Remove any fields not needed in the new model:
            for delete_str in [""]:
                data.pop(delete_str)

            new_ig = ImportedGrant(**data)
            new_ig.save()
