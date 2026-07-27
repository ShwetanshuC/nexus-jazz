#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def main():
    _env = Path(__file__).parent / ".env"
    if _env.exists():
        from dotenv import load_dotenv
        load_dotenv(_env)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_jazz.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
