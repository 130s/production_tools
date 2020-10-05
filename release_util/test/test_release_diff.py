#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import CalledProcessError
import os
import unittest

from release_util.release_diff import Diffs, ReleaseDiffVcs


class TestReleaseDiff(unittest.TestCase):
    search_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))

    def setUp(self):
        self.reldiff = ReleaseDiffVcs()

    def test_repos_diff(self):
        """
        @summary: Show that there's a diff for Realsense driver b/w 100.223.3 and 100.223.4.
        """
        path_repos_100_223_3 = os.path.abspath(os.path.join(search_path, "test_tags_100-223-3.repos"))
        path_repos_100_223_4 = os.path.abspath(os.path.join(search_path, "test_tags_100-223-4.repos"))

        # TODO See if there's a change b/w dev and release. May utilize the code from prepare_release
        diffs = self.reldiff.repos_diff(path_repos_100_223_3, path_repos_100_223_4)
        self.assertIsNone(diffs.changes_new)
        # Specific change made in 100-223-4. TBD the specifics of how to compare. Maybe commit message.
        self.assertIsEqual(diffs.changes_new.content, "xxxxx")

    def test_repos_diff_repo_removed(self):
        path_repos_100_223_3 = os.path.abspath(os.path.join(search_path, "test_tags_100-223-3.repos"))
        path_repos_foo = os.path.abspath(os.path.join(search_path, "test_foo.repos"))
        # Case where repo entry reduced
        diffs = repos_diff(path_repos_100_223_3, path_repos_foo)
        self.assertIsNone(diffs.changes_new)
        self.assertIsNotNone(diffs.changes_disappeared)
        # Case where a repo entry added
        diffs = repos_diff(path_repos_foo, path_repos_100_223_3)
        self.assertIsNotNone(diffs.changes_new)
        self.assertIsNone(diffs.changes_disappeared)
