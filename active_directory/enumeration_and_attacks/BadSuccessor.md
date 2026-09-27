# Before understanding BadSuccessor...

You first need to understand **why Microsoft created dMSAs.**

## The old problem

Suppose you have a service running as:
```
svc_sql
```

The SQL Server service uses:
```
Domain\User
Password
```

Problems:

- Password expires.
- Password needs rotation.
- Hundreds of services depend on it.
- Changing the password can break services.

Microsoft solved part of this with **gMSA (Group Managed Service Accounts)**.
```
SQL Server
      │
      ▼
gMSA
```

The Domain Controller rotates the password automatically.

Great.

---

## But another problem remained

Imagine a company has:

```
Old service account

svc_backup
```

used on 500 servers.

Microsoft wants administrators to migrate to a managed account.

Instead of:
```
Delete old account
Create new account
Reconfigure everything
```

they introduced **Delegated Managed Service Accounts (dMSAs)** in Windows Server 2025.

The idea:

```
Old Account
     │
     │ Migrated
     ▼
New dMSA
```

The dMSA becomes the **successor** of the old account.

Hence the name:
```
Successor
```

---

# What does "Successor" actually mean?

Imagine this user:

```
svc_sql
```

owns:

- Kerberos keys
- SPNs
- SID
- Group memberships
- Permissions

Microsoft wants:

```
svc_sql
      │
      ▼
dMSA_sql
```

Applications should continue working without administrators manually copying everything.

During authentication, the **KDC (Key Distribution Center)** can treat the dMSA as the legitimate replacement for the old account. That migration mechanism is the feature BadSuccessor abused.

---

# The idea behind BadSuccessor

Imagine this domain.
```
Administrator

Domain Admin

Enterprise Admin

svc_sql

svc_web
```

Microsoft expects:

```
svc_sql
     │
     ▼
dMSA_sql
```

Only the real replacement should exist.

But the original implementation effectively allowed an attacker who could create and configure a dMSA in the right place to create:

```
Administrator
      │
      ▼
evil_dMSA
```

The KDC accepted:

```
evil_dMSA

is the successor of

Administrator
```

That was the core design flaw.

---

# What happened during Kerberos?

Suppose the attacker authenticates as:
```
evil_dMSA
```

Normally Kerberos would issue:
```
TGT

for

evil_dMSA
```

Instead, before Microsoft's fix, the KDC could:

1. Notice the successor relationship.
2. Merge the predecessor's privileges into the dMSA.
3. Return Kerberos material based on that relationship.

In practical terms, the attacker could end up authenticating with the privileges of the linked high-value account.

---

# Visualising the attack

Normal migration:
```
Administrator
        │
        ▼
Official dMSA

Authentication

↓

Gets Administrator privileges
```

BadSuccessor:
```
Administrator
        │
        ▼
Attacker's dMSA

Authentication

↓

Gets Administrator privileges
```

The KDC trusted the successor relationship.

That was the problem.

---

# Why was this so dangerous?

Previous AD attacks often require:

- Password cracking
- NTLM relay
- Ticket theft
- Credential dumping

BadSuccessor didn't.

Instead:
```
Create dMSA

↓

Link it

↓

Authenticate

↓

Become Domain Admin
```

No password.

No hash.

No LSASS dump.

No Golden Ticket.

Just abusing the migration feature.

---

# What permissions were needed?

This is the part many people misunderstand.

You did **not** need Domain Admin.

Instead, you needed enough Active Directory rights to create and configure a dMSA where the migration feature could be abused.

A common example was:
```
Write access

or

Create Child

on an OU
```

Imagine:
```
Servers OU
```

The attacker has:
```
Create Child
```

That lets them create:
```
evil_dMSA
```

Then configure it to appear as the successor of a privileged account.

So:
```
Compromised Helpdesk

↓

Control over Servers OU

↓

Create dMSA

↓

Link to Domain Admin

↓

Authenticate

↓

Domain Admin
```

That relatively low privilege requirement is what made the attack particularly concerning.

---

# Why is controlling an OU enough?

Think of an OU like a folder:

```
Domain

│

├── Users

├── Servers

├── HR

└── IT
```

Suppose you control:
```
Servers OU
```

That means:
```
Create Computer

Create User

Create dMSA
```

The attack didn't require control over the Administrator account itself.

It abused the fact that the dMSA migration relationship was trusted by the KDC.

---

# Example attack chain

Imagine this AD.
```
Compromised User

↓

WriteDACL

↓

Servers OU

↓

Create evil_dMSA

↓

Configure successor

↓

Request Kerberos ticket

↓

Domain Admin
```

Notice that no password is stolen anywhere in this chain.

---

# Why was it called "BadSuccessor"?

Because the malicious dMSA became the **successor** of a privileged identity.
```
Administrator

↓

Bad Successor

↓

Attacker
```

The dMSA inherited what it never should have.