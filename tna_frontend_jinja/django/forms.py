from django import forms

from .helpers import django_field_errors


class TnaFormMixin:
    def error_summary(self, params=None):
        return django_field_errors(self, params=params)


class TnaForm(TnaFormMixin, forms.Form):
    pass