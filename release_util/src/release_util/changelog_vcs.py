from __future__ import print_function

import logging
import os
import random
import shlex
import subprocess
import sys


class Changelog_Vcs():
    _REPOS_TEMPPATH = "/cws/src/production_tools/release_util/test/pickone_release.repos"

    def __init__(self, args):
        self.log = logging.getLogger(__name__)        

    def main(self, args=None, stdout=None, stderr=None):
        args = args if args is not None else sys.argv[1:]
        
        cwd = os.path.abspath(os.getcwd())
        self.log.info("Current working path: {}".format(cwd))
        
        # Clone repos with the specified version in .repos file. Clone into the specified path if any.
        tmp_outpath_root = "/tmp"
        outpath = os.path.join(tmp_outpath_root, str(random.randint(1, 10000)))
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        try:
            self._clone_repos_subprocess(self._REPOS_TEMPPATH, outpath)
        except subprocess.CalledProcessError as e:
            self.log.info(str(e))
            self.log.info("Move on assuming there might be repos already under the current path.")

        if len(os.walk('dir_name').next()[1]) < 1:
            self.log.error("No repos found under cwd.")
            return 1
        else:
            # Print repos under the current path
            for path, dirs, files in os.walk(cwd):
                self.log.info(path)
                for f in files:
                    self.log.info(f)

        # for each repo,
        #   Search for changelog files.
        #   for each changelog file:
        #     Get the changelog entry of the specified version.
        #   Return set of changelog entries.

    def _clone_repos_subprocess(self, repos_path="test/pickone_release.repos", outpath="/tmp/1357"):
        """Temporary method to use subprocess to clone repos"""
        os.chdir(outpath)
        command = "vcs import \< {}".format(repos_path)
        subprocess.check_output(shlex.split(command))

