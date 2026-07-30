# Django forms integration

TNA Frontend Jinja supports Django projects for template rendering and includes a starter Django forms integration layer.

This guide shows how to use the packaged helpers and field classes, along with the underlying pattern they follow.

The packaged Django integration requires Django 5.2 or later because it relies on the field rendering API used by `BoundField.as_field_group()`.

A minimal reference application is included in `test/django` to show the expected project shape.

## Status

- Jinja template support is built in.
- Starter Django fields and helpers are included in the package.
- The Django support is intentionally narrower than the WTForms support.

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

For Django forms, the most effective approach is to render complete TNA components from field templates using the `BoundField` context.

This is usually a better fit than overriding widget templates directly because TNA components often need access to:

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

## 5. Render fields with `as_field_group()`

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

## 6. Build custom field templates when you need them

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

## 7. Add a form-level error summary

The package includes a `django_field_errors()` helper for building error-summary items from a Django form.

```jinja
{%- from 'components/error-summary/macro.html' import tnaErrorSummary -%}

{% if form.errors %}
  {{ tnaErrorSummary(django_field_errors(form)) }}
{% endif %}
```

## 8. Handle conditional validation in the form class

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

## 9. Included package structure

The shipped Django support is organised like this:

```text
tna_frontend_jinja/
  django/
    __init__.py
    fields.py
    forms.py
    helpers.py
    widgets.py
  templates/
    django/
      forms/
        fields/
          checkbox.html
          checkboxes.html
          date-input.html
          file-input.html
          radios.html
          select.html
          text-input.html
          textarea.html
```

Responsibilities:

- `fields.py`: reusable field subclasses with `template_name` defaults
- `forms.py`: optional base form with shared conventions
- `helpers.py`: error-summary helpers and attribute mapping helpers
- `widgets.py`: date widget handling for multi-part date inputs
- `templates/`: Jinja field templates that call TNA macros

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

## 11. Example app

A minimal Django 5.2+ example application is included at `test/django`.

Useful entry points:

- `test/django/app/app/settings.py`
- `test/django/app/app/jinja2.py`
- `test/django/app/app/forms.py`
- `test/django/app/app/urls.py`
- `test/django/app/templates/forms/example.html`
- `test/django/app/templates/forms/conditional.html`

## 12. How It Works

The implementation runs as a short pipeline from Django form binding to TNA macro rendering.

### 12.1. Public API import

Applications import the packaged fields and helpers from `tna_frontend_jinja.django`.

That module re-exports the field classes, helper registration object, and optional form mixin so consumers do not need to import from internal package modules directly.

### 12.2. Jinja environment registration

When the Django Jinja environment is created, call `DjangoFormsHelpers(env)`.

This registers the helper functions used by the field templates, including:

- `django_text_input_params`
- `django_radios_params`
- `django_select_params`
- `django_checkbox_params`
- `django_checkboxes_params`
- `django_file_input_params`
- `django_date_input_params`
- `django_field_errors`

These functions are added as Jinja globals and are later called from the packaged field templates.

### 12.3. Form declaration

Application forms declare fields using classes such as `TnaCharField`, `TnaRadioField`, or `TnaDateField`.

Each of these field classes primarily does two things:

- sets a `template_name` that Django will use when rendering the bound field as a field group
- optionally stores `tna_params` so component options can be merged in later

For standard one-input fields, the field class is thin. For date fields, `TnaBaseDateField` also configures a custom `MultiWidget` and parses multipart input back into a Python `date`.

### 12.4. Request binding and validation

In a view, the application instantiates the Django form with `request.POST` and optionally `request.FILES`.

On `POST`, calling `form.is_valid()` triggers Django's validation flow:

1. raw request values are read from the widgets
2. each field converts raw input into Python values
3. `clean()` runs for cross-field validation
4. errors are collected on the form and its bound fields

For date fields, the raw values come through `TnaDateInputWidget.value_from_datadict()` and are then parsed in `TnaBaseDateField.to_python()`.

### 12.5. Field-group rendering

In the Jinja template, each field is rendered with `as_field_group()`.

That is the main handoff into Django's field rendering API. Django uses the field's `template_name` to choose the correct field template for that bound field.

For example:

- `TnaCharField` uses the packaged text-input field template
- `TnaRadioField` uses the packaged radios field template
- `TnaDateField` uses the packaged date-input field template

### 12.6. BoundField to TNA params mapping

Each packaged field template is very small. Its job is to:

1. import the matching TNA component macro
2. call a helper such as `django_text_input_params(field)`
3. pass the resulting params into the macro

The helper layer is where Django's `BoundField` shape is converted into the parameter structure that the existing TNA macros expect.

That conversion includes:

- field ids and names
- labels and hints
- first error message
- current selected or entered value
- mapped choice items for radios, selects, and checkboxes
- component overrides from `tna_params`

### 12.7. Final macro rendering

Once the params have been built, the existing TNA component macros render the final HTML.

That means the Django layer does not reimplement TNA components. It only adapts Django form state into the same parameter contract already used elsewhere in the package.

### 12.8. Error summary flow

Field-level errors and form-level error summaries are handled separately.

- field templates receive `params.error`, which lets the component render inline error text
- page templates call `tnaErrorSummary(django_field_errors(form))`, which builds the top-of-page summary from `form.visible_fields()` and `form.non_field_errors()`

This keeps business validation in Django and keeps rendering concerns in the helper and template layers.

### 12.9. Conditional validation flow

Conditional validation remains standard Django form logic.

In the example app, `ConditionalExampleForm.clean()` adds errors to the dependent field using `add_error()`. Once Django has done that, the same rendering pipeline picks those errors up automatically in both the inline field error and the summary block.

## 13. What to avoid

- Avoid relying on widget templates alone for full component rendering.
- Avoid mixing default Django field markup with TNA component markup in the same form.
- Avoid model forms until you know they fit your service's validation and flow requirements.
- Avoid assuming feature parity with the WTForms integration.

## 14. Summary

The core pattern is:

1. use Jinja templates in Django
2. enable `django.forms.renderers.TemplatesSetting`
3. register `DjangoFormsHelpers` in the Jinja environment
4. use the packaged TNA Django field classes or create your own field subclasses with custom `template_name` values
5. render fields with `as_field_group()` so Django uses the field templates
6. use `django_field_errors()` for the error summary

That gives Django projects a similar developer experience to WTForms support while staying aligned with Django's own rendering model.