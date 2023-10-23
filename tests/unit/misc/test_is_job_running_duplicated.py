# (c) Copyright IBM Corp. 2023
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
from . import utils


def test_is_job_running_duplicated():
    utils.assert_duplicates(
        "/roles/start_cics/action_plugins/is_job_running.py",
        "/roles/stop_cics/action_plugins/is_job_running.py",
        "/roles/validate/action_plugins/is_job_running.py",
        "/plugins/action/is_job_running.py"
    )
