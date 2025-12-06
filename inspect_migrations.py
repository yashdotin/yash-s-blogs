import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()
from django.db import connections
from django.db.migrations.loader import MigrationLoader

try:
    loader = MigrationLoader(connections['default'])
    print('Disk migrations found:')
    for key in sorted(loader.disk_migrations.keys()):
        print(key)
    print('\nMigrations graph keys:')
    for app_label in sorted(loader.graph.leaf_nodes()):
        print(app_label)
except Exception as e:
    print('Error while loading migrations:')
    print(repr(e))
    # try to partially inspect disk migrations by importing modules directly
    import pkgutil
    import importlib
    import pathlib
    base = pathlib.Path('.')
    print('\nAttempting to scan installed apps for migrations files...')
    from django.apps import apps
    for app in apps.get_app_configs():
        mod = app.module.__name__
        mig_pkg = mod + '.migrations'
        try:
            pkg = importlib.import_module(mig_pkg)
        except Exception:
            # no migrations package
            continue
        package_path = getattr(pkg, '__path__', None)
        if not package_path:
            continue
        for finder, name, ispkg in pkgutil.iter_modules(package_path):
            if name.endswith('.py') or not ispkg:
                print(f'{app.label}: migration module -> {name}')

print('\nDone')
