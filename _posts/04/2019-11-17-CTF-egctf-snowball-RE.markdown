---
layout: post
title: EG-CTF "snowball" walkthrough
date: 2019-11-17
image: 04/00-main.jpg
tags: ctf ReverseEngineering
---

I have participated in [EG-CTF](https://ctf2019.egcert.eg/challenges) which is organized by [EG-CERT](https://www.egcert.eg/) and this a writeup for [snowball](https://github.com/r0ttenbeef/r0ttenbeef.github.io/raw/master/_posts/04/snowball.bin), a reverse engineering CTF challenge.

> Download CTF binary executable [Here](https://github.com/r0ttenbeef/r0ttenbeef.github.io/raw/master/_posts/04/snowball.bin)

### Enumeration

First I checked the file type and extract some info about that binary, it's ELF x64 stripped binary executable.

![01-filetype.png](/img/04/01-filetype.png)

Then I tried the to extract the binary strings and got some interesting strings.

![02-strings.png](/img/04/02-strings.png)

And then running the binary.

![11-run.png](/img/04/11-run.png)

Lets open the binary in **radare2** to analyze it and see what it actually does.

### Analysis

First I have opened the binary in **radare2** and analyzing its functions.

![04-interesting.png](/img/04/04-interesting.png)

I got **main** function right there, let us analyzing it.

![05-keychk.png](/img/04/05-keychk.png)

It's checking for the for the key supplied by counting the arguments, if no argument specified it will print `No key supplied` then exit.

![06-cmp14c.png](/img/04/06-cmp14c.png)

And here it's comparing the given argument with **14c**.

![07-cmptrue.png](/img/04/07-cmptrue.png)

So if it's false, it will print `Nope!` and exit.

![08-get-flag.png](/img/04/08-get-flag.png)

And if it's true, it will go to these set of instructions and print the flag, what i see here interesting also is that function call `fcn.00000a2a`, so lets analyze this.

![09-flag-mcrypt.png](/img/04/09-flag-mcrypt.png)

So it's using [mcrypt module](https://linux.die.net/man/3/mcrypt) which is an encryption/decryption liberary and it's using **CBC** Mode and **Rijndael-128** algorithm to decrypt the flag.

### Solving

Now lets run the binary again and tracing the library call by using [ltrace](http://man7.org/linux/man-pages/man1/ltrace.1.html)

![03-runltrace.png](/img/04/03-runltrace.png)

Looks like it's counting by hex value of the ascii character given to the binary and comparing to a hex value **14c**, so what i will do is something like bruteforcing the binary and get our flag.
I have created a python script to automate this task, [The script easy to understand](https://github.com/r0ttenbeef/r0ttenbeef.github.io/raw/master/_posts/04/solve.py).

```python
#!/usr/bin/python
import subprocess
import string
from colorama import Fore

ascii_low = string.ascii_lowercase
bin_path = "/tmp/0vbibK/snowball.bin"

for i in range(len(ascii_low)):
    popen = subprocess.Popen([bin_path, ascii_low[i]], stdout=subprocess.PIPE)
    output = popen.stdout.read()
    if "EGCTF" in output:
        print(Fore.GREEN + output.strip('\n'))
```

Now run our script..

![10-flag.png](/img/04/10-flag.png)

And here it is, the flag.

> EGCTF{R0ll1NG_Arou0nd}

