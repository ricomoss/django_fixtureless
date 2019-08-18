#! /usr/bin/env python
"""
Module that runs pylint on all python scripts found in a directory tree..
"""
import os
import re
import subprocess
import sys
from datetime import datetime


def _validate_todo(cur_file, file_as_string, msgs):
    """
    Validation to avoid TODOs being left in the code.  Create a Jira ticket if work needs
    to be done.

    :param cur_file:  Current file being parsed.
    :param file_as_string: file object
    """
    if re.findall(r'todo', file_as_string, flags=re.IGNORECASE):
        msgs.append('TODO found in {}. Make a ticket in Jira instead.'.format(cur_file))


def _validate_print(cur_file, file_as_string, msgs):
    """
    Rules:
    Print statements shouldn't be in production code.  Take out all
    debug code before committing.

    :param cur_file:  Current file being parsed.
    :param file_as_string: file object
    """
    # There are some files where we do want print statements
    files_to_skip = ()

    for file_to_skip in files_to_skip:
        if file_to_skip in cur_file:
            return

    if re.findall(r'print', file_as_string):
        msgs.append('Print statement found in {}. Remove all debug code.'.format(cur_file))


def _validate_files():
    """
    Set validation rules here.
    """
    cur_dir = os.getcwd()
    msgs = []
    validators = (_validate_todo, _validate_print, )
    for dirpath, _, files in os.walk(cur_dir):
        # We're only interested in Python packages
        if '__init__.py' not in files:
            continue

        for filename in files:
            cur_file = os.path.join(dirpath, filename)

            # Skip local files
            if _should_skip_file(cur_file):
                continue
            try:
                with open(cur_file, 'r') as file_pointer:
                    file_as_string = file_pointer.read()
                    for validator in validators:
                        validator(cur_file, file_as_string, msgs)
            except ValueError:
                pass

    if msgs:
        for msg in msgs:
            print(msg)
        sys.exit(1)


def _should_skip_file(cur_file):
    """
    Helper method to add conditions for skipping files.

    :param cur_file: The current file about to be evaluated.
    :return: True, if it should be skipped;False otherwise
    """
    # Don't check this file.
    if 'validate_repo.py' in cur_file:
        return True

    # Skip local files
    if cur_file.find('local') != -1:
        return True

    # Skip Tox Files
    if 'tox' in cur_file:
        return True

    return False


def _get_dirs(valid_dirs):
    """
    Get the valid directories for running pylint against

    :param valid_dirs: A list to append the valid directories
    """
    dirs = next(os.walk('.'))[1]
    for directory in dirs:
        try:
            files = next(os.walk(directory))[2]
        except IndexError:
            continue

        if '__init__.py' not in files:
            continue

        valid_dirs.append(directory)


def _run_cmd(valid_dirs):
    """
    Run the pylint command on the valid directories

    :param valid_dirs: The valid directories to run pylint against
    """
    rc_file = os.path.join(os.getcwd(), '.pylintrc')
    pylint_cmd = os.environ.get('PYLINT_COMMAND', 'pylint')
    cmd = [pylint_cmd, '--rcfile={}'.format(rc_file)]
    cmd.extend(valid_dirs)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    process.wait()
    report = process.stdout.read().decode('utf-8')
    print(report)
    match = re.search(r'\*+ Module \w', report)
    if match:
        print('You must maintain 10.00/10 on the pylint results.  Fix all problems!')
        sys.exit(1)


def _run_pylint():
    """
    Run pylint on the appropriate files in the repo.
    """
    valid_dirs = [os.getcwd()]
    _get_dirs(valid_dirs)
    _run_cmd(valid_dirs)


def _add_top_level_init():
    """
    Adds to a top level init so pylint doesn't freak out
    """
    with open('__init__.py', 'w') as init_file:
        init_file.write('')


def _remove_top_level_init():
    """
    Remove the top level init after the run is complete
    """
    os.remove('__init__.py')


def _validate_repo():
    """
    Run all validation steps.
    """
    start = datetime.now()
    try:
        _add_top_level_init()
        _run_pylint()
        _validate_files()
        print('Took {} seconds to validate this repo.'.format(datetime.now() - start))
    finally:
        _remove_top_level_init()


if __name__ == "__main__":
    _validate_repo()
