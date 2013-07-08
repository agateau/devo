#!/usr/bin/env python
import itertools
import logging
import os
import sys
from optparse import OptionParser

import yaml

import flog
import nanotify

from batchbuilderror import BatchBuildError
from cascadedconfig import CascadedConfig
from module import Module
from runner import Runner

USAGE = "%prog <project.yaml|module> [module1 [module2...]]"

BBCONFIG_DIR = os.path.expanduser("~/.config/devo/bb")
BASE_CONFIG_NAME = "_base.yaml"


def load_base_config_dict():
    """
    Load content of BASE_CONFIG_NAME
    """
    full_name = os.path.join(BBCONFIG_DIR, BASE_CONFIG_NAME)
    if not os.path.exists(full_name):
        return {}
    return yaml.load(open(full_name))


def list_yaml_files():
    """
    List all yaml files in BBCONFIG_DIR, except the base config file
    """
    for name in os.listdir(BBCONFIG_DIR):
        if not name.endswith(".yaml"):
            continue
        if name == BASE_CONFIG_NAME:
            continue
        yield name


def load_all_config_dicts():
    """
    Returns a list of all config dicts
    """
    lst = []
    for name in list_yaml_files():
        full_name = os.path.join(BBCONFIG_DIR, name)
        lst.append(yaml.load(open(full_name)))
    return lst


def load_config_dict_by_name(name):
    """
    Returns config dict for config named name, or None
    """
    full_name = os.path.join(BBCONFIG_DIR, name)
    for x in name, full_name:
        if os.path.exists(x):
            return yaml.load(open(x))
    return None


def print_all_project_modules():
    for name in sorted(list_yaml_files()):
        full_name = os.path.join(BBCONFIG_DIR, name)
        config = yaml.load(open(full_name))
        flog.h1(name)
        print_project_modules(config)


def print_project_modules(config):
    for dct in config["modules"]:
        flog.li(dct["name"])


def select_modules_from_config(name, base_dict):
    config = load_config_dict_by_name(name)
    if not config:
        flog.error("Could not find '%s' config file" % name)
        return None
    global_dict = config["global"]
    module_dicts = config["modules"]
    return [CascadedConfig(x, global_dict, base_dict) for x in module_dicts]


def select_modules_from_list(module_names, base_dict):
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
                config = CascadedConfig(dct, config_dict["global"], base_dict)
                module_configs.append(config)
                found = True
                break
        if not found:
            flog.error("Unknown module %s" % module_name)
            return None
    return module_configs


def apply_resume_from(lst, resume_from):
    lst = list(itertools.dropwhile(lambda x: x.flat_get("name") != resume_from, lst))
    if len(lst) == 0:
        flog.error("Unknown module %s" % resume_from)
        return None
    return lst


class BuildResult(object):
    def __init__(self):
        self.vcs_fails = []
        self.build_fails = []


def do_build(module_configs, log_dir, options):
    result = BuildResult()
    for config in module_configs:
        name = config.flat_get("name")
        assert name
        flog.h1(name)
        log_file_name = os.path.join(log_dir, name + ".log")
        log_file = open(log_file_name, "w")
        runner = Runner(log_file, options.verbose)
        module = Module(config, runner)

        # update/checkout
        if not options.no_src:
            try:
                if module.has_checkout():
                    module.update()
                else:
                    module.checkout()
            except BatchBuildError, exc:
                flog.error("%s failed to update/checkout: %s", name, exc)
                flog.p("See %s", log_file_name)
                result.vcs_fails.append([name, str(exc), log_file_name])
                nanotify.notify(name, "Failed to update/checkout", icon="dialog-warning")
                if options.fatal:
                    return result

        # Build
        try:
            if not options.src_only:
                if options.refresh_build:
                    module.refresh_build()
                module.configure()
                module.build()
                module.install()
                nanotify.notify(name, "Build successfully", icon="dialog-ok")
        except BatchBuildError, exc:
            flog.error("%s failed to build: %s", name, exc)
            flog.p("See %s", log_file_name)
            result.build_fails.append([name, str(exc), log_file_name])
            nanotify.notify(name, "Failed to build", icon="dialog-error")
            if options.fatal:
                return result
    return result


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

    parser.add_option("--fatal",
                      action="store_true", dest="fatal", default=False,
                      help="Stop on first build failure")

    (options, args) = parser.parse_args()
    logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%H:%M:%S", level=logging.DEBUG)

    if options.list:
        if len(args) > 0:
            name = args[0]
            config = load_config_dict_by_name(name)
            if not config:
                flog.error("No config named %s" % name)
                return 1
            print_project_modules(config)
        else:
            print_all_project_modules()
        return 0

    # Check devo name
    devo_name = os.environ.get("DEVO_NAME", None)
    if devo_name is None:
        flog.error("No devo set up")
        return 1
    flog.p("Using devo '%s'", devo_name)

    # Load config
    if len(args) == 0:
        parser.error("Missing args")

    base_dict = load_base_config_dict()
    if args[0].endswith(".yaml"):
        module_configs = select_modules_from_config(args[0], base_dict)
    else:
        module_configs = select_modules_from_list(args, base_dict)
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
        flog.p("Would build:")
        for module_config in module_configs:
            flog.li(module_config.flat_get("name"))
        return 0

    result = do_build(module_configs, log_dir, options)

    flog.h1("Summary")
    if result.vcs_fails:
        fails = result.vcs_fails
        flog.error("%d modules failed to update/checkout:", len(fails))
        for name, msg, log_file_name in fails:
            flog.li("%s: %s", name, msg)
            flog.li("%s: see %s", name, log_file_name)

    if result.build_fails:
        fails = result.build_fails
        flog.error("%d modules failed to build:", len(fails))
        for name, msg, log_file_name in fails:
            flog.li("%s: %s", name, msg)
            flog.li("%s: see %s", name, log_file_name)

    if not result.vcs_fails and not result.build_fails:
        flog.p("All modules updated and built successfully")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
# vi: ts=4 sw=4 et
