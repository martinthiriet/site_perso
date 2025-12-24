#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# sudo apt install texlive-full
# conda create --name brainmap-env python=3.9
# pip install django
# pip install django-extensions
#  sudo apt-get install pdf2svg


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
