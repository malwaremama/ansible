#!/usr/bin/env python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
Module: panos_backup2file
Short_Description: Capture running config from PAN-OS device
Description:
    - PanOS module that will capture the running config on the target host and write the XML output to a file.
Author: "Sandra Wenzel (@malwaremama) with assitance from Garfield Freeman"
Version: "1.0 - First release WAHOO!"
Requirements:
    - pandevice can be obtained from PyPi U(https://pypi.python.org/pypi/pandevice)
Options:
    ip_address:
        description:
            - The IP address (or hostname) of the PAN-OS device.
        required: true
    username:
        description:
            - Username credentials to use for authentication.
        required: false
        default: "admin"
    password:
        description:
            - Password credentials to use for authentication.
        required: true if API key is not used
    api_key:
        description:
            - API Key generated from the target PAN-OS device.
        required: true if plain-text password is not used
'''

EXAMPLES = '''
- name: snapshot of running config on PAN-OS device
  panos_backup2file:
    ip_address: '{{ mgmt_ip }}'
    username: '{{ username }}'
    api_key: '{{ api_key }}'
    password: '{{ password }}'

'''

RETURN = '''
status:
    description: success status
    returned: success
    type: string
    sample: "Done"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import get_exception
import time
import datetime

try:
    import pandevice
    from pandevice import base


    HAS_LIB = True
except ImportError:
    HAS_LIB = False

def main():
    argument_spec = dict(
        ip_address=dict(required=True),
        username=dict(default='admin'),
        password=dict(no_log=True),
        api_key=dict(no_log=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False,
                           required_one_of=[['api_key', 'password']])

    if not HAS_LIB:
        module.fail_json(msg='Missing required libraries.')

    ip_address = module.params["ip_address"]
    username = module.params["username"]
    password = module.params["password"]
    api_key = module.params['api_key']

    # Create the device connection using host IP address and the API key from '*-secrets.yml'
    device = base.PanDevice.create_from_device(ip_address, username, password, api_key=api_key)

    # Run operational command to target host and store variable as 'cfgfile'
    cfgfile = device.op('show config running', xml=True)

    #Use the timestamp to create a unique filename. Change "/tmp/" to desired folder location where the config file will be written to.
    filename = "/tmp/" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d') + "." + device.hostname + '.xml'
    # Write the config to a file
    with open (filename, "w+") as fd:
        fd.write(cfgfile)

    module.exit_json(msg="Done")

if __name__ == '__main__':
    main()
