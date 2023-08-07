---
layout: post
title: Port Custom Build of Kali Nethunter to an Unsupported Phone Walkthrough
date: 2023-08-07
image: 10/00-main.jpg
tags: android
---

## Introduction

Lately I was trying to port kali nethunter to my old phone with supported external wifi card and things to be worked without much issues that I have found while using custom pre-built kali nethunter roms and custom kernel and it appears non of them worked in a stable way and not much support for the external wifi cards (**Like the well-known TP-LINK W722N v2**) and some other tools. So I have decided to create my own custom build for kali nethunter and this blog post will be about my walkthrough on how I have created my custom build for my unsupported phone.

## Requirements

First it's recommended that you have PC or Laptop with ubuntu based linux distro installed on it, In this walkthrough I have used [**Linux Mint**](https://linuxmint.com/) with `adb` and `fastboot` tools installed.

Also you might need a windows virtual machine to use [**Mi Unlock**](https://en.miui.com/unlock/download_en.html) tool for this task only.

Phone used in this walkthrough is [**Poco X3 NFC**](https://www.gsmarena.com/xiaomi_poco_x3_nfc-10415.php).
- Manufacturer: **Xiaomi**
- Full Name: **Xiaomi Poco X3 NFC**
- Codename: **Surya**
- Operating System: **Upgradable to Android 13**
- Processor: **Qualcomm Snapdragon 732G**
- Architecture: **Arm64**
- Wi-Fi: **802.11 a/b/g/n/ac, Dual-band, Wi-Fi Direct, Wi-Fi Display, DLNA, Hotspot** *Can be used for Monitor/Injection Mode!*

Then you need an android phone with bootloader unlocked. In case of Xiaomi you will need the following steps:
- Sign in to your Mi Account
- Activate the Developer options (Settings -> About Phone -> 'Tab 3 times on MIUI version')
- Go to Additional Settings -> Developer Options -> Enable OEM Unlocking and Mi Unlock status (Permission required: tap Agree) -> Add Account and device
- The toast message should appear "**Added successfully. Mi Account is associated with this device now.**"
- Now Shut down your phone manually, and hold Volume down key and Power button to enter Fastboot mode.
- Download the [**Mi Unlock**](https://en.miui.com/unlock/download_en.html) tool from MIUI official website on you windows VM and connect your phone to PC using USB cable and pass it to the windows VM you have.
- Sign in to your Mi Account in **Mi Unlock** with the same account on your phone for sure, After that it will check if phone connected and click "Unlock". ![0.png](/img/10/0.png)

- Unfortunately you will have to wait like 168 hours to unlock so after this period of time you will be able to unlock you phone correctly. ![01.png](/img/10/01.png)

- So after this period repeat these process again and unlock it with Mi Unlock and the phone should be unlocked successfully. ![02.png](/img/10/02.png)

> **Be informed that this process will erase all your phone data so it's recommended to backup your data before starting. Also unlocking your phone it makes you phone vulnerable so make sure you are using an old phone that you are not using with any personal sensitive data.**

## Flash Custom ROM with Custom Recovery

Now we will have to flash custom ROM to be used with kali nethunter using custom recovery called [**TWRP**](https://twrp.me/about/) and check if TWRP have an official build for your device here: https://twrp.me/Devices/ but I didn't find my phone right there so I have searched for unofficial build of TWRP following with my phone codename.

Then I have used [**Lineage Custom ROM**](https://lineageos.org/) and I have found an official build already for my [**Surya phone**](https://wiki.lineageos.org/devices/surya/). ![03.png](/img/10/03.png)

Also it's recommended to download [**Magisk Manager**](https://magiskmanager.com/) to manage applications that requires root permissions and flashing modules. We will using it later to flash our custom build of kali nethunter.

So now we have 3 Files requried:
- TWRP Custom Recovery
- LineageOS Custom ROM
- Magisk Manager APK File

Now go to "Developer Options", enable "USB debugging" and then connect your phone to the laptop via USB cable and run `adb devices`, You should see the following output. ![04.png](/img/10/04.png)

So everything is prepared now, Start the flashing process.
- Reboot to the **Fastboot** Mode
```bash
adb reboot-bootloader
```

- Flash and boot from TWRP custom recovery
```bash
fastboot boot twrp-3.5.2_10-10-surya.img # write twrp image name
```

- You should see TWRP custom recovery opened, Now go to (Wipe -> Format Data) and type "yes" then hit enter. ![05.jpg](/img/10/05.jpg)

- Also again go to (Wipe -> Advanced Wipe) And select everything to be wiped. ![06.jpg](/img/10/06.jpg)

- Now back to your labtop, Push LineageOS custom ROM to the phone.
```bash
adb push lineage-20.0-20230731-nightly-surya-signed.zip /bluetooth
```

- Change Magisk Manager APK file extension to be `.zip` instead of `.apk` and push it to the phone.
```bash
cp Magisk-v26.1.apk Magisk-v26.1.zip
adb push Magisk-v26.1.zip /bluetooth
```

- Back to phone, Go to (Install -> "Up A Level" -> bluetooth -> "Select the custom ROM file" -> Swipe to confirm flash)

![07.gif](/img/10/07.gif)

- Then flash Magisk like we did with custom ROM

![08.gif](/img/10/08.gif)

- Now reboot the device

![09.gif](/img/10/09.gif)

- After device rebooted successfully, Enable the "USB Debugging" again from "Developer Options" and push magisk manager apk file to the phone
```bash
adb push Magisk-v26.1.apk /storage/emulated/0
```

- Then open the file manager, Click and install the magisk application. It may ask for reboot so go ahead.

I didn't want to install GApps as I was afraid to make any conflicts or causing any unstable behavior, But you can try it yourself after finishing the whole process.

## Find Kernel Sources and Making a Test Kernel

Before going any further I highly recommend to read the official [**Kali Nethunter Documentation**](https://www.kali.org/docs/nethunter) as it's very useful and I will quote alot from it.

So now we need a supported kernel source to work with, LineageOS have their opensource kernels available on github. In my case I will clone the kernel version "**4.14**" of Surya phone from https://github.com/LineageOS/android_kernel_xiaomi_surya branch **Lineage-20** so it will be compatible with our LineageOS custom ROM.

After cloning the kernel source open it and clone https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-kernel inside the root of the kernel's directory.
```bash
git clone https://github.com/LineageOS/android_kernel_xiaomi_surya.git
cd android_kernel_xiaomi_surya
git clone https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-kernel.git
```

Find your best matching local.config example file, for me I will use `local.config.allinone` config and will modify it.
```bash
cp local.config.examples/local.config.example.allinone local.config
```

To avoid issues while building the kernel, We will modify the `local.config` to use newer **toolchains**, So instead of using `linaro-4.9` we will use `linaro-5.5` like following.
```c
CROSS_COMPILE_ARM32_SRC="https://kali.download/nethunter-images/toolchains/linaro-armhf-5.5.tar.xz"
CCD32="${TD}/linaro-armhf-5.5"

CROSS_COMPILE_SRC="https://kali.download/nethunter-images/toolchains/linaro-aarch64-5.5.tar.xz"
CCD="${TD}/aarch64-5.5"
```

It's better to install these packages instead installing it from `build.sh` script as it will be more faster to do it in oneline than looping in each package.
```bash
apt install axel bc binutils-aarch64-linux-gnu build-essential ccache curl device-tree-compiler pandoc libncurses5-dev lynx lz4 fakeroot xz-utils whiptail zip unzip
```

Also before running `./build.sh` there's syntax error in line `847` so replace `THREADS = 10` with `THREADS=10` and then run the script.
![10.png](/img/10/10.png)

- Select "**S. Setup Environment and download toolchains.**"
- Then build test kernel so select "**2. Configure & compile kernel from scratch**"
- Select your device's defconfig, In my case I have selected "**surya_defconfig**" ![11.png](/img/10/11.png)
- Type `y` and press tab and click "Save" to save the current configuration to `.config` file then "Exit", It's just a test kernel it will be modified later then wait for it to finish kernel compiling.
- If build was successful, select "**8. Edit Anykernel config**" to add some device details like codename, boot_block, slot_device, etc. ![12.png](/img/10/12.png)
- Now let's create our first test kernel, Select "**6. Create Anykernel zip**"
- It will be available at `kali-nethunter-kernel/output/anykernel-NetHunter.zip`
- Flash the kernel like we flashed the custom ROM before in TWRP custom recovery.
```bash
adb reboot-bootloader
fastboot boot twrp-3.5.2_10-10-surya.img
adb push anykernel-NetHunter.zip /bluetooth
# Go to install -> Up A Level -> bluetooth -> anykernel-NetHunter.zip and swipe to flash
```
![13.png](/img/10/13.png)

## Patching the Kernel

As the Kali Nethunter documentation mentioned that some devices need additional patches to avoid build errors, Which it can be applied from their `build.sh` script.

So run `./build.sh` and select "**4. Apply NetHunter kernel patches**" and then select the patch directory closest matching to your kernel version, In my case the kernel version is **4.14**, After that apply every patch in the list but if it showed message like **Warning: The test run completed with errors, apply the patch anyway?** don't apply it and skip it to another patch and so on.

If you have created a fork from the kernel source, You should commit each patch you made in the kernel source.
