from copy import deepcopy

from ._shared import date_input_part


def _merge_params(base_params, custom_params):
    merged = deepcopy(base_params)

    for key, value in custom_params.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            nested = merged[key].copy()
            nested.update(value)
            merged[key] = nested
        else:
            merged[key] = value

    return merged


def _normalise_attributes(attributes):
    normalised = {}

    for key, value in attributes.items():
        if value is False or value is None:
            continue
        normalised[key] = "" if value is True else value

    return normalised


def _choice_value(value):
    if value is None:
        return ""
    return str(value)


def _flatten_choices(choices):
    flattened = []

    for value, label in choices:
        if isinstance(label, (list, tuple)):
            flattened.extend(_flatten_choices(label))
        else:
            flattened.append((value, label))

    return flattened


def _field_id(field):
    return field.id_for_label or field.auto_id or field.html_name


def _field_error(field):
    if field.errors:
        return {"text": field.errors[0]}
    return None


def _field_attributes(field):
    attributes = deepcopy(field.field.widget.attrs)

    if field.field.required:
        attributes.setdefault("required", True)
    if field.field.disabled:
        attributes.setdefault("disabled", True)
    if field.errors:
        attributes.setdefault("aria-invalid", "true")

    return _normalise_attributes(attributes)


def _base_params(field):
    return {
        "id": _field_id(field),
        "name": field.html_name,
        "label": field.label,
        "hint": field.help_text or None,
        "error": _field_error(field),
        "attributes": _field_attributes(field),
    }


def _custom_params(field):
    return getattr(field.field, "tna_params", {})


def _merge_field_params(field, params):
    return _merge_params(params, _custom_params(field))


def _choice_items(choices):
    return [
        {
            "value": _choice_value(value),
            "text": label,
        }
        for value, label in _flatten_choices(choices)
    ]


def _single_value_choice_params(field):
    params = _base_params(field)
    params["items"] = _choice_items(field.field.choices)
    params["selected"] = _choice_value(field.value())
    return _merge_field_params(field, params)


def django_text_input_params(field):
    params = _base_params(field)
    params["value"] = field.value() or ""

    input_type = getattr(field.field.widget, "input_type", None)
    if input_type:
        params["type"] = input_type

    max_length = getattr(field.field, "max_length", None)
    if max_length:
        params["maxLength"] = max_length

    return _merge_field_params(field, params)


def django_textarea_params(field):
    params = _base_params(field)
    params["value"] = field.value() or ""

    rows = field.field.widget.attrs.get("rows")
    if rows:
        params["rows"] = rows

    return _merge_field_params(field, params)


def django_select_params(field):
    return _single_value_choice_params(field)


def django_radios_params(field):
    return _single_value_choice_params(field)


def django_checkboxes_params(field):
    params = _base_params(field)

    selected_values = field.value() or []
    if not isinstance(selected_values, (list, tuple, set)):
        selected_values = [selected_values]
    selected_values = {_choice_value(value) for value in selected_values}

    params["items"] = [
        {
            **item,
            "checked": item["value"] in selected_values,
        }
        for item in _choice_items(field.field.choices)
    ]

    return _merge_field_params(field, params)


def django_checkbox_params(field):
    params = _base_params(field)
    params["label"] = field.field.tna_params.get("label", "")

    checkbox_value = field.field.widget.attrs.get("value", "true")
    params["items"] = [
        {
            "value": checkbox_value,
            "text": getattr(field.field, "checkbox_label", None) or field.label,
            "checked": bool(field.value()),
        }
    ]

    return _merge_field_params(field, params)


def django_file_input_params(field):
    params = _base_params(field)
    params["multiple"] = bool(
        getattr(field.field.widget, "allow_multiple_selected", False)
        or field.field.widget.attrs.get("multiple")
    )

    return _merge_field_params(field, params)


def django_date_input_params(field):
    params = _base_params(field)
    widget = field.field.widget

    if field.form.is_bound:
        raw_values = widget.value_from_datadict(
            field.form.data,
            field.form.files,
            field.html_name,
        )
    else:
        raw_values = widget.decompress(field.value())

    values = {}
    for code, value in zip(field.field.field_codes, raw_values):
        if value:
            values[date_input_part(code)] = value

    params["value"] = values
    params["fields"] = list(field.field.field_codes)
    params["progressive"] = field.field.progressive

    return _merge_field_params(field, params)


def django_field_errors(form, params=None):
    summary_params = {
        "title": "There is a problem",
        "items": [],
    }

    for bound_field in form.visible_fields():
        if bound_field.errors:
            summary_params["items"].append(
                {
                    "text": bound_field.errors[0],
                    "href": f"#{_field_id(bound_field)}",
                }
            )

    for error in form.non_field_errors():
        summary_params["items"].append(
            {
                "text": error,
                "href": None,
            }
        )

    if params:
        return _merge_params(summary_params, params)

    return summary_params


class DjangoFormsHelpers:
    def __init__(self, env=None):
        self.env = env
        if env is not None:
            self.init_environment(env)

    def init_environment(self, env):
        self.env = env
        self.env.globals.update(
            {
                "django_checkbox_params": django_checkbox_params,
                "django_checkboxes_params": django_checkboxes_params,
                "django_date_input_params": django_date_input_params,
                "django_field_errors": django_field_errors,
                "django_file_input_params": django_file_input_params,
                "django_radios_params": django_radios_params,
                "django_select_params": django_select_params,
                "django_text_input_params": django_text_input_params,
                "django_textarea_params": django_textarea_params,
            }
        )
        return self.env