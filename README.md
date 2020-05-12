# `sh` Ansible Module



`sh` is a custom **Ansible Module** that lets you execute shell commands based on the output of another `shell command` or `python code`



## Features

* Can make your Shell commands idempotent
* Execute commands with conditional `shell commands` or `Python code`
  * **Condition can be:**
    * `stdout`
    * `rc` (`return code`/`exit_status`)
    * `stdout` & `rc`



---



## Usage



Full example is provided in [sample_playbook.yml](https://github.com/eslam-gomaa/sh_Ansible/blob/master/sample_playbook.yml)



```yaml
- name: Name of the task
  sh:
    cmd: #command to run
    condition: # command to run as a condition (can be bash command or python code)
    lang: bash  # bash || Python
    if_stdout: # If condition-command-stdout
```

`

| :Param      | :Description                               | :Default | :Type   | :Options     |
| ----------- | :----------------------------------------- | -------- | ------- | ------------ |
| `cmd`       | shell command to run                       |          | String  |              |
| `condition` | command/script to be executed as condition | None     | String  |              |
| `lang`      | the condition command/script language      | bash     | String  | bash, python |
| `if_rc`     | the `rc` of the `condition cmd`            | None     | Integer |              |
| `if_rc_operator` | operator for `if_rc`                  | `=`      | String  | `['=', '!=', '>', '<', '>=', '<=']` |
| `if_stdout` | the `stdout` of the `condition cmd`        | None     | String  |              |
| `if_stdout_operator` | operator for `if_stdout`          | `=`       | String | `['=', '!=']`|
| `regexp` | whether to use RegExp search towards `condition-command-stdout` | false | Bool | true, false |

## Examples



* Execute shell command based on the `stdout` of another command

```yaml
- name: run command basd of the "stdout" of another command
  sh:
    cmd: 'hostnamectl'
    condition: 'hostname'
    lang: bash
    if_stdout: 'ansible'
  register: test_bash

- debug:
    var: test_bash
```



---



* Execute shell command based on the `stdout` &  `rc` of a Python code

```yaml
- name: run command based on Python code
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
  register: test_python

- debug:
    var: test_python
```



---


### RegEXP & user-defined operators are now supported

Example: [advanced_example.yml](./advanced_example.yml)

![](https://i.imgur.com/HjmTJS2.png)

![](https://i.imgur.com/blgmT32.png)
