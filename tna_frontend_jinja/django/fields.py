from django import forms
from django.core.exceptions import ValidationError
class TnaFieldMixin:
    def __init__(self, *args, tna_params=None, **kwargs):
        self.tna_params = tna_params or {}
        super().__init__(*args, **kwargs)


class TnaCharField(TnaFieldMixin, forms.CharField):
    template_name = "django/forms/fields/text-input.html"


class TnaEmailField(TnaFieldMixin, forms.EmailField):
    template_name = "django/forms/fields/text-input.html"


class TnaTextareaField(TnaFieldMixin, forms.CharField):
    widget = forms.Textarea
    template_name = "django/forms/fields/textarea.html"


class TnaRadioField(TnaFieldMixin, forms.ChoiceField):
    widget = forms.RadioSelect
    template_name = "django/forms/fields/radios.html"


class TnaSelectField(TnaFieldMixin, forms.ChoiceField):
    widget = forms.Select
    template_name = "django/forms/fields/select.html"


class TnaCheckboxesField(TnaFieldMixin, forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    template_name = "django/forms/fields/checkboxes.html"


class TnaBooleanField(TnaFieldMixin, forms.BooleanField):
    template_name = "django/forms/fields/checkbox.html"

    def __init__(self, *args, checkbox_label=None, **kwargs):
        self.checkbox_label = checkbox_label
        super().__init__(*args, **kwargs)


class TnaFileField(TnaFieldMixin, forms.FileField):
    template_name = "django/forms/fields/file-input.html"

