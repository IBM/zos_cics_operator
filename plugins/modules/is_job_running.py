# -*- coding: utf-8 -*-

# (c) Copyright IBM Corp. 2023,2024
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

DOCUMENTATION = r"""
---
module: is_job_running
short_description: Determine whether a job with a supplied name is running
description:
  - Determine whether a job with a supplied name is running
version_added: 1.0.0
author:
  - Stewart Francis (@stewartfrancis)
options:
  job_name:
    description: The name of the job
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Check if CICS is running
  is_job_running:
    job_name: RAPPLID
  register: is_cics_running
"""
