---
layout: post
title: Deploy Hidden Virtual Machine For VMProtections Evasion And Dynamic Analysis
date: 2023-07-02
image: 08/00-main.jpg
tags: Malware
---

## Introduction

Most of the malwares in the wild are adding some protections techniques to their malicious software against Virtual Machines to make their malwares more harder to run inside virtual machine or sandboxes for analysis purposes.
In this post I'm going to create a KVM based Windows 11 virtual machine trying to evade some VM detection tools.

## Virtual Machine Specs

Virtual Machine Hypervisor: **KVM**
Operating System: **Windows 10**
CPU Cores: **6**
RAM Size: **6244 MB**

## Create the Virtual Machine

Moving to the creation of our VM with specs mentioned earlier.
After providing the disk space, ram size and cpu cores change the MAC Address of the network interface you provided with known mac address vendor, You can download the mac vendors json files from [https://maclookup.app](https://maclookup.app/downloads/json-database) and choose whatever you want.
In this case I have choosed vendor **PHYGITALL SOLUÇÕES EM INTERNET DAS COISAS** and the mac address will be `8C:1F:64:B4:67:88`

![0.png](/img/08/0.png)

And leave the bios firmware and chipset as it is.
![1.png](/img/08/1.png)

Then apply and begin installation.

> **By the way you should know how to install windows os inside kvm hypervisor as it's a bit different from other hypervisors, Install the os and the QEMU tools and get back**


## Create VMProtected executable binary

At first I have created a simple golang binary that will pops up a windows message box when it executes successfully.

```go
package main

import "tawesoft.co.uk/go/dialog"

func main() {
        dialog.Alert("Software executed successfully - r0ttenbeef")
}
```

> *I just like using golang, You can use anything else you want.*

For the sake of this example I have used an already existing package instead of doing complicated windows API calls.
Now will try to compile the golang binary for windows 64bit system.

```bash
go mod init main
go get -v tawesoft.co.uk/go/dialog
GOOS=windows GOARCH=amd64 go build -v -o vmprotected.exe -ldflags="-s -w -H windowsgui"
```

So it should compile successfully and see file `vmprotected.exe`

![2.png](/img/08/2.png)

Now move the compiled binary `vmprotected.exe` to a windows box that have [VMProtect Demo Version](https://vmpsoft.com/) that we will try to evade it.
![3.png](/img/08/3.png)

After pressing on **Add Function** we will check the **Compilation Type** and give it value **Ultra (Mutation + Virtualization)** by doing bunch of clicks against it.

![4.png](/img/08/4.png)

And then go to **Options** and give yes to all values, We are trying to make it as hard as possible to be evaded right there.
Then press the compile button above behind the exe name.

![5.png](/img/08/5.png)

It should compile and packed successfully with output name **vmprotected.vmp.exe**, If we tried to run the exe it will pops up an error message "Sorry, this application cannot run under a Virtual Machine."

![6.png](/img/08/6.png)

## Bypass VMProtect detection

Now the virtual machine should be up and running, If we tried to open `taskmanager` and navigating to **Performance** tab we should see it's a virtual machine.
![7.png](/img/08/7.png)

We need to get rid of that detection, We can do this by modifying the vm XML using `virsh` .
- Turnoff the virtual machine
- Then edit the virtual machine xml
```bash
virsh edit <YOUR_MACHINE_NAME>
```
- Find the following line

```xml
<cpu mode='host-passthrough' check='none' migratable='on'>
	<topology sockets='1' dies='1' cores='6' threads='1'/>
```
- Under the `topology` tag add the following line

```xml
<feature policy='disable' name='hypervisor'/>
```
- Now before the `</features>` tag add the following line

```xml
<kvm>
	<hidden state='on'/>
</kvm>
```

So it should look like this

![8.png](/img/08/8.png)

Now start the vm again and check the `taskmanager`, it should looks different now.
![9.png](/img/08/9.png)

If we tried to run the vmprotected binary **vmprotected.vmp.exe** it should run normally now.

![10.png](/img/08/10.png)

## Bypass the CPUID detections

Alright that was surprisingly easy, We need it more harder so i will try to run [Pafish](https://github.com/a0rtega/pafish) now which is a testing tool that uses different techniques to detect virtual machines and malware analysis environments in the same way that malware families do.
When it tries to detect sandbox environment it passed a lot of entries due to the specs we have already defined.
![11.png](/img/08/11.png)

Another detection that **Pafish** does is detecting the hypervisor vendor

![12.png](/img/08/12.png)

If we checked the code of **Pafish** we will find out that it's grabbing it from **CPUID**

![13.png](/img/08/13.png)

We can evade this by doing the following:
- Turnoff the virtual machine
- Edit the virtual machine xml using `virsh`

```bash
virsh edit <MACHINE_NAME>
```
- Before the tag `</hyperv>` add the following

```xml
<vendor_id state='on' value='ANYTHING YOU WANT'/>
```

It should looks like this

![14.png](/img/08/14.png)

If we checked again will see it know passed successfully but "Checking hypervisor bit in cpuid feature bits" is not yet.

![15.png](/img/08/15.png)

If we check the **Pafish** code will see it checks for the [CPUID bits](https://www.kernel.org/doc/html/v5.14/virt/kvm/cpuid.html#kvm-cpuid-bits "Permalink to this headline") which returns a constant signatures

```python
function: KVM_CPUID_SIGNATURE (0x40000000)

returns:

eax = 0x40000001
ebx = 0x4b4d564b
ecx = 0x564b4d56
edx = 0x4d
```

![16.png](/img/08/16.png)

So to bypass this do the following:
- Turnoff the virtual machine
- Edit the virtual machine xml using `virsh`

```bash
virsh edit <MACHINE_NAME>
```
- Add and edit the lines between `<cpu` tags to be look like the following

```xml
<cpu mode='host-model' check='partial'>
    <topology sockets='1' dies='1' cores='6' threads='1'/>
    <feature policy='disable' name='svm'/>
    <feature policy='disable' name='vmx'/>
    <feature policy='disable' name='hypervisor'/>
    <feature policy='disable' name='aes'/>
    <feature policy='disable' name='rdtscp'/>
</cpu>
```

So it should looks like this
![17.png](/img/08/17.png)

So now it should pass the CPUID bits detection
![18.png](/img/08/18.png)

Here if you noticed that "Checking the difference between CPU timestamp counters (rdtsc) forcing VM exit" is traced, Actually patching the RDTSC VM Exit on CPUID is pain in the butt which is requires recompiling the host kernel from source, you can try this patch called [BetterTiming](https://github.com/SamuelTulach/BetterTiming) yourself.

## QEMU detection bypass

At the QEMU it didn't pass the first detection `Scsi port->bus->target id->logical unit id-> 0 identifier` which is an exact registry key path the checks for "Identifier" value.
![19.png](/img/08/19.png)

So if we changed "Identifier" value to something else it will bypass this detection.
![20.png](/img/08/20.png)

Also if you saw this registry in `Scsi Bus 1` like below:
![38.png](/img/08/38.png)

Then try to remove any mounted CDROM from the Virtual Machine and after shutting down the VM and rerun it again the registry key should disappear.
![39.png](/img/08/39.png)

Now at Bochs detection it traced the registry path `HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System`  and check for the "SystemBiosVersion" Value.
![21.png](/img/08/21.png)

So if we changed "SystemBiosVersion" value to something else it will bypass this detection.
![22.png](/img/08/22.png)

Now most of the detection has been bypassed.
![23.png](/img/08/23.png)

## Patching WMI Entries

There's another tool [al-khaser](https://github.com/LordNoteworthy/al-khaser) which also detects the VM/Sandbox environments that checks for more evidence about the running environment.

Here most of the WMI queries has detected that it's running inside a VM, We will try to modify some of it as there's multiple WMI classes that I wasn't able to modify it.

![24.png](/img/08/24.png)

If we checked the **al-khaser** source code in the WMI section, we will see that it's doing some queries against WMI classes.

![25.png](/img/08/25.png)

To manipulate this I have wrote an MOF [Managed Object Format](https://learn.microsoft.com/en-us/windows/win32/wmisdk/managed-object-format--mof-) to modify some of this WMI variables.

```csharp
#pragma namespace ("\\\\.\\root\\CIMv2")
#PRAGMA AUTORECOVER

/* PS C:> get-wmiobject -class Win32_BIOS */
class Win32_BIOS
{
    [key] string SMBIOSBIOSVersion;
	string Manufacturer;
	string SerialNumber;
	string Name;
	uint16 BiosCharacteristics[];
	string Version;
};

[DYNPROPS]
instance of Win32_BIOS
{
    SMBIOSBIOSVersion = "6.0";
	Manufacturer = "Synergies Intelligent Systems";
	SerialNumber = "b3 5b 87 f1 2d 24 70 8c-b3 5b 87 f1 2d 24 70 8c";
	Name = "Synergies Intelligent Systems Inc.";
	BiosCharacteristics = {1,2,3};
	Version = "INTEL  - 6040001";
};

/* PS C:> get-wmiobject -class Win32_ComputerSystem */
class Win32_ComputerSystem
{
	[key] string Name;
	string Domain;
	string Manufacturer;
	string Model;
	string OEMStringArray[];
};

[DYNPROPS]
instance of Win32_ComputerSystem
{
    Name = "IE11WIN8_1";
	Domain = "WORKGROUP";
	Manufacturer = "Synergies";
	Model = "Synergies Intelligent Systems";
	OEMStringArray = {"Dave Network Corp"};
};

/* PS C:> Get-WmiObject -Query "SELECT * FROM Win32_DiskDrive" */
class Win32_DiskDrive {
    [key] string Model;
    string Caption;
};

[DYNPROPS]
instance of Win32_DiskDrive {
    Model = "Synergies SCSI Disk Device";
    Caption = "Synergies SCSI Disk Device";
};

/* PS C:> Get-WmiObject -Query "SELECT * FROM Win32_Fan" */
class Win32_Fan {
    [key] string Name;
    string   Description;
    string   DeviceID;
    string   SystemName;
};

[DYNPROPS]
instance of Win32_Fan {
    Name = "Dave Network";
    Description = "Synergies Cooling Systems Status";
    DeviceID = "F0-22-1D-4E";
    SystemName = "Synergies Intelligent Systems";
};

/* PS C:> Get-WmiObject -Query "SELECT * FROM Win32_CacheMemory" */
class Win32_CacheMemory {
    [key] string Name;
    string   Description;
    string   DeviceID;
    string   Status;
};

[DYNPROPS]
instance of Win32_CacheMemory {
    Name = "Dave Network";
    Description = "Synergies Caching";
    DeviceID = "F0-22-1D-4E";
    Status = "Memory Caching Enabled";
};

/* PS C:> Get-WmiObject -Query "SELECT * FROM Win32_MemoryDevice" */
class Win32_MemoryDevice {
    [key] string Name;
    string   Description;
    string   DeviceID;
    string   Status;
};

[DYNPROPS]
instance of Win32_MemoryDevice {
    Name = "Dave Network";
    Description = "Synergies Memory Device";
    DeviceID = "F0-22-1D-4E";
    Status = "OK";
};

/* PS C:> Get-WmiObject -Query "SELECT * FROM Win32_VoltageProbe" */
class Win32_VoltageProbe {
    [key] string Name;
    string Description;
    string   DeviceID;
    string   Status;
};

[DYNPROPS]
instance of Win32_VoltageProbe {
    Name = "Dave Network";
    Description = "Synergies electronic voltmeter";
    DeviceID = "F0-22-1D-4E";
    Status = "OK";
};

/* PS C:> Get-WmiObject -Query "SELECT * FROM Win32_PortConnector" */
class Win32_PortConnector {
    [key] string Name;
    string Manufacturer;
    string Model;
};

[DYNPROPS]
instance of Win32_PortConnector {
    Name = "Dave Network";
    Manufacturer = "Synergies physical connection ports";
    Model = "Centronics";
};
```

Save it to a file with `.mof` extension and run it with mof compiler `mofcomp.exe`

```bash
mofcomp.exe wmi_hide.mof
```

It evaded most of it but still the WMI CIM ones as I didn't find a proper way to modify them.
![26.png](/img/08/26.png)

## Uninstall QEMU VirtIO driver (If installed)

When we running **al-khaser** in the **QEMU Detection** Section we will see its checking for some registry keys, files and processes.
![27.png](/img/08/27.png)

So we will need to uninstall the **QEMU Guest Agent** and its services.

Reattach the [VirtIO](https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.229-1/) ISO image from Virt-Manager
![28.png](/img/08/28.png)

Then restart the machine and open virtio-win mounted drive.
![29.png](/img/08/29.png)

Also check mark on "Remove all customized settings" and then click "Remove" and restart the machine to take effect.
Now will stop all QEMU Agent Services, Press WinKey + R and run `services.msc` and stop **QEMU Guest Agent** service and **QEMU Guest Agent VSS Provider**.
![30.png](/img/08/30.png)

After that open windows cmd with Admin Privileges, and go to `C:\Program Files\Qemu-ga` and run these two commands.
```powershell
.\qemu-ga.exe -s uninstall
.\qemu-ga.exe -s vss-uninstall
```
So the services should be removed completely. Unmount the disk driver and remove the Qemu-ga path.

Also remove "Spice Agent" Service and then delete its path at `C:\Program Files\Spice Agent` recursively. 

```powershell
sc delete spice-agent
```

## Firmware Table Changes

After the previous changes the QEMU changes passed except two other checks.
![31.png](/img/08/31.png)

Those check are actually checking some strings in the firmware tables of **SMBIOS** and **ACPI** like QEMU , BOCHS , BXPC as we see in the source code.
![32.png](/img/08/32.png)

If we used [FirmwareTablesView](https://www.nirsoft.net/utils/firmware_tables_view.html) in the Firmware Provider column we will see it more obviously.
![33.png](/img/08/33.png)

We can overwrite most of these strings by editing some elements to the XML of the machine by running `virsh edit <MACHINE_NAME>`, under `<os>` element add `<smbios mode='sysinfo'/>` , Then add the following elements under `<vcpu>` tag.

```xml
  <sysinfo type='smbios'>
    <bios>
      <entry name='vendor'>Dell Inc.</entry>
      <entry name='version'>2.5.2</entry>
      <entry name='date'>01/28/2015</entry>
      <entry name='release'>2.5</entry>
    </bios>
    <system>
      <entry name='manufacturer'>Dell Inc.</entry>
      <entry name='product'>PowerEdge R720</entry>
      <entry name='version'>Not Specified</entry>
      <entry name='serial'>H5DR542</entry>
      <entry name='uuid'>SHOULD MATCH THE UUID OF THE DOMAIN .. CHECK THE ELEMENT uuid ABOVE</entry>
      <entry name='sku'>SKU=NotProvided;ModelName=PowerEdge R720</entry>
      <entry name='family'>Not Specified</entry>
    </system>
    <baseBoard>
      <entry name='manufacturer'>Dell Inc.</entry>
      <entry name='product'>12NR12</entry>
      <entry name='version'>A02</entry>
      <entry name='serial'>.5KT0B123.ABCDE000000001.</entry>
      <entry name='asset'>Not Specified</entry>
      <entry name='location'>Null Location</entry>
    </baseBoard>
    <chassis>
      <entry name='manufacturer'>Lenovo</entry>
      <entry name='version'>none</entry>
      <entry name='serial'>J30038ZR</entry>
      <entry name='asset'>none</entry>
      <entry name='sku'>Default string</entry>
    </chassis>
    <oemStrings>
      <entry>myappname:some arbitrary data</entry>
      <entry>otherappname:more arbitrary data</entry>
    </oemStrings>
  </sysinfo>
```

Surely you can modify all these strings between the `<entry>` elements, Then poweroff the machine and poweron again and check the FirmwareTablesView.
![34.png](/img/08/34.png)

The changes has its effects but still some strings related to the QEMU, I actually tried alot of steps to change it non of them worked until now. However we will move to the next step.

## Manipulating the registry keys

In the beginning of this post I have showed an example of modifying the registry key `HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\SystemBiosVersion` so now we will proceed modifying it.

In **al-khaser** program uses multiple of registry keys to detect the VM environment, We will try to modify all of them to evade the VM detection.

So in this registry key `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\SCSI` there's a lot of keys that contains strings like `Red_Hat` and `QEMU`, So we should modify all of these strings.

So here **al-khaser** checking for multiple registry key values in `registry_disk_enum` function.
![35.png](/img/08/35.png)

So in the path `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\SCSI` we see most of registry key values contains "QEMU" string.
![36.png](/img/08/36.png)

So every key that contains value "QEMU" and "VirtIO" should be replaced by any other strings which is easy to do.
![37.png](/img/08/37.png)

The problem here is you have to change registry subkey that contains same strings but you will face a permission issue, As the program checks all keys and subkeys in the registry path looking for the strings mentioned earlier.

> I will stop right there until doing more researches about more VM detection evasion. Will add more techniques later if possible.

