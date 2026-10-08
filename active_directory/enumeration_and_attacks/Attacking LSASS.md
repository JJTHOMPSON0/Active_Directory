In addition to acquiring copies of the SAM database to extract and crack password hashes, we will also benefit from targeting the [Local Security Authority Subsystem Service (LSASS)](https://en.wikipedia.org/wiki/Local_Security_Authority_Subsystem_Service).LSASS is a core Windows process responsible for enforcing security policies, handling user authentication, and storing sensitive credential material in memory.

![Diagram of Windows authentication process showing interactions between WinLogon.exe, lsass.exe, authentication packages, NTLM, and Kerberos.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/lsassexe_diagram.png)

Upon initial logon, LSASS will:

- Cache credentials locally in memory
- Create [access tokens](https://docs.microsoft.com/en-us/windows/win32/secauthz/access-tokens)
- Enforce security policies
- Write to Windows' [security log](https://docs.microsoft.com/en-us/windows/win32/eventlog/event-logging-security)

Let's cover some of the techniques and tools we can use to dump LSASS memory and extract credentials from a target running Windows.

## Dumping LSASS process memory

Similar to the process of attacking the SAM database, it would be wise for us first to create a copy of the contents of LSASS process memory via the generation of a memory dump. Creating a dump file lets us extract credentials offline using our attack host. Keep in mind conducting attacks offline gives us more flexibility in the speed of our attack and requires less time spent on the target system. There are countless methods we can use to create a memory dump, so let's cover techniques that can be performed using tools already built into Windows.

#### Task Manager method

With access to an interactive graphical session on the target, we can use task manager to create a memory dump. This requires us to:

1. Open `Task Manager`
2. Select the `Processes` tab
3. Find and right click the `Local Security Authority Process`
4. Select `Create dump file`

![Task Manager showing Local Security Authority Process with right-click menu open, highlighting 'Create dump file' option, and lsass.DMP file in search results.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/taskmanagerdump.png)

A file called `lsass.DMP` is created and saved in `%temp%`. This is the file we will transfer to our attack host. We can use the file transfer method discussed in the previous section of this module to transfer the dump file to our attack host.

#### Rundll32.exe & Comsvcs.dll method

The Task Manager method is dependent on us having a GUI-based interactive session with a target. We can use an alternative method to dump LSASS process memory through a command-line utility called [rundll32.exe](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/rundll32). This way is faster than the Task Manager method and more flexible because we may gain a shell session on a Windows host with only access to the command line. It is important to note that modern anti-virus tools recognize this method as malicious activity.

Before issuing the command to create the dump file, we must determine what process ID (`PID`) is assigned to `lsass.exe`. This can be done from cmd or PowerShell:

#### Finding LSASS's PID in cmd

From cmd, we can issue the command `tasklist /svc` to find `lsass.exe` and its process ID.

![](../../../ZMEDIA/Pasted%20image%2020261008220507.png)

#### Finding LSASS's PID in PowerShell

From PowerShell, we can issue the command `Get-Process lsass` and see the process ID in the `Id` field.

![](../../../ZMEDIA/Pasted%20image%2020261008220524.png)
Once we have the PID assigned to the LSASS process, we can create a dump file.

#### Creating a dump file using PowerShell

With an elevated PowerShell session, we can issue the following command to create a dump file:

```powershell
PS C:\Windows\system32> rundll32 C:\windows\system32\comsvcs.dll, MiniDump 672 C:\lsass.dmp full
```

With this command, we are running `rundll32.exe` to call an exported function of `comsvcs.dll` which also calls the MiniDumpWriteDump (`MiniDump`) function to dump the LSASS process memory to a specified directory (`C:\lsass.dmp`). Recall that most modern AV tools recognize this as malicious activity and prevent the command from executing. In these cases, we will need to consider ways to bypass or disable the AV tool we are facing. AV bypassing techniques are outside of the scope of this module.

If we manage to run this command and generate the `lsass.dmp` file, we can proceed to transfer the file onto our attack box to attempt to extract any credentials that may have been stored in LSASS process memory.

## Using Pypykatz to extract credentials

Once we have the dump file on our attack host, we can use a powerful tool called [pypykatz](https://github.com/skelsec/pypykatz) to extract credentials from the `.dmp` file. Pypykatz is an implementation of Mimikatz written entirely in Python. 
#### Running Pypykatz

The command initiates the use of `pypykatz` to parse the secrets hidden in the LSASS process memory dump. We use `lsa` in the command because LSASS is a subsystem of the `Local Security Authority`, then we specify the data source as a `minidump` file, proceeded by the path to the dump file stored on our attack host. Pypykatz parses the dump file and outputs the findings:

 ![](../../../ZMEDIA/Pasted%20image%2020261008220656.png)

Lets take a more detailed look at some of the useful information in the output.

#### MSV

![](../../../ZMEDIA/Pasted%20image%2020261008220709.png)

[MSV](https://docs.microsoft.com/en-us/windows/win32/secauthn/msv1-0-authentication-package) is an authentication package in Windows that LSA calls on to validate logon attempts against the SAM database. Pypykatz extracted the `SID`, `Username`, `Domain`, and even the `NT` & `SHA1` password hashes associated with the bob user account's logon session stored in LSASS process memory. This will prove helpful in the next step of our attack covered at the end of this section.

#### WDIGEST

![](../../../ZMEDIA/Pasted%20image%2020261008220724.png)

`WDIGEST` is an older authentication protocol enabled by default in `Windows XP` - `Windows 8` and `Windows Server 2003` - `Windows Server 2012`. LSASS caches credentials used by WDIGEST in clear-text. This means if we find ourselves targeting a Windows system with WDIGEST enabled, we will most likely see a password in clear-text. Modern Windows operating systems have WDIGEST disabled by default. Additionally, it is essential to note that Microsoft released a security update for systems affected by this issue with WDIGEST. We can study the details of that security update [here](https://msrc-blog.microsoft.com/2014/06/05/an-overview-of-kb2871997/).

#### Kerberos

![](../../../ZMEDIA/Pasted%20image%2020261008220740.png)

[Kerberos](https://web.mit.edu/kerberos/#what_is) is a network authentication protocol used by Active Directory in Windows Domain environments. Domain user accounts are granted tickets upon authentication with Active Directory. This ticket is used to allow the user to access shared resources on the network that they have been granted access to without needing to type their credentials each time. LSASS caches `passwords`, `ekeys`, `tickets`, and `pins` associated with Kerberos. It is possible to extract these from LSASS process memory and use them to access other systems joined to the same domain.

#### DPAPI

![](../../../ZMEDIA/Pasted%20image%2020261008220755.png)

Mimikatz and Pypykatz can extract the DPAPI `masterkey` for logged-on users whose data is present in LSASS process memory. These masterkeys can then be used to decrypt the secrets associated with each of the applications using DPAPI and result in the capturing of credentials for various accounts. DPAPI attack techniques are covered in greater detail in the [Windows Privilege Escalation](https://academy.hackthebox.com/module/details/67) module.