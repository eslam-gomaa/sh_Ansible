import subprocess

#################
##################################
def runcommand(cmd):
    import subprocess

    #import os
    #env = dict(os.environ)  # Make a copy of the current environment

    info = {}
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True)
    std_out, std_err = proc.communicate()
    info['rc'] = proc.returncode
    info['stdout'] = std_out.rstrip()
    info['stderr'] = std_err.rstrip()
    ## Python's rstrip() method
    # strips all kinds of trailing whitespace by default, not just one newline
    return info
    #print(runcommand('ifconfig -a'))


def shell2(cmd, lang ,condition=None,  if_rc=None, if_stdout=None, env=False):

    info = {}
    info['cmd']     = None
    info['cmd_run'] = None
    info['condition'] = {}
    info['condition']['lang']   = lang
    info['condition']['cmd']    = condition
    info['condition']['if_rc']     = if_rc
    info['condition']['if_stdout'] = if_stdout


    if lang == 'bash':
        if condition is None:
            c = runcommand(cmd)
            info['cmd'] = c
            info['cmd_run'] = 0
            return info
        else:
            b = runcommand(condition)
            if (if_rc is not None) and (if_stdout is not None):
                if (b['stdout'] == if_stdout) and (b['rc'] == if_rc):
                    c = runcommand(cmd)
                    info['cmd'] = c
                    info['condition']['cmd'] = b
                    info['cmd_run'] = 0
                    info['condition']['if_rc']     = if_rc
                    info['condition']['if_stdout'] = if_stdout
                else:
                    info['condition']['cmd'] = b
                    info['cmd_run'] = 1
                    info['condition']['if_stdout'] = if_stdout
                    info['condition']['if_rc']     = if_rc
            elif if_rc is not None:
                if b['rc'] == if_rc:
                    c = runcommand(cmd)
                    info['cmd'] = c
                    info['condition']['cmd'] = b
                    info['cmd_run'] = 0
                    info['condition']['if_rc']  = if_rc
                else:
                    info['condition']['cmd'] = b
                    info['cmd_run'] = 1
                    info['condition']['if_rc']  = if_rc
            elif if_stdout is not None:
                if b['stdout'] == if_stdout:
                    c = runcommand(cmd)
                    info['cmd'] = c
                    info['condition']['cmd'] = b
                    info['cmd_run'] = 0
                    info['condition']['if_stdout'] = if_stdout
                else:
                    info['condition']['cmd'] = b
                    info['cmd_run'] = 1
                    info['condition']['if_stdout'] = if_stdout

    elif lang == 'python':
        info['cmd_run'] = 1

    return info
##################################
#################

from ansible.module_utils.basic import *


def main():
    fields = {
        "cmd": {"required": True, "type": "str"},
        "condition": {"default": None, "type": "str"},
        "lang": {"default": 'bash', "type": "str", "choices": ['bash']},
        "if_rc": {"default": None, "type": "int"},
        "if_stdout": {"default": None, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    run = shell2(cmd=module.params['cmd'],
                 condition=module.params['condition'],
                 lang=module.params['lang'],
                 if_rc=module.params['if_rc'],
                 if_stdout=module.params['if_stdout']
                 )

    if not run['cmd'] is None:
        if run['cmd']['stderr']:
            module.fail_json(msg=run['cmd'])

    if run['cmd_run'] == 1:
        changed_ = False
    else:
        changed_ = True


    module.exit_json(changed=changed_, meta=run)

if __name__ == '__main__':
    main()