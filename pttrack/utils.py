import json
import string
import collections
import datetime

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Prefetch, Q

from . import models as mymodels
from workup import models as workupmodels
from . import forms as myforms
from appointment.models import Appointment


def all_variations(name):
    '''
    all_variations is a function that is used to help search for all
    variations of a string that have either added, removed, or changed
    1 letter. Function returns a list of all variations of the input string.
    '''
    all_vars = []
    if name is None or len(name) == 0:
        return all_vars
    if len(name) == 1:
        all_vars.append(name)
        return all_vars
    else:
        #try all variations of switching letters, other than first letter
        for i in range(1,len(name)):
            #remove letter
            all_vars.append(name[:i] + name[i+1:])
            #change letter and add letter
            for j in string.ascii_lowercase:
                all_vars.append(name[:i] + j + name[i+1:])
                all_vars.append(name[:i] + j + name[i:])

        all_vars.append(name)
        return all_vars

def return_duplicates(first_name_str, last_name_str):
    '''
    search database for all variations of first and last name off by 1
    letter (except for first letter must be correct) and return matching
    results.  First name may also be abbreviated (to cover cases like
    ben and benjamin)
    '''
    first_name_var = all_variations(first_name_str.capitalize())
    last_name_var = all_variations(last_name_str.capitalize())
    if len(first_name_var) == 0 or len(last_name_var) == 0:
        return
    return mymodels.Patient.objects.filter((Q(first_name__in=first_name_var) |
        Q(first_name__startswith=first_name_str)) &
        Q(last_name__in=last_name_var))