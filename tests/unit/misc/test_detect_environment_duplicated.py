# (c) Copyright IBM Corp. 2023
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
from . import utils


def test_is_job_running_duplicated():
    utils.assert_duplicates(
        "/roles/wazi_sandbox_conventions/action_plugins/detect_environment.py",
        "/plugins/action/detect_environment.py"
    )
