import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    from dotenv import load_dotenv
    load_dotenv(_env)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus_jazz.settings")

application = get_wsgi_application()
