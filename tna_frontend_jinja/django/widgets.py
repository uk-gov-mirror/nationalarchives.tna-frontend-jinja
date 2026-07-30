import datetime

from django import forms

from ._shared import date_input_part, trim_progressive_values


class TnaDateInputWidget(forms.MultiWidget):
    def __init__(self, field_codes=("d", "m", "y"), progressive=False, attrs=None):
        self.field_codes = tuple(field_codes)
        self.progressive = progressive
        widgets = [
            forms.TextInput(attrs={"inputmode": "numeric"})
            for _ in self.field_codes
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, datetime.date):
            values = {
                "day": str(value.day),
                "month": str(value.month),
                "year": str(value.year),
            }
            return [values[date_input_part(code)] for code in self.field_codes]

        if isinstance(value, (list, tuple)):
            values = [str(item) for item in value]
            return values + [""] * (len(self.field_codes) - len(values))

        return [""] * len(self.field_codes)

    def value_from_datadict(self, data, files, name):
        values = [
            data.get(f"{name}-{date_input_part(code)}", "")
            for code in self.field_codes
        ]

        return trim_progressive_values(values, self.progressive)