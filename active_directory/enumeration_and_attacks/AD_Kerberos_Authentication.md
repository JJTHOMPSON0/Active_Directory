# Active Directory Kerberos & Authentication Notes

## 1. NTDS.dit vs SAM

### NTDS.dit

-   Exists only on Domain Controllers.
-   Stores Active Directory objects:
    -   Domain users
    -   Domain computer accounts
    -   Groups
    -   Password data (encrypted)

To extract domain password hashes you typically need: - `NTDS.dit` -
`SYSTEM` registry hive (contains the BootKey used during decryption).

### SAM

Located at:

`C:\Windows\System32\config\SAM`

Stores **local account** password hashes.

Requires: - `SAM` - `SYSTEM`

to recover local password hashes.

### Important

A promoted Domain Controller no longer authenticates normal local user
accounts through a standalone local SAM for administrative logons; the
built-in Administrator becomes a **domain** account.

------------------------------------------------------------------------

# 2. Windows Logon Types

## Type 2 -- Interactive

Physical or console login. Examples: - Keyboard/monitor - VM console

Creates a full user session.

Useful because credential material may remain in LSASS.

------------------------------------------------------------------------

## Type 3 -- Network

Examples: - SMB - RPC - File shares - WinRM network authentication

No desktop session.

Common during lateral movement.

------------------------------------------------------------------------

## Type 4 -- Batch

Scheduled Tasks.

------------------------------------------------------------------------

## Type 5 -- Service

Windows services.

Examples: - SQL Server - IIS - Exchange

Often run using privileged service accounts.

------------------------------------------------------------------------

## Type 7 -- Unlock

Unlocking an already logged-in workstation.

No new authentication occurs.

------------------------------------------------------------------------

## Type 8 -- NetworkCleartext

Basic authentication and similar protocols.

Credentials may be available in LSASS depending on protocol.

------------------------------------------------------------------------

## Type 9 -- NewCredentials

Created by:

`runas /netonly`

Local identity stays the same.

Remote authentication uses different credentials.

------------------------------------------------------------------------

## Type 10 -- RemoteInteractive

Remote Desktop (RDP).

Creates an interactive desktop session.

------------------------------------------------------------------------

## Type 11 -- CachedInteractive

Domain login using cached credentials when a DC is unavailable.

------------------------------------------------------------------------

# 3. Pass-the-Ticket (/ptt)

`/ptt` = Pass-The-Ticket

Not a PowerShell parameter.

Common in: - Rubeus - Mimikatz

Purpose:

Injects a Kerberos ticket into the current logon session so Windows
immediately begins using it.

Example:

`Rubeus.exe asktgt /user:alice /aes256:<key> /ptt`

Without `/ptt`, the ticket is usually only displayed or saved.

------------------------------------------------------------------------

# 4. Kerberos Ticket Types

## TGT

Ticket Granting Ticket.

Issued by the Authentication Service.

Used to request Service Tickets.

Signed using the KRBTGT account key.

------------------------------------------------------------------------

## TGS

Service Ticket.

Issued for one specific service.

Encrypted using the target service account's key.

------------------------------------------------------------------------

# 5. Golden Ticket

A forged **TGT**.

Requires: - KRBTGT NTLM or AES key.

Capabilities: - Impersonate almost any domain user. - Request legitimate
service tickets across the domain.

Scope: Entire domain.

------------------------------------------------------------------------

# 6. Silver Ticket
HTB machine-***signed***

A forged **Service Ticket (TGS)**.

Requires: - Service account key - Computer account key - NTLM hash or
AES key of that service account

Works only for the targeted service.

Usually bypasses requesting a TGS from the KDC.

Useful even when NTLM pass-the-hash is unsuitable because the target
expects Kerberos.

------------------------------------------------------------------------

# 7. Why Silver Tickets Exist

Knowing a service account's secret lets you:

-   Authenticate with NTLM where supported (Pass-the-Hash), OR
-   Forge Kerberos service tickets.

Silver Tickets are valuable because:

-   Kerberos-only services may reject NTLM.
-   No TGS request is needed from the KDC.
-   The forged ticket can represent another user if accepted by the
    service and environment.

------------------------------------------------------------------------

# 8. Diamond Ticket

A modified legitimate TGT.

Process:

1.  Obtain a genuine TGT.
2.  Modify selected authorization information.
3.  Re-sign with the KRBTGT key.

Requires: - KRBTGT key. - Ability to obtain a legitimate TGT.

Purpose:

Stealth.

Capabilities are essentially the same as a Golden Ticket, but the ticket
more closely resembles one legitimately issued by the KDC.

------------------------------------------------------------------------

# 9. Skeleton Key

Not a ticket attack.

Requires: - SYSTEM-level compromise of a Domain Controller.

Technique:

Patch LSASS in memory so an attacker-chosen password is accepted for
many accounts without changing their real passwords.

Characteristics:

-   Does not modify NTDS.dit.
-   Does not change user passwords.
-   Exists only in memory.
-   Lost after reboot.

------------------------------------------------------------------------

# 10. Comparison

  ----------------------------------------------------------------------------
  Attack            Needs        Forged Object                Scope
  ----------------- ------------ ---------------------------- ----------------
  Golden Ticket     KRBTGT key   TGT                          Entire domain

  Silver Ticket     Service      TGS                          One service
                    account key                               

  Diamond Ticket    KRBTGT key + Modified TGT                 Entire domain
                    legitimate                                
                    TGT                                       

  Skeleton Key      SYSTEM on DC None (patches LSASS)         Authentication
                                                              handled by
                                                              patched DC
  ----------------------------------------------------------------------------

------------------------------------------------------------------------

# Key Takeaways

-   NTDS.dit stores **domain** credentials, not local SAM accounts.
-   SAM + SYSTEM are required for local account hashes.
-   `/ptt` injects Kerberos tickets into the current logon session.
-   Golden Tickets forge TGTs.
-   Silver Tickets forge service tickets.
-   Diamond Tickets modify legitimate TGTs for improved realism.
-   Skeleton Key patches authentication logic rather than forging
    tickets.
