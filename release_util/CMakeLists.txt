cmake_minimum_required(VERSION 2.8.3)
project(release_util)
find_package(catkin REQUIRED)

catkin_python_setup()

catkin_package(
)

catkin_install_python(PROGRAMS bin/changelog_vcs
                      DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
