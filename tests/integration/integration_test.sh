#!/usr/bin/env bash
# (c) Copyright IBM Corp. 2023
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)
set -eux # This is important to ensure that return codes from failing tests are propagated

function __run_test__(){
    local playbook=$1
    local should_pass=$2
    local wazi_yml_path=${ANSIBLE_COLLECTIONS_PATH}/ansible_collections/ibm/ibm_zos_cics_operator/inventories/wazi.yml
    export ANSIBLE_INVENTORY_ANY_UNPARSED_IS_FAILED=True
    ansible-playbook -i $wazi_yml_path $playbook && __passed $should_pass $1 || __failed $should_pass $1
}

function __passed(){
    local should_have_passed=$1
    if [ $should_have_passed -eq 1 ]
    then
        echo "Playbook $playbook passed as expected"
    else 
        echo "Playbook $playbook was expected to fail but passed"
        exit 1
    fi
}

function __failed(){
    local should_have_passed=$1
    if [ $should_have_passed -eq 1 ]
    then
        echo "Playbook $playbook was expected to pass but failed"
        exit 1
    else
        echo "Playbook $playbook failed as expected"
    fi
}
