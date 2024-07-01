# -*- coding: utf-8 -*-

# (c) Copyright IBM Corp. 2024
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)

DOCUMENTATION = r'''
---
module: validate_inputs
short_description: Validate the parameters provided by the user
description:
  - abc
version_added: 2.0.0
author:
  - Kiera Bennett (@KieraBennett)
options:
  applid:
    description:
      - The application identifier of the CICS region. This must be no longer than 8 characters.
    type: str
    required: true
  cics_hlq:
    description:
      - The high level qualifier used in the names of CICS data sets.
      - For example, if the high level qualifier is CICSTS61.CICS, then the location of the
        C(SDFHLOAD) library of the CICS installation is C(CICSTS61.CICS.SDFHLOAD).
    type: str
    required: true
  cics_license:
    description:
      - The location of the C(SDFHLIC) library.
    type: str
    required: true
  cics_usshome:
    description:
      - The file path to the USS home directory for CICS.
    type: str
    required: true
  cpsm_hlq:
    description:
      - The high level qualifier used in the data set names of CICSPlex SM load libraries.
      - For example, if the high level qualifier is CICSTS61.CPSM, then the location of the
        C(SEYULOAD) library of the CICSPlex SM installation is C(CICSTS61.CPSM.SEYULOAD).
      - This parameter is required if you want to provision an SMSS
    type: str
    required: true
  cmci_port:
    description:
      - The HTTP port for the CMCI connection. This parameter is required if you want to provision an SMSS
    type: int
    required: true
  dfltuser:
    description:
      - The DFLTUSER parameter specifies the RACF® user ID of the default user; that is,
        the user whose security attributes are used to protect CICS® resources in the absence of other,
        more specific, user identification.
    type: str
    required: true
  le_hlq:
    description:
      - The high level qualifier used in the data set names of the Language Environment runtime libraries.
    type: str
    required: true
  region_hlq:
    description:
      - The high level qualifier used in the names of the region data sets.
      - The location of the region data sets to be created by using a template, for example,
          C(REGIONS.ABCD0001.<< data_set_name >>).
      - The base location of the region data sets with a template.
    type: str
    required: true
  pyz:
    description:
      - The installation location of the IBM Open Enterprise SDK for Python.
    type: str
    required: true
  sys_id:
    description:
      - The system identifier of the CICS region. This must be 1-4 characters long.
    type: str
    required: true
  user:
    description:
      - The z/OS user ID used to provision data sets and submit jobs.
    type: str
    required: true
  zfs_path:
    description:
      - Path to a zFS file system with the correct permissions to mount.
    type: str
    required: true
  zoau:
    description:
      - The installation directory of the Z Open Automation Utilities (ZOAU).
    type: str
    required: true
'''


EXAMPLES = r'''
- name: "Validate Input"
  ibm.ibm_zos_cics_operator.validate_inputs:
    applid: "IYKPO21A"
    cics_hlq: DFH.V6R1M0.CICS
    cics_license: DFH.V6R1M0.SDFHLIC
    cics_usshome: /usr/lpp/cicsts/dfh610
    cpsm_hlq: DFH.V6R1M0.CPSM
    cmci_port: 12345
    dfltuser: CICSUSER
    le_hlq: CEE
    pyz: /usr/lpp/IBM/cyp/v3r11/pyz/
    region_hlq: IBMUSER.TESTRGS
    sys_id: 021A
    user: CICSUSER
    zfs_path: /u/ibmuser/testrgs
    zoau: /usr/lpp/IBM/zoautil
'''

RETURN = r'''
changed:
  description: True if the system was changed.
  returned: always
  type: bool
failed:
  description: True if the Ansible task failed, otherwise False.
  returned: always
  type: bool
msg:
  description: A string containing an error message if applicable
  returned: always
  type: str
'''

import re
import errno
import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils._data_set_utils import _run_listds
from ansible_collections.ibm.ibm_zos_cics.plugins.module_utils._response import MVSExecutionException
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import BetterArgParser
__metaclass__ = type

SYS_ID = 'sys_id'
APPLID = 'applid'
ZFS_PATH = 'zfs_path'
USER = 'user'
PYZ = 'pyz'
ZOAU = 'zoau'
DFLTUSER = 'dfltuser'
REGION_HLQ = 'region_hlq'
LE_HLQ = 'le_hlq'
CICS_HLQ = 'cics_hlq'
CPSM_HLQ = 'cpsm_hlq'
CMCI_PORT = 'cmci_port'
CICS_LICENSE = 'cics_license'
CICS_USSHOME = 'cics_usshome'
VAR_REGEX = '^[A-Z0-9@#$]+$'


class AnsibleValidationModule(object):
    def __init__(self):
        self.dds = []
        self._module = AnsibleModule(
            argument_spec=self.init_argument_spec()
        )
        self.failed = False
        self.changed = False
        self.msg = ""
        self.module_args = self._module.params
        self.result = dict(changed=self.changed, failed=self.failed, msg=self.msg)

    def main(self):
        self.validate_variables()
        self.validate_file_paths()
        self.validate_high_level_qualifiers()
        self._module.exit_json(**self.result)

    def validate_variables(self):
        vars_to_validate = {SYS_ID: {"min": 1, "max": 4}, APPLID: {"min": 1, "max": 8}, DFLTUSER: {"min": 1, "max": 8},
                            USER: {"min": 1, "max": 8}}

        for var, lengths in vars_to_validate.items():
            minimum = lengths.get("min")
            maximum = lengths.get("max")
            val = self.module_args[var]
            if not self.check_valid_length(val, minimum, maximum):
                self._fail(f"{var} must be between {minimum} and {maximum} characters. Value was {val}")

            if not self.meets_regex_requirements(val, VAR_REGEX):
                self._fail(f"Parameter '{var}' with value '{val}' was not valid. {var} must only contain acceptable characters\
                           (A-Z, 0-9, @, # or $)")

    def meets_regex_requirements(self, value, regex):
        # Emulate python-3.4 re.fullmatch()
        if re.match(regex, value, flags=0):
            return True
        return False

    def check_valid_length(self, value, minimum, maximum):
        if (len(value) < minimum or len(value) > maximum):
            return False
        return True

    def validate_smss(self):
        cmci_port = int(self.module_args[CMCI_PORT])
        cpsm_hlq = self.module_args[CPSM_HLQ]

        if cmci_port != 0:
            if cmci_port < 0:
                self._fail(f"cmci_port {cmci_port} is not a valid port number")
            seyuload_path = cpsm_hlq + ".SEYULOAD"
            seyuauth_path = cpsm_hlq + ".SEYUAUTH"
            ds_paths = [seyuload_path, seyuauth_path]
            self._check_ds_paths(ds_paths)

    def validate_data_sets(self):
        cics_hlq = self.module_args[CICS_HLQ]
        le_hlq = self.module_args[LE_HLQ]

        sdfhlic_path = self.module_args[CICS_LICENSE]
        sdfhauth_path = cics_hlq + ".SDFHAUTH"
        sdfhload_path = cics_hlq + ".SDFHLOAD"
        sceerun_path = le_hlq + ".SCEERUN"
        sceerun2_path = le_hlq + ".SCEERUN2"
        sceecics_path = le_hlq + ".SCEECICS"

        ds_paths = [
            sdfhlic_path,
            sdfhauth_path,
            sdfhload_path,
            sceerun_path,
            sceerun2_path,
            sceecics_path
        ]

        self._check_ds_paths(ds_paths)

    def _check_ds_paths(self, paths):
        for path in paths:
            self.check_safe_path(path)
            if not self.is_existing_data_set(path):
                self._fail(f"{path} does not exist")

    def validate_file_paths(self):
        path_keys = [ZFS_PATH, PYZ, ZOAU, CICS_USSHOME]
        for path_key in path_keys:
            path = self.module_args[path_key]
            self.check_safe_path(path)
            if not self.is_existing_file_path(path):
                self._fail(f"{path} does not exist")

    def is_existing_file_path(self, path):
        return os.path.exists(path)

    def is_existing_data_set(self, data_set):
        try:
            return _run_listds(data_set)[1]
        except MVSExecutionException as e:
            self._fail(e.message)

    def validate_high_level_qualifiers(self):
        try:
            BetterArgParser(self.get_arg_defs()).parse_args(self.module_args)
        except ValueError as e:
            self._fail(e.args[0])

    def get_arg_defs(self):
        variable_definitions = self.init_argument_spec()
        list_of_data_sets = [CICS_HLQ, LE_HLQ, REGION_HLQ]
        if int(self.module_args[CMCI_PORT]) != 0:
            list_of_data_sets.append(CPSM_HLQ)

        for data_set in list_of_data_sets:
            if "." in self.module_args[data_set]:
                self.update_arg_def(variable_definitions[data_set], "data_set_base")
            else:
                self.update_arg_def(variable_definitions[data_set], "qualifier")
        return variable_definitions

    def update_arg_def(self, dict_to_update, arg_type):
        dict_to_update.update({"arg_type": arg_type})
        dict_to_update.pop("type")

    def check_safe_path(self, user_path):
        try:
            path = os.path.splitdrive(user_path)[1]
            for path_part in path.split(os.path.sep):
                try:
                    os.lstat(os.path.sep + path_part)
                except OSError as e:
                    if e.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                        self._fail(f"{user_path} is an invalid path. Name too long or too large.")
                except ValueError as e:
                    self._fail(f"Failed whilst validating {user_path}. Error message: {e}")
        except TypeError as e:
            self._fail(f"Failed whilst validating {user_path}. Error message: {e}")

    def _fail(self, msg):  # type: (str) -> None
        self.result = {
            "changed": False,
            "failed": True,
            "msg": msg,
        }
        self._module.fail_json(**self.result)

    @staticmethod
    def init_argument_spec():  # type: () -> dict
        return {
            APPLID: {
                "type": "str",
                "required": True
            },
            CICS_HLQ: {
                "type": "str",
                "required": True
            },
            CICS_LICENSE: {
                "type": "str",
                "required": True
            },
            CICS_USSHOME: {
                "type": "str",
                "required": True
            },
            CMCI_PORT: {
                "type": "int",
                "required": True
            },
            CPSM_HLQ: {
                "type": "str",
                "required": True
            },
            DFLTUSER: {
                "type": "str",
                "required": True
            },
            LE_HLQ: {
                "type": "str",
                "required": True
            },
            REGION_HLQ: {
                "type": "str",
                "required": True
            },
            PYZ: {
                "type": "str",
                "required": True
            },
            SYS_ID: {
                "type": "str",
                "required": True
            },
            USER: {
                "type": "str",
                "required": True
            },
            ZFS_PATH: {
                "type": "str",
                "required": True
            },
            ZOAU: {
                "type": "str",
                "required": True
            }
        }


def main():
    AnsibleValidationModule().main()


if __name__ == '__main__':
    main()
