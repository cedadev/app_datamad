# encoding: utf-8
"""
Views relating to the grants
"""
__author__ = 'Richard Smith'
__date__ = '10 Dec 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

# Datamad2 imports
from datamad2.models import Grant, Document, DataProduct, ImportedGrant
from .base import DATAPRODUCT_TABLE_CLASS_MAP, DATAPRODUCT_FORM_CLASS_MAP
from .generic import ObjectDeleteView
import datamad2.forms as datamad_forms
from datamad2.utils import generate_document_from_template, get_verbose_name

# Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.views.generic.edit import UpdateView
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from django.http import FileResponse
from django.contrib import messages
from django.core import serializers

# Utility imports
from jinja2.exceptions import TemplateError as Jinja2TemplateError

# Python imports
import os
import operator
from datetime import datetime
import io
import time
import json


@login_required
def grant_detail(request, pk):
    """
    Grant detail page
    :param request: WSGI Request
    :param pk: Grant ID
    :return:
    """
    grant = get_object_or_404(Grant, pk=pk)
    imported_grant = grant.importedgrant

    docs = grant.document_set.filter(type='support')
    dmp_docs = grant.document_set.filter(type='dmp')

    if grant.parent_grant:
        parent_docs = grant.parent_grant.document_set.filter(type='support')
        parent_dmps = grant.parent_grant.document_set.filter(type='dmp')

    else:
        parent_docs = Document.objects.none()
        parent_dmps = Document.objects.none()

    return render(request, 'datamad2/grant_detail.html', {
        'imported_grant': imported_grant,
        'supporting_docs': docs | parent_docs,
        'dmp_docs': dmp_docs | parent_dmps,
    })


@login_required
def grant_visibility(request, pk, action):
    """

    :param request:
    :param pk:
    :param action:
    :return:
    """

    grant = get_object_or_404(Grant, pk=pk)
    if action == 'show':
        grant.hide_record = False
    elif action == 'hide':
        grant.hide_record = True

    grant.save()

    return HttpResponse(status=200)


@login_required
def grant_history(request, pk):
    """
    Displays the grant history table
    :param request: WSGI Request
    :param pk: Grant ID
    :return:
    """
    grant = get_object_or_404(Grant, pk=pk)
    return render(request, 'datamad2/grant_history.html', {'grant': grant})


@login_required
def grant_history_detail(request, pk, imported_pk):
    """
    Displays the grant detail with changes highlighted
    :param request: WSGI Request
    :param pk: Grant ID
    :param imported_pk: ImportedGrant ID
    :return:
    """
    grant = get_object_or_404(Grant, pk=pk)
    imported_grant = get_object_or_404(ImportedGrant, pk=imported_pk)
    return render(request, 'datamad2/grant_detail_history.html', {'grant': grant, 'imported_grant': imported_grant})


class DataProductView(LoginRequiredMixin, TemplateView):
    """
    Lists all the data products for the specified grant
    """
    template_name = 'datamad2/dataproduct_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        grant = get_object_or_404(Grant, pk=kwargs['pk'])
        context['grant'] = grant
        context['data_products'] = {
            product: table(grant.dataproduct_set.filter(data_product_type=product))
            for product, table in DATAPRODUCT_TABLE_CLASS_MAP.items()
        }
        return context


class DataProductUpdateCreateView(LoginRequiredMixin, UpdateView):
    """
    Update or create a new data product
    """
    template_name = 'datamad2/dataproduct_form_view.html'
    model = DataProduct

    def get_initial(self):
        initial = super().get_initial()
        initial['grant_id'] = get_object_or_404(Grant, pk=self.kwargs['pk']).pk
        initial['data_product_type'] = self.kwargs['data_product_type']
        return initial

    def get_success_url(self):
        return reverse('dataproduct_view', kwargs={'pk': self.kwargs['pk']})

    def get_form_class(self):
        """Return the form class to use in this view."""
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )

        form_class = DATAPRODUCT_FORM_CLASS_MAP.get(self.kwargs['data_product_type'])
        return form_class

    def get_object(self, **kwargs):
        """
        This modification means this view behaves as an update or create view.
        If the object doesn't exist, it will create one.
        """
        try:
            return self.model.objects.get(pk=self.kwargs['dp_pk'])
        except (ObjectDoesNotExist, KeyError):
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grant'] = get_object_or_404(Grant, pk=self.kwargs['pk'])
        context['data_product_type'] = self.kwargs['data_product_type']
        return context


class DataProductDeleteView(ObjectDeleteView):
    """
    Delete a Data Product
    """
    model = DataProduct
    pk_url_kwarg = 'dp_pk'

    def get_success_url(self):
        return reverse('dataproduct_view', kwargs={'pk': self.kwargs['pk']})


class DocumentGenerationSelectView(LoginRequiredMixin, FormView):
    """
    View which displays the available templates for document generation
    Only displays the forms created by the logged in users datacentre
    """
    template_name = 'datamad2/generate_document_from_template.html'
    form_class = datamad_forms.DocumentGenerationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imported_grant'] = get_object_or_404(Grant, pk=self.kwargs['pk']).importedgrant
        return context

    def form_valid(self, form):
        template = form.cleaned_data['document_template']
        grant = Grant.objects.get(pk=self.kwargs['pk'])
        context = {
            'grant': grant
        }

        # Catch template issues and inform the user of the issue to provide them
        # the chance to solve the issue without support. TemplateError is baseclass
        # for all Jinja2 Template Render issues.
        try:
            doc = generate_document_from_template(template, context)
        except Jinja2TemplateError as e:
            messages.error(self.request, f'Error Rendering Document: "{e}"')
            return redirect('grant_generate_document_select', pk=self.kwargs['pk'])

        download_filename = f'{grant.grant_ref.replace("/", "_")}_{template.type.upper()}' \
                            f'{os.path.splitext(template.template.name)[1]}'

        return FileResponse(open(doc, 'rb'), as_attachment=True, filename=download_filename)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['datacentre'] = self.request.user.data_centre
        return kwargs


class ChangeClaimFormView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Form to allow the user to reassign the primary datacentre
    """
    model = Grant
    template_name = 'datamad2/change_claim.html'
    form_class = datamad_forms.UpdateClaimForm
    permission_denied_message = "Your data centre does not match the datacentre of the grant"

    def test_func(self):
        """
        Test to make sure that the user either comes from a datacentre which
        has responsibility for the grant or the grant has not been claimed.
        Aims to prevent users from unclaiming or reassigning grants already
        assigned to another datacentre

        :return: bool
        """
        grant = get_object_or_404(Grant, pk=self.kwargs['pk'])
        user_datacentre = self.request.user.data_centre
        grant_datacentre = grant.assigned_data_centre
        return grant_datacentre is None or grant_datacentre == user_datacentre

    def get_success_url(self):
        return reverse('grant_detail', kwargs={'pk': self.kwargs['pk']})


class GrantInfoEditView(LoginRequiredMixin, UpdateView):
    """
    View which presents a form with the editable grant information
    """
    model = Grant
    form_class = datamad_forms.GrantInfoForm
    template_name = 'datamad2/grantinfo_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        if "update_linked" in self.request.POST:
            grant = get_object_or_404(Grant, pk=pk)
            grant.update_linked_grants
        
        return reverse('grant_detail', kwargs={'pk': pk}) + '#editable-info'


class SearchResultsExportView(LoginRequiredMixin, FormView):
    """
    Export
    """ 
    form_class = datamad_forms.GrantFieldsExportForm
    template_name = 'datamad2/grant_export_form.html'
    success_url = reverse_lazy('results_export')

    def form_valid(self, form):

        search_form = datamad_forms.DatamadFacetedSearchForm(
            self.request.GET,
            selected_facets=self.request.GET.getlist("selected_facets"),
            load_all=True
        )

        selected_columns = [column for column, value in form.cleaned_data.items() if value]
        verbose_columns = [get_verbose_name(Grant, c, sep='.') for c in selected_columns]
        
        if search_form.is_valid():
            qs = search_form.search()

            with io.StringIO() as stream:

                # Add provenance information
                stream.write('Provenance:\n')
                stream.write(f'Search URL, {self.request.build_absolute_uri()}\n')

                # Add column headers
                stream.write(f'{",".join(verbose_columns)}\n')

                for item in qs:

                    grant = item.object

                    row = operator.attrgetter(*selected_columns)(grant)

                    # Make sure all values are converted to strings
                    row = [f'"{item}"' for item in row]
                    line = f'{",".join(row)}\n'
                    stream.write(line)

                filename = f'datamad_search_results_{datetime.now().strftime("%Y-%m-%dT%H_%M")}.csv'
                response = HttpResponse(stream.getvalue())
                response['Content-Type'] = 'text/plain'
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response


            # Attempts at pulling back relevant Grants and ImportedGrants in less time than 12-20 minutes
            # Slowdown caused by repeated database queries (7300 with current database contents), need to
            # do it in one or two and pull back latest from Grant that matches ImportedGrant.
            # TODO, finish
            """
            tic = time.perf_counter()
            qs = search_form.search()
            qs = qs.models(Grant, ImportedGrant)
            qs = qs.load_all()

            data = list(map(lambda x: x.get_stored_fields(), qs))
            es_col_names = list(data[0].keys())
            
            toc = time.perf_counter()
            print("es query time = " + str(toc - tic))

            # Reorder selected_columns and es_selected_cols into es download order, generate verbose columns
            # d = {s.split(".")[1]: s for s in selected_columns}
            # sel_cols_ordered = [d[c] for c in es_col_names if c in d]

            verbose_columns = [get_verbose_name(Grant, c, sep='.') for c in selected_columns]

            # Strip importedgrant. from selected_columns so it matches es index name
            es_selected_cols = [s.replace('importedgrant.', '') for s in selected_columns]

            # Try Django query sets as Haystack isn't being used properly in the original anyway:
            djan_qs = ImportedGrant.objects.all().select_related("grant")

            data_djan_qs = serializers.serialize("json", ImportedGrant.objects.select_related("grant").all())
            json_djan = json.loads(data_djan_qs)

            tic = time.perf_counter()
            data_djan_qs_ig = serializers.serialize("json", ImportedGrant.objects.all())
            data_djan_qs_g = serializers.serialize("json", Grant.objects.all())

            test = ImportedGrant.grant.all()[0]
            temp = Grant.importedgrant_set.all()
            json_djan_ig = json.loads(data_djan_qs_ig)
            json_djan_g = json.loads(data_djan_qs_g)
            toc = time.perf_counter()
            print("django query time = " + str(toc - tic))


            

            with io.StringIO() as stream:

                # Add provenance information
                stream.write('Provenance:\n')
                stream.write(f'Search URL, {self.request.build_absolute_uri()}\n')

                # Add column headers
                stream.write(f'{",".join(verbose_columns)}\n')

                tic = time.perf_counter()
                for item in qs:

                    grant = item.object
                    lemon = list(grant)

                    row_temp = operator.attrgetter(*selected_columns)(grant)

                    # Make sure all values are converted to strings
                    row_temp = [f'"{item}"' for item in row_temp]
                    line = f'{",".join(row_temp)}\n'
                    stream.write(line)
                    
                toc= time.perf_counter()
                print("es query time orig with load_all()= " + str(toc - tic))

                missing_cols_new = [x for x in es_selected_cols if x not in es_col_names]
                missing_cols_old = 

                lime = grant.importedgrant
                old_query_v2 = list(vars(grant.importedgrant))

                # add in missing "functions" to old_query list
                old_query.append(["child_grant", "dataproduct_set", "date_added", "digital_data_products",
                                  "dmp_agreed_date", "document_set", ])


                filename = f'datamad_search_results_{datetime.now().strftime("%Y-%m-%dT%H_%M")}.csv'
                response = HttpResponse(stream.getvalue())
                response['Content-Type'] = 'text/plain'
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

                for row in data:
                    # Remove entries not in selected_columns
                    row_sel_cols = {i:row[i] for i in row if i not in es_selected_cols}

                    # Make sure all values are converted to strings
                    row = [f'"{item}"' for item in row.values()]
                    line = f'{",".join(row)}\n'
                    stream.write(line)      

                filename = f'datamad_search_results_{datetime.now().strftime("%Y-%m-%dT%H_%M")}.csv'
                response = HttpResponse(stream.getvalue())
                response['Content-Type'] = 'text/plain'
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response
        """
            
        # Add error message if search form validation fails
        error_string = ''
        for field, errors in search_form.errors.items():
            error_string += f'{field}\n'
            for error in errors:
                error_string += f'\t{error}\n'

        messages.error(self.request, f'An error occurred with the search parameters:\n{error_string}')

        return self.render_to_response(self.get_context_data(form=form))