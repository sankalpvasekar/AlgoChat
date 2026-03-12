import os
import django
from django.conf import settings
from django.urls import get_resolver

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def list_urls(lis, acc=None):
    if acc is None:
        acc = []
    if not lis:
        return
    for entry in lis:
        if hasattr(entry, 'url_patterns'):
            list_urls(entry.url_patterns, acc)
        else:
            acc.append(str(entry.pattern))
    return acc

resolver = get_resolver()
all_urls = list_urls(resolver.url_patterns)
print("\n--- Registered URL Patterns ---")
for url in sorted(all_urls):
    print(f" - {url}")
