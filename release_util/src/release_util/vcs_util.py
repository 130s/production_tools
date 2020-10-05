from __future__ import print_function

import git
import logging
import os
import sys


class VcsUtil():
    def __init__(self):
        self.log = logging.getLogger(__name__)

    def get_a_changelog(self, repo_path, changelog_filename="CHANGELOG.rst"):
        """
        @summary Generate a list of changelog for a repo given by a path.
        @param repo_path: Path to a local repo.
        @deprecated: This is temporary. Code is basically copied from caking_pkg.cli.tag_changelog.main.
            This should be ported in upstream to avoid maintenance.
        """
        import datetime
        from catkin_pkg.changelog import get_changelog_from_path
        from catkin_pkg.package_version import bump_version
        from catkin_pkg.packages import find_packages, verify_equal_package_versions
        from catkin_pkg.cli.tag_changelog import get_forthcoming_label, rename_section

        # find packages in the given path
        packages = find_packages(repo_path)
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
            changelog_path = os.path.join(repo_path, pkg_path, changelog_filename)
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
        new_label = '{} ({})'.format(new_version, datetime.date.today().isoformat())
        for (pkg_name, changelog_path, changelog, forthcoming_label) in changelogs:
            print("Renaming section '{}' to '{}' in package '{}'...".format(
                forthcoming_label, new_label, pkg_name))
            data = rename_section(changelog.rst, forthcoming_label, new_label)
            new_changelog_data.append((changelog_path, data))

        print('Writing updated changelog files...')
        for (changelog_path, data) in new_changelog_data:
            with open(changelog_path, 'wb') as f:
                f.write(data.encode('utf-8'))
