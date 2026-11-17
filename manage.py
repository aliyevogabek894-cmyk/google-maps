#!/usr/bin/env python
"""Turon Odob-Ilm Raqamli Maktab Platformasi — Django boshqaruv utilitasi."""
import os
import sys


def main():
    """Buyruq qatori vazifalarini ishga tushiradi."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django kutubxonasi topilmadi. Virtual muhit faollashtirilganini va "
            "requirements.txt o'rnatilganini tekshiring."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
