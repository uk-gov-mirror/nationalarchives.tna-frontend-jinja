DATE_INPUT_PARTS = {
    "d": "day",
    "m": "month",
    "y": "year",
}


def date_input_part(code):
    return DATE_INPUT_PARTS[code]


def trim_progressive_values(values, progressive):
    if progressive and "" in values:
        return values[: values.index("")]
    return values