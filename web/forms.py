from django import forms
from django.forms import Form


class SearchForm(Form):
    search_term = forms.CharField(label='Search text', max_length=100)
    distance = forms.IntegerField(label='Distance from your location', max_value=100, required=False)
