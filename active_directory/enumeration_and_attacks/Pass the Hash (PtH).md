A [Pass the Hash (PtH)](https://attack.mitre.org/techniques/T1550/002/) attack is a technique where an attacker uses a password hash instead of the plain text password for authentication. The attacker doesn't need to decrypt the hash to obtain a plaintext password. PtH attacks exploit the authentication protocol, as the password hash remains static for every session until the password is changed.

Let's assume we obtain the password hash (`64F12CDDAA88057E06A81B54E73B949B`) for the account `julio` from the domain `inlanefreight.htb`. Let's see how we can perform Pass the Hash attacks from Windows and Linux machines.

## Introduction to Windows NTLM

Microsoft's [Windows New Technology LAN Manager (NTLM)](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview) is a set of security protocols that authenticates users' identities while also protecting the integrity and confidentiality of their data. NTLM is a single sign-on (SSO) solution that uses a challenge-response protocol to verify the user's identity without having them provide a password.

Despite its known flaws, NTLM is still commonly used to ensure compatibility with legacy clients and servers, even on modern systems. While Microsoft continues to support NTLM, Kerberos has taken over as the default authentication mechanism in Windows 2000 and subsequent Active Directory (AD) domains.

With NTLM, passwords stored on the server and domain controller are not "salted," which means that an adversary with a password hash can authenticate a session without knowing the original password. We call this a `Pass the Hash (PtH) Attack`.

## Pass the Hash with Mimikatz (Windows)

The first tool we will use to perform a Pass the Hash attack is [Mimikatz](https://github.com/gentilkiwi). Mimikatz has a module named `sekurlsa::pth` that allows us to perform a Pass the Hash attack by starting a process using the hash of the user's password. To use this module, we will need the following:

- `/user` - The user name we want to impersonate.
- `/rc4` or `/NTLM` - NTLM hash of the user's password.
- `/domain` - Domain the user to impersonate belongs to. In the case of a local user account, we can use the computer name, localhost, or a dot (.).
- `/run` - The program we want to run with the user's context (if not specified, it will launch cmd.exe).

#### Pass the Hash from Windows Using Mimikatz
![](../../ZMEDIA/Pasted%20image%2020261008222305.png)

Now we can use cmd.exe to execute commands in the user's context. For this example, `julio` can connect to a shared folder named `julio` on the DC.

![Command prompt showing mimikatz execution with privilege escalation and directory listing commands.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/pth_julio.jpg)

## Pass the Hash with PowerShell Invoke-TheHash (Windows)

Another tool we can use to perform Pass the Hash attacks on Windows is [Invoke-TheHash](https://github.com/Kevin-Robertson/Invoke-TheHash). This tool is a collection of PowerShell functions for performing Pass the Hash attacks with WMI and SMB. WMI and SMB connections are accessed through the .NET TCPClient. Authentication is performed by passing an NTLM hash into the NTLMv2 authentication protocol. Local administrator privileges are not required client-side, but the user and hash we use to authenticate need to have administrative rights on the target computer. For this example we will use the user `julio` and the hash `64F12CDDAA88057E06A81B54E73B949B`.

When using `Invoke-TheHash`, we have two options: SMB or WMI command execution. To use this tool, we need to specify the following parameters to execute commands in the target computer:

- `Target` - Hostname or IP address of the target.
- `Username` - Username to use for authentication.
- `Domain` - Domain to use for authentication. This parameter is unnecessary with local accounts or when using the @domain after the username.
- `Hash` - NTLM password hash for authentication. This function will accept either LM:NTLM or NTLM format.
- `Command` - Command to execute on the target. If a command is not specified, the function will check to see if the username and hash have access to WMI on the target.

The following command will use the SMB method for command execution to create a new user named mark and add the user to the Administrators group.

#### Invoke-TheHash with SMB

![](../../ZMEDIA/Pasted%20image%2020261008222423.png)

We can also get a reverse shell connection in the target machine. 

To get a reverse shell, we need to start our listener using Netcat on our Windows machine, which has the IP address `172.16.1.5`. We will use port `8001` to wait for the connection.

#### Netcat listener

```powershell
PS C:\tools> .\nc.exe -lvnp 8001  listening on [any] 8001 ...
```

To create a simple reverse shell using PowerShell, we can visit [revshells.com](https://www.revshells.com/), set our IP `172.16.1.5` and port `8001`, and select the option `PowerShell #3 (Base64)`, as shown in the following image.

![Reverse Shell Generator interface with IP 172.16.1.5, port 8001, and PowerShell Base64 payload.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/rshellonline.jpg)

Now we can execute `Invoke-TheHash` to execute our PowerShell reverse shell script in the target computer. Notice that instead of providing the IP address, which is `172.16.1.10`, we will use the machine name `DC01` (either would work).

#### Invoke-TheHash with WMI

![](../../ZMEDIA/Pasted%20image%2020261008222516.png)

The result is a reverse shell connection from the DC01 host (172.16.1.10).

![PowerShell and command prompt showing Invoke-TheHash execution with network connection details and whoami command output.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/pth_invoke_the_hash.jpg)

## Pass the Hash with Impacket (Linux)

[Impacket](https://github.com/SecureAuthCorp/impacket) has several tools we can use for different operations such as `Command Execution` and `Credential Dumping`, `Enumeration`, etc. For this example, we will perform command execution on the target machine using `PsExec`.

#### Pass the Hash with Impacket PsExec

![](../../ZMEDIA/Pasted%20image%2020261008222533.png)

There are several other tools in the Impacket toolkit we can use for command execution using Pass the Hash attacks, such as:

- [impacket-wmiexec](https://github.com/SecureAuthCorp/impacket/blob/master/examples/wmiexec.py)
- [impacket-atexec](https://github.com/SecureAuthCorp/impacket/blob/master/examples/atexec.py)
- [impacket-smbexec](https://github.com/SecureAuthCorp/impacket/blob/master/examples/smbexec.py)

## Pass the Hash with NetExec (Linux)

[NetExec](https://github.com/Pennyw0rth/NetExec) is a post-exploitation tool that helps automate assessing the security of large Active Directory networks. We can use NetExec to try to authenticate to some or all hosts in a network looking for one host where we can authenticate successfully as a local admin. 
#### Pass the Hash with NetExec

![](../../ZMEDIA/Pasted%20image%2020261008222549.png)
If we want to perform the same actions but attempt to authenticate to each host in a subnet using the local administrator password hash, we could add `--local-auth` to our command. This method is helpful if we obtain a local administrator hash by dumping the local SAM database on one host and want to check how many (if any) other hosts we can access due to local admin password re-use. If we see `Pwn3d!`, it means that the user is a local administrator on the target computer. We can use the option `-x` to execute commands. It is common to see password reuse against many hosts in the same subnet. Organizations will often use gold images with the same local admin password or set this password the same across multiple hosts for ease of administration. If we run into this issue on a real-world engagement, a great recommendation for the customer is to implement the [Local Administrator Password Solution (LAPS)](https://www.microsoft.com/en-us/download/details.aspx?id=46899), which randomizes the local administrator password and can be configured to have it rotate on a fixed interval.

#### NetExec - Command Execution

![](../../ZMEDIA/Pasted%20image%2020261008222723.png)

Review the [NetExec documentation Wiki](https://www.netexec.wiki/) to learn more about the tool's extensive features.

## Pass the Hash with evil-winrm (Linux)

[Evil-WinRM](https://github.com/Hackplayers/evil-winrm) is another tool we can use to authenticate using the Pass the Hash attack with PowerShell remoting. If SMB is blocked or we don't have administrative rights, we can use this alternative protocol to connect to the target machine.

#### Pass the Hash with evil-winrm
![](../../ZMEDIA/Pasted%20image%2020261008222738.png)

**Note:** When using a domain account, we need to include the domain name, for example: administrator@inlanefreight.htb

## Pass the Hash with RDP (Linux)

We can perform an RDP PtH attack to gain GUI access to the target system using tools like `xfreerdp`.

There are a few caveats to this attack:

- `Restricted Admin Mode`, which is disabled by default, should be enabled on the target host; otherwise, you will be presented with the following error:

![Error message: Account restrictions prevent signing in due to blank passwords, limited sign-in times, or policy restrictions.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/rdp_session-4.png)

This can be enabled by adding a new registry key `DisableRestrictedAdmin` (REG_DWORD) under `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa` with the value of 0. It can be done using the following command:

#### Enable Restricted Admin Mode to allow PtH

```cmd
c:\tools> reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f
```

![Registry Editor showing path to Lsa with DisableRestrictedAdmin set to 0.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/rdp_session-5.png)

Once the registry key is added, we can use `xfreerdp` with the option `/pth` to gain RDP access:

#### Pass the Hash using RDP

![](../../ZMEDIA/Pasted%20image%2020261008222815.png)

![Windows desktop accessed via FreeRDP with Parrot Terminal showing command execution and desktop icons for Recycle Bin, Invoke-TheHash, and mimikatz.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/rdp_session_new.jpg)

## UAC limits Pass the Hash for local accounts

UAC (User Account Control) limits local users' ability to perform remote administration operations. When the registry key `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\LocalAccountTokenFilterPolicy` is set to 0, it means that the built-in local admin account (RID-500, "Administrator") is the only local account allowed to perform remote administration tasks. Setting it to 1 allows the other local admins as well.

**Note:** There is one exception, if the registry key `FilterAdministratorToken` (disabled by default) is enabled (value 1), the RID 500 account (even if it is renamed) is enrolled in UAC protection. This means that remote PTH will fail against the machine when using that account.

These settings are only for local administrative accounts. If we get access to a domain account with administrative rights on a computer, we can still use Pass the Hash with that computer. If you want to learn more about LocalAccountTokenFilterPolicy, you can read Will Schroeder's blog post [Pass-the-Hash Is Dead: Long Live LocalAccountTokenFilterPolicy](https://posts.specterops.io/pass-the-hash-is-dead-long-live-localaccounttokenfilterpolicy-506c25a7c167).