import os

class Module(object):
    def __init__(self, global_config, config, runner):
        self.name = config["name"]
        self.runner = runner

        self.global_config = global_config
        self.config = config

        self.base_dir = os.path.expanduser(global_config["base-dir"])
        self.src_dir = os.path.join(self.base_dir, self.name)
        self.build_dir = os.path.join(os.environ["DEVO_BUILD_BASE_DIR"], self.name)

    def has_checkout(self):
        return os.path.exists(self.src_dir)

    def checkout(self):
        repo_type = self.config["repo-type"]
        if repo_type != "kdegit":
            url = self.config["repo-url"]

        if repo_type == "svn":
            cmd = "svn checkout %s %s" % (url, self.name)
        elif repo_type == "git":
            cmd = "git clone %s %s" % (url, self.name)
        elif repo_type == "kdegit":
            cmd = "git clone kde:%s %s" % (self.name, self.name)
        elif repo_type == "bzr":
            cmd = "bzr branch %s %s" % (url, self.name)
        self.runner.run(self.base_dir, cmd)

    def update(self):
        repo_type = self.config["repo-type"]

        if repo_type == "svn":
            cmd = "svn update"
        elif repo_type in ("git", "kdegit"):
            cmd = "git pull"
        elif repo_type == "bzr":
            cmd = "bzr pull"
        self.runner.run(self.src_dir, cmd)

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
