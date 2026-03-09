import os
import sys


MIN_PYTHON = (3, 11)
DJANGO_SERIES = (5, 2)


def validate_runtime() -> None:
    if os.getenv("SKIP_RUNTIME_VALIDATION") == "1":
        return

    if sys.version_info < MIN_PYTHON:
        current = ".".join(map(str, sys.version_info[:3]))
        required = ".".join(map(str, MIN_PYTHON))
        raise RuntimeError(
            f"This project requires Python {required}+ (current: {current})."
        )

    try:
        import django
    except ImportError:
        return

    if django.VERSION[:2] != DJANGO_SERIES:
        found = django.get_version()
        required = ".".join(map(str, DJANGO_SERIES))
        raise RuntimeError(
            f"This project requires Django {required}.x (current: {found})."
        )
