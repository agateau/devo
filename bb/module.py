import logging
import os
import shutil

import vcs

class Module(object):
    def __init__(self, config, runner):
        self.config = config
        self.runner = runner
        self.name = self.config.flat_get("name")
        assert self.name is not None

        self.base_dir = os.environ["DEVO_SOURCE_BASE_DIR"]
        self.src_dir = os.path.join(self.base_dir, self.name)
        self.build_dir = os.path.join(os.environ["DEVO_BUILD_BASE_DIR"], self.name)

        # Init repository stuff
        repo_type = self.config.get("repo-type")
        assert repo_type is not None

        self.branch = self.config.get("branch", "")

        self.url = self.config.get("repo-url", "")
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
        configure = self.config.get("configure", "devo-cmake " + self.src_dir)
        configure_opts = self.config.get("configure-options", "")
        self.runner.run(self.build_dir, configure + " " + configure_opts)

    def build(self):
        if not os.path.exists(self.build_dir):
            self.configure()
        build = self.config.get("build", "make")
        build_opts = self.config.get("build-options", "")
        self.runner.run(self.build_dir, build + " " + build_opts)

    def install(self):
        install = self.config.get("install", "make install")
        install_opts = self.config.get("install-options", "")
        self.runner.run(self.build_dir, install + " " + install_opts)
