---
layout: post
title: Install ElementaryOS 8 with Luks Encrypted LVM Partitions
date: 2025-01-14
image: 12/00-main.png
tags: linux
---

Finally elementaryOS 8 has been released and available to download with a lot of changes and improvements like Creating a new **Secure Session** that meant to respect user privacy, productive **multitasking and window management** features, etc.
Please read this official blog for more details about improvements regarding ElementaryOS 8 : [https://blog.elementary.io/os-8-available-now/](https://blog.elementary.io/os-8-available-now/)
I always like to install my linux distro in encrypted partition with **Luks Encryption** along side with windows, But unfortunately it's not a straight forward installation so this is why I'm writing this post on how it should be done correctly.

## Prerequisites

This installation guide requires that your computer boots with **UEFI** as the installation is totally different when booting using **legacy BIOS** which I think it might not be supported in this case so it's recommended to configure your BIOS to boot in UEFI mode not legacy mode.

Now you can download elementary OS from official website [https://elementary.io/](https://elementary.io/) and burn it into your USB drive.

![1.png](/img/12/1.png)

I always like to use `dd` utility to write ISO to my USB.
- First: Format your device with FAT before writing the ISO to your flash drive "Replace **/dev/sdX** with actual partition name of your drive".
```bash
sudo mkfs.vfat -n EOS -I /dev/sdX
```
- Second: Write elementaryos ISO to the formatted flash drive using `dd` command.
```bash
dd if=elementaryos-8.0-stable.20241122rc.iso of=/dev/sdX bs=1M status=progress
```

Now you can restart your device and boot from USB drive using whatever BIOS management key of your device.

## Installation - With known issues and fixes

When booting into your flash drive, ElementaryOS will start to boot and installer will shows.
ISSUE: I had and issue after selecting "Custom Install (Advanced)" while installing elementaryos, It was closing unexpectedly and nothing shows!, So follow up this guide if you had the same issue.

- Press **ALT + CTRL + F3** to start another TTY console and login with user **elementary** without password. ![2.png](/img/12/2.png)
- And then restart lightdm service: `sudo systemctl restart lightdm` and you will see the installer popup again.
- Select language and keyboard layout until you reach "Try or Install" page, Select **Try Demo Mode** and Click **Next**. ![3.png](/img/12/3.png)
- After that connect your WIFI and open terminal, Then execute the following commands to update the elementary installer to latest version.
```bash
sudo apt update
sudo apt install io.elementary.installer
```
- Now start the elementary installer from terminal by running `io.elementary.installer` and your will find that issue is fixed.
## Setup LVM Encrypted Partitions

In this part we will format our partition we need to install elementaryos with LuksFormat and setup LVM partitions.
ElementaryOS requires **/boot/efi** partition to be installed so what we are going to do is partitioning our disk like the following:
- 500MB: /boot/efi "FAT32"
- 1.5GB: /boot "EXT4"
- Rest of the disk size for encrypted partiton:
	- 2GB: SWAP - *Optional*
	- Rest of the disk: / - *Root Partition*

We will going to do this with **Gparted** segment our partitions as above, So we need to create 3 partitions like the following screenshot. ![4.png](/img/12/4.png)

Now lets start the encrypted LVM process, In my case the partition is named **/dev/vda3**.
- Step 1: Format the partition with LuksFormat
```bash
sudo cryptsetup luksFormat /dev/vda3
```
- Step 2: Open the encrypted partition with LuksOpen
```bash
sudo cryptsetup luksOpen /dev/vda3 eos_crypt
```
- Step 3: Initialize phyiscal volume to be used by LVM
```bash
sudo pvcreate /dev/mapper/eos_crypt
```
- Step 4: Create volume group
```bash
sudo vgcreate eos_crypt /dev/mapper/eos_crypt
```
- Step 5: Create a logical volume, One for swap partition and one for root partition
```bash
sudo lvcreate -L2G eos_crypt -n swap #SWAP Partition
sudo lvcreate -l 100%FREE eos_crypt -n root #Root Partition
```
## Installation

Now go to the installer and select **Custom Install (Advanced)** and select the partition that we have encrypted, In my case its /dev/vda3, It will ask you to enter the password to decrypt the partition and the device name. Type the name of the volume group we created earlier. ![5.png](/img/12/5.png)

We will deal with these partitions only. ![6.png](/img/12/6.png)

- /dev/vda1: **/boot/efi** "fat32"
- /dev/vda2: **/boot** "ext4"
- /dev/dm-1: **swap**
- /dev/dm-2: **Root /** "ext4"

So it will be similar to following screenshot. ![7.png](/img/12/7.png)

Now you can click on **Next** to start the installation process. After restarting it will ask you to unlock the disk. ![8.png](/img/12/8.png)

