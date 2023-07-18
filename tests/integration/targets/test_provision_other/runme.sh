#!/usr/bin/env bash
# (c) Copyright IBM Corp. 2023
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
set -eux # This is important to ensure that return codes from failing tests are propagated

source ${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/ibm/ibm_zos_cics_operator/tests/integration/integration_test.sh

__run_test__ playbooks/test_provision_success.yml 1
exit 0