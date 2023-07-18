# (c) Copyright IBM Corp. 2023
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
import os
import filecmp


def test_is_job_running_duplicated():
    start = os.getcwd() + "/roles/start_cics/action_plugins/is_job_running.py"
    stop = os.getcwd() + "/roles/stop_cics/action_plugins/is_job_running.py"
    validate = os.getcwd() + "/roles/validate/action_plugins/is_job_running.py"
    collection = os.getcwd() + "/plugins/action/is_job_running.py"
    compare(start, stop)
    compare(start, validate)
    compare(start, collection)


def compare(file1, file2):
    if (not filecmp.cmp(file1, file2)):
        raise BaseException(f"{file1} and {file2} must be identical, but were not")
