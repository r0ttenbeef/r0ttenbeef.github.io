---
layout: post
title: Bypass Microsoft Intune URL Blocking Browser's Policy
date: 2025-09-17
image: 15/00-main.png
tags:
  - Bypass
  - activedirectory
---
Today's article is about bypassing the domains blocked on browsers by using Microsoft Intune policies, Which is a cloud-based service that provides **Mobile Device Management (MDM)** and **Mobile Application Management (MAM)** which helps organizations manage and controls the employee's devices (Like smartphones, laptops and tablets) and applications.

---

## Introduction: Understanding Intune MDM Domain Blocking

Microsoft Intune blocks domains on the browser level via **Device configuration policies**. In this case, We will try to bypass domain blocking in chrome and edge browsers.
If we checked edge browser, We could see the applied policies by going to [edge://policy](edge://policy) and you will find all policies including the policy responsible for domain blocking. ![1.jpeg](/img/15/1.jpeg)

Same case for chrome [chrome://policy](chrome://policy) you will see the same policy. ![2.jpeg](/img/15/2.jpeg)

## Discovery: Identifying the Registry Keys Controlling Domain Access

After doing some researches, I found that these domain values of the policy itself are stored in registry keys in different paths depends on the browser itself.
- Chrome: **HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Policies\Google\Chrome\URLBlocklist**
- Edge: **HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Policies\Microsoft\Edge\URLBlocklist**
![3.jpeg](/img/15/3.jpeg)

## Experiment: Testing Domain Access Before any Modifications

If you managed to try access one of already blocked domain on Edge (chatgpt.com as an example), It will show browser error "**chatgpt.com is blocked. Your organization doesn't allow you to view this site.**" ![4.jpeg](/img/15/4.jpeg)

Similar case for Chrome it will shows "**chatgpt.com is blocked. Your organization doesn't allow you to view this site.**" ![5.jpeg](/img/15/5.jpeg)

## Manipulation: Editing Registry Keys to Bypass Restrictions

Until we have access to registry key via "regedit" and have the permission of modifying registry keys, We can bypass domain blocking restrictions by manipulating the mentioned registry keys above to be able to access the blocked domains.
For example, We will try to go low-profile and edit the only registry key the holds our domain that we want to access, Like chatgpt.com in our case. ![6.jpeg](/img/15/6.jpeg)

So what we are going to do is to replace the value of this highlighted registry key in the screenshot above to something else, I replaced the domain with "-" and that's it. ![7.jpeg](/img/15/7.jpeg)

After that open [edge://policy](edge://policy) and reload the policies from "Reload Policies" button. ![8.jpeg](/img/15/8.jpeg)

Now if we tried to access the blocked domain which is chatgpt.com it will open without any problem. ![9.jpeg](/img/15/9.jpeg)

## Detection: Identify Registry-Based Bypasses of Intune Domain Restrictions

The issue here that if we tried to search for the modified registry key path in **Microsoft Defender for Endpoint** It would not appear in the device's timeline logs. ![10.jpeg](/img/15/10.jpeg)

I have reported this to Microsoft Support and they said that Microsoft Defender not monitoring all registry keys states, Just monitoring the critical registry keys modifications.
Another thing that might be quite useful is to monitor the executed process itself, Which is "regedit.exe" but even with these logs it will not tell you the exact modified registry key. But it might be something like an indicator there's something odd is happening and needs to be investigated. ![11.jpeg](/img/15/11.jpeg)

## Prevention: Strengthening Intune Policies Against Registry-Based Bypasses

To prevent registry key manipulation completely, You can reach that by creating a policy that prevents running any tools like **regedit.exe**, **reg.exe** by using of Intune MDM.
1. Create a group and add the devices you want to prevent them from modifying registry keys. ![12.jpeg](/img/15/12.jpeg)
2. Create a policy in intune **Devices -> Configuration -> Create -> New policy**.
	1. Select platform: **Windows 10 or later**
	2. Profile type: **Settings Catalog**
3. Give the policy the preferred name and click on next. ![13.jpeg](/img/15/13.jpeg)
4. On **Configuration Settings**, Hit **Add settings** and it will open side windows with search bar, Try to search "Registry Editing" and it will shows in **Administrative Templates\System**. When you check the template you will find the settings we want **Prevent access to registry editing tools** Select it. ![14.jpeg](/img/15/14.jpeg)
5. After that enable the **Disable regedit from running silently** and **Prevent access to registry editing tools** and hit next. ![15.jpeg](/img/15/15.jpeg)
6. Leave **Scope tags** as Default.
7. Assign the group we added earlier by clicking on **Add groups** tab, Check on the group and click on **Select**. ![16.jpeg](/img/15/16.jpeg)
8. Review your settings and create the policy.

After applying the policy, We will try to run **regedit** or **reg.exe** and will see that an error is showing up with message: **Registry editing has been disabled by your administrator** which is what we want. ![17.jpeg](/img/15/17.jpeg)