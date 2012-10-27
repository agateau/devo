import logging
import os
import shutil

import vcs

class Module(object):
    def __init__(self, global_config, config, runner):
        self.name = config["name"]
        self.runner = runner

        self.global_config = global_config
        self.config = config

        self.base_dir = os.path.expanduser(global_config["base-dir"])
        self.src_dir = os.path.join(self.base_dir, self.name)
        self.build_dir = os.path.join(os.environ["DEVO_BUILD_BASE_DIR"], self.name)

        # Init repository stuff
        repo_type = self._get_opt("repo-type", "")
        assert repo_type != ""

        self.branch = self._get_opt("branch", "")

        self.url = self._get_opt("repo-url", "")
        if repo_type == "svn":
            self.vcs = vcs.Svn(self)
        elif repo_type == "git":
            self.vcs = vcs.Git(self)
        elif repo_type == "kdegit":
            self.vcs = vcs.KdeGit(self)
        elif repo_type == "bzr":
            self.vcs = vcs.Bzr(self)
        elif repo_type == "hg":
            self.vcs = vcs.Hg(self)
        else:
            raise Exception("Unknown repo-type: %s" % repo_type)

    def has_checkout(self):
        return os.path.exists(self.src_dir)

    def checkout(self):
        self.vcs.checkout()

    def update(self):
        self.vcs.update()

    def refresh_build(self):
        if os.path.exists(self.build_dir):
            logging.info("Removing dir '%s'" % self.build_dir)
            shutil.rmtree(self.build_dir)

    def configure(self):
        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)
        configure = self._get_opt("configure", "devo-cmake " + self.src_dir)
        configure_opts = self._get_opt("configure-options", "")
        self.runner.run(self.build_dir, configure + " " + configure_opts)

    def build(self):
        if not os.path.exists(self.build_dir):
            self.configure()
        build = self._get_opt("build", "make")
        build_opts = self._get_opt("build-options", "")
        self.runner.run(self.build_dir, build + " " + build_opts)

    def install(self):
        install = self._get_opt("install", "make")
        install_opts = self._get_opt("install-options", "install")
        self.runner.run(self.build_dir, install + " " + install_opts)

    def _get_opt(self, key, default_value):
        return self.config.get(key, self.global_config.get(key, default_value))
