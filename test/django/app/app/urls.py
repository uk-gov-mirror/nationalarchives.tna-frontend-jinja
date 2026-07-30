from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path

from .forms import ConditionalExampleForm, ExampleForm


def index(request):
    return render(
        request,
        "index.html",
        {
            "links": [
                {"href": "/forms/example/", "text": "Example form"},
                {"href": "/forms/conditional/", "text": "Conditional form"},
            ]
        },
    )


def example_form(request):
    form = ExampleForm(request.POST or None, request.FILES or None)
    success = request.method == "POST" and form.is_valid()
    return render(request, "forms/example.html", {"form": form, "success": success})


def conditional_form(request):
    form = ConditionalExampleForm(request.POST or None)
    success = request.method == "POST" and form.is_valid()
    return render(
        request,
        "forms/conditional.html",
        {"form": form, "success": success},
    )


def healthcheck(_request):
    return HttpResponse("ok")


urlpatterns = [
    path("", index),
    path("forms/example/", example_form),
    path("forms/conditional/", conditional_form),
    path("healthcheck/live/", healthcheck),
]