
## Operating system structure

In Windows operating systems, the root directory is <drive_letter>:\ (commonly C drive). The root directory (also known as the boot partition) is where the operating system is installed. Other physical and virtual drives are assigned other letters, for example, Data (E:). The directory structure of the boot partition is as follows:

|Directory|Function|
|---|---|
|Perflogs|Can hold Windows performance logs but is empty by default.|
|Program Files|On 32-bit systems, all 16-bit and 32-bit programs are installed here. On 64-bit systems, only 64-bit programs are installed here.|
|Program Files (x86)|32-bit and 16-bit programs are installed here on 64-bit editions of Windows.|
|ProgramData|This is a hidden folder that contains data that is essential for certain installed programs to run. This data is accessible by the program no matter what user is running it.|
|Users|This folder contains user profiles for each user that logs onto the system and contains the two folders Public and Default.|
|Default|This is the default user profile template for all created users. Whenever a new user is added to the system, their profile is based on the Default profile.|
|Public|This folder is intended for computer users to share files and is accessible to all users by default. This folder is shared over the network by default but requires a valid network account to access.|
|AppData|Per user application data and settings are stored in a hidden user subfolder (i.e., cliff.moore\AppData). Each of these folders contains three subfolders. The Roaming folder contains machine-independent data that should follow the user's profile, such as custom dictionaries. The Local folder is specific to the computer itself and is never synchronized across the network. LocalLow is similar to the Local folder, but it has a lower data integrity level. Therefore it can be used, for example, by a web browser set to protected or safe mode.|
|Windows|The majority of the files required for the Windows operating system are contained here.|
|System, System32, SysWOW64|Contains all DLLs required for the core features of Windows and the Windows API. The operating system searches these folders any time a program asks to load a DLL without specifying an absolute path.|
|WinSxS|The Windows Component Store contains a copy of all Windows components, updates, and service packs.|

---

### Exploring Directories Using Command Line

We can explore the file system using the [dir](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/dir) command.

```c
C:\htb> dir c:\ /a  Volume in drive C has no label. Volume Serial Number is F416-77BE  Directory of c:\ 08/16/2020  10:33 AM    <DIR>          $Recycle.Bin 06/25/2020  06:25 PM    <DIR>          $WinREAgent 07/02/2020  12:55 PM             1,024 AMTAG.BIN 06/25/2020  03:38 PM    <JUNCTION>     Documents and Settings [C:\Users] 08/13/2020  06:03 PM             8,192 DumpStack.log 08/17/2020  12:11 PM             8,192 DumpStack.log.tmp 08/27/2020  10:42 AM    37,752,373,248 hiberfil.sys 08/17/2020  12:11 PM    13,421,772,800 pagefile.sys 12/07/2019  05:14 AM    <DIR>          PerfLogs 08/24/2020  10:38 AM    <DIR>          Program Files 07/09/2020  06:08 PM    <DIR>          Program Files (x86) 08/24/2020  10:41 AM    <DIR>          ProgramData 06/25/2020  03:38 PM    <DIR>          Recovery 06/25/2020  03:57 PM             2,918 RHDSetup.log 08/17/2020  12:11 PM        16,777,216 swapfile.sys 08/26/2020  02:51 PM    <DIR>          System Volume Information 08/16/2020  10:33 AM    <DIR>          Users 08/17/2020  11:38 PM    <DIR>          Windows                7 File(s) 51,190,943,590 bytes              13 Dir(s)  261,310,697,472 bytes free
```

The [tree](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/tree) utility is useful for graphically displaying the directory structure of a path or disk.

```c
C:\htb> tree "c:\Program Files (x86)\VMware" Folder PATH listing Volume serial number is F416-77BE C:\PROGRAM FILES (X86)\VMWARE ├───VMware VIX │   ├───doc │   │   ├───errors │   │   ├───features │   │   ├───lang │   │   │   └───c │   │   │       └───functions │   │   └───types │   ├───samples │   └───Workstation-15.0.0 │       ├───32bit │       └───64bit └───VMware Workstation     ├───env    ├───hostd    │   ├───coreLocale    │   │   └───en    │   ├───docroot    │   │   ├───client    │   │   └───sdk    │   ├───extensions    │   │   └───hostdiag    │   │       └───locale    │   │           └───en    │   └───vimLocale    │       └───en    ├───ico    ├───messages    │   ├───ja    │   └───zh_CN    ├───OVFTool    │   ├───env    │   │   └───en    │   └───schemas    │       ├───DMTF    │       └───vmware    ├───Resources    ├───tools-upgraders    └───x64
```

The `tree` command can provide us with a large amount of information. The following command can be used to walk through all the files in the C drive, one screen at a time. This command can be modified to be run against any directory.

```c
tree c:\ /f | more
```

## File System

---

There are 5 types of Windows file systems: FAT12, FAT16, FAT32, NTFS, and exFAT. FAT12 and FAT16 are no longer used on modern Windows operating systems. We will touch upon the FAT32 and exFAT file systems for this training, but our main focus will be the NTFS file system.

FAT32 (File Allocation Table) is widely used across many types of storage devices such as USB memory sticks and SD cards but can also be used to format hard drives. The "32" in the name refers to the fact that FAT32 uses 32 bits of data for identifying data clusters on a storage device.

**`Pros of FAT32:`**

- Device compatibility - it can be used on computers, digital cameras, gaming consoles, smartphones, tablets, and more.
- Operating system cross-compatibility - It works on all Windows operating systems starting from Windows 95 and is also supported by MacOS and Linux.

**`Cons of FAT32:`**

- Can only be used with files that are less than 4GB.
- No built-in data protection or file compression features.
- Must use third-party tools for file encryption.

NTFS (New Technology File System) is the default Windows file system since Windows NT 3.1. In addition to making up for the shortcomings of FAT32, NTFS also has better support for metadata and better performance due to improved data structuring.

**`Pros of NTFS:`**

- NTFS is reliable and can restore the consistency of the file system in the event of a system failure or power loss.
- Provides security by allowing us to set granular permissions on both files and folders.
- Supports very large-sized partitions.
- Has journaling built-in, meaning that file modifications (addition, modification, deletion) are logged.

**`Cons of NTFS:`**

- Most mobile devices do not support NTFS natively.
- Older media devices such as TVs and digital cameras do not offer support for NTFS storage devices.

---

### Permissions

The NTFS file system has many basic and advanced permissions. Some of the key permission types are:

|Permission Type|Description|
|---|---|
|Full Control|Allows reading, writing, changing, deleting of files/folders.|
|Modify|Allows reading, writing, and deleting of files/folders.|
|List Folder Contents|Allows for viewing and listing folders and subfolders as well as executing files. Folders only inherit this permission.|
|Read and Execute|Allows for viewing and listing files and subfolders as well as executing files. Files and folders inherit this permission.|
|Write|Allows for adding files to folders and subfolders and writing to a file.|
|Read|Allows for viewing and listing of folders and subfolders and viewing a file's contents.|
|Traverse Folder|This allows or denies the ability to move through folders to reach other files or folders. For example, a user may not have permission to list the directory contents or view files in the documents or web apps directory in this example c:\users\bsmith\documents\webapps\backups\backup_02042020.zip but with Traverse Folder permissions applied, they can access the backup archive.|

Files and folders inherit the NTFS permissions of their parent folder for ease of administration, so administrators do not need to explicitly set permissions for each file and folder, as this would be extremely time-consuming. If permissions do need to be set explicitly, an administrator can disable permissions inheritance for the necessary files and folders and then set the permissions directly on each.

---

### Integrity Control Access Control List (icacls)

NTFS permissions on files and folders in Windows can be managed using the File Explorer GUI under the security tab. Apart from the GUI, we can also achieve a fine level of granularity over NTFS file permissions in Windows from the command line using the icacls utility.

We can list out the NTFS permissions on a specific directory by running either `icacls` from within the working directory or `icacls C:\Windows` against a directory not currently in.

```c
C:\htb> icacls c:\windows c:\windows NT SERVICE\TrustedInstaller:(F)            NT SERVICE\TrustedInstaller:(CI)(IO)(F)           NT AUTHORITY\SYSTEM:(M)           NT AUTHORITY\SYSTEM:(OI)(CI)(IO)(F)           BUILTIN\Administrators:(M)           BUILTIN\Administrators:(OI)(CI)(IO)(F)           BUILTIN\Users:(RX)           BUILTIN\Users:(OI)(CI)(IO)(GR,GE)           CREATOR OWNER:(OI)(CI)(IO)(F)           APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES:(RX)           APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES:(OI)(CI)(IO)(GR,GE)           APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APPLICATION PACKAGES:(RX)           APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APPLICATION PACKAGES:(OI)(CI)(IO)(GR,GE) Successfully processed 1 files; Failed processing 0 files
```

The resource access level is listed after each user in the output. The possible inheritance settings are:

- `(CI)`: container inherit
- `(OI)`: object inherit
- `(IO)`: inherit only
- `(NP)`: do not propagate inherit
- `(I)`: permission inherited from parent container

In the above example, the `NT AUTHORITY\SYSTEM` account has object inherit, container inherit, inherit only, and full access permissions. This means that this account has full control over all file system objects in this directory and subdirectories.

Basic access permissions are as follows:

- `F` : full access
- `D` :  delete access
- `N` :  no access
- `M` :  modify access
- `RX` :  read and execute access
- `R` :  read-only access
- `W` :  write-only access

We can add and remove permissions via the command line using `icacls`. Here we are executing `icacls` in the context of a local administrator account showing the `C:\users` directory where the `joe` user does not have any write permissions.

```c
C:\htb> icacls c:\Users c:\Users NT AUTHORITY\SYSTEM:(OI)(CI)(F)          BUILTIN\Administrators:(OI)(CI)(F)         BUILTIN\Users:(RX)         BUILTIN\Users:(OI)(CI)(IO)(GR,GE)         Everyone:(RX)         Everyone:(OI)(CI)(IO)(GR,GE) Successfully processed 1 files; Failed processing 0 files
```

Using the command `icacls c:\users /grant joe:f` we can grant the joe user full control over the directory, but given that `(oi)` and `(ci)` were not included in the command, the joe user will only have rights over the `c:\users` folder but not over the user subdirectories and files contained within them.

```c
C:\htb> icacls c:\users /grant joe:f processed file: c:\users Successfully processed 1 files; Failed processing 0 files
```

```c
C:\htb> >icacls c:\users c:\users WS01\joe:(F)          NT AUTHORITY\SYSTEM:(OI)(CI)(F)         BUILTIN\Administrators:(OI)(CI)(F)         BUILTIN\Users:(RX)         BUILTIN\Users:(OI)(CI)(IO)(GR,GE)         Everyone:(RX)         Everyone:(OI)(CI)(IO)(GR,GE) Successfully processed 1 files; Failed processing 0 files
```

These permissions can be revoked using the command `icacls c:\users /remove joe`.

`icacls` is very powerful and can be used in a domain setting to give certain users or groups specific permissions over a file or folder, explicitly deny access, enable or disable inheritance permissions, and change directory/file ownership.

A full listing of `icacls` command-line arguments and detailed permission settings can be found [here](https://ss64.com/nt/icacls.html).

## NTFS vs. Share Permissions

---

Microsoft owns over [70%](https://gs.statcounter.com/os-market-share/desktop/worldwide/#monthly-201804-202104) of the global market share on desktop operating systems with Windows. This explains why most malware authors choose to write malware for Windows and why many perceive Windows as less secure than other operating systems. From a business perspective it just makes sense for malware authors to expend resources on writing malware for Windows. It is a high-value target. It is also worth noting that to this day, the infamous `EternalBlue` vulnerability still haunts unpatched Windows systems running `SMBv1` and often paves the way for ransomware to shut down organizations.

The `Server Message Block protocol` (`SMB`) is used in Windows to connect shared resources like files and printers. It is used in large, medium, and small enterprise environments. See the image below to visualize this concept:

![Diagram of file sharing using SMB: A client sends an SMB request to a server, which responds. The server accesses file systems and printers, displaying a file directory.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/smb_diagram.png)


#### Share permissions

|Permission|Description|
|---|---|
|`Full Control`|Users are permitted to perform all actions given by Change and Read permissions as well as change permissions for NTFS files and subfolders|
|`Change`|Users are permitted to read, edit, delete and add files and subfolders|
|`Read`|Users are allowed to view file & subfolder contents|

#### NTFS Basic permissions

| Permission             | Description                                                                                                                         |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `Full Control`         | Users are permitted to add, edit, move, delete files & folders as well as change NTFS permissions that apply to all allowed folders |
| `Modify`               | Users are permitted or denied permissions to view and modify files and folders. This includes adding or deleting files              |
| `Read & Execute`       | Users are permitted or denied permissions to read the contents of files and execute programs                                        |
| `List folder contents` | Users are permitted or denied permissions to view a listing of files and subfolders                                                 |
| `Read`                 | Users are permitted or denied permissions to read the contents of files                                                             |
| `Write`                | Users are permitted or denied permissions to write changes to a file and add new files to a folder                                  |
| `Special Permissions`  | A variety of advanced permissions options                                                                                           |

#### NTFS special permissions

|Permission|Description|
|---|---|
|`Full control`|Users are permitted or denied permissions to add, edit, move, delete files & folders as well as change NTFS permissions that apply to all permitted folders|
|`Traverse folder / execute file`|Users are permitted or denied permissions to access a subfolder within a directory structure even if the user is denied access to contents at the parent folder level. Users may also be permitted or denied permissions to execute programs|
|`List folder/read data`|Users are permitted or denied permissions to view files and folders contained in the parent folder. Users can also be permitted to open and view files|
|`Read attributes`|Users are permitted or denied permissions to view basic attributes of a file or folder. Examples of basic attributes: system, archive, read-only, and hidden|
|`Read extended attributes`|Users are permitted or denied permissions to view extended attributes of a file or folder. Attributes differ depending on the program|
|`Create files/write data`|Users are permitted or denied permissions to create files within a folder and make changes to a file|
|`Create folders/append data`|Users are permitted or denied permissions to create subfolders within a folder. Data can be added to files but pre-existing content cannot be overwritten|
|`Write attributes`|Users are permitted or denied to change file attributes. This permission does not grant access to creating files or folders|
|`Write extended attributes`|Users are permitted or denied permissions to change extended attributes on a file or folder. Attributes differ depending on the program|
|`Delete subfolders and files`|Users are permitted or denied permissions to delete subfolders and files. Parent folders will not be deleted|
|`Delete`|Users are permitted or denied permissions to delete parent folders, subfolders and files.|
|`Read permissions`|Users are permitted or denied permissions to read permissions of a folder|
|`Change permissions`|Users are permitted or denied permissions to change permissions of a file or folder|
|`Take ownership`|Users are permitted or denied permission to take ownership of a file or folder. The owner of a file has full permissions to change any permissions|

Keep in mind that NTFS permissions apply to the system where the folder and files are hosted. Folders created in NTFS inherit permissions from parent folders by default. It is possible to disable inheritance to set custom permissions on parent and subfolders, as we will do later in this module. The share permissions apply when the folder is being accessed through SMB, typically from a different system over the network. This means someone logged in locally to the machine or via RDP can access the shared folder and files by simply navigating to the location on the file system and only need to consider NTFS permissions. The permissions at the NTFS level provide administrators much more granular control over what users can do within a folder or file.

---

### Creating a Network Share

To get a solid fundamental understanding of SMB and it's relationship to NTFS, we will create a network share on the `Windows 10 target box`.

In this case, we will create a shared folder by first creating a new folder on the Windows 10 desktop. Keep in mind that in most large enterprise environments, shares are created on a Storage Area Network (SAN), Network Attached Storage device (NAS), or a separate partition on drives accessed via a server operating system like Windows Server. If we ever come across shares on a desktop operating system, it will either be a small business or it could be a beachhead system used by a penetration tester or malicious attacker to gather and exfiltrate data.

We will go through this process using the GUI in Windows.

#### Creating the Folder

![Windows desktop with a context menu open, showing options for creating new folders, shortcuts, and documents.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/creating_directory.png)

We are going to use the `Advanced Sharing` option to configure our share.

#### Making the Folder a Share

![Windows desktop showing 'Company Data Properties' with advanced sharing settings, including share name, user limit, and comments.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/configuring_share.png)

Notice how the share name automatically defaults to the name of the folder. Also, we can see that it is possible to limit the number of users that can be connected to this share simultaneously. In a real-world environment it is a good practice for administrators to set this number according to the number of users that regularly need access to the resource being shared.

Similar to NTFS permissions, there is an `access control list` (`ACL`) for shared resources. We can consider this the SMB permissions list. Keep in mind that with shared resources, both the SMB and NTFS permissions lists apply to every resource that gets shared in Windows. The ACL contains `access control entries` (`ACEs`). Typically these ACEs are made up of `users` & `groups` (also called security principals) as they are a suitable mechanism for managing and tracking access to shared resources.

Notice the default access control entry and permissions settings.

#### Share Permissions ACL (Sharing Tab)

![Permissions window for 'Company Data' showing 'Everyone' group with read permission allowed.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/share_permissions.png)

For now, we are going to apply these settings to test the effect of this ACL and the permissions applied as-is. We will test connectivity from the Pwnbox by opening terminal and using `smbclient`.

Note: A server is technically a software function used to service the requests of a client. In this case, the Pwnbox is our client, and the Windows 10 target box is our server.

#### Using smbclient to list available shares

```shell
zemar@htb[/htb]$ smbclient -L SERVER_IP -U htb-student Enter WORKGROUP\htb-student's password:      Sharename       Type      Comment    ---------       ----      -------    ADMIN$          Disk      Remote Admin    C$              Disk      Default share    Company Data    Disk    IPC$            IPC       Remote IPC
```

#### Connecting to the Company Data share

```shell
zemar@htb[/htb]$ smbclient '\\SERVER_IP\Company Data' -U htb-student Password for [WORKGROUP\htb-student]: Try "help" to get a list of possible commands. smb: \>
```

What could potentially block us from accessing this share if all our entries are correct and our permissions list has the Everyone group present with at least Read permissions?

---

### Windows Defender Firewall Considerations

It is the Windows Defender Firewall that could potentially be blocking access to the SMB share. Since we are connecting from a Linux-based system the firewall has blocked access from any device that is not joined to the same `workgroup`. It is also important to note that when a Windows system is part of a workgroup, all `netlogon` requests are authenticated against that particular Windows system's `SAM` database. When a Windows system is joined to a Windows Domain environment, all netlogon requests are authenticated against `Active Directory`. The primary difference between a workgroup and a Windows Domain in terms of authentication, is with a workgroup the local SAM database is used and in a Windows Domain a centralized network-based database (Active Directory) is used. We must know this information when attempting to logon & authenticate with a Windows system. Consider where the htb-student account is hosted to properly connect to the target.

In terms of the firewall blocking connections, this can be tested by completely deactivating each firewall profile in Windows or by enabling specific predefined inbound firewall rules in the `Windows Defender Firewall advanced security settings`. Like most firewalls, Windows Defender Firewall permits or denies traffic (access & connection requests in this case) flowing `inbound` &/or `outbound`

The different inbound and outbound rules are associated with the different firewall profiles in defender.

Windows Defender Firewall Profiles:

- `Public`
- `Private`
- `Domain`

It is a best practice to enable predefined rules or add custom exceptions rather than deactivating the firewall altogether. Unfortunately, it is very common for firewalls to be left completely deactivated for the sake of convenience or lack of understanding. Firewall rules on desktop systems can be centrally managed when joined to a Windows Domain environment through the use of Group Policy. Group Policy concepts and configurations are outside of the scope of this module.

Once the proper `inbound` firewall rules are enabled we will successfully connect to the share. Keep in mind that we can only connect to the share because the user account we are using (`htb-student`) is in the `Everyone group`. Recall that we left the specific share permissions for the Everyone group set to Read, which quite literally means we will only be able to Read files on this share. Once a connection is established with a share, we can create a `mount point` from our Pwnbox to the Windows 10 target box's file system. This is where we must also consider that NTFS permissions apply alongside share permissions. Recall that NTFS is the default file system in Windows. Lets jump back to our xfreerdp session with our Windows 10 target box and take a look at the NTFS permissions on the Company Data folder.

#### NTFS Permissions ACL (Security Tab)

![Company Data Properties window showing security permissions for SYSTEM, htb-student, and Administrators, with full control allowed for htb-student.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/ntfs.png)

There's more granular control with NTFS permissions that can be applied to users and groups. Anytime we see a gray checkmark next to a permission, it was inherited from a parent directory. By default, all NTFS permissions are inherited from the parent directory. In the Windows world, the `C:\ drive` is the parent directory to rule all directories unless a system administrator were to disable inheritance inside a newly created folder’s advanced Security settings.

In many cases, the system administrator(s) of an organization would be responsible for deciding what permissions a user or group of users gets over network resources. This is why many spear-phishing attacks are directed at system administrators and other IT leaders. They have lots of influence over what is allowed in the environments they oversee, even more so than an organization's non-technical c-level leaders in many cases. For example, the doctors or executives working in a hospital will not have administrative rights over the network, but the system administrators will.

Now lets give the Everyone group `Full control` at the share level and test the impact of the change by trying to create a mount point to the share from the Desktop of our Pwnbox

#### Mounting to the Share

```shell
zemar@htb[/htb]$ sudo mount -t cifs -o username=htb-student,password=Academy_WinFun! //ipaddoftarget/"Company Data" /home/user/Desktop/
```

If this command is not working check the syntax. If the syntax is correct yet the command is still not working, `cifs-utils` may need to be installed. This can be done with the following command:

#### Installing CIFS Utilities

```shell
zemar@htb[/htb]$ sudo apt-get install cifs-utils
```

Once we have successfully created the mount point on the Desktop on our Pwnbox, we should look at a couple of tools built-in to Windows that will allow us to track and monitor what we have done.

The `net share` command allows us to view all the shared folders on the system. Notice the share we created and also the C:\ drive.

`Do you remember us sharing the C:\ drive?`

We didn't manually share C:. The most important drive with the most critical files on a Windows system is shared via SMB at install. This means anyone with the proper access could remotely access the entire C:\ of each Windows system on a network.

We can also see the share we created.

#### Displaying Shares using net share

```c
C:\Users\htb-student> net share Share name   Resource                        Remark ------------------------------------------------------------------------------- C$           C:\                             Default share IPC$                                         Remote IPC ADMIN$       C:\WINDOWS                      Remote Admin Company Data C:\Users\htb-student\Desktop\Company Data The command completed successfully.
```

`Computer Management` is another tool we can use to identify and monitor shared resources on a Windows system.

#### Monitoring Shares from Computer Management

![Computer Management window showing shared folders, including 'Company Data', with context menu options like expand, manage, and properties.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/computer_management.png)

We can poke around in `Shares`, `Sessions`, and `Open Files` to get an idea of what information this provides us. Should there be a situation where we assist an individual or organization with responding to a breach related to SMB, these are some great places to check and start to understand how the breach may have happened and what may have been left behind.

#### Viewing Share access logs in Event Viewer

`Event Viewer` is another good place to investigate actions completed on Windows. Almost every operating system has a logging mechanism and a utility to view the logs that were captured. Know that a log is like a journal entry for a computer, where the computer writes down all the actions that were performed and numerous details associated with that action. We can view the logs created for every action we performed when accessing the Windows 10 target box, as well as when creating, editing and accessing the shared folder.

![Event Viewer showing security logs with multiple 'Audit Success' entries, highlighting Event ID 5059 for Microsoft Windows security auditing.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/event_viewer.png)

---