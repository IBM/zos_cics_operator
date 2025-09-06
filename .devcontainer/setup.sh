#!/usr/bin/env bash
# Copy contents to the .ssh directory
cp -r /root/.ssh-local/. /root/.ssh
if [ -e  /root/.ssh/config ]; then
    # If config file exists
    mv ~/.ssh/config ~/.ssh/config-local
    touch ~/.ssh/config
    cat ~/.ssh/config-local > ~/.ssh/config
    rm ~/.ssh/config-local
fi

git config --global --add safe.directory /workspace/collections/ansible_collections/ibm/zos_cics_operator

pip install --user ansible-core==2.18

ansible-galaxy collection install -r /workspace/collections/ansible_collections/ibm/zos_cics_operator/collections/requirements.yml -p /workspace/collections
ansible-galaxy collection install community.general -p /workspace/collections

echo -e "[defaults]\nstdout_callback=community.general.yaml\nCOLLECTIONS_PATHS=/workspace/collections" > ~/.ansible.cfg

pip install -r /workspace/collections/ansible_collections/ibm/zos_cics_operator/dev-requirements.txt
