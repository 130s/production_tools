#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import CalledProcessError
import os
import pytest

from release_util.changelog_vcs import Changelog_Vcs


class TestChangelog():
    search_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))

    @pytest.fixture
    def clog_vcs(self):
        return Changelog_Vcs()

    @pytest.fixture
    def path_repos_100_223_3(self, search_path):
        return os.path.abspath(os.path.join(search_path, "test_tags_100-223-3.repos"))

    @pytest.fixture
    def path_repos_100_223_4(self, search_path):
        return os.path.abspath(os.path.join(search_path, "test_tags_100-223-4.repos"))

    def test_is_downmost_repo_present(self, clog_vcs, path_repos_100_223_3):
        """
        @summary: TBD
        """
        REPO_DOWNMOST = "rosbridge_suite"
        assert clog_vcs.is_downmost_repo_present(
            REPO_DOWNMOST, path_repos_100_223_3)
