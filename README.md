This role add information about name of config file where interface is configured under ifupdown system.
This information is stored under `ansible_local` fact as `ansible_local.ifupdown_cfg`, for example
```
ansible_local.ifupdown_cfg.lo = /etc/network/interfaces
ansible_local.ifupdown_cfg.eth0 = /etc/network/interfaces.d/eth0
ansible_local.ifupdown_cfg.tun3 = /etc/network/intefaces.d/my_tuns
```

Example playbook:
```
---
- hosts: all
  gather_facts: false
  roles:
   - ifupdown_configs_fact
  post_tasks:
   - setup:
   - var=ansible_local.ifupdown_cfg
```

P.S. You need to update facts after this role (Use `gather_facts:true ` for next play or call `setup` module as one of the task).

This role works only with ifupdown system (Ubuntu up to 16.04, Debian). It does not support netplan (Ubuntu 18.04) or centos networking.
