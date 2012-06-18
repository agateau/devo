import os
import logging
import subprocess

from batchbuilderror import BatchBuildError

class Runner(object):
    def __init__(self, log_file, verbose):
        self.log_file = log_file
        self.verbose = verbose

    def _info_log(self, msg):
        logging.info(msg)
        print >>self.log_file, "devo-batchbuild: " + msg

    def cd(self, name):
        self._info_log("Entering dir '%s'" % name)
        os.chdir(name)

    def run(self, command):
        self._info_log("Running command '%s'" % command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        while True:
            out = process.stdout.readline()
            self.log_file.write(out)
            self.log_file.flush()
            if self.verbose:
                print self.log_file
            process.poll()
            ret = process.returncode
            if ret is not None:
                if ret != 0:
                    raise BatchBuildError("Command '%s' failed with exit code %d" % (command, ret))
                else:
                    return
