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
# These files must be identical and tests/unit/test_is_job_running_duplicated.py
# verifies this constraint.


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()

        job_query_result = self._execute_module(
            module_name="ibm.ibm_zos_core.zos_job_query",
            module_args=dict(job_name=module_args["job_name"]),
            task_vars=task_vars
        )

        if job_query_result.get("failed") is True:
            raise Exception(job_query_result.items())

        running_jobs = [job for job in job_query_result["jobs"] if job["ret_code"] is None]

        return {"running": len(running_jobs) == 1}
