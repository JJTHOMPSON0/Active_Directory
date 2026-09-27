# Windows Sessions
#### Interactive

An interactive, or local logon session, is initiated by a user authenticating to a local or domain system by entering their credentials. An interactive logon can be initiated by logging directly into the system, by requesting a secondary logon session using the `runas` command via the command line, or through a Remote Desktop connection.

#### Non-interactive

Non-interactive accounts in Windows differ from standard user accounts as they do not require login credentials. There are 3 types of non-interactive accounts: the Local System Account, Local Service Account, and the Network Service Account. Non-interactive accounts are generally used by the Windows operating system to automatically start services and applications without requiring user interaction. These accounts have no password associated with them and are usually used to start services when the system boots or to run scheduled tasks.

There are differences between the three types of accounts:

| Account                 | Description                                                                                                                                                                                                                                                            |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Local System Account    | Also known as the `NT AUTHORITY\SYSTEM` account, this is the most powerful account in Windows systems. It is used for a variety of OS-related tasks, such as starting Windows services. This account is more powerful than accounts in the local administrators group. |
| Local Service Account   | Known as the `NT AUTHORITY\LocalService` account, this is a less privileged version of the SYSTEM account and has similar privileges to a local user account. It is granted limited functionality and can start some services.                                         |
| Network Service Account | This is known as the `NT AUTHORITY\NetworkService` account and is similar to a standard domain user account. It has similar privileges to the Local Service Account on the local machine. It can establish authenticated sessions for certain network services.        |

# Interacting with the Windows Operating System

## Remote Desktop Protocol (RDP)

[RDP](https://support.microsoft.com/en-us/help/186607/understanding-the-remote-desktop-protocol-rdp) is a proprietary Microsoft protocol which allows a user to connect to a remote system over a network connection and obtain a graphical user interface. The user connects using RDP client software to a target system running RDP server software. RDP uses port 3389 to open a dedicated network channel for sending data back and forth. When connecting via RDP, a user can access the GUI as if they were actually sitting at the computer and logging into it locally. RDP is often used by system administrators to administer remote systems quickly. It can also allow users to access their work computers when traveling or working from home after connecting to a Virtual Private Network (VPN).

---

## Windows Command Line

Command-line interfaces give users greater control over their systems and can be used to perform a wide variety of day-to-day, administrative, and troubleshooting tasks. It can be leveraged to introduce automation to perform certain tasks quickly (such as adding many users to a domain at once). In Windows operating systems, the main two ways to interact with the system from the command line are via the Command Prompt (CMD) and PowerShell.

The [Windows Command Reference](https://download.microsoft.com/download/5/8/9/58911986-D4AD-4695-BF63-F734CD4DF8F2/ws-commands.pdf) from Microsoft is a comprehensive A-Z command reference which includes an overview, usage examples, and command syntax for most Windows commands, and familiarity with it is recommended.

---

## CMD

The Command Prompt (cmd.exe) is used to enter and execute commands. A user can enter one-off commands such as `ipconfig` to view IP address information or perform more advanced tasks such as setting up scheduled tasks or creating scripts and batch files. The Command prompt can be opened from the Start Menu, by typing `cmd` in the run dialogue box, or by directly launching the binary from `C:\Windows\system32\cmd.exe`.

After launching `cmd.exe` we can type `help` to see a listing of available commands.

```cmd
C:\htb> help For more information on a specific command, type HELP command-name ASSOC          Displays or modifies file extension associations. ATTRIB         Displays or changes file attributes. BREAK          Sets or clears extended CTRL+C checking. BCDEDIT        Sets properties in boot database to control boot loading. CACLS          Displays or modifies access control lists (ACLs) of files. CALL           Calls one batch program from another. CD             Displays the name of or changes the current directory. CHCP           Displays or sets the active code page number. CHDIR          Displays the name of or changes the current directory. CHKDSK         Checks a disk and displays a status report. CHKNTFS        Displays or modifies the checking of disk at boot time. CLS            Clears the screen. CMD            Starts a new instance of the Windows command interpreter. COLOR          Sets the default console foreground and background colors. COMP           Compares the contents of two files or sets of files. COMPACT        Displays or alters the compression of files on NTFS partitions. CONVERT        Converts FAT volumes to NTFS.  You cannot convert the                current drive. COPY           Copies one or more files to another location. <SNIP>
```

For more information about a specific command, we can type `help <command name>`.

```cmd
C:\htb> help schtasks SCHTASKS /parameter [arguments] Description:     Enables an administrator to create, delete, query, change, run and    end scheduled tasks on a local or remote system. Parameter List:     /Create         Creates a new scheduled task.     /Delete         Deletes the scheduled task(s).     /Query          Displays all scheduled tasks.     /Change         Changes the properties of scheduled task.     /Run            Runs the scheduled task on demand.     /End            Stops the currently running scheduled task.     /ShowSid        Shows the security identifier corresponding to a scheduled task name.     /?              Displays this help message. Examples:     SCHTASKS    SCHTASKS /?    SCHTASKS /Run /?    SCHTASKS /End /?    SCHTASKS /Create /?    SCHTASKS /Delete /?    SCHTASKS /Query  /?    SCHTASKS /Change /?    SCHTASKS /ShowSid /?
```

Note that certain commands have their own help menus, which can be accessed by typing `<command> /?`. For example, information about the `ipconfig` command can be seen below.

```cmd
C:\htb> ipconfig /? USAGE:     ipconfig [/allcompartments] [/? | /all |                                 /renew [adapter] | /release [adapter] |                                 /renew6 [adapter] | /release6 [adapter] |                                 /flushdns | /displaydns | /registerdns |                                 /showclassid adapter |                                 /setclassid adapter [classid] |                                 /showclassid6 adapter |                                 /setclassid6 adapter [classid] ] where     adapter             Connection name                       (wildcard characters * and ? allowed, see examples)     Options:       /?               Display this help message       /all             Display full configuration information.       /release         Release the IPv4 address for the specified adapter.       /release6        Release the IPv6 address for the specified adapter.       /renew           Renew the IPv4 address for the specified adapter.       /renew6          Renew the IPv6 address for the specified adapter.       /flushdns        Purges the DNS Resolver cache.       /registerdns     Refreshes all DHCP leases and re-registers DNS names       /displaydns      Display the contents of the DNS Resolver Cache.       /showclassid     Displays all the dhcp class IDs allowed for adapter.       /setclassid      Modifies the dhcp class id.       /showclassid6    Displays all the IPv6 DHCP class IDs allowed for adapter.       /setclassid6     Modifies the IPv6 DHCP class id. <SNIP
```

---

## PowerShell

Windows PowerShell is a command shell that was designed by Microsoft to be more geared towards system administrators. PowerShell, like the Windows command line, has an interactive command prompt as well as a powerful scripting environment. PowerShell is built on top of the .NET Framework, which is used for building and running applications on Windows. This makes it a very powerful tool for interfacing directly with the operating system.

Like the command prompt, PowerShell gives us direct access to the file system, and we run the majority of the same commands that we can within a cmd shell.

---

## Cmdlets

PowerShell utilizes [cmdlets](https://docs.microsoft.com/en-us/powershell/scripting/developer/cmdlet/cmdlet-overview?view=powershell-7), which are small single-function tools built into the shell. There are more than 100 core cmdlets, and many additional ones have been written, or we can author our own to perform more complex tasks. PowerShell also supports both simple and complex scripts used for system administration tasks, automation, and more.

Cmdlets are in the form of `Verb-Noun`. For example, the command `Get-ChildItem` can be used to list our current directory. Cmdlets also take arguments or flags. We can type `Get-ChildItem -` and hit the tab key to iterate through the arguments. A command such as `Get-ChildItem -Recurse` will show us the contents of our current working directory and all subdirectories. Another example would be `Get-ChildItem -Path C:\Users\Administrator\Documents` to get the contents of another directory. Finally, we can combine arguments such as this to list all subdirectories' contents within another directory recursively: `Get-ChildItem -Path C:\Users\Administrator\Downloads -Recurse`.

---

## Aliases

Many cmdlets in PowerShell also have aliases. For example, the aliases for the cmdlet `Set-Location`, to change directories, is either `cd` or `sl`. Meanwhile, the aliases for `Get-ChildItem` are `ls` and `gci`. We can view all available aliases by typing `Get-Alias`.

```powershell
PS C:\htb> get-alias CommandType     Name                                               Version    Source -----------     ----                                               -------    ------ Alias           % -> ForEach-Object Alias           ? -> Where-Object Alias           ac -> Add-Content Alias           asnp -> Add-PSSnapin Alias           cat -> Get-Content Alias           cd -> Set-Location Alias           CFS -> ConvertFrom-String                          3.1.0.0    Microsoft.PowerShell.Utility Alias           chdir -> Set-Location Alias           clc -> Clear-Content Alias           clear -> Clear-Host Alias           clhy -> Clear-History Alias           cli -> Clear-Item Alias           clp -> Clear-ItemProperty
```


We can also set up our own aliases with `New-Alias` and get the alias for any cmdlet with `Get-Alias -Name`.

```powershell
PS C:\htb> New-Alias -Name "Show-Files" Get-ChildItem PS C:\> Get-Alias -Name "Show-Files" CommandType     Name                                               Version    Source -----------     ----                                               -------    ------ Alias           Show-Files
```

PowerShell has a help system for cmdlets, functions, scripts, and concepts. This is not installed by default, but we can either run the `Get-Help <cmdlet-name> -Online` command to open the online help for a cmdlet or function in our web browser. We can type `Update-Help` to download and install help files locally.

```powershell
PS C:\htb> help TOPIC     Windows PowerShell Help System SHORT DESCRIPTION     Displays help about Windows PowerShell cmdlets and concepts. LONG DESCRIPTION     Windows PowerShell Help describes Windows PowerShell cmdlets,    functions, scripts, and modules, and explains concepts, including    the elements of the Windows PowerShell language.     Windows PowerShell does not include help files, but you can read the    help topics online, or use the Update-Help cmdlet to download help files    to your computer and then use the Get-Help cmdlet to display the help    topics at the command line.     You can also use the Update-Help cmdlet to download updated help files    as they are released so that your local help content is never obsolete.     Without help files, Get-Help displays auto-generated help for cmdlets,    functions, and scripts.   ONLINE HELP    You can find help for Windows PowerShell online in the TechNet Library    beginning at http://go.microsoft.com/fwlink/?LinkID=108518.     To open online help for any cmdlet or function, type:         Get-Help <cmdlet-name> -Online         <SNIP>
```

Typing a command such as `Get-Help Get-AppPackage` will return just the partial help unless the Help files are installed.

```powershell
PS C:\htb>  Get-Help Get-AppPackage NAME     Get-AppxPackage SYNTAX     Get-AppxPackage [[-Name] <string>] [[-Publisher] <string>] [-AllUsers] [-PackageTypeFilter {None | Main |    Framework | Resource | Bundle | Xap | Optional | All}] [-User <string>] [-Volume <AppxVolume>]    [<CommonParameters>] ALIASES     Get-AppPackage REMARKS     Get-Help cannot find the Help files for this cmdlet on this computer. It is displaying only partial help.        -- To download and install Help files for the module that includes this cmdlet, use Update-Help.
```
---

## Running Scripts

The PowerShell ISE (Integrated Scripting Environment) allows users to write PowerShell scripts on the fly. It also has an autocomplete/lookup function for PowerShell commands. The PowerShell ISE allows us to write and run scripts in the same console, which allows for quick debugging.

We can run PowerShell scripts in a variety of ways. If we know the functions, we can run the script either locally or after loading into memory with a download cradle like the below example.

```powershell
PS C:\htb> .\PowerView.ps1;Get-LocalGroup |fl Description     : Users of Docker Desktop Name            : docker-users SID             : S-1-5-21-674899381-4069889467-2080702030-1004 PrincipalSource : Local ObjectClass     : Group Description     : VMware User Group Name            : __vmware__ SID             : S-1-5-21-674899381-4069889467-2080702030-1003 PrincipalSource : Local ObjectClass     : Group Description     : Members of this group can remotely query authorization attributes and permissions for resources on                   this computer. Name            : Access Control Assistance Operators SID             : S-1-5-32-579 PrincipalSource : Local ObjectClass     : Group Description     : Administrators have complete and unrestricted access to the computer/domain Name            : Administrators SID             : S-1-5-32-544 PrincipalSource : Local <SNIP>
```

One common way to work with a script in PowerShell is to import it so that all functions are then available within our current PowerShell console session: `Import-Module .\PowerView.ps1`. We can then either start a command and cycle through the options or type `Get-Module` to list all loaded modules and their associated commands.

```powershell
PS C:\htb> Get-Module | select Name,ExportedCommands | fl Name             : Appx ExportedCommands : {[Add-AppxPackage, Add-AppxPackage], [Add-AppxVolume, Add-AppxVolume], [Dismount-AppxVolume,                    Dismount-AppxVolume], [Get-AppxDefaultVolume, Get-AppxDefaultVolume]...} Name             : Microsoft.PowerShell.LocalAccounts ExportedCommands : {[Add-LocalGroupMember, Add-LocalGroupMember], [Disable-LocalUser, Disable-LocalUser],                    [Enable-LocalUser, Enable-LocalUser], [Get-LocalGroup, Get-LocalGroup]...} Name             : Microsoft.PowerShell.Management ExportedCommands : {[Add-Computer, Add-Computer], [Add-Content, Add-Content], [Checkpoint-Computer,                    Checkpoint-Computer], [Clear-Content, Clear-Content]...} Name             : Microsoft.PowerShell.Utility ExportedCommands : {[Add-Member, Add-Member], [Add-Type, Add-Type], [Clear-Variable, Clear-Variable], [Compare-Object,                    Compare-Object]...} Name             : PSReadline ExportedCommands : {[Get-PSReadLineKeyHandler, Get-PSReadLineKeyHandler], [Get-PSReadLineOption,                    Get-PSReadLineOption], [Remove-PSReadLineKeyHandler, Remove-PSReadLineKeyHandler],                   [Set-PSReadLineKeyHandler, Set-PSReadLineKeyHandler]...}
```

---

## Execution Policy

Sometimes we will find that we are unable to run scripts on a system. This is due to a security feature called the `execution policy`, which attempts to prevent the execution of malicious scripts. The possible policies are:

|**Policy**|**Description**|
|---|---|
|`AllSigned`|All scripts can run, but a trusted publisher must sign scripts and configuration files. This includes both remote and local scripts. We receive a prompt before running scripts signed by publishers that we have not yet listed as either trusted or untrusted.|
|`Bypass`|No scripts or configuration files are blocked, and the user receives no warnings or prompts.|
|`Default`|This sets the default execution policy, `Restricted` for Windows desktop machines and `RemoteSigned` for Windows servers.|
|`RemoteSigned`|Scripts can run but requires a digital signature on scripts that are downloaded from the internet. Digital signatures are not required for scripts that are written locally.|
|`Restricted`|This allows individual commands but does not allow scripts to be run. All script file types, including configuration files (`.ps1xml`), module script files (`.psm1`), and PowerShell profiles (`.ps1`) are blocked.|
|`Undefined`|No execution policy is set for the current scope. If the execution policy for ALL scopes is set to undefined, then the default execution policy of `Restricted` will be used.|
|`Unrestricted`|This is the default execution policy for non-Windows computers, and it cannot be changed. This policy allows for unsigned scripts to be run but warns the user before running scripts that are not from the local intranet zone.|

Below is an example of the current execution policy for all scopes.

```powershell
PS C:\htb> Get-ExecutionPolicy -List         Scope ExecutionPolicy        ----- --------------- MachinePolicy       Undefined    UserPolicy       Undefined      Process       Undefined  CurrentUser       Undefined LocalMachine    RemoteSigned
```

The execution policy is not meant to be a security control that restricts user actions. A user can easily bypass the policy by either typing the script contents directly into the PowerShell window, downloading and invoking the script, or specifying the script as an encoded command. It can also be bypassed by adjusting the execution policy (if the user has the proper rights) or setting the execution policy for the current process scope (which can be done by almost any user as it does not require a configuration change and will only be set for the duration of the user's session).

Below is an example of changing the execution policy for the current process (session).

```powershell
PS C:\htb> Set-ExecutionPolicy Bypass -Scope Process Execution Policy Change The execution policy helps protect you from scripts that you do not trust. Changing the execution policy might expose you to the security risks described in the about_Execution_Policies help topic at https:/go.microsoft.com/fwlink/?LinkID=135170. Do you want to change the execution policy? [Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "N"): Y
```


We can now see that the execution policy has been changed.

```powershell
PS C:\htb>  Get-ExecutionPolicy -List         Scope ExecutionPolicy        ----- --------------- MachinePolicy       Undefined    UserPolicy       Undefined      Process          Bypass  CurrentUser       Undefined LocalMachine    RemoteSigned
```


# Windows Management Instrumentation (WMI)

WMI is a subsystem of PowerShell that provides system administrators with powerful tools for system monitoring. The goal of WMI is to consolidate device and application management across corporate networks. WMI is a core part of the Windows operating system and has come pre-installed since Windows 2000. It is made up of the following components:

|**Component Name**|**Description**|
|---|---|
|WMI service|The Windows Management Instrumentation process, which runs automatically at boot and acts as an intermediary between WMI providers, the WMI repository, and managing applications.|
|Managed objects|Any logical or physical components that can be managed by WMI.|
|WMI providers|Objects that monitor events/data related to a specific object.|
|Classes|These are used by the WMI providers to pass data to the WMI service.|
|Methods|These are attached to classes and allow actions to be performed. For example, methods can be used to start/stop processes on remote machines.|
|WMI repository|A database that stores all static data related to WMI.|
|CIM Object Manager|The system that requests data from WMI providers and returns it to the application requesting it.|
|WMI API|Enables applications to access the WMI infrastructure.|
|WMI Consumer|Sends queries to objects via the CIM Object Manager.|

Some of the uses for WMI are:

- Status information for local/remote systems
- Configuring security settings on remote machines/applications
- Setting and changing user and group permissions
- Setting/modifying system properties
- Code execution
- Scheduling processes
- Setting up logging

These tasks can all be performed using a combination of PowerShell and the WMI Command-Line Interface (WMIC). WMI can be run via the Windows command prompt by typing `WMIC` to open an interactive shell or by running a command directly such as `wmic computersystem get name` to get the hostname. We can view a listing of WMIC commands and aliases by typing `WMIC /?`.

```cmd
C:\htb> wmic /? WMIC is deprecated. [global switches] <command> The following global switches are available: /NAMESPACE           Path for the namespace the alias operate against. /ROLE                Path for the role containing the alias definitions. /NODE                Servers the alias will operate against. /IMPLEVEL            Client impersonation level. /AUTHLEVEL           Client authentication level. /LOCALE              Language id the client should use. /PRIVILEGES          Enable or disable all privileges. /TRACE               Outputs debugging information to stderr. /RECORD              Logs all input commands and output. /INTERACTIVE         Sets or resets the interactive mode. /FAILFAST            Sets or resets the FailFast mode. /USER                User to be used during the session. /PASSWORD            Password to be used for session login. /OUTPUT              Specifies the mode for output redirection. /APPEND              Specifies the mode for output redirection. /AGGREGATE           Sets or resets aggregate mode. /AUTHORITY           Specifies the <authority type> for the connection. /?[:<BRIEF|FULL>]    Usage information. For more information on a specific global switch, type: switch-name /? Press any key to continue, or press the ESCAPE key to stop
```

The following command example lists information about the operating system.

```cmd
C:\htb> wmic os list brief BuildNumber  Organization  RegisteredUser  SerialNumber             SystemDirectory      Version 19041                      Owner           00123-00123-00123-AAOEM  C:\Windows\system32  10.0.19041
```

WMIC uses aliases and associated verbs, adverbs, and switches. The above command example uses `LIST` to show data and the adverb `BRIEF` to provide just the core set of properties. An in-depth listing of verbs, switches, and adverbs is available [here](https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmic). WMI can be used with PowerShell by using the `Get-WmiObject` [module](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-wmiobject?view=powershell-5.1). This module is used to get instances of WMI classes or information about available classes. This module can be used against local or remote machines.

Here we can get information about the operating system.

```powershell
PS C:\htb> Get-WmiObject -Class Win32_OperatingSystem | select SystemDirectory,BuildNumber,SerialNumber,Version | ft SystemDirectory     BuildNumber SerialNumber            Version ---------------     ----------- ------------            ------- C:\Windows\system32 19041       00123-00123-00123-AAOEM 10.0.19041
```

We can also use the `Invoke-WmiMethod` [module](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/invoke-wmimethod?view=powershell-5.1), which is used to call the methods of WMI objects. A simple example is renaming a file. We can see that the command completed properly because the `ReturnValue` is set to 0.

```powershell
PS C:\htb> Invoke-WmiMethod -Path "CIM_DataFile.Name='C:\users\public\spns.csv'" -Name Rename -ArgumentList "C:\Users\Public\kerberoasted_users.csv" __GENUS          : 2 __CLASS          : __PARAMETERS __SUPERCLASS     : __DYNASTY        : __PARAMETERS __RELPATH        : __PROPERTY_COUNT : 1 __DERIVATION     : {} __SERVER         : __NAMESPACE      : __PATH           : ReturnValue      : 0 PSComputerName   :
```

This section provides a brief overview of `WMI`, `WMIC`, and combining `WMIC` and `PowerShell`. `WMI` has a wide variety of uses for both blue team and red team operators. Later sections of this course will show some ways that `WMI` can be leveraged offensively for both enumeration and lateral movement.