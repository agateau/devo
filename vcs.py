class Svn(object):
    def __init__(self, module):
        self.module = module

    def checkout(self):
        url = self.module.url
        if url[-1] != "/":
            url += "/"
        cmd = "svn checkout %s %s" % (url + self.module.branch, self.module.name)
        self.module.runner.run(self.module.base_dir, cmd)

    def update(self):
        self.module.runner.run(self.module.src_dir, "svn up")


class Git(object):
    def __init__(self, module):
        self.module = module

    def checkout(self):
        cmd = "git clone %s %s" % (self.module.url, self.module.name)
        self.module.runner.run(self.module.base_dir, cmd)

    def update(self):
        self.module.runner.run(self.module.src_dir, "git pull")


class KdeGit(Git):
    def checkout(self):
        cmd = "git clone kde:%s %s" % (self.module.name, self.module.name)
        self.module.runner.run(self.module.base_dir, cmd)


class Bzr(object):
    def __init__(self, module):
        self.module = module

    def checkout(self):
        cmd = "bzr branch %s %s" % (self.module.url, self.module.name)
        self.module.runner.run(self.module.src_dir, cmd)

    def update(self):
        self.module.runner.run(self.module.src_dir, "bzr up")
