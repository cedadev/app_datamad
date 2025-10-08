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
            # options["rollback_date"] = datetime.datetime(2025, 9, 10, 9, 7, 4, tzinfo=datetime.timezone.utc) # Prod
            options["rollback_date"] = datetime.datetime(2025, 8, 10, 12, 23, 00, tzinfo=datetime.timezone.utc) # Staging
            # options["rollback_date"] = datetime.datetime(2025, 10, 3, 12, 00, 00, tzinfo=datetime.timezone.utc) # MP local
        else:
            # Change rollback into a datetime
            options["rollback_date"] = datetime.datetime.strptime(options['rollback_date'], '%Y%m%d').date()

        if options["rollback_field"] is None:
            # Default field to rollback
            options["rollback_field"] = ["facility"]
            
        # Prefetch related, prefetch object? To think
        # Select related grant to reduce by one query per loop.
        siebel_grants = ImportedGrant.objects.filter(grant_ref__contains='/1').filter(actual_end_date__gt=datetime.datetime(2024, 5, 31, tzinfo=datetime.timezone.utc))


        # Needed to stop processing every imported grant (as there will be one per change/ creation_date)
        # Only want to process the imported grant before rollback_date once.
        grant_ref_list = []

        if siebel_grants:
            for current_ig in siebel_grants:
                siebel_grant = current_ig.grant

                # Look into efficiency with "-creation_date" vs reverse
                # Think about replacing previous_ig = ig_history[0] with .first() on line below
                ig_history = siebel_grant.importedgrant_set.filter(creation_date__lt=options["rollback_date"]).order_by('creation_date').reverse()
                
                if ig_history:
                    previous_ig = ig_history[0]
                    grant_ref = previous_ig.grant_ref

                    if grant_ref not in grant_ref_list:  # Stops multiple ig_history's being processed, new creation_dates and then constantly overwriting itself unnecessarily.
                        grant_ref_list.append(grant_ref)
                    
                        for field in options["rollback_field"]:
                            previous_value = getattr(previous_ig, field)
                            setattr(current_ig, field, previous_value) # Not ideal, as theoretically you could break the internal behavior of the object after setting the new attribute. But it works in a very clumsy way...
                        
                        data = model_to_dict(current_ig)

                        # Remove any fields not needed in the new model:
                        for delete_str in ["id", "grant"]:
                            data.pop(delete_str)

                        new_ig = ImportedGrant(**data)
                        new_ig.save()
