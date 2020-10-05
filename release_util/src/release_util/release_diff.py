from __future__ import print_function

import git
import logging
import os
import random
import shlex
import subprocess
import sys

from release_util.vcs_util import VcsUtil

class Diffs(object):
    def __init__(self, repos_name_old, repos_name_new):
        self._repos_name_old = repos_name_old
        self._repos_name_new = repos_name_new
        self._changes_new = None  # changes only found in new.
        self._changes_disappeared = None  # changes only found in old.

    @property
    def changes_new(self):
        return self._changes_new

    @property.setter
    def changes_new(self, changes_new):
        self._changes_new = changes_new

    @property
    def changes_disappeared(self):
        return self._changes_disappeared

    @property.setter
    def changes_disappeared(self, changes_disappeared):
        self._changes_disappeared = changes_disappeared


class ReleaseDiffVcs(object):
    _REPOS_TEMPPATH = "/cws/src/production_tools/release_util/test/pickone_release.repos"
    _TMP_WORKDIR_ROOT = "/tmp"
    _TMP_WORKDIR = "release_tools"
    EXTENSION_SUPPORTED_CLONER = [".repos"]

    def __init__(self, args):
        self.log = logging.getLogger(__name__)        
        self._vcs_util = VcsUtil()

    def repos_diff(self, path_repos_older, path_repos_newer):
        """
        @summary: Show the diff of repos b/w the 2 versions in older and newer.
        @param: path_repos_older
        @param: path_repos_newer
        """
        # List the repositoriess in old and new repos file.
        
        # Compare repos one by one.
        # Print the result.
        self._vcs_util
        for path_repos_newer
