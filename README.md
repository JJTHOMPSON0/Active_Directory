---
hidden: true
---

# README

A beginner-friendly collection of notes on Active Directory and Windows internals, covering enumeration, attacks, privilege escalation, and C2 frameworks.

> 📖 **Read the full notes on GitBook** _(link your GitBook space here)_

***

## 📁 Structure

```
active_directory/
├── intro/                   # AD fundamentals, protocols, users, policies
├── enumeration_and_attacks/ # Enumeration techniques, exploits, lateral movement
└── command_and_control/
    └── sliver/              # Sliver C2 framework

windows/                     # Windows OS fundamentals & internals
```

***

## 🗂️ Topics

### Active Directory — Intro

| Note                                                                                       | Description                  |
| ------------------------------------------------------------------------------------------ | ---------------------------- |
| [Active Directory Fundamentals](<active_directory/intro/Active Directory Fundamentals.md>) | Core AD concepts             |
| [Active Directory Protocols](<active_directory/intro/Active Directory Protocols.md>)       | LDAP, Kerberos, NTLM etc.    |
| [All About Users](<active_directory/intro/All About Users.md>)                             | User objects and attributes  |
| [RODCs](active_directory/intro/RODCs.md)                                                   | Read-Only Domain Controllers |
| [Securities and Policies](<active_directory/intro/Securities and Policies.md>)             | GPOs and security policies   |

### Active Directory — Enumeration & Attacks

| Note                                                                                                   | Description                 |
| ------------------------------------------------------------------------------------------------------ | --------------------------- |
| [AD Enumeration](<active_directory/enumeration_and_attacks/Active Directory Enumeration.md>)           | Full enumeration cheatsheet |
| [Kerberoasting](active_directory/enumeration_and_attacks/Kerberoasting.md)                             | SPN-based hash cracking     |
| [AD CS ESC8](<active_directory/enumeration_and_attacks/AD CS ESC8.md>)                                 | Certificate Services abuse  |
| [BadSuccessor](active_directory/enumeration_and_attacks/BadSuccessor.md)                               | dMSA privilege escalation   |
| [Cross-Forests Trusts Abuse](<active_directory/enumeration_and_attacks/Cross-Forests Trusts Abuse.md>) | Forest trust attacks        |
| [MSSQL Attacks](<active_directory/enumeration_and_attacks/MSSQL ATTACKS.md>)                           | SQL Server lateral movement |
| [GodPotato (LPE)](<active_directory/enumeration_and_attacks/GodPotato (LPE).md>)                       | Local privilege escalation  |
| _(and more...)_                                                                                        |                             |

### Windows Fundamentals

| Note                                                                                | Description               |
| ----------------------------------------------------------------------------------- | ------------------------- |
| [Core of the OS](<windows/Core of the Operating System.md>)                         | Kernel, processes, memory |
| [Interacting with Windows](<windows/Interacting with Windows.md>)                   | CLI, PowerShell, GUI      |
| [Working with Services & Processes](<windows/Working with Service & Processess.md>) | Service management        |

***

## 🤝 Contributing

Open to contributions! Notes are continuously updated. PRs and suggestions are welcome.
