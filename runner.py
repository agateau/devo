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

    def run(self, cwd, command):
        self._info_log("Running command '%s' in dir '%s'" % (command, cwd))
        process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
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
