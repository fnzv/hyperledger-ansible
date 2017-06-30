#!/usr/bin/python
from lxml import _elementpath
DOCUMENTATION = '''
---
module: cryptogen_extract
short_description:
    - Retrieve certificates and keys generated by the Hyperledger 
      cryptogen utility.
description:
    - A module for extracting from the file system the output generated by the
      Hyperledger utility "crypt-config" which generates PKI certificates
      and keys.  The result is a JSON object whose structure mirrors the
      layout generated by cryptogen in the file system.  In the deepest
      nesting of the JSON object, the path to the generated certificates and
      keys are stored in arrays with the node identifiers "certificates" and
      "keys", respectively.  All extracted paths are relative.
author: Keoja LLC
'''

EXAMPLES = '''
- name: Retrieve the certificates and keys generated by crypto-config.
  hl_crypto_keys:
  register: cryptokeys
'''

# Recursively descend the file system layout generated by the crypto-config
# tool, collecting the certificates and keys it generated.  Put them into
# a JSON structure that makes the paths and file names easily accessible.
def collect_certifications_and_keys(parent_path, path):
    retValue = {}
    certificates = []
    keys = []
    abs_path = path
    
    for d in os.listdir(abs_path):
        abs_path_extended = os.path.join(abs_path, d)
        if os.path.isdir(abs_path_extended):
           retValue[str(d)] = collect_certifications_and_keys(parent_path, abs_path_extended)
        else:
            # Key?
            if isKey(d):
                temp = { "path" : makeRelativePath(parent_path,abs_path_extended), "filename": d }
                keys.append( temp )
            else:
                temp = { "path" : makeRelativePath(parent_path,abs_path_extended), "filename": d }
                certificates.append(temp)

    # Any Keys?
    if len(keys) > 0:
        retValue['keys'] = keys;
        
    # Any Certificates?
    if len(certificates) > 0:
        retValue['certificates'] = certificates

    # Add in the path of the current folder
    retValue['path'] = makeRelativePath(parent_path,abs_path)
        
    return retValue

def isKey(fileName):    
    return fileName.endswith("_sk") or fileName.endswith('key')
    
def makeRelativePath( parent_path, path ):
    return os.path.relpath(path,parent_path)
        
def main():

    module = AnsibleModule(
        argument_spec = dict(
            path    = dict(required=True)
        ),
        add_file_common_args=True,
        supports_check_mode=True
    )

    path = os.path.expanduser(module.params['path'])
    
    try:
        # Does the path the caller gave us exist?
        if os.path.exists(path):
            # Is it a folder?
            if os.path.isdir(path) :
                # Yes
                parent_path = os.path.abspath(os.path.join(path,os.pardir))
                module.exit_json(changed=True, certificates_and_keys=json.dumps(collect_certifications_and_keys(parent_path, path)))
            else: 
                module.fail_json(changed=False, msg='The path "' + str(os.path.abspath(path)) + '" is not a folder.')
        else:            
            module.fail_json(changed=False, msg='The path "' + str(os.path.abspath(path)) + '" does not exist.')   

    #handle exceptions
    except Exception, e:
        module.fail_json( msg='Error: ' + str(e) )

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
