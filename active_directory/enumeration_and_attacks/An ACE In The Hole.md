# Access Control List (ACL) Abuse Primer

---

For security reasons, not all users and computers in an AD environment can access all objects and files. These types of permissions are controlled through Access Control Lists (ACLs). Posing a serious threat to the security posture of the domain, a slight misconfiguration to an ACL can leak permissions to other objects that do not need it.

---

## Access Control List (ACL) Overview

In their simplest form, ACLs are lists that define a) who has access to which asset/resource and b) the level of access they are provisioned. The settings themselves in an ACL are called `Access Control Entries` (`ACEs`). Each ACE maps back to a user, group, or process (also known as security principals) and defines the rights granted to that principal. Every object has an ACL, but can have multiple ACEs because multiple security principals can access objects in AD. ACLs can also be used for auditing access within AD.

There are two types of ACLs:

1. `Discretionary Access Control List` (`DACL`) - defines which security principals are granted or denied access to an object. DACLs are made up of ACEs that either allow or deny access. When someone attempts to access an object, the system will check the DACL for the level of access that is permitted. If a DACL does not exist for an object, all who attempt to access the object are granted full rights. If a DACL exists, but does not have any ACE entries specifying specific security settings, the system will deny access to all users, groups, or processes attempting to access it.
2. `System Access Control Lists` (`SACL`) - allow administrators to log access attempts made to secured objects.

We see the ACL for the user account `forend` in the image below. Each item under `Permission entries` makes up the `DACL` for the user account, while the individual entries (such as `Full Control` or `Change Password`) are ACE entries showing rights granted over this user object to various users and groups.

#### Viewing forend's ACL

![Active Directory Users and Computers window showing Advanced Security Settings for 'forend' with permission entries for various principals, including 'Authenticated Users' and 'Angela Dunn'.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/DACL_example.png)

The SACLs can be seen within the `Auditing` tab.

#### Viewing the SACLs through the Auditing Tab

![Active Directory Users and Computers window showing Advanced Security Settings for 'forend' with auditing entries for 'Everyone' on descendant organizational units.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/SACL_example.png)

---

## Access Control Entries (ACEs)

As stated previously, Access Control Lists (ACLs) contain ACE entries that name a user or group and the level of access they have over a given securable object. There are `three` main types of ACEs that can be applied to all securable objects in AD:

|**ACE**|**Description**|
|---|---|
|`Access denied ACE`|Used within a DACL to show that a user or group is explicitly denied access to an object|
|`Access allowed ACE`|Used within a DACL to show that a user or group is explicitly granted access to an object|
|`System audit ACE`|Used within a SACL to generate audit logs when a user or group attempts to access an object. It records whether access was granted or not and what type of access occurred|

Each ACE is made up of the following `four` components:

1. The security identifier (SID) of the user/group that has access to the object (or principal name graphically)
2. A flag denoting the type of ACE (access denied, allowed, or system audit ACE)
3. A set of flags that specify whether or not child containers/objects can inherit the given ACE entry from the primary or parent object
4. An [access mask](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/7a53f60e-e730-4dfe-bbe9-b21b62eb790b?redirectedfrom=MSDN) which is a 32-bit value that defines the rights granted to an object

We can view this graphically in `Active Directory Users and Computers` (`ADUC`). In the example image below, we can see the following for the ACE entry for the user `forend`:

#### Viewing Permissions through Active Directory Users & Computers

![Active Directory Users and Computers window showing permission entry for Angela Dunn with various permissions like 'Read all properties' and 'Write all properties' for this object and all descendant objects.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/ACE_example.png)

1. The security principal is Angela Dunn ([adunn@inlanefreight.local](mailto:adunn@inlanefreight.local))
2. The ACE type is `Allow`
3. Inheritance applies to the "This object and all descendant objects,” meaning any child objects of the `forend` object would have the same permissions granted
4. The rights granted to the object, again shown graphically in this example

When access control lists are checked to determine permissions, they are checked from top to bottom until an access denied is found in the list.

---

## Why are ACEs Important?

Attackers utilize ACE entries to either further access or establish persistence. These can be great for us as penetration testers as many organizations are unaware of the ACEs applied to each object or the impact that these can have if applied incorrectly. They cannot be detected by vulnerability scanning tools, and often go unchecked for many years, especially in large and complex environments. During an assessment where the client has taken care of all of the "low hanging fruit" AD flaws/misconfigurations, ACL abuse can be a great way for us to move laterally/vertically and even achieve full domain compromise. Some example Active Directory object security permissions are as follows. These can be enumerated (and visualized) using a tool such as BloodHound, and are all abusable with PowerView, among other tools:

- `ForceChangePassword` abused with `Set-DomainUserPassword`
- `Add Members` abused with `Add-DomainGroupMember`
- `GenericAll` abused with `Set-DomainUserPassword` or `Add-DomainGroupMember`
- `GenericWrite` abused with `Set-DomainObject`
- `WriteOwner` abused with `Set-DomainObjectOwner`
- `WriteDACL` abused with `Add-DomainObjectACL`
- `AllExtendedRights` abused with `Set-DomainUserPassword` or `Add-DomainGroupMember`
- `AddSelf` abused with `Add-DomainGroupMember`

In this module, we will cover enumerating and leveraging four specific ACEs to highlight the power of ACL attacks:

- [ForceChangePassword](https://bloodhound.specterops.io/resources/edges/force-change-password#forcechangepassword) - gives us the right to reset a user's password without first knowing their password (should be used cautiously and typically best to consult our client before resetting passwords).
- [GenericWrite](https://bloodhound.specterops.io/resources/edges/generic-write#genericwrite) - gives us the right to write to any non-protected attribute on an object. If we have this access over a user, we could assign them an SPN and perform a Kerberoasting attack (which relies on the target account having a weak password set). Over a group means we could add ourselves or another security principal to a given group. Finally, if we have this access over a computer object, we could perform a resource-based constrained delegation attack which is outside the scope of this module.
- [AddSelf](https://bloodhound.specterops.io/resources/edges/add-self#addself) - shows security groups that a user can add themselves to.
- [GenericAll](https://bloodhound.specterops.io/resources/edges/generic-all#genericall) - this grants us full control over a target object. Again, depending on if this is granted over a user or group, we could modify group membership, force change a password, or perform a targeted Kerberoasting attack. If we have this access over a computer object and the [Local Administrator Password Solution (LAPS)](https://www.microsoft.com/en-us/download/details.aspx?id=46899) is in use in the environment, we can read the LAPS password and gain local admin access to the machine which may aid us in lateral movement or privilege escalation in the domain if we can obtain privileged controls or gain some sort of privileged access.

This graphic, adapted from a graphic created by [Charlie Bromberg (Shutdown)](https://twitter.com/_nwodtuhs), shows an excellent breakdown of the varying possible ACE attacks and the tools to perform these attacks from both Windows and Linux (if applicable). In the following few sections, we will mainly cover enumerating and performing these attacks from a Windows attack host with mentions of how these attacks could be performed from Linux. A later module specifically on ACL Attacks will go much further in-depth on each of the attacks listed in this graphic and how to perform them from Windows and Linux.

![Flowchart showing WriteDacl and WriteOwner permissions with associated actions like Grant Rights, GenericWrite, and AddMember, including Linux and Windows tools for each action.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/ACL_attacks_graphic.png)

We will run into many other interesting ACEs (privileges) in Active Directory from time to time. The methodology for enumerating possible ACL attacks using tools such as BloodHound and PowerView and even built-in AD management tools should be adaptable enough to assist us whenever we encounter new privileges in the wild that we may not yet be familiar with. For example, we may import data into BloodHound and see that a user we have control over (or can potentially take over) has the rights to read the password for a Group Managed Service Account (gMSA) through the [ReadGMSAPassword](https://bloodhound.specterops.io/resources/edges/read-gmsa-password) edge. In this case, there are tools such as [GMSAPasswordReader](https://github.com/rvazarkar/GMSAPasswordReader) that we could use, along with other methods, to obtain the password for the service account in question. Other times we may come across extended rights such as [Unexpire-Password](https://learn.microsoft.com/en-us/windows/win32/adschema/r-unexpire-password) or [Reanimate-Tombstones](https://learn.microsoft.com/en-us/windows/win32/adschema/r-reanimate-tombstones) using PowerView and have to do a bit of research to figure out how to exploit these for our benefit. It's worth familiarizing yourself with all of the [BloodHound edges](https://bloodhound.specterops.io/resources/edges/overview) and as many Active Directory [Extended Rights](https://learn.microsoft.com/en-us/windows/win32/adschema/extended-rights) as possible as you never know when you may encounter a less common one during an assessment.

---

## ACL Attacks in the Wild

We can use ACL attacks for:

- Lateral movement
- Privilege escalation
- Persistence

Some common attack scenarios may include:

| Attack                                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Abusing forgot password permissions` | Help Desk and other IT users are often granted permissions to perform password resets and other privileged tasks. If we can take over an account with these privileges (or an account in a group that confers these privileges on its users), we may be able to perform a password reset for a more privileged account in the domain.                                                                                                                                                |
| `Abusing group membership management` | It's also common to see Help Desk and other staff that have the right to add/remove users from a given group. It is always worth enumerating this further, as sometimes we may be able to add an account that we control into a privileged built-in AD group or a group that grants us some sort of interesting privilege.                                                                                                                                                           |
| `Excessive user rights`               | We also commonly see user, computer, and group objects with excessive rights that a client is likely unaware of. This could occur after some sort of software install (Exchange, for example, adds many ACL changes into the environment at install time) or some kind of legacy or accidental configuration that gives a user unintended rights. Sometimes we may take over an account that was given certain rights out of convenience or to solve a nagging problem more quickly. |


# ACL Enumeration

---

Let's jump into enumerating ACLs using PowerView and walking through some graphical representations using BloodHound. We will then cover a few scenarios/attacks where the ACEs we enumerate can be leveraged to gain us further access in the internal environment.

---

## Enumerating ACLs with PowerView

We can use PowerView to enumerate ACLs, but the task of digging through _all_ of the results will be extremely time-consuming and likely inaccurate. For example, if we run the function `Find-InterestingDomainAcl` we will receive a massive amount of information back that we would need to dig through to make any sense of:

#### Using Find-InterestingDomainAcl

![](../../ZMEDIA/Pasted%20image%2020260707100630.png)

If we try to dig through all of this data during a time-boxed assessment, we will likely never get through it all or find anything interesting before the assessment is over. Now, there is a way to use a tool such as PowerView more effectively -- by performing targeted enumeration starting with a user that we have control over. Let's focus on the user `wley`, which we obtained after solving the last question in the `LLMNR/NBT-NS Poisoning - from Linux` section. Let's dig in and see if this user has any interesting ACL rights that we could take advantage of. We first need to get the SID of our target user to search effectively.

```powershell
PS C:\htb> Import-Module .\PowerView.ps1 PS C:\htb> $sid = Convert-NameToSid wley
```

We can then use the `Get-DomainObjectACL` function to perform our targeted search. In the below example, we are using this function to find all domain objects that our user has rights over by mapping the user's SID using the `$sid` variable to the `SecurityIdentifier` property which is what tells us _who_ has the given right over an object. One important thing to note is that if we search without the flag `ResolveGUIDs`, we will see results like the below, where the right `ExtendedRight` does not give us a clear picture of what ACE entry the user `wley` has over `damundsen`. This is because the `ObjectAceType` property is returning a GUID value that is not human readable.

Note that this command will take a while to run, especially in a large environment. It may take 1-2 minutes to get a result in our lab.

#### Using Get-DomainObjectACL

![](../../ZMEDIA/Pasted%20image%2020260707100702.png)
We could Google for the GUID value `00299570-246d-11d0-a768-00aa006e0529` and uncover [this](https://docs.microsoft.com/en-us/windows/win32/adschema/r-user-force-change-password) page showing that the user has the right to force change the other user's password. Alternatively, we could do a reverse search using PowerShell to map the right name back to the GUID value.

Note that if PowerView has already been imported, the cmdlet shown below will result in an error. Therefore, we may need to run it from a new PowerShell session.

#### Performing a Reverse Search & Mapping to a GUID Value
![](../../ZMEDIA/Pasted%20image%2020260707100717.png)

This gave us our answer, but would be highly inefficient during an assessment. PowerView has the `ResolveGUIDs` flag, which does this very thing for us. Notice how the output changes when we include this flag to show the human-readable format of the `ObjectAceType` property as `User-Force-Change-Password`.

#### Using the -ResolveGUIDs Flag
![](../../ZMEDIA/Pasted%20image%2020260707100730.png)

It is essential that we understand what our tools are doing and have alternative methods in our toolkit in case a tool fails or is blocked. Before moving on, let's take a quick look at how we could do this using the [Get-Acl](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl?view=powershell-7.2) and [Get-ADUser](https://docs.microsoft.com/en-us/powershell/module/activedirectory/get-aduser?view=windowsserver2022-ps) cmdlets which we may find available to us on a client system. Knowing how to perform this type of search without using a tool such as PowerView is greatly beneficial and could set us apart from our peers. We may be able to use this knowledge to achieve results when a client has us work from one of their systems, and we are restricted down to what tools are readily available on the system without the ability to pull in any of our own.

This example is not very efficient, and the command can take a long time to run, especially in a large environment. It will take much longer than the equivalent command using PowerView. In this command, we've first made a list of all domain users with the following command:

#### Creating a List of Domain Users

```powershell
PS C:\htb> Get-ADUser -Filter * | Select-Object -ExpandProperty SamAccountName > ad_users.txt
```

We then read each line of the file using a `foreach` loop, and use the `Get-Acl` cmdlet to retrieve ACL information for each domain user by feeding each line of the `ad_users.txt` file to the `Get-ADUser` cmdlet. We then select just the `Access property`, which will give us information about access rights. Finally, we set the `IdentityReference` property to the user we are in control of (or looking to see what rights they have), in our case, `wley`.

#### A Useful foreach Loop
![](../../ZMEDIA/Pasted%20image%2020260707100753.png)

Once we have this data, we could follow the same methods shown above to convert the GUID to a human-readable format to understand what rights we have over the target user.

So, to recap, we started with the user `wley` and now have control over the user `damundsen` via the `User-Force-Change-Password` extended right. Let's use Powerview to hunt for where, if anywhere, control over the `damundsen` account could take us.

#### Further Enumeration of Rights Using damundsen
![](../../ZMEDIA/Pasted%20image%2020260707100805.png)

Now we can see that our user `damundsen` has `GenericWrite` privileges over the `Help Desk Level 1` group. This means, among other things, that we can add any user (or ourselves) to this group and inherit any rights that this group has applied to it. A search for rights conferred upon this group does not return anything interesting.

Let's look and see if this group is nested into any other groups, remembering that nested group membership will mean that any users in group A will inherit all rights of any group that group A is nested into (a member of). A quick search shows us that the `Help Desk Level 1` group is nested into the `Information Technology` group, meaning that we can obtain any rights that the `Information Technology` group grants to its members if we just add ourselves to the `Help Desk Level 1` group where our user `damundsen` has `GenericWrite` privileges.

#### Investigating the Help Desk Level 1 Group with Get-DomainGroup
![](../../ZMEDIA/Pasted%20image%2020260707100818.png)

This is a lot to digest! Let's recap where we're at:

- We have control over the user `wley` whose hash we retrieved earlier in the module (assessment) using Responder and cracked offline using Hashcat to reveal the cleartext password value
- We enumerated objects that the user `wley` has control over and found that we could force change the password of the user `damundsen`
- From here, we found that the `damundsen` user can add a member to the `Help Desk Level 1` group using `GenericWrite` privileges
- The `Help Desk Level 1` group is nested into the `Information Technology` group, which grants members of that group any rights provisioned to the `Information Technology` group

Now let's look around and see if members of `Information Technology` can do anything interesting. Once again, doing our search using `Get-DomainObjectACL` shows us that members of the `Information Technology` group have `GenericAll` rights over the user `adunn`, which means we could:

- Modify group membership
- Force change a password
- Perform a targeted Kerberoasting attack and attempt to crack the user's password if it is weak

#### Investigating the Information Technology Group
![](../../ZMEDIA/Pasted%20image%2020260707100832.png)
Finally, let's see if the `adunn` user has any type of interesting access that we may be able to leverage to get closer to our goal.

#### Looking for Interesting Access

![](../../ZMEDIA/Pasted%20image%2020260707100902.png)

The output above shows that our `adunn` user has `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-In-Filtered-Set` rights over the domain object. This means that this user can be leveraged to perform a DCSync attack. We will cover this attack in-depth in the `DCSync` section.

---

## Enumerating ACLs with BloodHound

Now that we've enumerated the attack path using more manual methods like PowerView and built-in PowerShell cmdlets, let's look at how much easier this would have been to identify using the extremely powerful BloodHound tool. Let's take the data we gathered earlier with the SharpHound ingestor and upload it to BloodHound. Next, we can set the `wley` user as our starting node, select the `Node Info` tab and scroll down to `Outbound Control Rights`. This option will show us objects we have control over directly, via group membership, and the number of objects that our user could lead to us controlling via ACL attack paths under `Transitive Object Control`. If we click on the `1` next to `First Degree Object Control`, we see the first set of rights that we enumerated, `ForceChangePassword` over the `damundsen` user.

#### Viewing Node Info through BloodHound

![BloodHound interface showing node info for WLEY@INLANEFREIGHT.LOCALl with execution and control rights, connected to DAMUNDSEN@INLANEFREIGHT.LOCAL via ForceChangePassword.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/wley_damundsen.png)

If we right-click on the line between the two objects, a menu will pop up. If we select `Help`, we will be presented with help around abusing this ACE, including:

- More info on the specific right, tools, and commands that can be used to pull off this attack
- Operational Security (Opsec) considerations
- External references.

We'll dig into this menu more later on.

#### Investigating ForceChangePassword Further

![Popup window in BloodHound showing ForceChangePassword capability for WLEY@INLANEFREIGHT.LOCAL to change DAMUNDSEN@INLANEFREIGHT.LOCAL's password without knowing the current password.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/help_edge.png)

If we click on the `16` next to `Transitive Object Control`, we will see the entire path that we painstakingly enumerated above. From here, we could leverage the help menus for each edge to find ways to best pull off each attack.

#### Viewing Potential Attack Paths through BloodHound

![BloodHound graph showing WLEY@INLANEFREIGHT.LOCAL's connections to various groups and users, including CONTRACTORS, FILE SHARE, and DOMAIN USERS, with relationships like MemberOf and ForceChangePassword.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/wley_path.png)

Finally, we can use the pre-built queries in BloodHound to confirm that the `adunn` user has DCSync rights.

#### Viewing Pre-Build queries through BloodHound

![BloodHound graph showing ADUNN@INLANEFREIGHT.LOCAL's connections to various groups and users, including DOMAIN ADMINS and ENTERPRISE DOMAIN CONTROLLERS, with relationships like MemberOf and GetChangesAll.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/adunn_dcsync.png)

We've now enumerated these attack paths in multiple ways. The next step will be performing this attack chain from start to finish. Let's dig in!


# ACL Abuse Tactics

---

## Abusing ACLs

Once again, to recap where we are and where we want to get to. We are in control of the `wley` user whose NTLMv2 hash we retrieved by running Responder earlier in the assessment. Lucky for us, this user was using a weak password, and we were able to crack the hash offline using Hashcat and retrieve the cleartext value. We know that we can use this access to kick off an attack chain that will result in us taking control of the `adunn` user who can perform the DCSync attack, which would give us full control of the domain by allowing us to retrieve the NTLM password hashes for all users in the domain and escalate privileges to Domain/Enterprise Admin and even achieve persistence. To perform the attack chain, we have to do the following:

1. Use the `wley` user to change the password for the `damundsen` user
2. Authenticate as the `damundsen` user and leverage `GenericWrite` rights to add a user that we control to the `Help Desk Level 1` group
3. Take advantage of nested group membership in the `Information Technology` group and leverage `GenericAll` rights to take control of the `adunn` user

So, first, we must authenticate as `wley` and force change the password of the user `damundsen`. We can start by opening a PowerShell console and authenticating as the `wley` user. Otherwise, we could skip this step if we were already running as this user. To do this, we can create a [PSCredential object](https://docs.microsoft.com/en-us/dotnet/api/system.management.automation.pscredential?view=powershellsdk-7.0.0).

#### Creating a PSCredential Object

```powershell
PS C:\htb> $SecPassword = ConvertTo-SecureString '<PASSWORD HERE>' -AsPlainText -Force PS C:\htb> $Cred = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\wley', $SecPassword)
```

Next, we must create a [SecureString object](https://docs.microsoft.com/en-us/dotnet/api/system.security.securestring?view=net-6.0) which represents the password we want to set for the target user `damundsen`.

#### Creating a SecureString Object

```powershell
PS C:\htb> $damundsenPassword = ConvertTo-SecureString 'Pwn3d_by_ACLs!' -AsPlainText -Force
```

Finally, we'll use the [Set-DomainUserPassword](https://powersploit.readthedocs.io/en/latest/Recon/Set-DomainUserPassword/) PowerView function to change the user's password. We need to use the `-Credential` flag with the credential object we created for the `wley` user. It's best to always specify the `-Verbose` flag to get feedback on the command completing as expected or as much information about errors as possible. We could do this from a Linux attack host using a tool such as `pth-net`, which is part of the [pth-toolkit](https://github.com/byt3bl33d3r/pth-toolkit).

#### Changing the User's Password
![](../../ZMEDIA/Pasted%20image%2020260707101026.png)

We can see that the command completed successfully, changing the password for the target user while using the credentials we specified for the `wley` user that we control. Next, we need to perform a similar process to authenticate as the `damundsen` user and add ourselves to the `Help Desk Level 1` group.

#### Creating a SecureString Object using damundsen

```powershell
PS C:\htb> $SecPassword = ConvertTo-SecureString 'Pwn3d_by_ACLs!' -AsPlainText -Force PS C:\htb> $Cred2 = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\damundsen', $SecPassword)
```

Next, we can use the [Add-DomainGroupMember](https://powersploit.readthedocs.io/en/latest/Recon/Add-DomainGroupMember/) function to add ourselves to the target group. We can first confirm that our user is not a member of the target group. This could also be done from a Linux host using the `pth-toolkit`.

#### Adding damundsen to the Help Desk Level 1 Group

![](../../ZMEDIA/Pasted%20image%2020260707101113.png)

![](../../ZMEDIA/Pasted%20image%2020260707101134.png)

A quick check shows that our addition to the group was successful.

#### Confirming damundsen was Added to the Group

![](../../ZMEDIA/Pasted%20image%2020260707101153.png)

At this point, we should be able to leverage our new group membership to take control over the `adunn` user. Now, let's say that our client permitted us to change the password of the `damundsen` user, but the `adunn` user is an admin account that cannot be interrupted. Since we have `GenericAll` rights over this account, we can have even more fun and perform a targeted Kerberoasting attack by modifying the account's [servicePrincipalName attribute](https://docs.microsoft.com/en-us/windows/win32/adschema/a-serviceprincipalname) to create a fake SPN that we can then Kerberoast to obtain the TGS ticket and (hopefully) crack the hash offline using Hashcat.

We must be authenticated as a member of the `Information Technology` group for this to be successful. Since we added `damundsen` to the `Help Desk Level 1` group, we inherited rights via nested group membership. We can now use [Set-DomainObject](https://powersploit.readthedocs.io/en/latest/Recon/Set-DomainObject/) to create the fake SPN. We could use the tool [targetedKerberoast](https://github.com/ShutdownRepo/targetedKerberoast) to perform this same attack from a Linux host, and it will create a temporary SPN, retrieve the hash, and delete the temporary SPN all in one command.

#### Creating a Fake SPN
![](../../ZMEDIA/Pasted%20image%2020260707101206.png)

If this worked, we should be able to Kerberoast the user using any number of methods and obtain the hash for offline cracking. Let's do this with Rubeus.

#### Kerberoasting with Rubeus
![](../../ZMEDIA/Pasted%20image%2020260707101225.png)

Great! We have successfully obtained the hash. The last step is to attempt to crack the password offline using Hashcat. Once we have the cleartext password, we could now authenticate as the `adunn` user and perform the DCSync attack, which we will cover in the next section.

---

## Cleanup

In terms of cleanup, there are a few things we need to do:

1. Remove the fake SPN we created on the `adunn` user.
2. Remove the `damundsen` user from the `Help Desk Level 1` group
3. Set the password for the `damundsen` user back to its original value (if we know it) or have our client set it/alert the user

This order is important because if we remove the user from the group first, then we won't have the rights to remove the fake SPN.

First, let's remove the fake SPN from the `adunn` account.

#### Removing the Fake SPN from adunn's Account
![](../../ZMEDIA/Pasted%20image%2020260707101246.png)
Next, we'll remove the user from the group using the `Remove-DomainGroupMember` function.

#### Removing damundsen from the Help Desk Level 1 Group
![](../../ZMEDIA/Pasted%20image%2020260707101259.png)

We can confirm the user was indeed removed:

#### Confirming damundsen was Removed from the Group

```powershell
PS C:\htb> Get-DomainGroupMember -Identity "Help Desk Level 1" | Select MemberName |? {$_.MemberName -eq 'damundsen'} -Verbose
```

Even though we performed as much cleanup as possible, we should still include every modification that we make in our final assessment report. Our client will want to be apprised of any changes within the environment, and recording everything we do during an assessment in writing helps our client and us should questions arise.

This is just one example attack path. There could be many attack paths in a large domain, some shorter and some more complicated. While this path was fictional for this specific lab environment, I have seen similar attack paths during real-world engagements, and ACL attacks often come into play for furthering access. Sometimes, though, an ACL attack chain may be too time-consuming or potentially destructive, so we may prefer to enumerate the path to present our client with enough evidence to understand the issue and perform remediation.

---

## Detection and Remediation

A few recommendations around ACLs include:

1. `Auditing for and removing dangerous ACLs`

Organizations should have regular AD audits performed but also train internal staff to run tools such as BloodHound and identify potentially dangerous ACLs that can be removed.

2. `Monitor group membership`

Visibility into important groups is paramount. All high-impact groups in the domain should be monitored to alert IT staff of changes that could be indicative of an ACL attack chain.

3. `Audit and monitor for ACL changes`

Enabling the [Advanced Security Audit Policy](https://docs.microsoft.com/en-us/archive/blogs/canitpro/step-by-step-enabling-advanced-security-audit-policy-via-ds-access) can help in detecting unwanted changes, especially [Event ID 5136: A directory service object was modified](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-5136) which would indicate that the domain object was modified, which could be indicative of an ACL attack. If we look at the event log after modifying the ACL of the domain object, we will see some event ID `5136` created:

#### Viewing Event ID 5136

![Windows Event Viewer showing Security log entry for Event ID 5136, indicating a Directory Service change by administrator on 3/24/2022 at 10:53 AM. Audit Success for INLANEFREIGHT.LOCAL domain.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/event5136.png)

If we check out the `Details` tab, we can see that the pertinent information is written in [Security Descriptor Definition Language (SDDL)](https://docs.microsoft.com/en-us/windows/win32/secauthz/security-descriptor-definition-language) which is not human readable.

#### Viewing Associated SDDL

![Windows Event Viewer displaying Security log entry for Event ID 5136, showing Directory Service change details with audit success on 3/24/2022 at 10:53 AM.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/event5136_sddl.png)

We can use the [ConvertFrom-SddlString cmdlet](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertfrom-sddlstring?view=powershell-7.2) to convert this to a readable format.

#### Converting the SDDL String into a Readable Format

![](../../ZMEDIA/Pasted%20image%2020260707101400.png)
![](../../ZMEDIA/Pasted%20image%2020260707101417.png)
If we choose to filter on the `DiscretionaryAcl` property, we can see that the modification was likely giving the `mrb3n` user `GenericWrite` privileges over the domain object itself, which could be indicative of an attack attempt.

![](../../ZMEDIA/Pasted%20image%2020260707101503.png)
![](../../ZMEDIA/Pasted%20image%2020260707101521.png)

There are many tools out there that can be used to help monitor AD. These tools, when used in conjunction with a highly mature AD secure posture, and combined with built-in tools such as the various ways we can monitor for and alert on events in Active Directory, can help to detect these types of attacks and prevent them from going any further.

In the next section, we'll walk through the DCSync attack, which is the result of the attack path we just worked through and is a common way to achieve domain compromise.

# DCSync

---

Based on our work in the previous section, we now have control over the user `adunn` who has DCSync privileges in the INLANEFREIGHT.LOCAL domain. Let's dig deeper into this attack and go through examples of leveraging it for full domain compromise from both a Linux and a Windows attack host.

---

## Scenario Setup

In this section, we will move back and forth between a Windows and Linux attack host as we work through the various examples. You can spawn the hosts for this section at the end of this section and RDP into the MS01 Windows attack host with the credentials `htb-student:Academy_student_AD!`. For the portion of this section that requires interaction from a Linux host (secretsdump.py) you can open a PowerShell console on MS01 and SSH to `172.16.5.225` with the credentials `htb-student:HTB_@cademy_stdnt!`. This could also likely be done all from Windows using a version of `secretsdump.exe` compiled for Windows as there are several GitHub repos of the Impacket toolkit compiled for Windows, or you can do that as a side challenge.

---

## What is DCSync and How Does it Work?

DCSync is a technique for stealing the Active Directory password database by using the built-in `Directory Replication Service Remote Protocol`, which is used by Domain Controllers to replicate domain data. This allows an attacker to mimic a Domain Controller to retrieve user NTLM password hashes.

The crux of the attack is requesting a Domain Controller to replicate passwords via the `DS-Replication-Get-Changes-All` extended right. This is an extended access control right within AD, which allows for the replication of secret data.

To perform this attack, you must have control over an account that has the rights to perform domain replication (a user with the Replicating Directory Changes and Replicating Directory Changes All permissions set). Domain/Enterprise Admins and default domain administrators have this right by default.

#### Viewing adunn's Replication Privileges through ADSI Edit

![ADSI Edit window showing DC=INLANEFREIGHT,DC=LOCAL properties with user Angela Dunn selected, displaying permissions for directory changes.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/adnunn_right_dcsync.png)

It is common during an assessment to find other accounts that have these rights, and once compromised, their access can be utilized to retrieve the current NTLM password hash for any domain user and the hashes corresponding to their previous passwords. Here we have a standard domain user that has been granted the replicating permissions:

#### Using Get-DomainUser to View adunn's Group Membership
![](../../ZMEDIA/Pasted%20image%2020260707101640.png)

PowerView can be used to confirm that this standard user does indeed have the necessary permissions assigned to their account. We first get the user's SID in the above command and then check all ACLs set on the domain object (`"DC=inlanefreight,DC=local"`) using [Get-ObjectAcl](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainObjectAcl/) to get the ACLs associated with the object. Here we search specifically for replication rights and check if our user `adunn` (denoted in the below command as `$sid`) possesses these rights. The command confirms that the user does indeed have the rights.

#### Using Get-ObjectAcl to Check adunn's Replication Rights

![](../../ZMEDIA/Pasted%20image%2020260707101659.png)

If we had certain rights over the user (such as [WriteDacl](https://bloodhound.specterops.io/resources/edges/write-dacl)), we could also add this privilege to a user under our control, execute the DCSync attack, and then remove the privileges to attempt to cover our tracks. DCSync replication can be performed using tools such as Mimikatz, Invoke-DCSync, and Impacket’s secretsdump.py. Let's see a few quick examples.

Running the tool as below will write all hashes to files with the prefix `inlanefreight_hashes`. The `-just-dc` flag tells the tool to extract NTLM hashes and Kerberos keys from the NTDS file.

#### Extracting NTLM Hashes and Kerberos Keys Using secretsdump.py

![](../../ZMEDIA/Pasted%20image%2020260707101718.png)

We can use the `-just-dc-ntlm` flag if we only want NTLM hashes or specify `-just-dc-user <USERNAME>` to only extract data for a specific user. Other useful options include `-pwd-last-set` to see when each account's password was last changed and `-history` if we want to dump password history, which may be helpful for offline password cracking or as supplemental data on domain password strength metrics for our client. The `-user-status` is another helpful flag to check and see if a user is disabled. We can dump the NTDS data with this flag and then filter out disabled users when providing our client with password cracking statistics to ensure that data such as:

- Number and % of passwords cracked
- top 10 passwords
- Password length metrics
- Password re-use

reflect only active user accounts in the domain.

If we check the files created using the `-just-dc` flag, we will see that there are three: one containing the NTLM hashes, one containing Kerberos keys, and one that would contain cleartext passwords from the NTDS for any accounts set with [reversible encryption](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/store-passwords-using-reversible-encryption) enabled.

#### Listing Hashes, Kerberos Keys, and Cleartext Passwords

```shellsession
haphestus@htb[/htb]$ ls inlanefreight_hashes* 

inlanefreight_hashes.ntds  inlanefreight_hashes.ntds.cleartext  inlanefreight_hashes.ntds.kerberos
```

While rare, we see accounts with these settings from time to time. It would typically be set to provide support for applications that use certain protocols that require a user's password to be used for authentication purposes.

#### Viewing an Account with Reversible Encryption Password Storage Set

![Active Directory Users and Computers showing PROXYAGENT properties with account options and expiration settings.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/reverse_encrypt.png)

When this option is set on a user account, it does not mean that the passwords are stored in cleartext. Instead, they are stored using RC4 encryption. The trick here is that the key needed to decrypt them is stored in the registry (the [Syskey](https://docs.microsoft.com/en-us/windows-server/security/kerberos/system-key-utility-technical-overview)) and can be extracted by a Domain Admin or equivalent. Tools such as `secretsdump.py` will decrypt any passwords stored using reversible encryption while dumping the NTDS file either as a Domain Admin or using an attack such as DCSync. If this setting is disabled on an account, a user will need to change their password for it to be stored using one-way encryption. Any passwords set on accounts with this setting enabled will be stored using reversible encryption until they are changed. We can enumerate this using the `Get-ADUser` cmdlet:

#### Enumerating Further using Get-ADUser
![](../../ZMEDIA/Pasted%20image%2020260707101754.png)

We can see that one account, `proxyagent`, has the reversible encryption option set with PowerView as well:

#### Checking for Reversible Encryption Option using Get-DomainUser
![](../../ZMEDIA/Pasted%20image%2020260707101805.png)

We will notice the tool decrypted the password and provided us with the cleartext value.

#### Displaying the Decrypted Password

```shellsession
haphestus@htb[/htb]$ cat inlanefreight_hashes.ntds.cleartext 
 
proxyagent:CLEARTEXT:Pr0xy_ILFREIGHT!
```

I have been on a few engagements where all user accounts were stored using reversible encryption. Some clients may do this to be able to dump NTDS and perform periodic password strength audits without having to resort to offline password cracking.

We can perform the attack with Mimikatz as well. Using Mimikatz, we must target a specific user. Here we will target the built-in administrator account. We could also target the `krbtgt` account and use this to create a `Golden Ticket` for persistence, but that is outside the scope of this module.

Also it is important to note that Mimikatz must be ran in the context of the user who has DCSync privileges. We can utilize `runas.exe` to accomplish this:

#### Using runas.exe
![](../../ZMEDIA/Pasted%20image%2020260707101845.png)

From the newly spawned powershell session, we can perform the attack:

#### Performing the Attack with Mimikatz

![](../../ZMEDIA/Pasted%20image%2020260707101903.png)

---

## Moving On

In the next section, we'll see some ways to enumerate and take advantage of remote access rights that may be granted to a user we control. These methods include Remote Desktop Protocol (RDP), WinRM (or PsRemoting), and SQL Server admin access.