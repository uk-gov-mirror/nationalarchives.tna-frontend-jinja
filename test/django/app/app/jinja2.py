from pathlib import Path

from django.templatetags.static import static
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, select_autoescape

from tna_frontend_jinja.django import DjangoFormsHelpers


def environment(**options):
    options.setdefault("autoescape", select_autoescape(["html"]))
    env = Environment(**options)
    templates_dir = Path(__file__).resolve().parent.parent / "templates"
    env.loader = ChoiceLoader(
        [
            FileSystemLoader(str(templates_dir)),
            PackageLoader("tna_frontend_jinja"),
        ]
    )
    env.globals.update({"static": static})
    DjangoFormsHelpers(env)
    return env