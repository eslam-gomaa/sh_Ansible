#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, eslam.gomaa <linkedin.com/in/eslam-gomaa>

DOCUMENTATION = '''
---
module: sh
short_description: Run your shell commands in an idempotent way
version_added: "1.0"
description:
    - Run your sell commands based on the output of another 'shell commands' or 'python code'
        - If the condition not met, the command will not run and will be not marked as 'changed'
        - the condition can be rc OR stdout OR (rc+stdout)

options:
    cmd:
        description:
            - A shell command to run on the remote hosts
        required: true
        type: str

    condition:
        description:
            - A 'shell command' or 'python code' to run on the remote hosts as a condition
        required: false
        default: None
        type: str

    lang:
        description:
            - the language of the condition command/code
        required: false
        default: bash
        type: str

    if_rc:
        description:
            - RUN THE COMMAND -> if the 'rc' of the condition command/code matches the provided value
        required: false
        default: None
        type: int

    if_stdout:
        description:
            - RUN THE COMMAND -> if the 'if_stdout' of the condition command/code matches the provided value
        required: false
        default: None
        type: str    

author:
    - eslam.gomaa (linkedin.com/in/eslam-gomaa)
'''

EXAMPLES = '''
 ----------------------------------------------------

# Example 1

- name: run shell command based on the "stdout" of another shell command
  sh:
    cmd: 'hostname'
    condition: 'hostname'
    lang: bash
    if_stdout: 'ansible1'


 ----------------------------------------------------

# Example 2

- name: run command based of the "rc" of another command --  multi line
  sh:
    cmd: |
      export pass='password'
      export users_file=/root/users.txt
      echo 'user-test' > $users_file

          if [ -f $1 ] ; then
              for i in $( cat /root/users.txt ); do
                 useradd "$i"
                 echo "User $i created successfully"
                 echo $pass | passwd "$i" --stdin
              done
          else
              echo "Input is NOT a file"
          fi
    condition: 'cat /etc/passwd | grep user-test'
    lang: bash
    if_rc: 1

 ----------------------------------------------------

# Example 3

- name: run shell command based on "stdout" of Python code
  sh:
    cmd: echo 'Execute some commands '
    condition: |
      import socket
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      result = sock.connect_ex(('127.0.0.1',22))
      if result == 0:
         print "open"
      else:
         print "not-open"
      sock.close()
    lang: python
    if_stdout: 'open'

 ----------------------------------------------------

# Example 4

- name: run shell command based on "stdout" + "rc" of Python code
  sh:
    cmd: echo 'Execute some commands '
    condition: |
      import socket
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      result = sock.connect_ex(('127.0.0.1',24))
      if result == 0:
         print "open"
         sock.close()
      else:
         print "not-open"
         sock.close()
         exit(1)
    lang: python
    if_rc: 1
    if_stdout: 'not-open'

 ----------------------------------------------------    
'''

RETURN = '''
cmd:
    description: output of the command     
    type: dict
    returned: If the command did run

cmd_run:
    description: if == 0 then the command did run, if == 1 then the command did not run
    type: int
    returned: always

condition:
    description: output of the condition command/code
    type: dict
    returned: If the condition command did run    
                 
'''


##############################################
#######################
############
#!/usr/bin/python

import re
import operator

def runcommand(cmd):
    """
    function to execute shell commands and returns a dic of
    """
    import subprocess

    info = {}
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True,)
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

    file = '/tmp/{}.py'.format(random.randint(0, 1))
    py_file = open(file, "w+")
    py_file.write('#!/usr/bin/{}\n'.format(python_version))
    py_file.write('\n')
    py_file.write(code)
    # make file executable
    os.chmod(file,
             stat.S_IRUSR | stat.S_IWRITE | stat.S_IEXEC | stat.S_IRGRP | stat.S_IROTH | stat.S_IXGRP | stat.S_IXOTH)
    # we need to close the file before executing the command otherwise 'runcommand' function will not execute
    py_file.close()
    cmd = runcommand('{} {}'.format(python_version, file))  # Run the script and get the output
    os.remove(file)  # Remove the script file
    return cmd

def custom_operator(value1, oper, value2):
    operators = ['=', '!=', '>', '<', '>=', '<=']
    if not oper in operators:
        raise ValueError("Invalid Opeator - Supported operators are only: " + str(operators))
    bool = None
    if oper == '=':
        bool = operator.eq(value1, value2)
    elif oper == '!=':
        bool = operator.ne(value1, value2)
    elif oper == '>':
        bool = operator.gt(value1, value2)
    elif oper == '>=':
        bool = operator.ge(value1, value2)
    elif oper == '<':
        bool = operator.lt(value1, value2)
    elif oper == '<=':
        bool = operator.le(value1, value2)
    return bool

def shell2(cmd, lang, condition=None, if_rc=None, if_stdout=None, regexp= False, if_stdout_operator='=', if_rc_operator='='):
    info = {}
    info['cmd'] = None
    info['cmd_run'] = None
    info['condition'] = {}
    info['condition']['lang'] = lang
    info['condition']['cmd'] = condition
    info['condition']['if_rc'] = if_rc
    info['condition']['if_stdout'] = if_stdout

    if condition is None:
        c = runcommand(cmd)
        info['cmd'] = c
        info['cmd_run'] = 0
        return info

    if lang == 'bash':
        b = runcommand(condition)
        if (if_rc is not None) and (if_stdout is not None):
            found = []
            if regexp:
                if if_stdout_operator == '=':
                    if_stdout_operator = '>'
                elif if_stdout_operator == '!=':
                    if_stdout_operator = '<'
                pattern = re.compile(r"\b{}\b".format(if_stdout))
                found = pattern.findall(b['stdout'])
                search = (custom_operator(found, if_stdout_operator, 0)) and (custom_operator(b['rc'], if_rc_operator, if_rc))
            else:
                search = (custom_operator(b['stdout'], if_stdout_operator, if_stdout)) and (custom_operator(b['rc'], if_rc_operator, if_rc))
            if search:
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_rc'] = if_rc
                info['condition']['if_stdout'] = if_stdout
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = found

            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_stdout'] = if_stdout
                info['condition']['if_rc'] = if_rc
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = found
        elif if_rc is not None:
            if custom_operator(b['rc'], if_rc_operator, if_rc):
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_rc'] = if_rc
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = []
            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_rc'] = if_rc
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = []
        elif if_stdout is not None:
            found = []
            if regexp:
                if if_stdout_operator == '=':
                    if_stdout_operator = '>'
                elif if_stdout_operator == '!=':
                    if_stdout_operator = '<'
                pattern = re.compile(r"\b{}\b".format(if_stdout))
                found = pattern.findall(b['stdout'])
                search = (custom_operator(found, if_stdout_operator, 0))
            else:
                search = (custom_operator(b['stdout'], if_stdout_operator, if_stdout))

            if search:
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_stdout'] = if_stdout
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = found
            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_stdout'] = if_stdout
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = found

    elif lang == 'python':
        b = run_py_code(condition)
        if (if_rc is not None) and (if_stdout is not None):
            found = []
            if regexp:
                if if_stdout_operator == '=':
                    if_stdout_operator = '>'
                elif if_stdout_operator == '!=':
                    if_stdout_operator = '<'
                pattern = re.compile(r"\b{}\b".format(if_stdout))
                found = pattern.findall(b['stdout'])
                search = (custom_operator(found, if_stdout_operator, 0)) and (custom_operator(b['rc'], if_rc_operator, if_rc))
            else:
                search = (custom_operator(b['stdout'], if_stdout_operator, if_stdout)) and (custom_operator(b['rc'], if_rc_operator, if_rc))

            if search:
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_rc'] = if_rc
                info['condition']['if_stdout'] = if_stdout
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = found
            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_stdout'] = if_stdout
                info['condition']['if_rc'] = if_rc
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = found
        elif if_rc is not None:
            if custom_operator(b['rc'], if_rc_operator, if_rc):
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_rc'] = if_rc
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = []
            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_rc'] = if_rc
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = []
        elif if_stdout is not None:
            found = []
            if regexp:
                if if_stdout_operator == '=':
                    if_stdout_operator = '>'
                elif if_stdout_operator == '!=':
                    if_stdout_operator = '<'
                pattern = re.compile(r"\b{}\b".format(if_stdout))
                found = pattern.findall(b['stdout'])
                search = (custom_operator(found, if_stdout_operator, 0))
            else:
                search = (custom_operator(b['stdout'], if_stdout_operator, if_stdout))

            if search:
                c = runcommand(cmd)
                info['cmd'] = c
                info['condition']['cmd'] = b
                info['cmd_run'] = 0
                info['condition']['if_stdout'] = if_stdout
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = found
            else:
                info['condition']['cmd'] = b
                info['cmd_run'] = 1
                info['condition']['if_stdout'] = if_stdout
                info['condition']['regexp'] = regexp
                info['condition']['regexp_match'] = found

    return info

# lang --> bash
# print(shell2(cmd='export test=love && echo $test',condition='ifconfig pnet0', lang='bash', if_stdout='pnet[0-9]+', regexp=True, if_stdout_operator='='))


############
#######################
##############################################

from ansible.module_utils.basic import *

def main():
    fields = {
        "cmd": {"required": True, "type": "str"},
        "condition": {"default": None, "type": "str"},
        "lang": {"default": 'bash', "type": "str", "choices": ['bash', 'python']},
        "if_rc": {"default": None, "type": "int"},
        "if_stdout": {"default": None, "type": "str"},
        "if_stdout_operator": {"default": "=", "type": "str", "choices": ['=', '!=']},
        "if_rc_operator": {"default": "=", "type": "str", "choices": ['=', '!=', '>', '<', '>=', '<=']},
        "regexp": {"default": False, "type": "bool"},
    }

    module = AnsibleModule(argument_spec=fields)

    run = shell2(cmd=module.params['cmd'],
                 condition=module.params['condition'],
                 lang=module.params['lang'],
                 if_rc=module.params['if_rc'],
                 if_stdout=module.params['if_stdout'],
                 regexp=module.params['regexp'],
                 if_rc_operator=module.params['if_rc_operator'],
                 if_stdout_operator=module.params['if_stdout_operator']
                 )

    cmd_list = ['yum', 'wget', 'apt', 'apt-get', 'aptitude' ]
    cmd_split = module.params['cmd'].split()
    for x in cmd_split:
        for y in cmd_list:
            if x == y:
                module.warn("It's recommended to use Ansible Module for (" + x + ") instead of using explicit commands")


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