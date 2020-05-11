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
    cmd: command to run
    condition: command to run as a condition # cab be bash command or python code
    lang: bash  # bash || Python
    if_stdout: 'ansible'
```



```yaml
- name: Name of the task
  sh:
    cmd: command to run
    condition: | command to run as a condition # multi line
      hostname
      ifconfig
      etc...
    lang: bash  # bash || Python
    if_rc: 0 # you can use "if_stdout" + "if_rc"
```



| :Param      | :Description                               | :Default | :Type   | :Options     |
| ----------- | :----------------------------------------- | -------- | ------- | ------------ |
| `cmd`       | shell command to run                       |          | String  |              |
| `condition` | command/script to be executed as condition | None     | String  |              |
| `lang`      | the condition command/script language      | bash     | String  | bash, python |
| `if_rc`     | the `rc` of the `condition cmd`            | None     | Integer |              |
| `if_stdout` | the `stdout` of the `condition cmd`        | None     | String  |              |



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

* use REGEXP search as a condition to run the command

```yaml
    - name: use REGEXP search as a condition to run the command
      sh:
        cmd: 'hostnamectl'
        condition: 'ifconfig -a'
        lang: bash
        if_stdout: 'eth[0-9]'
        regexp: true
      register: test_regexp

    - debug:
        var: test_regexp
```

