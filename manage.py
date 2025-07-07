#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line

        #Call django.setup() first
        import django
        django.setup()

        #--- TEMP: Load db_backup.json if not already loaded ---
        import os
        from django.db import connection
        from django.core.management import call_command
        from django.apps import apps

        if os.path.exists("db_backup.json"):
            if apps.is_installed('django.contrib.auth'):
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM auth_user")
                    if cursor.fetchone()[0] == 0:
                        print("Loading data from db_backup.json...")
                        call_command('loaddata', 'db_backup.json')
                        print("Data loaded!")
                    else:
                        print("ℹData already exists. Skipping load.")
        # --- END TEMP ---

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
