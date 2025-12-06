import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','project.settings')
import django
django.setup()
import pkgutil, importlib
from django.apps import apps

found = []
for app in apps.get_app_configs():
    mig_pkg_name = app.module.__name__ + '.migrations'
    try:
        mig_pkg = importlib.import_module(mig_pkg_name)
    except Exception:
        continue
    package_path = getattr(mig_pkg, '__path__', None)
    if not package_path:
        continue
    for finder, name, ispkg in pkgutil.iter_modules(package_path):
        mod_name = mig_pkg_name + '.' + name
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            # skip modules that fail to import
            continue
        # inspect module for Migration class
        for obj_name in dir(mod):
            obj = getattr(mod, obj_name)
            try:
                deps = getattr(obj, 'dependencies')
            except Exception:
                deps = None
            if deps:
                for dep in deps:
                    if isinstance(dep, (tuple, list)) and dep and dep[0] == 'accounts':
                        found.append((mod_name, obj_name, dep))

if not found:
    print('No migration dependencies referencing accounts found in scanned migration modules.')
else:
    print('Found references:')
    for item in found:
        print(item)
