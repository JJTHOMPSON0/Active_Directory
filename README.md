# HOME

## 🛡️ Welcome to the Security Knowledge Base

A practical, beginner-to-advanced reference library covering Active Directory exploitation, Windows OS internals, privilege escalation, and Command & Control operations.

Use the categories below to jump into any module.

***

### 📚 Explore by Category

#### 🏢 1. [Introduction to Active Directory](<active_directory/intro/Active Directory Fundamentals.md>)

Understand how Active Directory is structured, how authentication works, and how policies govern enterprise networks.

* **Active Directory Fundamentals** — Forests, domains, trusts, OUs, and objects.
* **Active Directory Protocols** — Deep dive into LDAP, Kerberos, SMB, and RPC.
* **All About Users** — User accounts, service accounts, and attributes.
* **RODCs (Read-Only Domain Controllers)** — Architecture and credential caching.
* **Securities and Policies** — GPOs, password policies, and security baselines.

***

#### ⚔️ 2. [Active Directory Attacks & Enumeration](<active_directory/enumeration_and_attacks/Active Directory Enumeration.md>)

Actionable attack guides, credential harvesting techniques, and privilege escalation vectors.

* **Active Directory Enumeration** — Full enumeration cheatsheet.
* **Kerberoasting** — Service Principal Name (SPN) extraction and cracking.
* **AD CS ESC8** — Active Directory Certificate Services NTLM relaying.
* **AD Delegation (RBCD)** — Resource-Based Constrained Delegation abuse.
* **BadSuccessor** — Delegated Managed Service Account (dMSA) exploitation.
* **BloodHound Alternative** — Graph visualization and graph-less alternatives.
* **GodPotato (Local Privilege Escalation)** — Abusing `SeImpersonatePrivilege` to SYSTEM.
* **MSSQL Attacks** — Database link crawling and command execution.

***

#### 💻 3. [Windows Fundamentals & Internals](<windows/Core of the Operating System.md>)

Essential Windows operating system mechanisms, architecture, and administration tools.

* **Core of the Operating System** — File systems, NTFS permissions, and system architecture.
* **Interacting with Windows** — CMD, PowerShell, and system navigation.
* **Deep into Windows** — Registry, SAM hive, and system configuration.
* **Working with Services & Processes** — Windows services, process trees, and privileges.
* **Further Windows Usage** — System management and utility tools.

***

#### 🎯 4. [Command & Control (C2)](<active_directory/command_and_control/sliver/Sliver download and CLI.md>)

Frameworks and operational infrastructure for post-exploitation.

* **Sliver Download and CLI** — Setting up BishopFox's Sliver C2, listeners, and implants.

***

### 🙏 Acknowledgements & Credits

* [**HackTheBox**](https://www.hackthebox.com/) **& HTB Academy** — Invaluable labs, realistic Active Directory attack paths, and high-quality module content that formed the foundation for many of the techniques and scenarios documented here.
* [**ChatGPT (OpenAI)**](https://chatgpt.com/) — Assisted in structuring, refining, debugging commands, and synthesizing concepts into accessible cheatsheets and explanations.
