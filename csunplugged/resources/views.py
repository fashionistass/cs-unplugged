"""Views for the resource application."""

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views import generic
from resources.models import Resource
from resources.utils.resource_pdf_cache import resource_pdf_cache
from resources.utils.get_options_html import get_options_html
from utils.group_lessons_by_age import group_lessons_by_age
from resources.utils.get_resource_generator import get_resource_generator
from utils.errors.QueryParameterMissingError import QueryParameterMissingError
from utils.errors.QueryParameterInvalidError import QueryParameterInvalidError
from utils.errors.QueryParameterMultipleValuesError import QueryParameterMultipleValuesError

RESPONSE_CONTENT_DISPOSITION = 'attachment; filename="{filename}.pdf"'


class IndexView(generic.ListView):
    """View for the resource application homepage."""

    template_name = "resources/index.html"
    context_object_name = "all_resources"

    def get_queryset(self):
        """Get queryset of all resources.

        Returns:
            Queryset of all resources ordered by name.
        """
        return Resource.objects.order_by("name")


def resource(request, resource_slug):
    """View for a specific resource in the resources application.

    Args:
        request: HttpRequest object.
        resource_slug: The slug of the requested resource.

    Returns:
        HTML response of webpage, 404 if not found.
    """
    resource = get_object_or_404(Resource, slug=resource_slug)
    context = dict()
    generator = get_resource_generator(resource.generator_module)
    context["options_html"] = get_options_html(generator.get_options(), generator.get_local_options(), request.GET)
    context["resource"] = resource
    context["debug"] = settings.DEBUG
    context["resource_thumbnail_base"] = "{}img/resources/{}/thumbnails/".format(settings.STATIC_URL, resource.slug)
    context["grouped_lessons"] = group_lessons_by_age(resource.lessons.all())
    context["copies_amount"] = settings.RESOURCE_COPY_AMOUNT
    if resource.thumbnail_static_path:
        context["thumbnail"] = resource.thumbnail_static_path
    return render(request, "resources/resource.html", context)


def generate_resource(request, resource_slug):
    """View for generated PDF of a specific resource.

    Args:
        request: HttpRequest object.
        resource_slug: The slug of the requested resource.

    Returns:
        HTML response containing PDF of resource, 404 if not found.
    """
    resource = get_object_or_404(Resource, slug=resource_slug)
    if not request.GET:
        raise Http404("No parameters given for resource generation.")
    try:
        generator = get_resource_generator(resource.generator_module, request.GET)
    except (QueryParameterMissingError,
            QueryParameterInvalidError,
            QueryParameterMultipleValuesError) as e:
        raise Http404(e) from e

    # TODO: Weasyprint handling in production
    # TODO: Add creation of PDF as job to job queue
    if settings.DJANGO_PRODUCTION:
        # Return cached static PDF file of resource.
        # Currently developing system for dynamically rendering
        # custom PDFs on request (https://github.com/uccser/render).
        return resource_pdf_cache(resource.name, generator)
    else:
        (pdf_file, filename) = generator.pdf(resource.name)
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = RESPONSE_CONTENT_DISPOSITION.format(filename=filename)
        return response
