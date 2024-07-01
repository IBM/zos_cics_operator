#!/usr/bin/env bash
# (c) Copyright IBM Corp. 2023,2024
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
set -eux # This is important to ensure that return codes from failing tests are propagated

function __run_test__(){
    local playbook=$1
    local debug_me=${2:-foo}
    local inventory_path=${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/ibm/ibm_zos_cics_operator/inventories/inventory_zos.yml
    export ANSIBLE_INVENTORY_ANY_UNPARSED_IS_FAILED=True
    export ANSIBLE_INSTALL_LOCATION=/usr/local/bin/ansible-playbook

    if [ $debug_me -eq 1 ]
    then
        python -m debugpy --wait-for-client --listen 0.0.0.0:5678 $ANSIBLE_INSTALL_LOCATION -i $inventory_path $playbook
    else
        ansible-playbook -i $inventory_path $playbook
    fi
}
