The [Windows client authentication process](https://docs.microsoft.com/en-us/windows-server/security/windows-authentication/credentials-processes-in-windows-authentication) involves multiple modules responsible for logon, credential retrieval, and verification. Among the various authentication mechanisms in Windows, Kerberos is one of the most widely used and complex. The [Local Security Authority](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection) (`LSA`) is a protected subsystem that authenticates users, manages local logins, oversees all aspects of local security, and provides services for translating between user names and security identifiers (SIDs).

The security subsystem maintains security policies and user accounts on a computer system. On a Domain Controller, these policies and accounts apply to the entire domain and are stored in Active Directory. Additionally, the LSA subsystem provides services for access control, permission checks, and the generation of security audit messages.

#### Windows authentication process diagram

![Diagram of Windows Authentication Process showing interactions between WinLogon.exe, LogonUI, lsass.exe, and authentication packages like NTLM and Kerberos.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/Auth_process1.png)

Local interactive logon is handled through the coordination of several components: the logon process ([WinLogon](https://www.microsoftpressstore.com/articles/article.aspx?p=2228450&seqNum=8)), the logon user interface process (`LogonUI`), credential providers, the Local Security Authority Subsystem Service (`LSASS`), one or more authentication packages, and either the Security Accounts Manager (`SAM`) or Active Directory. Authentication packages, in this context, are Dynamic-Link Libraries (DLLs) responsible for performing authentication checks. For example, for non-domain-joined and interactive logins, the `Msv1_0.dll` authentication package is typically used.

`WinLogon` is a trusted system process responsible for managing security-related user interactions, such as:

- Launching `LogonUI` to prompt for credentials at login
- Handling password changes
- Locking and unlocking the workstation

To obtain a user's account name and password, WinLogon relies on credential providers installed on the system. These credential providers are `COM` objects implemented as DLLs.

WinLogon is the only process that intercepts login requests from the keyboard, which are sent via RPC messages from `Win32k.sys`. At logon, it immediately launches the `LogonUI` application to present the graphical user interface. Once the user's credentials are collected by the credential provider, WinLogon passes them to the Local Security Authority Subsystem Service (`LSASS`) to authenticate the user.

#### LSASS

The [Local Security Authority Subsystem Service](https://en.wikipedia.org/wiki/Local_Security_Authority_Subsystem_Service) (`LSASS`) is comprised of multiple modules and governs all authentication processes. Located at `%SystemRoot%\System32\Lsass.exe` in the file system, it is responsible for enforcing the local security policy, authenticating users, and forwarding security audit logs to the `Event Log`. In essence, LSASS serves as the gatekeeper in Windows-based operating systems. A more detailed illustration of the LSASS architecture can be found [here](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc961760\(v=technet.10\)?redirectedfrom=MSDN).

|**Authentication Packages**|**Description**|
|---|---|
|`Lsasrv.dll`|The LSA Server service both enforces security policies and acts as the security package manager for the LSA. The LSA contains the Negotiate function, which selects either the NTLM or Kerberos protocol after determining which protocol is to be successful.|
|`Msv1_0.dll`|Authentication package for local machine logons that don't require custom authentication.|
|`Samsrv.dll`|The Security Accounts Manager (SAM) stores local security accounts, enforces locally stored policies, and supports APIs.|
|`Kerberos.dll`|Security package loaded by the LSA for Kerberos-based authentication on a machine.|
|`Netlogon.dll`|Network-based logon service.|
|`Ntdsa.dll`|Directory System Agent (DSA) that manages the Active Directory database (ntds.dit), processes LDAP queries, and handles replication between domain controllers. Only loaded on Domain Controllers.|

Source: [Microsoft Docs](https://docs.microsoft.com/en-us/windows-server/security/windows-authentication/credentials-processes-in-windows-authentication).

Each interactive logon session creates a separate instance of the WinLogon service. The [Graphical Identification and Authentication](https://docs.microsoft.com/en-us/windows/win32/secauthn/gina) (`GINA`) architecture is loaded into the process area used by WinLogon, receives and processes the credentials, and invokes the authentication interfaces via the [LSALogonUser](https://docs.microsoft.com/en-us/windows/win32/api/ntsecapi/nf-ntsecapi-lsalogonuser) function.

#### SAM database

The [Security Account Manager](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc756748\(v=ws.10\)?redirectedfrom=MSDN) (`SAM`) is a database file in Windows operating systems that stores user account credentials. It is used to authenticate both local and remote users and uses cryptographic protections to prevent unauthorized access. User passwords are stored as hashes in the registry, typically in the form of either `LM` or `NTLM` hashes. The SAM file is located at `%SystemRoot%\system32\config\SAM` and is mounted under `HKLM\SAM`. Viewing or accessing this file requires `SYSTEM` level privileges.

Windows systems can be assigned to either a workgroup or domain during setup. If the system has been assigned to a workgroup, it handles the SAM database locally and stores all existing users locally in this database. However, if the system has been joined to a domain, the Domain Controller (`DC`) must validate the credentials from the Active Directory database (`ntds.dit`), which is stored in `%SystemRoot%\NTDS\ntds.dit`.

To improve protection against offline cracking of the SAM database, Microsoft introduced a feature in Windows NT 4.0 called `SYSKEY` (`syskey.exe`). When enabled, SYSKEY partially encrypts the SAM file on disk, ensuring that password hashes for all local accounts are encrypted with a system-generated key.

#### Credential Manager

![Diagram of Windows logon process showing interactions between user input, Logon UI, Credential Provider, WinLogon, and Local Security Authority.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/308/img/authn_credman_credprov.png)

Source: [Microsoft Docs](https://docs.microsoft.com/en-us/windows-server/security/windows-authentication/credentials-processes-in-windows-authentication).

Credential Manager is a built-in feature of all Windows operating systems that allows users to store and manage credentials used to access network resources, websites, and applications. These saved credentials are stored per user profile in the user's `Credential Locker`. The credentials are encrypted and stored at the following location:

```powershell
PS C:\Users\[Username]\AppData\Local\Microsoft\[Vault/Credentials]\
```

There are various methods to decrypt credentials saved using Credential Manager. We will practice hands-on with some of these methods in this module.