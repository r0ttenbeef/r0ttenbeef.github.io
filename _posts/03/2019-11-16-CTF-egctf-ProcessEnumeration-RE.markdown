---
layout: post
title: EG-CTF "Process Enumeration" walkthrough
date: 2019-11-16
image: 03/00-main.jpg
tags: ctf ReverseEngineering
---

I have participated in [EG-CTF](https://ctf2019.egcert.eg/challenges) which is organized by [EG-CERT](https://www.egcert.eg/) and this a writeup for *Process Enumeration* a reverse engineering CTF challenge.

### Enumeration

First I tried to run the *Process_Enum.exe* file and this is the output i got.

![01-runexe.png](/img/03/01-runexe.png)

So what i get here is that executable file enumerating the running processes in my machine nothing else, so i have opened it in IDA to analyze what it is doing exactly.

![02-justpe.png](/img/03/02-justpe.png)

So it's just a PE file, and let us see the binary strings first.

![03-strings.png](/img/03/03-strings.png)

There is an interesting string right here:

`** Flag is \"EGCTF{\%s}\"\n\n`

So our flag will go right there, i clicked it to see it in .rdata section.

![04-interstingstrings.png](/img/03/04-interstingstrings.png)

There is more interesting strings right here that we should go for each one of them.
```assembly
** %s exist in the system
Error!!!!!
** Computer name: %s
** System is not authorized !!!!!
** %s is the authorized system
```
now lets see the data XREF for these strings by double clicking the `DATA XREF: sub_401070+B7` to see what are these strings being used.

![05-enumprocs.png](/img/03/05-enumprocs.png)

this is the instructions for getting running processes with its **PID**.

![06-cname.png](/img/03/06-cname.png)

and what i understand here that while enumerating the running processes it checks for a specific process name and if exists will print `** PROCNAME.EXE is exists in the system` and then getting the machine pc name **NetBIOS name** by calling (GetComputerNameW)[https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getcomputernamew] function, and then making a short jump if not equal something to print `Error!!!!!`.

![07-chksys.png](/img/03/07-chksys.png)

if the requirements are met it will print `** Computer name: NAME` and it's comparing two strings and then short jump if true to instructions that prints `** SOMETHING is the authorized system`

![07-chksys.png](/img/03/07-chksys.png)

and after that it goes to a set of instructions that leads to our flag.

![08-flag-instructions.png](/img/03/08-flag-instructions.png)

![09-get-flag.png](/img/03/09-get-flag.png)

so i have to debug that binary for better understanding, In this case i will use **x64dbg** debugger.

### Debugging

While debugging i see that when the executable enumerating the processes it checks for **egctf.exe**.

![10-chkexename.png](/img/03/10-chkexename.png)

so what i have done is renaming the binary itself to **egctf.exe**

![11-renameexe.png](/img/03/11-renameexe.png)

and running it again.

![12-output1.png](/img/03/12-output1.png)

it has printed more information after checking for **egctf.exe** process and it looks like it is checking for computer name `** Computer name: FLARE-PC`.

While analyzing the executable in **IDA** we saw a string `** %s is the authorized system` which explain that `** System is not authorized !!!!!` string is printed because it checks for the current user privilages to see it has **SYSTEM** privilages or not.

Alright, let us debug the new renamed executable file.

![13-cnamefunc.png](/img/03/13-cnamefunc.png)

And double clicking the `** Computer name: %s` string

![14-bigpic.png](/img/03/14-bigpic.png)

![15-bigpic2.png](/img/03/15-bigpic2.png)

And i have set a breakpoint on it and pressed _F9_ to run.

![16-breakpoint.png](/img/03/16-breakpoint.png)

Steping through some instructions and it's setting a value to **EAX** `labtop-CTFGeek` and pushing to the stack and then calling **wciscmp** to compare it with the local machine name from **GetComputerNameW** function.

![17-cmpcname.png](/img/03/17-cmpcname.png)

So what to do now is to rename the computer name to `labtop-CTFGeek`

![18-changename.png](/img/03/18-changename.png)

And adding a user with low privilage

![19-adduser.png](/img/03/19-adduser.png)

Then restarting the machine and login to our new user

![20-login.png](/img/03/20-login.png)

And run the renamed executable file

![21-flag.png](/img/03/21-flag.png)

And here is the flag xD

> EGCTF{w3lc0m3t03gecertn4t10n4lctf}

Hope u enjoyed this post.
