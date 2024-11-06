#!/usr/bin/env python
# SPDX-License-Identifier: GPL-2.0
# Copyright Don Zickus <dzickus@redhat.com>

from argparse import ArgumentParser
import os
import sys
import logging
import traceback
import yaml


class TestPlan:
    """Define the fields inside the test section."""
    def __init__(self, tests):
        self.tests = {}
        for t in tests:
            if 'name' not in t or 'cmd' not in t:
                raise Exception('Missing fields "name" or "cmd" in test section')

            if t['name'] in self.tests:
                raise Exception(f'Duplicate test name ({t["name"]}) in test section')

            url = t['url'] if 'url' in t else None
            param = t['param'] if 'param' in t else None
            wd = t['working_directory'] if 'working_directory' in t else None
            env = t['env'] if 'env' in t else None

            value = {'Url': url,
                     'Working Directory': wd,
                     'Cmd': t['cmd'],
                     'Env': env,
                     'Param': param,
                     }
            self.tests[t['name']] = value

    def __str__(self):
        output = ""
        for (name, test) in self.tests.items():
            output += f"\n  {name}:"
            for (k, v) in test.items():
                output += f"\n    {k}: {v}"

        return output

    def print_cmd(self):
        """Print the test command."""
        output = ""
        for test in self.tests.values():
            wd = f"cd {test['Working Directory']} && " if test['Working Directory'] else ""
            env = f"{test['Env']}" if test['Env'] else ""
            param = f"{test['Param']}" if test['Param'] else ""

            output += f"{wd}{env}{test['Cmd']}{param}"

        return output


class Maintainer:
    """Define the fields inside the maintainer section."""
    def __init__(self, maintainers):
        self.maintainers = {}
        for m in maintainers:
            if 'name' not in m or 'email' not in m:
                raise Exception('Missing fields "name" or "email" in maintainer section')

            if 'name' in self.maintainers:
                raise Exception('Duplicate maintainer name in maintainer section')

            self.maintainers[m['name']] = m['email']

    def __str__(self):
        output = ""
        for (k, v) in self.maintainers.items():
            output += f"\n  {k} <{v}>"

        return output


class Subsystem:
    """Define the fields inside a test section."""
    __mandatory = (
        "maintainer",

        "list",

        "dependency",

        # the actual test command
        "test",
    )

    __optional = (
        # version of test to use
        "version",

        # stuff
        "hardware",
    )

    def __init__(self, name, data):
        """Data is a yaml subsystem section."""
        self.name = name

        for m in self.__mandatory:
            if m not in data:
                raise Exception('Missing mandatory field "%s" in subsystem %s' % (m, name))

            try:
                value = data[m]
                if m == "test":
                    value = TestPlan(data[m])
                elif m == "maintainer":
                    value = Maintainer(data[m])

                setattr(self, m, value)
            except Exception as ex:
                raise Exception(f'Section {name}: {ex}')

        for o in self.__optional:
            value = data[o] if o in data else None
            setattr(self, o, value)

        for field in data.keys():
            if field not in self.__mandatory and \
               field not in self.__optional:
                raise Exception('Unsupported field "%s" in section %s' % (field, name))

    def __str__(self):
        """Print the info self object."""
        return f"""
Subsystem:    {self.name}
Maintainer:   {self.maintainer}
Mailing List: {self.list}
Version:      {self.version}
Dependency:   {self.dependency}
Test:         {self.test}
Hardware:     {self.hardware}
        """


class TestYaml:
    """Define the format of the yaml file."""
    subsystems = {}

    def __init__(self, data):
        for section in data:
            subsystem = Subsystem(section, data[section])

            if subsystem.name in self.subsystems:
                raise Exception('Duplicate subsystem name detected: %s' % subsystem.name)
            self.subsystems[subsystem.name] = subsystem


def config_logging(verbose):
    """configure logging"""
    level = 'DEBUG' if verbose else 'INFO'

    logger = logging.getLogger()
    logger.setLevel(level)


def read_yaml(yaml_file):
    """Parse provided yaml file."""
    try:
        yfile = yaml_file
        if not yfile:
            yfile = os.path.join(os.path.dirname(__file__), 'test.yaml')

        with open(yfile, 'r') as yfile_p:
            data = yaml.safe_load(yfile_p)

        # validate the yaml data matches supported variables
        sections = TestYaml(data)
    except Exception as ex:
        sys.stderr.write(f'ERROR: Processing YAML file {yfile}\n{ex}\n')
        logging.debug("%s" % traceback.format_exc())
        sys.exit(1)

    return sections


def output_section(data, user_subsystem, info):
    """Provide test output based on user selected subsystem and args."""
    if user_subsystem not in data.subsystems:
        sys.stderr.write(f'No subsystem: {user_subsystem} in provide yaml file\n')
        sys.stderr.write(f'{data.subsystems.keys()}\n')
        sys.exit(1)

    subsystem = data.subsystems[user_subsystem]
    if info:
        print(subsystem)
    else:
        print(f'{subsystem.test.print_cmd()}')


def main():
    """Main"""

    parser = ArgumentParser(description='Test catalog')
    parser.add_argument('-s', '--subsystem', help='Select subystem to use')
    parser.add_argument('-f', '--file', help='YAML with tests to use.  Default test.yaml')
    parser.add_argument('-i', '--info', action='store_true',
                        help='Print info about tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    if not args.subsystem:
        sys.stderr.write('Must provide a subsystem to select\n')
        sys.exit(1)
    subsystem = args.subsystem

    config_logging(args.verbose)

    data = read_yaml(args.file)
    output_section(data, subsystem, args.info)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ninterrupted.")
        sys.exit(1)
    except Exception as ex:
        sys.stderr.write(f'ERROR: {ex}\n')
        sys.stderr.write(f'{traceback.format_exc()}\n')
        sys.exit(1)
