---
layout: post
title: Active Directory Local Lab Environment Setup
date: 2020-05-04
image: 05/00-main.jpg
tags: redteam activedirectory
---

## Introduction
In this blog post i'm going to setup a windows server on my local machine which is vulnerable for different types of windows attacks.
The main reason for this is to practice some sort of things like setting up an Active Directory environment, Active Directory attacks, Windows privilege escalation techniques, Common misconfigurations and more.
Here i will NOT explain too much about how to do an enumeration or attacking, I will just focus on building this local server for practicing in the future, there is a **lot** of tutorials down there about active directory attacks and techniques so you can go read them and practice on the local virtual machine server we will going to create so you will be able to work with your own hand.

## Host System Requirements
Don't panic we will not going insane here, The machine we are going to make will be straight forward with only one domain forest and only one active directory, just one virtual machine, and you can develop it later and make it much more bigger.

**Host Minimum System Requirements:**
- 6 GB of RAM
- Core i5 CPU
- A good graphic card "*not heavily required but recommended*"

We are not going to use too much space to the hard disk.

**Local Virtual Server Requirements:**
- Virtual Box
- Windows Server 2008
- CPU Cores : 2
- Memory Size : 2048 MB
- File Size : 50 GB

Why using windows server 2008?, I'm using windows server 2008 instead of windows server 2016 because there is a lot of attacking techniques mitigated in windows server 2016 that you gonna miss, Always start with weakest part and go up for higher levels.

Here it is, my final Virtual Box configurations


![01-vm](/img/05/01-vm.png)

Now let us start installing our local server.

## Initial Installing
It's like an ordinary windows installing, so you can go with the *Next Next Install* thing.
And here it is, A fresh install of Windows Server 2008.


![02-fresh-install.png](/img/05/02-fresh-install.png)

## Installing Active Directory

Now lets start with installing Active Directory role, so we going to set this server as a **Domain Controller** so it's recommended to give the domain controller a static IP Adress, and then we will proceed to active directory installing.

1. Start **Server Manager** and click **View Network Connections** button.


![03-server-manager.png](/img/05/03-server-manager.png)

2. Give the Server A static IP Address, Default Gateway
>	- Notice that we typed at the **Preferred DNS Server** your localhost address, because we gonna set a DNS Server to this server, and used **1.1.1.1** DNS of cloudflare as an Alternative DNS Server, You can use Google DNS if you want.

![04-static-ip.png](/img/05/04-static-ip.png)


 3. Go to **Server Manager** at **Roles** tab and click **Add Roles**

![05-server-role.png](/img/05/05-server-role.png)

After Next, Next, Install the installation will begin.

![06-installation-progress.png](/img/05/06-installation-progress.png)

And now the Active Directory Role installed successfully, and reboot the server.

![07-installation-result.png](/img/05/07-installation-result.png)

Pay Attention to this message below, this is because the server is not joined a domain yet, We will set the domain controller from there.

![08-dcpromo.png](/img/05/08-dcpromo.png)

4. We will create a new domain in a new forest so you have to choose this.

![09-new-forest.png](/img/05/09-new-forest.png)

And type the **FQDN** "Fully Qualified Domain Name", The domain name should not look like a real online domain which might interfere with domain controller name, so it's not recommended to use something that have *.com*, *.net* or something similar, I will call it **MEGACORP.LOCAL** as a FQDN for the server.

![10-FQDN.png](/img/05/10-FQDN.png)

Go with the default installation settings.

![11-dns-server.png](/img/05/11-dns-server.png)

While Setting the DNS server you will see a pop-up window that will tell you something about dns server delegation, Ignore that and hit yes.

![12-shared-folders.png](/img/05/12-shared-folders.png)

You will see some shared folders, we will go through this while configuring our vulnerable server.

Now continue with your installation until it finish, then reboot the server.

## Adding Domain Users

After installing the AD server we need to add a various domain users to the active directory Organizational Unit "**OU**" which is like a container that holds Users, Groups and Computer that joined the domain.

So we will navigate to **Active Directory Users and Computers** and create a new Organizational Unit, I will call it *People*

![13-OU.png](/img/05/13-OU.png)

And adding some users to the OU.

![14-new-user.png](/img/05/14-new-user.png)

I will add many users to the domain with a different options to the one user, my naming convention here will be the characters in the *rick and morty* movie, yeah why not xD.

![15-rick.png](/img/05/15-rick.png)

The set the password for the user, I will make his password is : **03frisco07degu?**
Notice that i choosed this password from *rockyou.txt* wordlist so we can crack his password easily while attacking the server.

![16-user-pass.png](/img/05/16-user-pass.png)

Now the user *rick* created successfully, I will add many users to the OU with the same way.


### Lets Recap

So my Users and their passwords are the following:

|rick   |morty   |summer   |jerry   |beth   |
|---|---|---|---|---|
|03frisco07degu?   |fr6B@fu4bCMV5D#xu*7   |Amy@girl987   |sleepygary<3   |(lovemy3kids)   |
|from rockyou.txt   |   |from rockyou.txt   |   |from rockyou.txt   |

I have choosed some passwords from rockyou.txt to be useful in our attacking later.

## Configuring The Server

Now what we are going to do is configure each user for a specific attack method so lets begin.

> ## Enabling Windows Remote Management "WinRM"

Windows Remote Management is a command-line tool which is used for server management via remote shell.
In our perspective, WinRM is useful in our attacks which we could login to a some domain-joined user via remote shell.

Before going for WinRM enabling process I'll create a group for **Remote Management** users which will have authorization for PS Remoting.

Like we did before with **People** OU we will create a new organizational unit called **MegaGroups**.

![17-new-OU.png](/img/05/17-new-OU.png)

And creating a new group inside **MegaGroups** OU.

![18-new-group.png](/img/05/18-new-group.png)

Then will call it **Remote Management**.

![19-remote-management.png](/img/05/19-remote-management.png)

And I will add *rick* and *morty* users to **Remote Management** Group.

![20-add-users.png](/img/05/20-add-users.png)

And the same with *morty* user.

Now lets enable WinRM by navigating to **Group Policy Management** and creating a GPO to the domain.


![21-GPO.png](/img/05/21-GPO.png)

And I'll call it *Enable WinRM*

![22-new-GPO.png](/img/05/22-new-GPO.png)

After the GPO has been created, we will edit it.

![23-edit-GPO.png](/img/05/23-edit-GPO.png)

Now we need to expand and navigate to the following:

> *Computer Configuration > Policies > Administrative Templates > Windows Components > Windows Remote Management (WinRM) > WinRM Service*

And then edit the **Allow automatic configuration of listeners**

![24-GPO-editor.png](/img/05/24-GPO-editor.png)

Select *Enabled* radio button and assign an asterisk to **IPv4 filter** and **IPv6 filter** to allow messages from any IP address and hit OK.

![25-enable-winrm.png](/img/05/25-enable-winrm.png)

Then we need to make WinRM starts with the system, In the **Group Policy Management Editor** expand and navigate to:

> *Computer Configuration > Preferences > Control Panel Settings > Services*


![26-new-service.png](/img/05/26-new-service.png)

And make WinRM service start automatically.

![27-winrm-service.png](/img/05/27-winrm-service.png)

Now update the group policy object.

![28-gpupdate.png](/img/05/28-gpupdate.png)


![29-updating-policy.png](/img/05/29-updating-policy.png)


After updating the group policy the WinRM is enabled now, The server’s firewall will automatically be configured to allow the relevant traffic in.

You have to notice that not all the users could use it, so we will allow a specific users to use the Windows remote managment by opening the Powershell console and running this command.
```
Set-PSSessionConfiguration -Name Microsoft.Powershell -ShowSecurityDescriptorUI -Force
```
And add the group we created earlier on our OU.

![30-add-group.png](/img/05/30-add-group.png)

> *Notice : Make sure that you Allow **Full Control***

Then click Apply and OK, This should have enabled the WinRM for our two users.

You can check the WinRM running service by run:
```
winrm e winrm/config/listener
```
And also you can connect one of these users with [Evil-Winrm](https://github.com/Hackplayers/evil-winrm) from linux with the credentials you have set earlier.

![31-evil-winrm.png](/img/05/31-evil-winrm.png)

> ## LDAP Anonymous Authentication

When it came to Active Directory server, LDAP shows.

[LDAP](https://docs.microsoft.com/en-us/previous-versions/windows/desktop/ldap/lightweight-directory-access-protocol-ldap-api) or **Lightweight Directory Access Protocol** is a service protocol which is like a way of speaking to Active Directory with LDAP Queries in a nutshell.

It's very important to know about LDAP in depth, and how you enumerate it, so what we are gonna do here is to make **Anonymous Authentication** to LDAP without providing any credentials.

This will make LDAP enumeration easier, and LDAP Anonymous Access is very common in the wild too.

So let us enable it by opening **ADSI Edit** and right-click to choose *Connect to...*

![32-ADSI.png](/img/05/32-ADSI.png)

As image above in **Select a Well known Naming Context** Select **Configuration** then press OK.

Now expand those trees like below until reach to **Directory Service** and click **Properties**.

![33-directory-service.png](/img/05/33-directory-service.png)

Here in **dSHeuristics** attribute, change its value to `0000002` due to enable Anonymous authentication to LDAP.

![34-dSHeuristics.png](/img/05/34-dSHeuristics.png)

After clicking OK, You will be able to authenticate to LDAP anonymously, You will notice diffrences while enumerating LDAP with tools like *ldapsearch* and *nmap NSEs* like *ldap-search.nse*.


> ## Storing Password In The User Description

A thing you might see commonly while doing a real life pentesting, Is that the sys admins might store user password in his description like down below.

![35-password-description.png](/img/05/35-password-description.png)

Which can any user see his password in the description and login to this user.

![36-net-users.png](/img/05/36-net-users.png)

![37-meme1.jpg](/img/05/37-meme1.jpg)

> ## Group Policy Preferences Abusing

[Group Policy Preferences](https://en.wikipedia.org/wiki/Group_Policy#Group_Policy_preferences) or **GPP** released with windows Server 2008, Windows 7, Windows Server 2008 R2.

What is intersting about the GPP is its XML files that stored in *SYSVOL* shared folder, So it's very important to check for the *SYSVOL* folder in SMB during the AD Domain.

Any group policy file that need to use a local or domain password stores the password in one of those XML files encrypted with **AES256** encryption algorithm, The thing here is that Microsoft put the decryption key online on the Microsoft docs [Here](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-gppref/2c15cbf0-f086-4c74-8b70-1f2fa45dd4be?redirectedfrom=MSDN) which makes it so easy to decrypt the GPP Passwords no matter how powerful the password is.


`4e 99 06 e8  fc b6 6c c9  fa f4 93 10  62 0f fe e8`

`f4 96 e8 06  cc 05 79 90  20 9b 09 a4  33 b6 6c 1b`

![38-meme2.png](/img/05/38-meme2.png)

So to generate this will navigate to **Group Policy Management** and edit the **Default Domain Policy** Object.

![39-default-domain-policy.png](/img/05/39-default-domain-policy.png)

Here I will add a domain user to the **Local Users and Groups**, I will choose *morty* user to new local user.

![40-new-localuser.png](/img/05/40-new-localuser.png)

I have created it with his user account password `fr6B@fu4bCMV5D#xu*7` this will be decrypted easily with the  key the Microsoft provided to us.

After clicking OK, the password we have set will be store in a XML file inside *SYSVOL*, we can see this by navigating to `C:\Windows\SYSVOL\sysvol\<DOMAIN>\Policies` and search for the XML files.

![41-sysvol.png](/img/05/41-sysvol.png)

As we can see, the encrypted base64 password exist in `cpassword`, A lot of tools could help you to decrypt it.


> ## KRB_AS_REP Roasting "Kerberos Pre-Authentication" 

[Kerberos](https://en.hackndo.com/kerberos/) in a nutshell is:

- A protocol for authentication
- Uses tickets to authenticate which is served by KDC
- Avoids storing passwords locally or sending them over the internet
- Involves a trusted 3rd-party
- Built on symmetric-key cryptography

And I highly recommend to read about it in depth due to understand how Kerberos protocol is working.

What we are going to do is configuring *rick* user for **not requring kerberos preauthentication** which will allow us to perform a **Kerberos Pre-Authentication** attack against the server.

![42-kerb-as-rep.png](/img/05/42-kerb-as-rep.png)

So we will be able to grab his **Kerberos AS-REP** ticket hash and cracking it.

> ## Kerberoasting

The Kerberoasting attack is about requesting Kerberos service tickets **TGS** from authentication server, which any valid domain user can grab the **TGS** from a service account as a hash that we can crack it.

> *There is alot of good articles and blog posts about kerberoasting attack that you should go check on.*

At first we will use *summer* domain user as a service account, It doesn't have to be a part for real service so for the sake of this post we will create it for a fake service that doesn't exist.

So to do this we need to open **ADUC** window and go to domain user *summer* and navigate to Properties to change the **Attributes**, But in Server 2008 the **Attribute Editor** tab doesn't exist in the user Properties while we in **ADUC**, But if we go to user Properties from **Active Directory Administrative Center** we will see **Attribute Editor** tab in user Properties which exactly what we want, Yeah it's Microsoft ¯\\\_( ͡• ͜ʖ ͡•)_/¯

![43-ADAC.png](/img/05/43-ADAC.png)

After opening properties and navigate to **Attribute Editor** we will have to edit **servicePrincipalName** attribute and give it a fake **SPN** for something like **ACTIVE/CIFS**, click Add then OK.

![44-SPN.png](/img/05/44-SPN.png)


> ## DCSync Attack

**DCsync** attack impersonates the default behavior of the Domain Controller which you can request anything from the Domain Controller including passwords, This kind of attack has its limits but very powerfull to own the entire domain.

From attacking perspective, the DCsync attack in a nutshell:

- Allow the attacker to impersonate the Domain Controller and request password hashes from the domain.
- Only accounts that have certain replication permissions with Active Directory can be targeted and used in DCSync attack.
- When you detect a possibility to perform a DCSync attack, You can grap the **LM:NTLM** hashes of the domain admin, and you can try to crack those hashes or performing a PTH or **Pass The Hash** technique to log into Administrator account.
- This attack can be performed with Impacket scripts or Mimikatz depends on you case scenario.

> *I highly recommended to go understand how DCSync work in depth*

Lets start configuring our server to be able to perform a DCSync attack.

We will give the user *beth* a permission to allow **Replicating Directory Changes**, By opening the **Active Directory Administrative Center** and open the domain properties.

![45-domain-properties.png](/img/05/45-domain-properties.png)

If we scroll down to Extensions and hitting **Advanced** in **Security** tab, We will see the **Replicating Directory Changes** permissions for the Domain Controllers, Administrators.

![46-domain-security.png](/img/05/46-domain-security.png)

What we going to do here is giving of the domain users *beth* this permissions by pressing **Add** and type the domain username.

![47-add-user.png](/img/05/47-add-user.png)

After hitting OK, You now allow the **Replicating Directory Changes** and **Replicating Directory Changes All** permissions.

![48-permissions.png](/img/05/48-permissions.png)

Then you will see now that *beth* user has the **Replicating Directory Changes** permissions.

![49-user-rdc.png](/img/05/49-user-rdc.png)

So if you enumerate this account with **BloodHound** or similar tool you might see that you can do DCSync attack from this account.

## Lets Recap

The main structure of our server now looks like this:

![50-infrastructure.jpg](/img/05/50-infrastructure.jpg)

Sure you can do this more way better than this, I'll leave that you to play with it.

The Server VM we have created here *VDI* file will be uploaded.
