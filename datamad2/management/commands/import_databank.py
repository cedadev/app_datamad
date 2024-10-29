# encoding: utf-8
"""
Import the latest data from the UKRI Databank database into the Datamad database

Based on import_database script written by Richard Smith
"""
__author__ = 'Matthew Paice'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'matthew.paice@stfc.ac.uk'

from django.core.management.base import BaseCommand
from datamad2.models import ImportedGrant, Grant

import pandas as pd
import math
from dateutil.parser import parse
from tqdm import tqdm
from django.core.exceptions import ObjectDoesNotExist
import io
import requests
from requests.auth import HTTPBasicAuth

class Command(BaseCommand):
    help = __doc__

