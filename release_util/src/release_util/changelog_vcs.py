from __future__ import print_function

import argparse
import git
import logging
import os
import random
import shlex
import subprocess
import sys


class Changelog_Vcs():
    _REPOS_TEMPPATH = "/cws/src/production_tools/release_util/test/pickone_release.repos"
    _TMP_WORKDIR_ROOT = "/tmp"
    _TMP_WORKDIR = "release_tools"
    EXTENSION_SUPPORTED_CLONER = [".repos"]

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def collect_repos(self, path_repos=None):
        """
        @param path_repos: str, absolute path of .repos file (TODO link to desc of ".repos")
        @return: TBD. List of changelog objects that catkin_generate_changelog can process the rest.
        @summary: 
        """
        pass

    def clone_repos_vcstool(self, repos_path="test/pickone_release.repos", outpath=""):
        """
        @summary Temporary method to use subprocess to clone repos
        @param outpath: Path on the file system to be used for the temporary file operation.
                        If empty the current path where the program is is going to be used.
        @return Num of repos cloned
        @deprecated: Use "vcs import" instead. Merely a duplicate of that.
        """
        if outpath:
            os.chdir(outpath)
            self.log.debug("Temporarily cloning repos at: {}".format(outpath))
        else:
            self.log.debug("Temporary path not passed. Work to be done at the current path: {}".format(os.path.abspath(os.path.curdir)))
        # TODO iteratively clone
        command = "vcs import \< {}".format(repos_path)
        subprocess.check_output(shlex.split(command))
        # TODO Count num of repos cloned.

    def _parse_args_catkin_changelog_gen(self, parser):
        """
        @param parser: argparse.ArgumentParser object.
        @summary: Same options that catkin_generate_changelog takes in. TODO Better delegate to the upstream
        """
        parser.add_argument(
            '-a', '--all', action='store_true', default=False,
            help='Generate changelog for all versions instead of only the forthcoming one (only supported when no changelog file exists yet)')
        parser.add_argument(
            '--only-merges', action='store_true', default=False,
            help='Skip all commits but merge commits to the changelog')
        parser.add_argument(
            '--print-root', action='store_true', default=False,
            help='Output changelog content to the console as if there would be only one package in the root of the repository')
        parser.add_argument(
            '--skip-contributors', action='store_true', default=False,
            help='Skip adding the list of contributors to the changelog')
        parser.add_argument(
            '--skip-merges', action='store_true', default=False,
            help='Skip adding merge commits to the changelog')
        parser.add_argument(
            '-y', '--non-interactive', action='store_true', default=False,
            help="Run without user interaction, confirming all questions with 'yes'")
        return parser

    def is_downmost_repo_present(self, name_downmost_repo, repos_path=None):
        """
        @summary: If repo-downmost is present locally in the current directory, move on.
                  If not, search in the .repos file and move on if it's found. If not found, warns and terminate.
        @param repos_path Path to a repos file. If None, search repos under the current dir.
        @rtype: bool
        """
        # Get a local repo's name. Ref. https://stackoverflow.com/a/60910561/577001
        remote_url = repo.remotes[0].config_reader.get("url")
        # W/o encode, string "u'production_tools'" (w/o double quote).
        reponame_local = os.path.splitext(os.path.basename(remote_url))[0].encode("utf-8")

        if reponame_local == name_downmost_repo:
            return True
        return False

    def get_a_changelog(self, repo_path):
        """
        @summary Generate a list of changelog for a repo given by a path.
        @deprecated: This method is temporary. Code is basically copied from
            caking_pkg.cli.tag_changelog.main. This should be ported in upstream to avoid
            unneccessary duplicated maintenance.
        @param repo_path: Path to a local repo
        """
        base_path = '.'  # TODO

        # find packages
        packages = find_packages(base_path)
        if not packages:
            raise RuntimeError('No packages found')
        print('Found packages: %s' % ', '.join([p.name for p in packages.values()]))

        # fetch current version and verify that all packages have same version number
        old_version = verify_equal_package_versions(packages.values())
        new_version = bump_version(old_version, args.bump)
        print('Tag version %s' % new_version)

        # check for changelog entries
        changelogs = []
        missing_forthcoming = []
        already_tagged = []
        for pkg_path, package in packages.items():
            changelog_path = os.path.join(base_path, pkg_path, CHANGELOG_FILENAME)
            if not os.path.exists(changelog_path):
                missing_forthcoming.append(package.name)
                continue
            changelog = get_changelog_from_path(changelog_path, package.name)
            if not changelog:
                missing_forthcoming.append(package.name)
                continue
            # check that forthcoming section exists
            forthcoming_label = get_forthcoming_label(changelog.rst)
            if not forthcoming_label:
                missing_forthcoming.append(package.name)
                continue
            # check that new_version section does not exist yet
            try:
                changelog.get_content_of_version(new_version)
                already_tagged.append(package.name)
                continue
            except KeyError:
                pass
            changelogs.append((package.name, changelog_path, changelog, forthcoming_label))
        if missing_forthcoming:
            print('The following packages do not have a forthcoming section in their changelog file: %s' % ', '.join(sorted(missing_forthcoming)), file=sys.stderr)
        if already_tagged:
            print("The following packages do already have a section '%s' in their changelog file: %s" % (new_version, ', '.join(sorted(already_tagged))), file=sys.stderr)

        # rename forthcoming sections to new_version including current date
        new_changelog_data = []
        new_label = '%s (%s)' % (new_version, datetime.date.today().isoformat())
        for (pkg_name, changelog_path, changelog, forthcoming_label) in changelogs:
            print("Renaming section '%s' to '%s' in package '%s'..." % (forthcoming_label, new_label, pkg_name))
            data = rename_section(changelog.rst, forthcoming_label, new_label)
            new_changelog_data.append((changelog_path, data))

        print('Writing updated changelog files...')
        for (changelog_path, data) in new_changelog_data:
            with open(changelog_path, 'wb') as f:
                f.write(data.encode('utf-8'))

    def get_changelog_upstream(self, repos_path="test/pickone_release.repos", dir_tmpwork=""):
        """
        @summary: Generate changelog for the upstream repo(s), then fetch them
                  (TBD determine either via Python object or file).

                  Open question: ATM, this method only handles forthcoming changes
                                 (while catkin_pkg.changelog_generator can handle previously released
                                 versions in addition).

                  Temporary interemediate process generates directory and files as:

                      /tmp/changelog_upstream
                      |- repo_a
                          |- pkg_k
                              |- CHANGELOG updated (*1) 
                          |- pkg_l
                              |- CHANGELOG updated
                      |- repo_b
                          |- pkg_m
                              |- CHANGELOG updated
                          |- pkg_n
                              |- CHANGELOG updated

                  (*1) "Updated" means the changelog for the forthcoming release is generated.
        @param dir_tmpwork: Temporary work directory. By default a randomized folder name under /tmp will be used.
        @return: TBD
        """
        # Clone upstream repos in a temp work dir.
        os.chdir(dir_tmpwork)
        tmp_outpath_root = os.path.join(self._TMP_WORKDIR_root, self._TMP_WORKDIR)

        cwd = os.path.abspath(os.getcwd())
        self.log.info("Current working path: {}".format(cwd))

        # Randomize the output folder path to avoid colliding.
        outpath = os.path.join(tmp_outpath_root, str(random.randint(1, 10000)))
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        self.log.info("Temporary path used: {}".format(outpath))

        try:
            self.clone_repos_vcstool(self._REPOS_TEMPPATH, outpath)
        except subprocess.CalledProcessError as e:
            self.log.info(str(e))
            self.log.info("Move on assuming there might be repos already under the current path.")

        # Change dir into each local repo

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

    def main(self, args=None, stdout=None, stderr=None):

        if response in ['y', 'n']:
            return response == 'y'

        print("Response '%s' was not recognized, please use one of the following options: y, Y, n, N" % response, file=sys.stderr)

        parser = argparse.ArgumentParser(description="Generate a changelog based on the 'most downstream' package.")

        # Same options that catkin_generate_changelog takes in. TODO Better delegate to the upstream
        parser = self._parse_args_catkin_changelog_gen(parser)

        # Add custom args
        parser.add_argument(
            '--path-reposfile', required=True,
            help="Absolute/Relative path to the '{}' file based on which the upstream repos are pulled.".format(EXTENSION_SUPPORTED_CLONER))
        parser.add_argument(
            '--repo-downmost', required=True,
            help='Name of the down-most package/repo')
        parser.add_argument(
            '--temp-workdir', default=self._TMP_WORKDIR_ROOT,
            help='Absolute path for the temporary work directory.')

        args = parser.parse_args(sysargs)

        # If repo-downmost is present locally in the current directory or the workspace, move on.
        # If not, search in the .repos file and move on if it's found. If not found, warns and terminate.
        if not _is_downmost_repo_present(args.repo-downmost):
            #TODO
            pass

        # Aggregate changelogs from all upstream packages of repo-downmost.
