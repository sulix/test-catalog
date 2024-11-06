# Linux Kernel Test Catalog

An attempt to map kernel subsystems to kernel tests that should be run on
patches or code by humans and CI systems.


Examples:

Find tests for a subsystem
./get_tests.py -s <subsystem>

Find info about subsystem tests
./get_tests.py -s <subsystem> --info

