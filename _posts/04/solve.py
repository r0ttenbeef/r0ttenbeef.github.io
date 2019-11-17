#!/usr/bin/python
import subprocess
import string
from colorama import Fore # text color

ascii_low = string.ascii_lowercase # generate lowercase ascii chars
bin_path = " " # snowball path

for i in range(len(ascii_low)):
    popen = subprocess.Popen([bin_path, ascii_low[i]], stdout=subprocess.PIPE) # run binary with arg from a to z
    output = popen.stdout.read()
    if "EGCTF" in output:
        print(Fore.GREEN + output.strip('\n'))
