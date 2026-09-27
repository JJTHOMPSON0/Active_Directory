# Active Directory Delegation Notes

## 1. Why Delegation Exists

A front-end service often needs to access a back-end service **as the
user**.

Example:

``` text
Alice
  |
  v
WEB01
  |
  v
SQL01
```

Without delegation, SQL01 sees `WEB01$`.

With delegation, SQL01 sees `Alice`.

Delegation = **allowing a service to act on behalf of a user** when
accessing another service.

------------------------------------------------------------------------

# 2. Unconstrained Delegation

When a user authenticates to a server trusted for unconstrained
delegation:

-   The KDC issues the service ticket **and forwards the user's TGT**.
-   The delegated server caches the user's TGT.
-   The server can later request TGS tickets for **any service**.

Flow:

``` text
User
 |
 v
WEB01 (Unconstrained)
 |
 +--> Has user's TGT
 |
 +--> Can request:
      LDAP/DC01
      CIFS/DC01
      MSSQL/SQL01
      HTTP/APP01
      etc.
```

### Risk

If an attacker compromises WEB01:

-   Steal cached TGTs
-   Request tickets to any service
-   Often leads to domain compromise if privileged users logged on

------------------------------------------------------------------------

# 3. Constrained Delegation

Instead of forwarding the user's TGT:

-   The service never receives the user's TGT.
-   The service asks the KDC for tickets only to approved services.

Configured through:

    msDS-AllowedToDelegateTo

Example:

    WEB01

    AllowedToDelegateTo

    MSSQLSvc/SQL01
    HTTP/APP01

WEB01 may impersonate users **only** to those SPNs.

------------------------------------------------------------------------

# 4. Meaning of "Delegate"

Delegation does NOT simply mean requesting tickets.

It means:

> A service is trusted to authenticate to another service **on behalf of
> a user**.

Goal:

    WEB01 ---> SQL01

    as Alice

The Kerberos ticket is simply the mechanism.

------------------------------------------------------------------------

# 5. S4U Extensions

Microsoft introduced Service-for-User (S4U) to support constrained
delegation.

There are two protocols:

-   S4U2Self
-   S4U2Proxy

------------------------------------------------------------------------

## S4U2Self

Meaning:

> "Give me a ticket for Alice to MY service."

Example:

    Client:
    Administrator

    Service:
    HOST/ATTACKBOX

Important:

-   This is **NOT a TGT**
-   It is a **TGS**
-   It only works for your own service

Purpose:

-   Creates an "evidence ticket"
-   Supports protocol transition
-   Allows a service to represent a user even if the user authenticated
    with NTLM/forms/etc.

------------------------------------------------------------------------

## S4U2Proxy

Meaning:

> "Using the evidence ticket, give me a ticket for the user to another
> service."

Example:

    Administrator
            |
            v
    CIFS/SQL01

The KDC checks:

-   Is delegation allowed?
-   Is the target SPN allowed?
-   Can this user be delegated?

If yes:

Returns a TGS for the target service.

------------------------------------------------------------------------

# 6. S4U Flow

    ATTACKBOX$

            |
            | S4U2Self
            v

    Administrator -> HOST/ATTACKBOX (TGS)

            |
            | S4U2Proxy
            v

    Administrator -> CIFS/SQL01 (TGS)

            |
            | Authenticate
            v

    SQL01

Notice:

You NEVER obtain:

    Administrator's TGT

Only service tickets (TGS).

------------------------------------------------------------------------

# 7. Traditional Constrained Delegation

Trust is configured on the **front-end** server.

    WEB01

    ↓

    AllowedToDelegateTo

    ↓

    SQL01

WEB01 decides where it may delegate.

------------------------------------------------------------------------

# 8. Resource-Based Constrained Delegation (RBCD)

Trust direction is reversed.

Configured on the **target** resource.

Attribute:

    msDS-AllowedToActOnBehalfOfOtherIdentity

Instead of:

    WEB01 trusts SQL01

It becomes:

    SQL01 trusts WEB01

------------------------------------------------------------------------

# 9. RBCD Attack Requirements

Typically you need:

-   Control of a computer account (or another account with an SPN)
-   Ability to authenticate as that account (machine password/hash/AES
    key/TGT)
-   Write permissions (GenericWrite, GenericAll, WriteDACL, etc.) on the
    target computer object
-   Ability to modify:

```{=html}
<!-- -->
```
    msDS-AllowedToActOnBehalfOfOtherIdentity

------------------------------------------------------------------------

# 10. Why Local Admin on the Controlled Machine?

Machine accounts own Kerberos credentials.

Local Administrator allows you to use or extract:

-   Machine password
-   NTLM hash
-   AES keys
-   Machine TGT

Without authenticating as the machine account, S4U requests cannot be
performed.

------------------------------------------------------------------------

# 11. Typical RBCD Attack

Example:

Control:

    ATTACKBOX$

Have write permissions over:

    SQL01

### Step 1

Modify SQL01:

    msDS-AllowedToActOnBehalfOfOtherIdentity

    ↓

    ATTACKBOX$

SQL01 now trusts ATTACKBOX.

### Step 2

Authenticate as ATTACKBOX.

### Step 3

Perform S4U2Self:

    Administrator
          ↓
    HOST/ATTACKBOX

### Step 4

Perform S4U2Proxy:

    Administrator
          ↓
    CIFS/SQL01

### Step 5

Authenticate to SQL01.

SQL01 believes Administrator connected.

You never know:

-   Administrator password
-   Administrator NTLM hash
-   Administrator TGT

------------------------------------------------------------------------

# 12. Can You Pick Any User?

Generally yes.

Examples:

-   Administrator
-   Alice
-   svc_sql
-   Bob

However:

Protected users cannot always be delegated.

Examples include:

-   Accounts marked "Account is sensitive and cannot be delegated"
-   Protected Users group members

------------------------------------------------------------------------

# 13. Scope of RBCD

If only SQL01 trusts ATTACKBOX:

Allowed:

    Administrator -> CIFS/SQL01
    Administrator -> HOST/SQL01
    Administrator -> MSSQLSvc/SQL01

Not allowed:

    Administrator -> LDAP/DC01
    Administrator -> CIFS/FILE01
    Administrator -> HTTP/WEB01

Only the trusting resource can be accessed.

------------------------------------------------------------------------

# 14. Why RBCD Is Powerful

Even though access is limited to one computer:

Compromising that computer may allow:

-   Dumping LSASS
-   Stealing cached credentials
-   Extracting machine secrets
-   Lateral movement
-   Privilege escalation

If the target is a Domain Controller, RBCD can lead to full domain
compromise.

------------------------------------------------------------------------

# 15. Important Distinctions

## Unconstrained Delegation

-   Receives user's TGT
-   Can request tickets to any service
-   Extremely dangerous

## Constrained Delegation

-   Never receives user's TGT
-   Uses S4U2Self + S4U2Proxy
-   Limited to configured services

## RBCD

-   Trust configured on target resource
-   Uses S4U2Self + S4U2Proxy
-   Limited to the resource that trusts your controlled account

------------------------------------------------------------------------

# 16. Key Takeaways

-   Delegation = acting on behalf of a user.
-   S4U2Self returns a **TGS to your own service**, never a TGT.
-   S4U2Proxy exchanges that TGS for a TGS to a permitted target
    service.
-   RBCD reverses the trust direction compared to traditional
    constrained delegation.
-   Write access to a computer object's
    `msDS-AllowedToActOnBehalfOfOtherIdentity` enables RBCD if you also
    control a suitable SPN-bearing account.
-   RBCD does **not** give universal impersonation; it only works
    against resources that explicitly trust your controlled account.
