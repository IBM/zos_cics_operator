# (c) Copyright IBM Corp. 2024
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
from . import utils


def test_validate_inputs_duplicated():
    utils.assert_duplicates(
        "/roles/validate/library/validate_inputs.py",
        "/plugins/modules/validate_inputs.py"
    )
