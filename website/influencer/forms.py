# your_app_name/forms.py

from django import forms
from .models import Influencer, Category, SuggestedInfluencerEdit, Content, Collaboration # Import all necessary models
from django_ckeditor_5.widgets import CKEditor5Widget # Import the CKEditor5 widget
