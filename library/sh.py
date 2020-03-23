

#################
##################################
def runcommand(cmd):
    import subprocess

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

def run_py_code(code, python_version='python'):
    import random
    import os
    import stat

    file = '/tmp/{}.py'.format(random.randint(0,1000))
    py_file = open(file,"w+")
    py_file.write('#!/usr/bin/{}\n'.format(python_version))
    py_file.write('\n')
    py_file.write(code)
    # make file executable
    os.chmod(file, stat.S_IRUSR | stat.S_IWRITE | stat.S_IEXEC | stat.S_IRGRP | stat.S_IROTH | stat.S_IXGRP | stat.S_IXOTH)
    # we need to close the file before executing the command otherwise 'runcommand' function will not execute
    py_file.close()
    cmd = runcommand('{} {}'.format(python_version, file)) # Run the script and get the output
    os.remove(file) # Remove the script file
    return cmd

def shell2(cmd, lang,condition=None,  if_rc=None, if_stdout=None, env=False):

    info = {}
    info['cmd']     = None
    info['cmd_run'] = None
    info['condition'] = {}
    info['condition']['lang']   = lang
    info['condition']['cmd']    = condition
    info['condition']['if_rc']     = if_rc
    info['condition']['if_stdout'] = if_stdout

    if condition is None:
        c = runcommand(cmd)
        info['cmd'] = c
        info['cmd_run'] = 0
        return info

    if lang == 'bash':
        b = runcommand(condition)
        if (if_rc is not None) and (if_stdout is not None):
            if (b['stdout'] == if_stdout) and (b['rc'] == if_rc):
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_rc'] = if_rc
                info['condition']['if_stdout'] = if_stdout
            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_stdout'] = if_stdout
                info['condition']['if_rc'] = if_rc
        elif if_rc is not None:
            if b['rc'] == if_rc:
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_rc'] = if_rc
            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_rc'] = if_rc
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
        b = run_py_code(condition)
        if (if_rc is not None) and (if_stdout is not None):
            if (b['stdout'] == if_stdout) and (b['rc'] == if_rc):
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_rc'] = if_rc
                info['condition']['if_stdout'] = if_stdout
            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_stdout'] = if_stdout
                info['condition']['if_rc'] = if_rc
        elif if_rc is not None:
            if b['rc'] == if_rc:
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_rc'] = if_rc
            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_rc'] = if_rc
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

    return info

##################################
#################

from ansible.module_utils.basic import *


def main():
    fields = {
        "cmd": {"required": True, "type": "str"},
        "condition": {"default": None, "type": "str"},
        "lang": {"default": 'bash', "type": "str", "choices": ['bash', 'python']},
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

    #cmd_args = module.params['cmd'].split()

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