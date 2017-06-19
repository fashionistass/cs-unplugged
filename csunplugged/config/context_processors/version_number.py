"""Context processor for displaying version number."""

from config import __version__


def version_number(request):
    """Return a string of the version number.

    Returns:
        Dictionary containing version number to add to context.
    """
    return {"VERSION_NUMBER": __version__}
