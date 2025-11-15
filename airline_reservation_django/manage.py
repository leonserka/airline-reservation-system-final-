#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "airline_project.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as e:
        raise ImportError(
            "Django could not be imported. Make sure it's installed and "
            "your environment is activated."
        ) from e

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
