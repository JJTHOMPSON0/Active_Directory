# All About Users

## User and Machine Accounts

***

User accounts are created on both local systems (not joined to AD) and in Active Directory to give a person or a program (such as a system service) the ability to log on to a computer and access resources based on their rights. When a user logs in, the system verifies their password and creates an access token. This token describes the security content of a process or thread and includes the user's security identity and group membership. Whenever a user interacts with a process, this token is presented. User accounts are used to allow employees/contractors to log in to a computer and access resources, to run programs or services under a specific security context (i.e., running as a highly privileged user instead of a network service account), and to manage access to objects and their properties such as network file shares, files, applications, etc.

Users can be assigned to groups that can contain one or more members. These groups can also be used to control access to resources. It can be easier for an administrator to assign privileges once to a group (which all group members inherit) instead of many times to each individual user. This helps simplify administration and makes it easier to grant and revoke user rights.

![Active Directory Users and Computers interface showing organizational units and security groups under INLANEFREIGHT.LOCAL, including Employees, Security Groups, and Service Accounts.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/74/all_users.png)

As we will see later in this module, user accounts can be provisioned many rights in Active Directory. They can be configured as basically read-only users who have read access to most of the environment (which are the permissions a standard Domain User receives) up to Enterprise Admin (with complete control of every object in the domain) and countless combinations in between. Because users can have so many rights assigned to them, they can also be misconfigured relatively easily and granted unintended rights that an attacker or a penetration tester can leverage.

It is difficult to manage human behavior and account for every user choosing weak or shared passwords, installing unauthorized software, or admins making careless mistakes or being overly permissive with account management. To combat this, an organization needs to have policies and procedures to combat issues that can arise around user accounts and must have defense in depth to mitigate the inherent risk that users bring to the domain.

Specifics on user-related misconfigurations and attacks are outside the scope of this module. Still, it is important to understand the sheer impact users can have within any Active Directory network and to understand the nuances between the different types of users/accounts we may encounter.

***

### Local Accounts

Local accounts are stored locally on a particular server or workstation. These accounts can be assigned rights on that host either individually or via group membership. Any rights assigned can only be granted to that specific host and will not work across the domain. Local user accounts are considered security principals but can only manage access to and secure resources on a standalone host. There are several default local user accounts that are created on a Windows system:

* `Administrator`: this account has the SID `S-1-5-domain-500` and is the first account created with a new Windows installation. It has full control over almost every resource on the system. It cannot be deleted or locked, but it can be disabled or renamed. Windows 10 and Server 2016 hosts disable the built-in administrator account by default and create another local account in the local administrator's group during setup.
* `Guest`: this account is disabled by default. The purpose of this account is to allow users without an account on the computer to log in temporarily with limited access rights. By default, it has a blank password and is generally recommended to be left disabled because of the security risk of allowing anonymous access to a host.
* `SYSTEM`: The SYSTEM (or `NT AUTHORITY\SYSTEM`) account on a Windows host is the default account installed and used by the operating system to perform many of its internal functions. Unlike the Root account on Linux, `SYSTEM` is a service account and does not run entirely in the same context as a regular user. Many of the processes and services running on a host are run under the SYSTEM context. One thing to note with this account is that a profile for it does not exist, but it will have permissions over almost everything on the host. It does not appear in User Manager and cannot be added to any groups. A `SYSTEM` account is the highest permission level one can achieve on a Windows host and, by default, is granted Full Control permissions to all files on a Windows system.
* `Network Service`: This is a predefined local account used by the Service Control Manager (SCM) for running Windows services. When a service runs in the context of this particular account, it will present credentials to remote services.
* `Local Service`: This is another predefined local account used by the Service Control Manager (SCM) for running Windows services. It is configured with minimal privileges on the computer and presents anonymous credentials to the network.

It is worth studying Microsoft's documentation on [local default accounts](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/local-accounts) in-depth to gain a better understanding of how the various accounts work together on an individual Windows system and across a domain network. Take some time to look them over and understand the nuances between them.

***

### Domain Users

Domain users differ from local users in that they are granted rights from the domain to access resources such as file servers, printers, intranet hosts, and other objects based on the permissions granted to their user account or the group that account is a member of. Domain user accounts can log in to any host in the domain, unlike local users. For more information on the many different Active Directory account types, check out this [link](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/active-directory-accounts). One account to keep in mind is the `KRBTGT` account, however. This is a type of local account built into the AD infrastructure. This account acts as a service account for the Key Distribution service providing authentication and access for domain resources. This account is a common target of many attackers since gaining control or access will enable an attacker to have unconstrained access to the domain. It can be leveraged for privilege escalation and persistence in a domain through attacks such as the [Golden Ticket](https://attack.mitre.org/techniques/T1558/001/) attack.

***

### User Naming Attributes

Security in Active Directory can be improved using a set of user naming attributes to help identify user objects like logon name or ID. The following are a few important Naming Attributes in AD:

|                           |                                                                                                                                                                                                                                                                                  |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `UserPrincipalName` (UPN) | This is the primary logon name for the user. By convention, the UPN uses the email address of the user.                                                                                                                                                                          |
| `ObjectGUID`              | This is a unique identifier of the user. In AD, the ObjectGUID attribute name never changes and remains unique even if the user is removed.                                                                                                                                      |
| `SAMAccountName`          | This is a logon name that supports the previous version of Windows clients and servers.                                                                                                                                                                                          |
| `objectSID`               | The user's Security Identifier (SID). This attribute identifies a user and its group memberships during security interactions with the server.                                                                                                                                   |
| `sIDHistory`              | This contains previous SIDs for the user object if moved from another domain and is typically seen in migration scenarios from domain to domain. After a migration occurs, the last SID will be added to the `sIDHistory` property, and the new SID will become its `objectSID`. |

**Common User Attributes**

```powershell
PS C:\htb Get-ADUser -Identity htb-student DistinguishedName : CN=htb student,CN=Users,DC=INLANEFREIGHT,DC=LOCAL Enabled           : True GivenName         : htb Name              : htb student ObjectClass       : user ObjectGUID        : aa799587-c641-4c23-a2f7-75850b4dd7e3 SamAccountName    : htb-student SID               : S-1-5-21-3842939050-3880317879-2865463114-1111 Surname           : student UserPrincipalName : htb-student@INLANEFREIGHT.LOCAL
```

For a deeper look at user object attributes, check out this [page](https://docs.microsoft.com/en-us/windows/win32/ad/user-object-attributes). Many attributes can be set for any object in AD. Many objects will never be used or are not relevant to us as security professionals. Still, it is essential to familiarize ourselves with the most common and more obscure ones that may contain sensitive data or help mount an attack.

***

### Domain-joined vs. Non-Domain-joined Machines

When it comes to computer resources, there are several ways they are typically managed. Below we will discuss the differences between a host joined to a domain versus a host that is only in a workgroup.

**`Domain joined`**

Hosts joined to a domain have greater ease of information sharing within the enterprise and a central management point (the DC) to gather resources, policies, and updates from. A host joined to a domain will acquire any configurations or changes necessary through the domain's Group Policy. The benefit here is that a user in the domain can log in and access resources from any host joined to the domain, not just the one they work on. This is the typical setup you will see in enterprise environments.

**`Non-domain joined`**

Non-domain joined computers or computers in a `workgroup` are not managed by domain policy. With that in mind, sharing resources outside your local network is much more complicated than it would be on a domain. This is fine for computers meant for home use or small business clusters on the same LAN. The advantage of this setup is that the individual users are in charge of any changes they wish to make to their host. Any user accounts on a workgroup computer only exist on that host, and profiles are not migrated to other hosts within the workgroup.

It is important to note that a machine account (`NT AUTHORITY\SYSTEM` level access) in an AD environment will have most of the same rights as a standard domain user account. This is important because we do not always need to obtain a set of valid credentials for an individual user's account to begin enumerating and attacking a domain (as we will see in later modules). We may obtain `SYSTEM` level access to a domain-joined Windows host through a successful remote code execution exploit or by escalating privileges on a host. This access is often overlooked as only useful for pillaging sensitive data (i.e., passwords, SSH keys, sensitive files, etc.) on a particular host. In reality, access in the context of the `SYSTEM` account will allow us read access to much of the data within the domain and is a great launching point for gathering as much information about the domain as possible before proceeding with applicable AD-related attacks.

## Active Directory Groups

***

After users, groups are another significant object in Active Directory. They can place similar users together and mass assign rights and access. Groups are another key target for attackers and penetration testers, as the rights that they confer on their members may not be readily apparent but may grant excessive (and even unintended) privileges that can be abused if not set up correctly. There are many [built-in groups](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/active-directory-security-groups#about-active-directory-groups) in Active Directory, and most organizations also create their own groups to define rights and privileges, further managing access within the domain. The number of groups in an AD environment can snowball and become unwieldy, potentially leading to unintended access if left unchecked. It is essential to understand the impact of using different group types and for any organization to periodically `audit` which groups exist within their domain, the privileges that these groups grant their members, and check for excessive group membership beyond what is required for a user to perform their day-to-day work. Moving on, we will discuss the different types of groups that exist and the scopes they can be assigned to.

One question that comes up often is the difference between Groups and Organizational Units (OUs). As discussed earlier in the module, OUs are useful for grouping users, groups, and computers to ease management and deploying Group Policy settings to specific objects in the domain. Groups are primarily used to assign permissions to access resources. OUs can also be used to delegate administrative tasks to a user, such as resetting passwords or unlocking user accounts without giving them additional admin rights that they may inherit through group membership.

***

### Types of Groups

In simpler terms, groups are used to place users, computers, and contact objects into management units that provide ease of administration over permissions and facilitate the assignment of resources such as printers and file share access. For example, if an admin needs to assign 50 members of a department access to a new share drive, it would be time-consuming to add each user's account individually. Granting permissions this way would also make it more difficult to audit who has access to resources and difficult to clean up/revoke permissions. Instead, a sysadmin can either use an existing group or create a new group and grant that specific group permissions over the resource. From here, every user in the group will inherit the permissions based on their membership in the group. If the permissions need to be modified or revoked for one or more users, they could merely be removed from the group, leaving the other users unaffected and their permissions intact.

Groups in Active Directory have two fundamental characteristics: `type` and `scope`. The `group type` defines the group's purpose, while the `group scope` shows how the group can be used within the domain or forest. When creating a new group, we must select a group type. There are two main types: `security` and `distribution` groups.

**Group Type And Scope**

![Active Directory Users and Computers interface with 'New Object - Group' dialog open. Fields for Group name, Group scope, and Group type are visible under INLANEFREIGHT.LOCAL/Corp/Employees/HQ-NYC/IT.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/74/group-options2.png)

The `Security groups` type is primarily for ease of assigning permissions and rights to a collection of users instead of one at a time. They simplify management and reduce overhead when assigning permissions and rights for a given resource. All users added to a security group will inherit any permissions assigned to the group, making it easier to move users in and out of groups while leaving the group's permissions unchanged.

The `Distribution groups` type is used by email applications such as Microsoft Exchange to distribute messages to group members. They function much like mailing lists and allow for auto-adding emails in the "To" field when creating an email in Microsoft Outlook. This type of group cannot be used to assign permissions to resources in a domain environment.

***

### Group Scopes

There are three different `group scopes` that can be assigned when creating a new group.

1. Domain Local Group
2. Global Group
3. Universal Group

**Domain Local Group**

Domain local groups can only be used to manage permissions to domain resources in the domain where it was created. Local groups cannot be used in other domains but `CAN` contain users from `OTHER` domains. Local groups can be nested into (contained within) other local groups but `NOT` within global groups.

**Global Group**

Global groups can be used to grant access to resources in `another domain`. A global group can only contain accounts from the domain where it was created. Global groups can be added to both other global groups and local groups.

**Universal Group**

The universal group scope can be used to manage resources distributed across multiple domains and can be given permissions to any object within the same `forest`. They are available to all domains within an organization and can contain users from any domain. Unlike domain local and global groups, universal groups are stored in the Global Catalog (GC), and adding or removing objects from a universal group triggers forest-wide replication. It is recommended that administrators maintain other groups (such as global groups) as members of universal groups because global group membership within universal groups is less likely to change than individual user membership in global groups. Replication is only triggered at the individual domain level when a user is removed from a global group. If individual users and computers (instead of global groups) are maintained within universal groups, it will trigger forest-wide replication each time a change is made. This can create a lot of network overhead and potential for issues. Below is an example of the groups in AD and their scope settings. Please pay attention to some of the critical groups and their scope. ( Enterprise and Schema admins compared to Domain admins, for example.)

**AD Group Scope Examples**

```powershell
PS C:\htb> Get-ADGroup  -Filter * |select samaccountname,groupscope samaccountname                           groupscope --------------                           ---------- Administrators                          DomainLocal Users                                   DomainLocal Guests                                  DomainLocal Print Operators                         DomainLocal Backup Operators                        DomainLocal Replicator                              DomainLocal Remote Desktop Users                    DomainLocal Network Configuration Operators         DomainLocal Distributed COM Users                   DomainLocal IIS_IUSRS                               DomainLocal Cryptographic Operators                 DomainLocal Event Log Readers                       DomainLocal Certificate Service DCOM Access         DomainLocal RDS Remote Access Servers               DomainLocal RDS Endpoint Servers                    DomainLocal RDS Management Servers                  DomainLocal Hyper-V Administrators                  DomainLocal Access Control Assistance Operators     DomainLocal Remote Management Users                 DomainLocal Storage Replica Administrators          DomainLocal Domain Computers                             Global Domain Controllers                           Global Schema Admins                             Universal Enterprise Admins                         Universal Cert Publishers                         DomainLocal Domain Admins                                Global Domain Users                                 Global Domain Guests                                Global <SNIP>
```

Group scopes can be changed, but there are a few caveats:

* A Global Group can only be converted to a Universal Group if it is NOT part of another Global Group.
* A Domain Local Group can only be converted to a Universal Group if the Domain Local Group does NOT contain any other Domain Local Groups as members.
* A Universal Group can be converted to a Domain Local Group without any restrictions.
* A Universal Group can only be converted to a Global Group if it does NOT contain any other Universal Groups as members.

***

### Built-in vs. Custom Groups

Several built-in security groups are created with a Domain Local Group scope when a domain is created. These groups are used for specific administrative purposes and are discussed more in the next section. It is important to note that only user accounts can be added to these built-in groups as they do not allow for group nesting (groups within groups). Some examples of built-in groups included `Domain Admins`, which is a `Global` security group and can only contain accounts from its own domain. If an organization wants to allow an account from domain B to perform administrative functions on a domain controller in domain A, the account would have to be added to the built-in Administrators group, which is a `Domain Local` group. Though Active Directory comes prepopulated with many groups, it is common for most organizations to create additional groups (both security and distribution) for their own purposes. Changes/additions to an AD environment can also trigger the creation of additional groups. For example, when Microsoft Exchange is added to a domain, it adds various different security groups to the domain, some of which are highly privileged and, if not managed properly, can be used to gain privileged access within the domain.

***

### Nested Group Membership

Nested group membership is an important concept in AD. As mentioned previously, a Domain Local Group can be a member of another Domain Local Group in the same domain. Through this membership, a user may inherit privileges not assigned directly to their account or even the group they are directly a member of, but rather the group that their group is a member of. This can sometimes lead to unintended privileges granted to a user that are difficult to uncover without an in-depth assessment of the domain. Tools such as [BloodHound](https://github.com/BloodHoundAD/BloodHound) are particularly useful in uncovering privileges that a user may inherit through one or more nestings of groups. This is a key tool for penetration testers for uncovering nuanced misconfigurations and is also extremely powerful for sysadmins and the like to gain deep insights (visually) into the security posture of their domain(s).

Below is an example of privileges inherited through nested group membership. Though `DCorner` is not a direct member of `Helpdesk Level 1`, their membership in `Help Desk` grants them the same privileges that any member of `Helpdesk Level 1` has. In this case, the privilege would allow them to add a member to the `Tier 1 Admins` group (`GenericWrite`). If this group confers any elevated privileges in the domain, it would likely be a key target for a penetration tester. Here, we could add our user to the group and obtain privileges that members of the `Tier 1 Admins` group are granted, such as local administrator access to one or more hosts that could be used to further access.

**Examining Nested Groups via BloodHound**

![Diagram showing connections between email addresses and groups: DCORNER@INLANEFREIGHT.LOCAL is a member of HELP DESK@INLANEFREIGHT.LOCAL, which connects to HELP DESK LEVEL 1@INLANEFREIGHT.LOCAL and TIER 1 ADMINS@INLANEFREIGHT.LOCAL.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/74/bh_nested_groups.png)

***

### Important Group Attributes

Like users, groups have many [attributes](http://www.selfadsi.org/group-attributes.htm). Some of the most [important group attributes](https://docs.microsoft.com/en-us/windows/win32/ad/group-objects) include:

* `cn`: The `cn` or Common-Name is the name of the group in Active Directory Domain Services.
* `member`: Which user, group, and contact objects are members of the group.
* `groupType`: An integer that specifies the group type and scope.
* `memberOf`: A listing of any groups that contain the group as a member (nested group membership).
* `objectSid`: This is the security identifier or SID of the group, which is the unique value used to identify the group as a security principal.

Groups are fundamental objects in AD that can be used to group other objects together and facilitate the management of rights and access. Take the time to study the differences between group types and scopes. This knowledge is useful for administering AD as well as understanding the relationships between groups in the same and different domains and what information can be enumerated during the recon phase of a penetration test. Understanding how different group types can be utilized to perform attacks in a single domain and across trust boundaries is an excellent bit of knowledge to have. We deep-dived into Groups in this section, now let's examine the differences between `Rights` and `Privileges`.

## Active Directory Rights and Privileges

***

Rights and privileges are the cornerstones of AD management and, if mismanaged, can easily lead to abuse by attackers or penetration testers. Access rights and privileges are two important topics in AD (and infosec in general), and we must understand the difference. `Rights` are typically assigned to users or groups and deal with permissions to `access` an object such as a file, while `privileges` grant a user permission to `perform an action` such as run a program, shut down a system, reset passwords, etc. Privileges can be assigned individually to users or conferred upon them via built-in or custom group membership. Windows computers have a concept called `User Rights Assignment`, which, while referred to as rights, are actually types of privileges granted to a user. We will discuss these later in this section. We must have a firm grasp of the differences between rights and privileges in a broader sense and precisely how they apply to an AD environment.

***

### Built-in AD Groups

AD contains many [default or built-in security groups](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/active-directory-security-groups), some of which grant their members powerful rights and privileges which can be abused to escalate privileges within a domain and ultimately gain Domain Admin or SYSTEM privileges on a Domain Controller (DC). Membership in many of these groups should be tightly managed as excessive group membership/privileges is a common flaw in many AD networks that attackers look to abuse. Some of the most common built-in groups are listed below.

| Group Name                           | Description                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Account Operators`                  | Members can create and modify most types of accounts, including those of users, local groups, and global groups, and members can log in locally to domain controllers. They cannot manage the Administrator account, administrative user accounts, or members of the Administrators, Server Operators, Account Operators, Backup Operators, or Print Operators groups.            |
| `Administrators`                     | Members have full and unrestricted access to a computer or an entire domain if they are in this group on a Domain Controller.                                                                                                                                                                                                                                                     |
| `Backup Operators`                   | Members can back up and restore all files on a computer, regardless of the permissions set on the files. Backup Operators can also log on to and shut down the computer. Members can log onto DCs locally and should be considered Domain Admins. They can make shadow copies of the SAM/NTDS database, which, if taken, can be used to extract credentials and other juicy info. |
| `DnsAdmins`                          | Members have access to network DNS information. The group will only be created if the DNS server role is or was at one time installed on a domain controller in the domain.                                                                                                                                                                                                       |
| `Domain Admins`                      | Members have full access to administer the domain and are members of the local administrator's group on all domain-joined machines.                                                                                                                                                                                                                                               |
| `Domain Computers`                   | Any computers created in the domain (aside from domain controllers) are added to this group.                                                                                                                                                                                                                                                                                      |
| `Domain Controllers`                 | Contains all DCs within a domain. New DCs are added to this group automatically.                                                                                                                                                                                                                                                                                                  |
| `Domain Guests`                      | This group includes the domain's built-in Guest account. Members of this group have a domain profile created when signing onto a domain-joined computer as a local guest.                                                                                                                                                                                                         |
| `Domain Users`                       | This group contains all user accounts in a domain. A new user account created in the domain is automatically added to this group.                                                                                                                                                                                                                                                 |
| `Enterprise Admins`                  | Membership in this group provides complete configuration access within the domain. The group only exists in the root domain of an AD forest. Members in this group are granted the ability to make forest-wide changes such as adding a child domain or creating a trust. The Administrator account for the forest root domain is the only member of this group by default.       |
| `Event Log Readers`                  | Members can read event logs on local computers. The group is only created when a host is promoted to a domain controller.                                                                                                                                                                                                                                                         |
| `Group Policy Creator Owners`        | Members create, edit, or delete Group Policy Objects in the domain.                                                                                                                                                                                                                                                                                                               |
| `Hyper-V Administrators`             | Members have complete and unrestricted access to all the features in Hyper-V. If there are virtual DCs in the domain, any virtualization admins, such as members of Hyper-V Administrators, should be considered Domain Admins.                                                                                                                                                   |
| `IIS_IUSRS`                          | This is a built-in group used by Internet Information Services (IIS), beginning with IIS 7.0.                                                                                                                                                                                                                                                                                     |
| `Pre–Windows 2000 Compatible Access` | This group exists for backward compatibility for computers running Windows NT 4.0 and earlier. Membership in this group is often a leftover legacy configuration. It can lead to flaws where anyone on the network can read information from AD without requiring a valid AD username and password.                                                                               |
| `Print Operators`                    | Members can manage, create, share, and delete printers that are connected to domain controllers in the domain along with any printer objects in AD. Members are allowed to log on to DCs locally and may be used to load a malicious printer driver and escalate privileges within the domain.                                                                                    |
| `Protected Users`                    | Members of this [group](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/active-directory-security-groups#protected-users) are provided additional protections against credential theft and tactics such as Kerberos abuse.                                                                                                                   |
| `Read-only Domain Controllers`       | Contains all Read-only domain controllers in the domain.                                                                                                                                                                                                                                                                                                                          |
| `Remote Desktop Users`               | This group is used to grant users and groups permission to connect to a host via Remote Desktop (RDP). This group cannot be renamed, deleted, or moved.                                                                                                                                                                                                                           |
| `Remote Management Users`            | This group can be used to grant users remote access to computers via [Windows Remote Management (WinRM)](https://docs.microsoft.com/en-us/windows/win32/winrm/portal)                                                                                                                                                                                                             |
| `Schema Admins`                      | Members can modify the Active Directory schema, which is the way all objects with AD are defined. This group only exists in the root domain of an AD forest. The Administrator account for the forest root domain is the only member of this group by default.                                                                                                                    |
| `Server Operators`                   | This group only exists on domain controllers. Members can modify services, access SMB shares, and backup files on domain controllers. By default, this group has no members.                                                                                                                                                                                                      |

Below we have provided some output regarding domain admins and server operators.

**Server Operators Group Details**

As we can see above, the default state of the `Server Operators` group is to have no members and is a domain local group by default. In contrast, the `Domain Admins` group seen below has several members and service accounts assigned to it. Domain Admins are also Global groups instead of domain local. More on group membership can be found later in this module. Be wary of who, if anyone, you give access to these groups. An attacker could easily gain the keys to the enterprise if they gain access to a user assigned to these groups.

**Domain Admins Group Membership**

***

### User Rights Assignment

Depending on their current group membership, and other factors such as privileges that administrators can assign via Group Policy (GPO), users can have various rights assigned to their account. This Microsoft article on [User Rights Assignment](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/user-rights-assignment) provides a detailed explanation of each of the user rights that can be set in Windows. Not every right listed here is important to us from a security standpoint as penetration testers or defenders, but some rights granted to an account can lead to unintended consequences such as privilege escalation or access to sensitive files. For example, let's say we can gain write access over a Group Policy Object (GPO) applied to an OU containing one or more users that we control. In this example, we could potentially leverage a tool such as [SharpGPOAbuse](https://github.com/FSecureLABS/SharpGPOAbuse) to assign targeted rights to a user. We may perform many actions in the domain to further our access with these new rights. A few examples include:

| **Privilege**                   | **Description**                                                                                                                                                                                                                                                                                   |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SeRemoteInteractiveLogonRight` | This privilege could give our target user the right to log onto a host via Remote Desktop (RDP), which could potentially be used to obtain sensitive data or escalate privileges.                                                                                                                 |
| `SeBackupPrivilege`             | This grants a user the ability to create system backups and could be used to obtain copies of sensitive system files that can be used to retrieve passwords such as the SAM and SYSTEM Registry hives and the NTDS.dit Active Directory database file.                                            |
| `SeDebugPrivilege`              | This allows a user to debug and adjust the memory of a process. With this privilege, attackers could utilize a tool such as [Mimikatz](https://github.com/ParrotSec/mimikatz) to read the memory space of the Local System Authority (LSASS) process and obtain any credentials stored in memory. |
| `SeImpersonatePrivilege`        | This privilege allows us to impersonate a token of a privileged account such as `NT AUTHORITY\SYSTEM`. This could be leveraged with a tool such as JuicyPotato, RogueWinRM, PrintSpoofer, etc., to escalate privileges on a target system.                                                        |
| `SeLoadDriverPrivilege`         | A user with this privilege can load and unload device drivers that could potentially be used to escalate privileges or compromise a system.                                                                                                                                                       |
| `SeTakeOwnershipPrivilege`      | This allows a process to take ownership of an object. At its most basic level, we could use this privilege to gain access to a file share or a file on a share that was otherwise not accessible to us.                                                                                           |

There are many techniques available to abuse user rights detailed [here](https://blog.palantir.com/windows-privilege-abuse-auditing-detection-and-defense-3078a403d74e) and [here](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/privilege-escalation-abusing-tokens.html). Though outside the scope of this module, it is essential to understand the impact that assigning the wrong privilege to an account can have within Active Directory. A small admin mistake can lead to a complete system or enterprise compromise.

***

### Viewing a User's Privileges

After logging into a host, typing the command `whoami /priv` will give us a listing of all user rights assigned to the current user. Some rights are only available to administrative users and can only be listed/leveraged when running an elevated CMD or PowerShell session. These concepts of elevated rights and [User Account Control (UAC)](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/how-user-account-control-works) are security features introduced with Windows Vista that default to restricting applications from running with full permissions unless absolutely necessary. If we compare and contrast the rights available to us as an admin in a non-elevated console vs. an elevated console, we will see that they differ drastically. First, let's look at the rights available to a standard Active Directory user.

**Standard Domain User's Rights**

```powershell
PS C:\htb> whoami /priv PRIVILEGES INFORMATION ---------------------- Privilege Name                Description                    State ============================= ============================== ======== SeChangeNotifyPrivilege       Bypass traverse checking       Enabled SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

We can see that the rights are very `limited`, and none of the "dangerous" rights outlined above are present. Next, let's take a look at a privileged user. Below are the rights available to a Domain Admin user.

**Domain Admin Rights Non-Elevated**

We can see the following in a `non-elevated` console which does not appear to be anything more than available to the standard domain user. This is because, by default, Windows systems do not enable all rights to us unless we run the CMD or PowerShell console in an elevated context. This is to prevent every application from running with the highest possible privileges. This is controlled by something called [User Account Control (UAC)](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/how-user-account-control-works) which is covered in-depth in the [Windows Privilege Escalation](https://academy.hackthebox.com/course/preview/windows-privilege-escalation) module.

```powershell
PS C:\htb> whoami /priv PRIVILEGES INFORMATION ---------------------- Privilege Name                Description                          State ============================= ==================================== ======== SeShutdownPrivilege           Shut down the system                 Disabled SeChangeNotifyPrivilege       Bypass traverse checking             Enabled SeUndockPrivilege             Remove computer from docking station Disabled SeIncreaseWorkingSetPrivilege Increase a process working set       Disabled SeTimeZonePrivilege           Change the time zone                 Disabled
```

**Domain Admin Rights Elevated**

If we enter the same command from an elevated PowerShell console, we can see the complete listing of rights available to us:   User rights increase based on the groups they are placed in or their assigned privileges. Below is an example of the rights granted to a `Backup Operators` group member. Users in this group have other rights currently restricted by UAC (additional rights such as the powerful `SeBackupPrivilege` are not enabled by default in a standard console session). Still, we can see from this command that they have the `SeShutdownPrivilege`, which means they can shut down a domain controller. This privilege on its own could not be used to gain access to sensitive data but could cause a massive service interruption should they log onto a domain controller locally (not remotely via RDP or WinRM).

**Backup Operator Rights**

```powershell
PS C:\htb> whoami /priv PRIVILEGES INFORMATION ---------------------- Privilege Name                Description                    State ============================= ============================== ======== SeShutdownPrivilege           Shut down the system           Disabled SeChangeNotifyPrivilege       Bypass traverse checking       Enabled SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

As attackers and defenders, we need to understand the rights that are granted to users via membership from built-in security groups in Active Directory. It's not uncommon to find seemingly low privileged users added to one or more of these groups, which can be used to further access or compromise the domain. Access to these groups should be strictly controlled. It is typically best practice to leave most of these groups empty and only add an account to a group if a one-off action needs to be performed or a repetitive task needs to be set up. Any accounts added to one of the groups discussed in this section or granted extra privileges should be strictly controlled and monitored, assigned a very strong password or passphrase, and should be separate from an account used by a sysadmin to perform their day-to-day duties.

Now that we've begun to touch on some security considerations in AD related to user privileges and built-in group membership let's walk through some critical points for securing an Active Directory installation.
