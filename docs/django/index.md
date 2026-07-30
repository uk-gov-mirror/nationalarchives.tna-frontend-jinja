# Django forms integration

TNA Frontend Jinja supports Django projects for template rendering and includes a starter Django forms integration layer.

This guide shows how to use the packaged helpers and field classes, along with the underlying pattern they follow.

The packaged Django integration requires Django 5.2 or later because it relies on the field rendering API used by `BoundField.as_field_group()`.

A minimal reference application is included in `test/django` to show the expected project shape.

## Status

- Jinja template support is built in.
- Starter Django fields and helpers are included in the package.

## 0. Installation

```sh
# Install with Poetry
poetry add tna-frontend-jinja[django]

# Install with pip
pip install tna-frontend-jinja[django]
```

## 1. Configure Jinja and Django's form renderer

Ensure the Jinja backend is configured before the DjangoTemplates backend and that the package templates are included in `DIRS`.

```py
from django import forms
from jinja2 import Environment, select_autoescape
from tna_frontend_jinja.django import DjangoFormsHelpers


def environment(**options):
  options.setdefault("autoescape", select_autoescape(["html"]))
  env = Environment(**options)
  DjangoFormsHelpers(env)
  return env


TEMPLATES = [
  {
    "BACKEND": "django.template.backends.jinja2.Jinja2",
    "DIRS": [
      os.path.join(BASE_DIR, "app/templates"),
      os.path.join(get_path("platlib"), "tna_frontend_jinja/templates"),
    ],
    "APP_DIRS": True,
    "OPTIONS": {
      "environment": "config.jinja2.environment",
    },
  },
  {
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {
      "context_processors": [
        "django.template.context_processors.request",
      ],
    },
  },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"
```

`TemplatesSetting` is important because it makes Django resolve form, field, and widget templates through your configured template engines instead of the standalone default renderer.

`DjangoFormsHelpers` registers the Jinja globals used by the packaged Django field templates.

## 2. Render full components at the field level

Render complete TNA components from field templates using the `BoundField` context.

TNA components often need access to:

- the label
- the hint text
- the current value
- the field errors
- field ids and names
- grouped choices such as radios or checkboxes

## 3. Use the packaged starter field classes

The package includes starter field classes for common form patterns:

- `TnaCharField`
- `TnaEmailField`
- `TnaTextareaField`
- `TnaRadioField`
- `TnaSelectField`
- `TnaCheckboxesField`
- `TnaBooleanField`
- `TnaFileField`
- `TnaDateField`
- `TnaMonthField`
- `TnaYearField`
- `TnaProgressiveDateField`

Import them from `tna_frontend_jinja.django`.

```py
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
```

Each field accepts an optional `tna_params` argument for component-level customisation.

```py
name = TnaCharField(
  label="Your name",
  tna_params={"headingLevel": 2, "size": "m"},
)
```

`TnaBooleanField` also accepts an optional `checkbox_label` argument so the question label and the checkbox label can be different.

```py
agree = TnaBooleanField(
  label="Terms and conditions",
  checkbox_label="I agree to the terms and conditions",
)
```

## 4. Build forms with TNA fields

The simplest usage is to declare forms with the packaged fields and render each bound field using `as_field_group()`.

```py
from django import forms
from tna_frontend_jinja.django import (
  TnaCharField,
  TnaEmailField,
  TnaRadioField,
)


class ContactForm(forms.Form):
  name = TnaCharField(
    label="Your name",
    help_text="Enter your full name",
  )
  email = TnaEmailField(
    label="Email address",
  )
  contact_method = TnaRadioField(
    label="How should we contact you?",
    choices=[("email", "Email"), ("phone", "Phone")],
  )
```

## 5. Views and routing

Use a view to instantiate the form, handle `POST`, and render the template in the GET or invalid state.

```py
from django.shortcuts import redirect, render


def contact_view(request):
  form = ContactForm(request.POST or None, request.FILES or None)

  if request.method == "POST" and form.is_valid():
    return redirect("success")

  return render(request, "forms/contact.html", {"form": form})
```

This is the Django equivalent of the Flask routing section in the WTForms guide.

## 6. Templates

Each packaged field sets a `template_name`, so you can render it with Django's field-group rendering.

```jinja
{%- from 'components/error-summary/macro.html' import tnaErrorSummary -%}

{% if form.errors %}
  {{ tnaErrorSummary(django_field_errors(form)) }}
{% endif %}

<form method="post"{% if form.is_multipart() %} enctype="multipart/form-data"{% endif %}>
  {% csrf_token %}

  {{ form.name.as_field_group() }}
  {{ form.email.as_field_group() }}
  {{ form.contact_method.as_field_group() }}
</form>
```

## 7. Build custom field templates when you need them

Each field template receives `field` in its context. `field` is a Django `BoundField`.

That gives you access to:

- `field.label`
- `field.help_text`
- `field.errors`
- `field.id_for_label`
- `field.html_name`
- `field.value()`
- `field.field`, which is the underlying Django field

Example text input template:

```jinja
{%- from 'components/text-input/macro.html' import tnaTextInput -%}

{{ tnaTextInput(django_text_input_params(field)) }}
```

Example radios template:

```jinja
{%- from 'components/radios/macro.html' import tnaRadios -%}

{{ tnaRadios(django_radios_params(field)) }}
```

The packaged templates use these helper functions internally. Override them only when you need custom behaviour.

## 8. Add a form-level error summary

The package includes a `django_field_errors()` helper for building error-summary items from a Django form.

```jinja
{%- from 'components/error-summary/macro.html' import tnaErrorSummary -%}

{% if form.errors %}
  {{ tnaErrorSummary(django_field_errors(form)) }}
{% endif %}
```

## 9. Handle conditional validation in the form class

Conditional validation is usually best handled in `clean()`.

```py
class ContactPreferenceForm(forms.Form):
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
```

## 10. Supported starter field mapping

| Packaged field | Django widget | TNA component template |
| -------------- | ------------- | ---------------------- |
| `TnaCharField` | `TextInput` | `text-input` |
| `TnaEmailField` | `EmailInput` | `text-input` |
| `TnaTextareaField` | `Textarea` | `textarea` |
| `TnaRadioField` | `RadioSelect` | `radios` |
| `TnaSelectField` | `Select` | `select` |
| `TnaCheckboxesField` | `CheckboxSelectMultiple` | `checkboxes` |
| `TnaBooleanField` | `CheckboxInput` | `checkboxes` |
| `TnaFileField` | `ClearableFileInput` | `file-input` |
| `TnaDateField` | custom `MultiWidget` | `date-input` |
| `TnaMonthField` | custom `MultiWidget` | `date-input` |
| `TnaYearField` | custom `MultiWidget` | `date-input` |
| `TnaProgressiveDateField` | custom `MultiWidget` | `date-input` |

These date fields follow the same high-level behaviour as the WTForms variants: full date, month/year, year only, and progressive partial date input.