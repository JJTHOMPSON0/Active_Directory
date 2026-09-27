# What is GodPotato?

GodPotato belongs to the **"Potato" family** of Windows privilege escalation techniques:

- RottenPotato
- JuicyPotato
- RoguePotato
- PrintSpoofer
- **GodPotato**

All of them abuse Windows' **token impersonation mechanism**.

The basic idea is:

> "If I already have the privilege to impersonate another user's security token, can I trick Windows into giving me a SYSTEM token?"

GodPotato's answer is **yes**, under the right conditions. It leverages Windows COM/DCOM and RPC behaviour to coerce a SYSTEM component into authenticating locally, then uses the attacker's impersonation privilege to obtain a SYSTEM token and spawn a SYSTEM process.

---

# Where is it used in Active Directory?

This is an important distinction:

**GodPotato is NOT an Active Directory attack.**

It is a **local Windows privilege escalation**.

However, AD environments are full of Windows servers, so you'll see it constantly during AD penetration tests.

Typical attack chain:

```
Compromise Domain User
        │
        ▼
Gain RCE on SQL Server
        │
        ▼
Running as MSSQL service account
        │
        ▼
SeImpersonatePrivilege exists
        │
        ▼
Run GodPotato
        │
        ▼
Become NT AUTHORITY\SYSTEM
        │
        ▼
Dump LSASS
Extract credentials
Steal tickets
Move laterally
```

So in HTB AD labs you'll often see:

```
Kerberoast
      ↓
Crack service account password
      ↓
Login to MSSQL
      ↓
xp_cmdshell
      ↓
GodPotato
      ↓
SYSTEM
      ↓
Dump secrets
```

---

# Why does it work?

Windows services often need to act **on behalf of clients**.

For example:

```
User
  │
  ▼
IIS
```

IIS needs to access files as the user.

Windows therefore gives IIS the privilege:

```
SeImpersonatePrivilege
```

This allows the service to temporarily "become" the client.

GodPotato abuses this feature by convincing a SYSTEM process to authenticate to the attacker-controlled process, then impersonating that SYSTEM token.

---

# Conditions required

## 1. You already have code execution

You must already have a shell on the machine.

For example:

- Web shell
- Reverse shell
- Meterpreter
- Beacon
- Evil-WinRM session
- xp_cmdshell
- Scheduled task

Without code execution:

```
No shell
↓

No GodPotato
```

---

## 2. Your account has SeImpersonatePrivilege (or equivalent)

This is the biggest requirement.

Running:

```
whoami /priv
```

might show:

```
SeImpersonatePrivilege
Enabled
```

or

```
SeAssignPrimaryTokenPrivilege
```

If neither privilege is present, GodPotato won't work.

---

## 3. You're running as a service account

Most successful scenarios involve accounts such as:

- IIS App Pool
- MSSQL service
- SQL Agent
- Network Service
- Local Service
- Jenkins
- Exchange
- SharePoint

These commonly hold `SeImpersonatePrivilege` by design.

---

## 4. A compatible Windows version

GodPotato was created because earlier Potato variants stopped working on newer Windows releases.

Historically:

|Technique|Typical OS support|
|---|---|
|RottenPotato|Older Windows|
|JuicyPotato|Windows 7 / Server 2016 era|
|RoguePotato|Server 2019+|
|PrintSpoofer|Many newer builds|
|**GodPotato**|Broad support across many modern Windows Server versions (for example Server 2012 through Server 2022, depending on configuration and patches)|

---

# Typical HTB example

Imagine:

```
You cracked:

svc_sql
```

Login:

```
evil-winrm

or

MSSQL xp_cmdshell
```

Now:

```
whoami

svc_sql
```

Check privileges:

```
whoami /priv
```

Output:

```
SeImpersonatePrivilege
Enabled
```

At this point, experienced operators immediately think:

> "This is a Potato opportunity."

After a successful impersonation attack:

```
whoami

nt authority\system
```

---

# When will GodPotato NOT work?

It won't work if:

- You're just a normal domain user.
- `SeImpersonatePrivilege` is absent.
- You don't have code execution.
- The service account is heavily restricted and lacks the necessary privileges.
- The environment has mitigations that prevent the required impersonation path.

---

# Why is SYSTEM so valuable?

Once you become SYSTEM you can often:

- Dump LSASS credentials.
- Read the SAM and SECURITY hives.
- Extract cached domain credentials.
- Steal Kerberos tickets.
- Install persistence.
- Access protected files.
- Prepare for lateral movement.

On a **Domain Controller**, SYSTEM is especially powerful because it can access secrets such as the Active Directory database and machine credentials, enabling further compromise if additional conditions are met.

---

# Think of it like this

```
Attacker
     │
     ▼
Service Account
(IIS / MSSQL)
     │
     │  Has SeImpersonatePrivilege
     ▼
GodPotato
     │
     ▼
Trick SYSTEM process
     │
     ▼
Capture SYSTEM token
     │
     ▼
Impersonate SYSTEM
     │
     ▼
NT AUTHORITY\SYSTEM
```

This is the mental model used by many red teamers: after landing on a Windows host, they immediately check `whoami /priv`. If `SeImpersonatePrivilege` is enabled, they know a member of the Potato family (GodPotato, PrintSpoofer, or another variant) may provide a path from a service account to **NT AUTHORITY\SYSTEM**.