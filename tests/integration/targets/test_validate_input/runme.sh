#!/usr/bin/env bash
# (c) Copyright IBM Corp. 2024
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
set -eux # This is important to ensure that return codes from failing tests are propagated

H3N_ENV="$ANSIBLE_COLLECTIONS_PATH/ansible_collections/ibm/ibm_zos_cics/tests/integration/variables/h3n.yml"
source ${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/ibm/zos_cics_operator/tests/integration/integration_test.sh

__run_test__ playbooks/test_validate_input_success.yml
__run_test__ playbooks/test_validate_input_fail.yml
exit 0