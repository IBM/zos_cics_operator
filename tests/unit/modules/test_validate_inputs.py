# (c) Copyright IBM Corp. 2024
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
import json
import os

from unittest.mock import MagicMock
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.zos_mvs_raw import MVSCmdResponse
from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils import _data_set_utils
from ansible_collections.ibm.zos_cics_operator.tests.unit.helpers import validation_helper as helper
from ansible_collections.ibm.zos_cics_operator.plugins.modules.validate_inputs import (
    AnsibleValidationModule, VAR_REGEX, CICS_HLQ, LE_HLQ, SYS_ID, DFLTUSER, USER, APPLID, CICS_USSHOME, CMCI_PORT
)

default_arg_parms = {
    "applid": "TSTMEXYZ",
    "cics_hlq": "DFH.V6R1M0.CICS",
    "cpsm_hlq": "DFH.CPSM",
    "cmci_port": 12345,
    "cics_license": "DFH.V6R1M0.SDFHLIC",
    "cics_usshome": "/usr/lpp/cicsts/dfh610",
    "dfltuser": "CICSUSER",
    "le_hlq": "CEE",
    "region_hlq": "IBMUSER.TESTRGS",
    "pyz": "/usr/lpp/IBM/cyp/v3r12/pyz",
    "sys_id": "XYZ",
    "user": "IBMUSER",
    "zfs_path": "/u/ibmuser/testrgs",
    "zoau": "/usr/lpp/IBM/zoautil"
}


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


def initialise_module(args):
    parms = default_arg_parms
    parms.update(args)
    set_module_args(parms)
    validation_module = AnsibleValidationModule()
    validation_module._module.fail_json = MagicMock(return_value=None)
    validation_module._module.exit_json = MagicMock(return_value=None)
    return validation_module


def test_validate_file_path_golden():
    validation_module = initialise_module({})
    var = "123"
    assert validation_module.check_valid_length(var, 1, 8)


def test_validate_file_path_maximum():
    validation_module = initialise_module({})
    var = "abc"
    assert validation_module.check_valid_length(var, 1, 3)


def test_validate_file_path_too_long():
    validation_module = initialise_module({})
    var = "toolong"
    assert validation_module.check_valid_length(var, 1, 3) is False


def test_validate_against_regex_golden():
    validation_module = initialise_module({})
    var = "IYK2ABCD"
    assert validation_module.meets_regex_requirements(var, VAR_REGEX)


def test_validate_against_regex_false():
    validation_module = initialise_module({})
    var = "IYK2-ABD"
    assert validation_module.meets_regex_requirements(var, VAR_REGEX) is False


def test_validate_file_paths_all_valid():
    validation_module = initialise_module({})
    os.path.exists = MagicMock(return_value=True)
    validation_module.validate_file_paths()
    assert validation_module.result["failed"] is False


def test_validate_file_paths_invalid_file_path():
    file_path_name = "/you/wont/find/me"
    validation_module = initialise_module({CICS_USSHOME: file_path_name})

    validation_module.is_existing_file_path = MagicMock(side_effect=[True, True, True, False])
    validation_module.validate_file_paths()
    assert validation_module.result["failed"]
    assert validation_module.result["msg"] == f"{file_path_name} does not exist"


def test_is_existing_file_path_false():
    path = "/u/fakeuser"
    validation_module = initialise_module({})
    assert validation_module.is_existing_file_path(path) is False


def test_validate_variables():
    validation_module = initialise_module({SYS_ID: "VAL", APPLID: "VALID", DFLTUSER: "DUSER", USER: "USER"})
    validation_module.validate_variables()
    assert validation_module.result["failed"] is not True


def test_validate_variables_invalid_length():
    bad_string = "VALTOOLONG"
    validation_module = initialise_module({SYS_ID: bad_string, APPLID: "VALID", DFLTUSER: "DUSER", USER: "USER"})
    validation_module.validate_variables()
    assert validation_module.result["failed"]
    assert validation_module.result["msg"] == f"sys_id must be between 1 and 4 characters. Value was {bad_string}"


def test_validate_variables_invalid_regex():
    validation_module = initialise_module({SYS_ID: "VAL", APPLID: "VALID", DFLTUSER: "DUSER)", USER: "USER"})
    validation_module.validate_variables()
    assert validation_module.result["failed"]
    assert "dfltuser must only contain acceptable characters" in str(validation_module.result["msg"])


def test_validate_data_set_base():
    validation_module = initialise_module({CICS_HLQ: "INVALIDNAME.DATASET"})
    validation_module.validate_high_level_qualifiers()
    assert validation_module.result["failed"]
    assert validation_module.result["msg"] == 'Invalid argument "INVALIDNAME.DATASET" for type "data_set_base".'


def test_validate_data_set_qualifier():
    valid_qualifier = "valid"
    validation_module = initialise_module({LE_HLQ: valid_qualifier})
    validation_module.validate_high_level_qualifiers()
    assert validation_module.result["failed"] is False


def test_validate_data_set_qualifier_invalid():
    invalid_qualifier = "CEEEEINVALIDNAME"
    validation_module = initialise_module({LE_HLQ: invalid_qualifier})
    validation_module.validate_high_level_qualifiers()
    assert validation_module.result["failed"]
    assert validation_module.result["msg"] == f'Invalid argument "{invalid_qualifier}" for type "qualifier".'


def test_is_safe_path():
    validation_module = initialise_module({})
    path = "/this/is/a/safe/path"
    validation_module.check_safe_path(path)
    assert validation_module.result["failed"] is False


def test_is_safe_path_data_set():
    validation_module = initialise_module({})
    path = "this.is.a.safe.dataset.path"
    validation_module.check_safe_path(path)
    assert validation_module.result["failed"] is False


def test_is_safe_path_invalid_file_path_null_bytes():
    validation_module = initialise_module({})
    path = "/this/isnt\x00/a/safe/path"
    validation_module.check_safe_path(path)
    assert validation_module.result["failed"]
    assert "embedded null" in validation_module.result["msg"]


def test_is_safe_path_invalid_dataset_null_bytes():
    validation_module = initialise_module({})
    path = "this.isnt.\x00.a.safe.path"
    validation_module.check_safe_path(path)
    assert validation_module.result["failed"]
    assert "embedded null" in validation_module.result["msg"]


def test_is_safe_path_invalid_file_path_integer():
    validation_module = initialise_module({})
    path = 2344523
    validation_module.check_safe_path(path)
    assert validation_module.result["failed"]
    assert validation_module.result["msg"] == "Failed whilst validating 2344523. Error message: expected str, bytes or os.PathLike object, not int"


def test_is_safe_path_invalid_file_path_in():
    validation_module = initialise_module({})
    path = 2344523
    validation_module.check_safe_path(path)
    assert validation_module.result["failed"]
    assert validation_module.result["msg"] == "Failed whilst validating 2344523. Error message: expected str, bytes or os.PathLike object, not int"


def test_is_safe_path_invalid_file_path_too_long():
    validation_module = initialise_module({})
    path = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    validation_module.check_safe_path(path)
    assert validation_module.result["failed"]
    assert validation_module.result["msg"] == f"{path} is an invalid path. Name too long or too large."


def test_invalid_cmci_port():
    port = int(-5)
    validation_module = initialise_module({CMCI_PORT: port})
    _data_set_utils._execute_listds = MagicMock(
        side_effect=[
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.CPSM.SEYULOAD", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.CPSM.SEYUAUTH", "VSAM"), stderr=""),
        ]
    )
    validation_module.validate_smss()
    assert validation_module.result["failed"] is True
    assert validation_module.result["msg"] == f"cmci_port {port} is not a valid port number"


def test_valid_cmci_port():
    port = int(5)
    validation_module = initialise_module({CMCI_PORT: port})
    _data_set_utils._execute_listds = MagicMock(
        side_effect=[
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.CPSM.SEYULOAD", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.CPSM.SEYUAUTH", "VSAM"), stderr=""),
        ]
    )
    validation_module.validate_smss()
    assert validation_module.result["failed"] is False


def test_validate_data_sets():
    validation_module = initialise_module({})
    _data_set_utils._execute_listds = MagicMock(
        side_effect=[
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.V6R1M0.SDFHLIC", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.V6R1M0.CICS.SDFHAUTH", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.V6R1M0.CICS.SDFHLOAD", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("CEE.SCEERUN", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("CEE.SCEERUN2", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("CEE.SCEECICS", "VSAM"), stderr=""),
        ]
    )
    validation_module.validate_data_sets()
    assert validation_module.result["failed"] is False


def test_validate_data_sets_missing_one_data_set():
    validation_module = initialise_module({})
    _data_set_utils._execute_listds = MagicMock(
        side_effect=[
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.V6R1M0.SDFHLIC", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.V6R1M0.CICS.SDFHAUTH", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("DFH.V6R1M0.CICS.SDFHLOAD", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("CEE.SCEERUN", "VSAM"), stderr=""),
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set("CEE.SCEERUN2", "VSAM"), stderr=""),
            MVSCmdResponse(rc=8, stdout=helper.LISTDS_data_set_doesnt_exist("CEE.SCEECICS"), stderr=""),
        ]
    )
    validation_module.validate_data_sets()
    assert validation_module.result["failed"] is True
    assert validation_module.result["msg"] == "CEE.SCEECICS does not exist"


def test_validate_data_sets_missing_all_data_sets():
    validation_module = initialise_module({})
    _data_set_utils._execute_listds = MagicMock(
        side_effect=[
            MVSCmdResponse(rc=8, stdout=helper.LISTDS_data_set_doesnt_exist("DFH.V6R1M0.SDFHLIC"), stderr=""),
            MVSCmdResponse(rc=8, stdout=helper.LISTDS_data_set_doesnt_exist("DFH.V6R1M0.CICS.SDFHAUTH"), stderr=""),
            MVSCmdResponse(rc=8, stdout=helper.LISTDS_data_set_doesnt_exist("DFH.V6R1M0.CICS.SDFHLOAD"), stderr=""),
            MVSCmdResponse(rc=8, stdout=helper.LISTDS_data_set_doesnt_exist("CEE.SCEERUN"), stderr=""),
            MVSCmdResponse(rc=8, stdout=helper.LISTDS_data_set_doesnt_exist("CEE.SCEERUN2"), stderr=""),
            MVSCmdResponse(rc=8, stdout=helper.LISTDS_data_set_doesnt_exist("CEE.SCEECICS"), stderr=""),
        ]
    )
    validation_module.validate_data_sets()
    assert validation_module.result["failed"] is True
    assert validation_module.result["msg"] == "CEE.SCEECICS does not exist"


def test__check_ds_paths():
    ds_path = "SOME.DS.PATH"
    validation_module = initialise_module({})
    _data_set_utils._execute_listds = MagicMock(
        side_effect=[
            MVSCmdResponse(rc=0, stdout=helper.LISTDS_data_set(ds_path, "VSAM"), stderr=""),
        ]
    )
    validation_module._check_ds_paths([ds_path])
    assert validation_module.result["failed"] is False


def test__check_ds_paths_dont_exist():
    ds_path = "SOME.DS.PATH"
    validation_module = initialise_module({})
    _data_set_utils._execute_listds = MagicMock(
        side_effect=[
            MVSCmdResponse(rc=8, stdout=helper.LISTDS_data_set_doesnt_exist(ds_path), stderr=""),
        ]
    )
    validation_module._check_ds_paths([ds_path])
    assert validation_module.result["failed"] is True
    assert validation_module.result["msg"] == f"{ds_path} does not exist"
