---
layout: post
title: Backdooring PE file
date: 2019-11-05
image: /img/02/00-main.jpg
tags: redteam ReverseEngineering
---

In this blog post i will show a technique to inject a shellcode backdoor inside a PE file.

### Introduction

In this post i will inject a shellcode inside a PE file by adding a section header which will create a **code cave** inside the executable file.
According to [Wikipedia](https://en.wikipedia.org/wiki/Code_cave) the **code cave** is:

`A **code cave** is a series of null bytes in a process's memory. The code cave inside a process's memory is often a reference to a section of the code’s script functions that have capacity for the injection of custom instructions. For example, if a script’s memory allows for 5 bytes and only 3 bytes are used, then the remaining 2 bytes can be used to add additional code to the script without making significant changes.`


### Prerequisits

### Preprations

### Starting

#### 1. Creating PE section header


#### 2. Hijack exectution flow


#### 3. Inject shellcode backdoor code


#### 4. Restore execution flow
