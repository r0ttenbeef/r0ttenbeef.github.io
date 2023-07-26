---
layout: post
title: BlackMega Malware Analysis VM
date: 2023-07-26
image: 09/00-main.png
tags: Malware Automation
---
## Introduction

Convert windows virtual machine to a lab for malware analysis using ansible playbooks for automated installation of malware analysis tools and gadgets, Debloating useless windows services to reduce windows traffic noise and overwhelming running processes.

- Github Repository: [https://github.com/r0ttenbeef/BlackMega-VM](https://github.com/r0ttenbeef/BlackMega-VM)

## Requirements

Just an up and running up-to-date windows 10 or windows 11 virtual machine without bother doing any extra installation.

Also make sure to take a snapshot before running the playbook in case any damages could happen.

## Recommended Specs

- Operating System: **Windows 10**
- CPU Cores: **6**
- RAM Size: **6244 MB**
- Disk Space: **100 GiB**

## Add your own tools

The default BlackMega VM tools are installed using [Chocolaty](https://chocolatey.org/) package manager for windows for easy and fast installation, The tools list are stored in `group_vars/all.yml` as it's easy to be modified as needed.

## Fast Demo

A short small demonstration video after finishing blackmega-vm installation, Click the image down below.

[![](/img/09/01-Thum.png)](/img/09/BlackMega-VM_Demo.mp4)

## Windows configurations before running

Before running ansible playbook there's some changes to be made on windows machine first.

### Enable Windows Remote Management (WinRM)

Ansible will use WinRM protocol to connect the windows machine.

1. Make the network private
![Pasted image 20230717154700](https://github.com/r0ttenbeef/BlackMega-VM/assets/48027449/e67ca391-d4a3-400b-9d11-605434a14501)

2. Enable WinRM from powershell (Run as Administrator)
```powershell
winrm quickconfig
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
```


3. Disable Windows Defender and Firewall
![Pasted image 20230717172211](https://github.com/r0ttenbeef/BlackMega-VM/assets/48027449/1e87666d-2bcb-454b-9bee-e73182a6f4fa)

4. Disable User Account Control Settings (UAC)
![Pasted image 20230718003110](https://github.com/r0ttenbeef/BlackMega-VM/assets/48027449/d0c84f78-ee5e-4f43-bd29-8cb66b32500d)

5. Make sure that the user is in **Administrators** group
![Pasted image 20230722190015](https://github.com/r0ttenbeef/BlackMega-VM/assets/48027449/1ec81bee-e288-48cd-92f0-2794d5de2f5e)

### Initiate the installation

After cloning the BlackMega VM repository install python **winrm** module.

```bash
pip install -r requirements
```


The hosts credentials should be stored at `hosts.ini` file like following example.

```ini
[windows_box]
10.0.20.5

[windows_box:vars]
ansible_user = "admin_user"
ansible_password = "pass123"
ansible_port = 5985
ansible_connection = winrm
ansible_winrm_transport = basic
```


Now you can start ansible playbook.

```bash
ansible-playbook start.yml -i hosts.ini
```


### Cleanup after finishing

You can now simply revert any critical you have made like disabling WinRM, Reactivate the UAC.

In `Desktop\My_Tools\Maintainance` folder you will see some tools that will help you enable any disabled services like windows updates, edge blocking, etc.
