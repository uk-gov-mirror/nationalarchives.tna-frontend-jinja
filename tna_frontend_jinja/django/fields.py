import calendar
import datetime

from django import forms
from django.core.exceptions import ValidationError

from .helpers import DATE_INPUT_PARTS, trim_progressive_values
from .widgets import TnaDateInputWidget


def _year_format(value, allow_two_digit_year):
    if allow_two_digit_year and len(value) <= 2:
        return "%y"
    return "%Y"


def _month_format(value):
    if value.isdigit():
        return "%m"
    if len(value) <= 3:
        return "%b"
    return "%B"


def _parse_date_parts(values, codes, allow_two_digit_year):
    formats = []

    for code, value in zip(codes, values, strict=False):
        if code == "d":
            formats.append("%d")
        elif code == "m":
            formats.append(_month_format(value))
        elif code == "y":
            formats.append(_year_format(value, allow_two_digit_year))

    return datetime.datetime.strptime(
        " ".join(values),
        " ".join(formats),
    ).date()


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


class TnaBaseDateField(TnaFieldMixin, forms.Field):
    template_name = "django/forms/fields/date-input.html"
    field_codes = ("d", "m", "y")
    progressive = False

    def __init__(
        self,
        *args,
        allow_two_digit_year=False,
        invalid_date_error_message="",
        end_of_partial_date_range=False,
        **kwargs,
    ):
        self.allow_two_digit_year = allow_two_digit_year
        self.end_of_partial_date_range = end_of_partial_date_range
        widget = kwargs.pop("widget", None) or TnaDateInputWidget(
            field_codes=self.field_codes,
            progressive=self.progressive,
        )
        super().__init__(*args, widget=widget, **kwargs)
        self.invalid_date_error_message = (
            invalid_date_error_message or f"{self.label} must be a real date"
        )

    def to_python(self, value):
        if value in self.empty_values:
            return None

        if isinstance(value, datetime.date):
            return value

        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.invalid_date_error_message)

        values = [str(item).strip() for item in value]
        if not any(values):
            return None

        values = trim_progressive_values(values, self.progressive)

        codes = self.field_codes[: len(values)] if self.progressive else self.field_codes
        if len(values) != len(codes) or any(not item for item in values):
            raise ValidationError(self.invalid_date_error_message)

        try:
            parsed_date = _parse_date_parts(
                values,
                codes,
                self.allow_two_digit_year,
            )
        except ValueError as exc:
            raise ValidationError(self.invalid_date_error_message) from exc

        if self.end_of_partial_date_range and "d" not in codes:
            if "m" in codes:
                parsed_date = parsed_date.replace(
                    day=calendar.monthrange(
                        parsed_date.year,
                        parsed_date.month,
                    )[1],
                )
            else:
                parsed_date = parsed_date.replace(month=12, day=31)

        return parsed_date

    def date_input_parts(self):
        return [DATE_INPUT_PARTS[code] for code in self.field_codes]


class TnaDateField(TnaBaseDateField):
    field_codes = ("d", "m", "y")


class TnaMonthField(TnaBaseDateField):
    field_codes = ("m", "y")


class TnaYearField(TnaBaseDateField):
    field_codes = ("y",)


class TnaProgressiveDateField(TnaBaseDateField):
    field_codes = ("y", "m", "d")
    progressive = True
