#!/usr/bin/env python
"""Utilitaire en ligne de commande de Django pour la gestion administrative."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django n'a pas pu être importé. Vérifiez qu'il est installé "
            "(pip install -r requirements.txt) et que votre virtualenv est actif."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
