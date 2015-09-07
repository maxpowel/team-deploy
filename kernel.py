import importlib
import os


def init():
    # Automatic load
    bundle_list = [bundle for bundle in os.listdir('bundles')
                   if os.path.isdir('bundles/%s' % bundle) and not bundle.startswith("_")]

    load_files = []
    init_bundle_functions = []
    # Load bundles
    for bundle in bundle_list:
        if os.path.isfile('bundles/%s/%s.py' % (bundle, bundle)):
            mod = importlib.import_module("bundles.%s.%s" % (bundle, bundle))
            init_bundle_functions.append(mod.init)
            options = mod.options
            if "load_files" in options:
                load_files.append(options['load_files'])

    # Load bundle files
    for bundle in bundle_list:
        for file_type in load_files:
            if os.path.isfile('bundles/%s/%s.py' % (bundle, file_type)):
                importlib.import_module("bundles.%s.%s" % (bundle, file_type))

    # Init bundles
    for init_function in init_bundle_functions:
        init_function()