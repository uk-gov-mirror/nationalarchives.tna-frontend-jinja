from django import forms

from tna_frontend_jinja.django import (
    TnaBooleanField,
    TnaCharField,
    TnaCheckboxesField,
    TnaDateField,
    TnaEmailField,
    TnaFileField,
    TnaMonthField,
    TnaProgressiveDateField,
    TnaRadioField,
    TnaSelectField,
    TnaTextareaField,
    TnaYearField,
)


class ExampleForm(forms.Form):
    username = TnaCharField(
        label="Username",
        help_text="This will be used to log in",
        max_length=256,
    )
    email = TnaEmailField(
        label="Email address",
        required=False,
    )
    biography = TnaTextareaField(
        label="Biography",
        required=False,
        tna_params={"rows": 6},
    )
    contact_method = TnaRadioField(
        label="How should we contact you?",
        choices=[("email", "Email"), ("phone", "Phone")],
    )
    topics = TnaCheckboxesField(
        label="Topics",
        required=False,
        choices=[("python", "Python"), ("django", "Django")],
    )
    category = TnaSelectField(
        label="Category",
        choices=[("", "Select a category"), ("news", "News"), ("blog", "Blog")],
    )
    agreed = TnaBooleanField(
        label="Terms and conditions",
        checkbox_label="I agree to the terms and conditions",
        required=False,
    )
    attachment = TnaFileField(
        label="Upload a file",
        required=False,
    )
    date_of_birth = TnaDateField(
        label="Date of birth",
        required=False,
        help_text="Enter your date of birth in the format DD MM YYYY",
    )
    month_of_birth = TnaMonthField(
        label="Month of birth",
        required=False,
        help_text="Enter your month of birth in the format MM YYYY",
    )
    year_of_birth = TnaYearField(
        label="Year of birth",
        required=False,
        help_text="Enter your year of birth in the format YYYY",
    )
    approximate_date = TnaProgressiveDateField(
        label="Approximate date",
        required=False,
        help_text="Enter the year, year and month, or the full date",
    )


class ConditionalExampleForm(forms.Form):
    contact_method = TnaRadioField(
        label="How should we contact you?",
        choices=[("email", "Email"), ("phone", "Phone")],
    )
    email = TnaEmailField(label="Email address", required=False)
    phone = TnaCharField(label="Phone number", required=False)

    def clean(self):
        cleaned_data = super().clean()
        contact_method = cleaned_data.get("contact_method")

        if contact_method == "email" and not cleaned_data.get("email"):
            self.add_error("email", "Enter an email address")

        if contact_method == "phone" and not cleaned_data.get("phone"):
            self.add_error("phone", "Enter a phone number")

        if contact_method != "email":
            cleaned_data["email"] = ""

        if contact_method != "phone":
            cleaned_data["phone"] = ""

        return cleaned_data