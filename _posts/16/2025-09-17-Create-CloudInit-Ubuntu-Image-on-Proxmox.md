---
layout: post
title: Create CloudInit Ubuntu Image on Proxmox
date: 2025-09-17
image: 16/00-main.jpg
tags:
  - Automation
  - linux
---
If you want to build a reusable Ubuntu template for your Proxmox environment, here’s a step-by-step guide with example screenshots.

My Configurations:
- Storage name: **SATA-Drive-1TB**
- Network Interface: **opfw_lan1**

---
### 1. Download the Ubuntu Cloud Image

* Go to [https://cloud-images.ubuntu.com/](https://cloud-images.ubuntu.com/) and choose the appropriate image for your use case (e.g., **ubuntu-noble-server-cloudimg-amd64.img**). ![Download Ubuntu cloud image](/img/16/1.png)

* In **Proxmox GUI**:
  * Navigate to **SATA-Drive-1TB → ISO Images → Download from URL**.
  * Paste the URL of the selected cloud image and download it.
![Proxmox ISO Images tab with “Download from URL” dialog open](/img/16/2.png)

---
### 2. Create a VM for the Template

1. **Proxmox GUI → Create VM**
2. **General:** Set **VM ID** (recommended: above 1000).
3. **OS:** Select **Do not use any media**.
4. **System:**
   * **Machine:** q35
   * **Qemu Agent:** ✔️
   * **BIOS:** OVMF (UEFI)
   * **Add EFI Disk:** ✔️
   * **EFI Storage:** SATA-Drive-1TB
   * **Format:** QEMU image format (qcow2)
   * **Pre-Enroll keys:** ✔️
5. **Disks:** Remove **scsi0** disk.
6. **CPU:** Leave default.
7. **Memory:** Set to **1024 MB**.
8. **Network:** Set **Bridge** to `opfw_lan1`.
9. **Create VM**.

![Proxmox “Create VM” wizard – System tab with q35, OVMF, and Qemu Agent selected](/img/16/3.png)

---
### 3. Remove CD/DVD Drive

* Go to **VM → Hardware** and remove the **CD/DVD Drive**.

---
### 4. Add Cloud-Init Drive

* Go to **Hardware → Add → CloudInit Drive**
* **Storage:** SATA-Drive-1TB → **Add**
![CloudInit drive added under VM hardware](/img/16/3.png)

---
### 5. Add Serial Port (optional)

* Go to **Hardware → Add → Serial Port**
* Select **0** → **Add**

---
### 6. Import Disk via Proxmox CLI

Run this command in your Proxmox shell:

```bash
qm disk import 1000 /mnt/pve/SATA-Drive-1TB/template/iso/ubuntu-noble-server-cloudimg-amd64.img SATA-Drive-1TB --format qcow2
```

---
### 7. Attach Imported Disk

```bash
qm set 1000 --scsihw virtio-scsi-pci --scsi0 SATA-Drive-1TB:1000/vm-1000-disk-1.qcow2
```

---
### 8. Configure VM and Convert to Template

* **Options → Boot Order:** Set **scsi0** as first boot device and disable **net0**.
* Right-click on VM → **Convert to Template** → Confirm.

> 💡 **Screenshot Example:** *Proxmox options tab with scsi0 set as boot order and VM context menu showing “Convert to Template”.*

---

You can now use this template with your configuration from cloud-init without need to re-install ubuntu server each time.