from django.templatetags.static import static
from jinja2 import Environment, PackageLoader, ChoiceLoader, select_autoescape

from tna_frontend_jinja.django import DjangoFormsHelpers


def environment(**options):
    options.setdefault("autoescape", select_autoescape(["html"]))
    env = Environment(**options)
    env.loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PackageLoader("tna_frontend_jinja"),
        ]
    )
    env.globals.update({"static": static})
    DjangoFormsHelpers(env)
    return env