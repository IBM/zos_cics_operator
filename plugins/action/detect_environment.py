#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) Copyright IBM Corp. 2023
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
from ansible.plugins.action import ActionBase

# All instances of this role must be identical.  Cloud broker does not execute playbooks
# in this collection using FQCN, so as far as Ansible in CB is concerned, we're
# executing an ad-hoc playbook.  That means that Ansible will search for referenced
# assets differently.
#
# In this case in CB, Ansible will look for action plugins relative to the
# playbook in an action_plugins directory, rather than the collection-specific
# location plugins/actions, relative to the collection root.  In order to make this
# collection executable as a collection and by cloud broker, this file is instead
# embedded in all roles that require it independently, to work around this limitation.
#
# These files must be identical and tests/unit/test_detect_environment_duplicated.py
# verifies this constraint.

WAZI_SANDBOX_PRE_26_PYTHON_HOME = "/usr/lpp/IBM/cyp/v3r9/pyz"
WAZI_SANDBOX_26_PYTHON_HOME = "/usr/lpp/IBM/cyp/pyz"


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Execute an SSH command that doesn't require a python interepreter
        shell_result = self._low_level_execute_command(f"file {WAZI_SANDBOX_PRE_26_PYTHON_HOME}/bin/python3")

        discovered = {}
        if "FSUM6484" not in shell_result['stdout']:
            # wazi sandbox pre 2.6
            pyz = WAZI_SANDBOX_PRE_26_PYTHON_HOME
            dfh_zos_stcjobs = "USER.Z25C.PROCLIB"
        else:
            # wazi sandbox 2.6
            pyz = WAZI_SANDBOX_26_PYTHON_HOME
            dfh_zos_stcjobs = "USER.Z25D.PROCLIB"

        zoau_home = "/usr/lpp/IBM/zoautil"
        dfh_zfs_mountpoint = "/u/ibmuser/regions"

        discovered.update({
            "pyz": pyz,
            "z_environment_vars": {
                "_BPXK_AUTOCVT": "ON",
                "ZOAU_HOME": zoau_home,
                "LIBPATH": f"{ zoau_home }/lib:{ pyz }/lib:/lib:/usr/lib:.",
                "PATH": f"{ zoau_home }/bin:{ pyz }/bin:/bin:/var/bin",
                "_CEE_RUNOPTS": "FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)",
                "_TAG_REDIR_ERR": "txt",
                "_TAG_REDIR_IN": "txt",
                "_TAG_REDIR_OUT": "txt",
                "LANG": "C",
                "PYTHONSTDINENCODING": "cp1047"
            },

            "DFH_APPLID_PREFIX": "ZCICS",
            "JOB_CARD": "JOB REGION=0M,MSGLEVEL=(1,1),MSGCLASS=R",
            "DFH_CICS_HLQ": "DFH610.CICS",
            "DFH_CICS_LICENSE_DATASET": "DFH610.SDFHLIC",
            "DFH_LE_HLQ": "CEE",
            "DFH_ZOS_STCJOBS": dfh_zos_stcjobs,
            "DFH_CICS_USSHOME": "/usr/lpp/cicsts/cicsts61",
            "DFH_REGION_CICSSVC": 216,
            "DFH_REGION_SIT": "6$",
            "DFH_REGION_DFLTUSER": "CICSUSER",
            "DFH_REGION_HLQ": "IBMUSER.REGIONS",
            "DFH_ZFS_MOUNTPOINT": dfh_zfs_mountpoint,
            "DFH_ZFS_METADATA": f"{ dfh_zfs_mountpoint }/metadata",
            "DFH_STC_JOB_CARD": "JOB REGION=0M,MSGLEVEL=(1,1),MSGCLASS=R,NOTIFY=IBMUSER",
            "DFH_ZOS_VSAM_UNIT": "SYSDA"
        })

        return dict(
            ansible_facts=discovered
        )
