#!/usr/bin/env python
import itertools
import logging
import os
import sys
from optparse import OptionParser

import yaml

import nanotify

from batchbuilderror import BatchBuildError
from cascadedconfig import CascadedConfig
from module import Module
from runner import Runner

USAGE = "%prog <project.yaml|module> [module1 [module2...]]"

BBCONFIG_DIR = os.path.expanduser("~/.config/devo/bb")


def list_all_modules():
    """
    Returns a dict project => [module_name1, module_name2,...]
    """
    dct = {}
    for name in os.listdir(BBCONFIG_DIR):
        if not name.endswith(".yaml"):
            continue
        full_name = os.path.join(BBCONFIG_DIR, name)
        config = yaml.load(open(full_name))
        dct[name] = [x["name"] for x in config["modules"]]
    return dct


def load_all_config_dicts():
    """
    Returns a list of all config dicts
    """
    lst = []
    for name in os.listdir(BBCONFIG_DIR):
        if not name.endswith(".yaml"):
            continue
        full_name = os.path.join(BBCONFIG_DIR, name)
        lst.append(yaml.load(open(full_name)))
    return lst


def find_config(name):
    """
    Returns full path of config named name, or None
    """
    full_name = os.path.join(BBCONFIG_DIR, name)
    for x in name, full_name, full_name + ".yaml":
        if os.path.exists(x):
            return x
    return None


def find_config_containing(name):
    """
    Returns full path of first config containing a module named name, or None
    """
    dct = list_all_modules()
    for key, lst in dct.items():
        if name in lst:
            return os.path.join(BBCONFIG_DIR, key)
    return None


def print_all_project_modules():
    dct = list_all_modules()
    for name in sorted(dct.keys()):
        print name
        print_project_modules(dct[name])


def print_project_modules(lst):
    for name in lst:
        print "- %s" % name


def select_modules_from_config(name):
    config_file_name = find_config(name)
    if config_file_name is None:
        logging.error("Could not find '%s' config file" % name)
        return None
    config = yaml.load(open(config_file_name))
    global_dict = config["global"]
    module_dicts = config["modules"]
    return [CascadedConfig(x, global_dict) for x in module_dicts]


def select_modules_from_list(module_names):
    def find_module(lst, name):
        for dct in lst:
            if dct["name"] == name:
                return dct
        return None

    config_dicts = load_all_config_dicts()

    module_configs = []
    for module_name in module_names:
        found = False
        for config_dict in config_dicts:
            module_dict_list = config_dict["modules"]

            dct = find_module(module_dict_list, module_name)
            if dct is not None:
                config = CascadedConfig(dct, config_dict["global"])
                module_configs.append(config)
                found = True
                break
        if not found:
            logging.error("Unknown module %s" % module_name)
            return None
    return module_configs


def apply_resume_from(lst, resume_from):
    lst = list(itertools.dropwhile(lambda x: x.flat_get("name") != resume_from, lst))
    if len(lst) == 0:
        logging.error("Unknown module %s" % resume_from)
        return None
    return lst


def do_build(module_configs, log_dir, options):
    fails = []
    for config in module_configs:
        name = config.flat_get("name")
        assert name
        logging.info("### %s" % name)
        log_file_name = os.path.join(log_dir, name + ".log")
        log_file = open(log_file_name, "w")
        runner = Runner(log_file, options.verbose)
        module = Module(config, runner)
        try:
            if not options.no_src:
                if module.has_checkout():
                    module.update()
                else:
                    module.checkout()
            if not options.src_only:
                if options.refresh_build:
                    module.refresh_build()
                module.configure()
                module.build()
                module.install()
                nanotify.notify(name, "Build successfully", icon="dialog-ok")
        except BatchBuildError, exc:
            logging.error("%s failed to build: %s", name, exc)
            logging.error("See %s", log_file_name)
            fails.append([name, str(exc), log_file_name])
            nanotify.notify(name, "Failed to build", icon="dialog-error")
    return fails


def main():
    parser = OptionParser(usage=USAGE)

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Print command output to stdout")

    parser.add_option("--dry-run",
                      action="store_true", dest="dry_run", default=False,
                      help="Just list what would be build")

    parser.add_option("--no-src",
                      action="store_true", dest="no_src", default=False,
                      help="Do not update source code")

    parser.add_option("--src-only",
                      action="store_true", dest="src_only", default=False,
                      help="Only update source code")

    parser.add_option("--resume-from", dest="resume_from", default=None,
                      metavar="MODULE",
                      help="Resume build from MODULE")

    parser.add_option("--refresh-build",
                      action="store_true", dest="refresh_build", default=False,
                      help="Delete build dir")

    parser.add_option("-l", "--list",
                      action="store_true", dest="list", default=False,
                      help="List available modules")

    (options, args) = parser.parse_args()
    logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%H:%M:%S", level=logging.DEBUG)

    if options.list:
        if len(args) > 0:
            dct = list_all_modules()
            name = args[0]
            lst = dct.get(name, None)
            if lst is None:
                logging.error("No module named %s" % name)
                return 1
            print_project_modules(lst)
        else:
            print_all_project_modules()
        return 0

    # Check devo name
    devo_name = os.environ.get("DEVO_NAME", None)
    if devo_name is None:
        logging.error("No devo set up")
        return 1
    logging.info("Using devo '%s'", devo_name)

    # Load config
    if len(args) == 0:
        parser.error("Missing args")

    if args[0].endswith(".yaml"):
        module_configs = select_modules_from_config(args[0])
    else:
        module_configs = select_modules_from_list(args)
    if module_configs is None:
        return 1

    if options.resume_from:
        module_configs = apply_resume_from(module_configs, options.resume_from)
    if module_configs is None:
        return 1

    # Setup logging
    log_dir = os.path.join(os.environ["DEVO_BUILD_BASE_DIR"], "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if options.dry_run:
        print "Would build:"
        for module_config in module_configs:
            print "- " + module_config.flat_get("name")
        return 0

    fails = do_build(module_configs, log_dir, options)

    if len(fails) > 0:
        logging.error("%d modules failed to build:", len(fails))
        for name, msg, log_file_name in fails:
            logging.error("- %s: %s", name, msg)
            logging.error("- %s: see %s", name, log_file_name)
    else:
        logging.info("All modules built successfully")

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
