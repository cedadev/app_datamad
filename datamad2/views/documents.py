# encoding: utf-8
"""
Views relating to document uploading and manipulating
"""
__author__ = 'Richard Smith'
__date__ = '10 Dec 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

# DataMAD imports
from datamad2.models import Document, Grant
import datamad2.forms as datamad_forms

# Django imports
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

# JQuery File Uploader Imports
from jfu.http import upload_receive, UploadResponse, JFUResponse

# Python imports
import re

DOCUMENT_NAMING_PATTERN_SIEBEL = re.compile(r"^(?P<grant_ref>\w*_\w*_\d*)_(?P<doc_type>\w*)(?P<extension>\.\w*)$")
DOCUMENT_NAMING_PATTERN_DATABANK = re.compile(r"^(?P<grant_ref>\d{5})_(?P<doc_type>\w*)(?P<extension>\.\w*)$")

class FormatError(Exception):
    pass


@login_required
def multiple_document_upload(request):
    """
    Handles the mutiple document upload feature
    :param request: WSGI Request
    :return:
    """
    if request.method == 'POST':

        file = upload_receive(request)

        name = str(file)

        try:
            m = DOCUMENT_NAMING_PATTERN_SIEBEL.match(name)
            if not m:  # Check document naming pattern against new UKRI convention, accept both, for now.
                m = DOCUMENT_NAMING_PATTERN_DATABANK.match(name)
                if not m:
                    m = DOCUMENT_NAMING_PATTERN_DATABANK.match(name)
                    if not m:
                        raise FormatError(f"File name {name} is not formatted correctly e.g \
                                          NE_G0123X_1_DMP.docx for NERC grant ref format \
                                          or 12345_DMP.docx for UKRI format.")

            grant_ref = m.group('grant_ref').replace('_', '/')

            file_type = m.group('doc_type').lower()
            if file_type != 'dmp':
                file_type = 'support'

            document = Document(upload=file)

            document.grant = Grant.objects.get(grant_ref=grant_ref)
            document.type = file_type
            document.save()
        except ValidationError:
            response = HttpResponse(status=400)
            response.reason_phrase = 'File already uploaded'

        except FormatError as exc:
            response = HttpResponse(status=400)
            response.reason_phrase = f'{exc}'

        except ObjectDoesNotExist:
            response = HttpResponse(status=404)
            response.reason_phrase = f'Grant ref: {grant_ref} not found'

        else:

            file_dict = {
                'name': file.name,
                'size': file.size,

                'url': document.upload.url,

                'deleteUrl': reverse('delete_file', kwargs={'pk': document.pk}),
                'deleteType': 'POST',
            }
            response = UploadResponse(request, file_dict)

        return response
    else:
        form = datamad_forms.MultipleDocumentUploadForm()
    return render(request, 'datamad2/multiple_document_upload.html', {
        'form': form,
        'JQ_OPEN': '{%',
        'JQ_CLOSE': '%}'
    })


@login_required
def document_upload(request, pk):
    """
    Handles the single document upload to the specified grant
    :param request: WSGI Request
    :param pk: Grant ID
    :return:
    """
    grant = get_object_or_404(Grant, pk=pk)

    if request.method == 'POST':
        form = datamad_forms.DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            name = str(request.FILES.get('upload'))
            try:
                # Check basic name format
                m = DOCUMENT_NAMING_PATTERN_SIEBEL.match(name)
                
                if not m:
                    m = DOCUMENT_NAMING_PATTERN_DATABANK.match(name)
                    if not m:
                        raise FormatError(f"File name {name} is not formatted correctly e.g \
                                          NE_G0123X_1_DMP.docx for NERC grant ref format \
                                          or 12345_DMP.docx for UKRI format.")

                # Check grant ref against grant you are trying to upload against
                grant_ref = (m.group('grant_ref')).replace('_', '/')
                if grant_ref != grant.grant_ref:
                    raise FormatError(f"Grant reference in file {name} does not match the grant you are uploading to.")

                # Extract the file type
                file_type = m.group('doc_type').lower()
                if file_type != 'dmp':
                    file_type = 'support'

                if file_type == 'dmp' and grant.dmp_agreed:
                    raise PermissionError('You are trying to upload a DMP to a grant where the DMP has been marked '
                                          'as final. If you intend to provide an update, you must clear the agreed '
                                          'status for the DMP before trying again.')

                # Create the document object
                document = form.save(commit=False)
                document.grant = grant
                document.type = file_type
                document.save()

                messages.success(request, 'File uploaded successfully')
                return redirect(reverse('grant_detail', kwargs={'pk': pk}))

            except ValidationError as exc:
                messages.error(request, f'The file {name} has already been uploaded ')

            except (FormatError, PermissionError) as exc:
                messages.error(request, f"{exc}")
    else:
        form = datamad_forms.DocumentForm(instance=grant)

    return render(request, 'datamad2/document_upload.html', {'form': form, 'grant': grant})


@login_required()
def delete_file(request, pk):
    """
    Delete specified file
    :param request: WSGI Request
    :param pk: Document ID
    :return:
    """
    if request.POST:
        success = True
        try:
            instance = Document.objects.get(pk=pk)
            instance.delete_file()
        except Document.DoesNotExist:
            success = False

        return JFUResponse(request, success)

    document = Document.objects.get(pk=pk)
    document.delete_file()
    return redirect(reverse('grant_detail', kwargs={'pk': document.grant.pk}))
