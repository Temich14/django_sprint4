from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

class AboutPage(TemplateView):
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found_view(request: HttpRequest, exception=None) -> HttpResponse:
    return render(request, 'pages/404.html', status=404)


def internal_server_error_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/500.html', status=500)


def csrf_failure_view(request: HttpRequest, reason: str = '') -> HttpResponse:
    return render(request, 'pages/403csrf.html', status=403)
