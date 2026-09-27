# Part 1: What is a Certificate?

Think of a certificate as a **digital ID card**.

A certificate says:

> "I am `Administrator@jinwoo.local`, and a trusted authority confirms this."

A certificate contains:

- Subject (owner)
- Public key
- Validity period
- Issuer
- Digital signature

Example:

```
Owner:
Administrator

Public Key:
A1B3F9...

Issued By:
JINWOO-CA

Valid Until:
2030
```

---

# Part 2: Why do we need certificates?

Passwords have problems.

- Can be guessed
- Can be stolen
- Users reuse them

Certificates let you authenticate **without sending your password**.

Instead of

```
Username
Password
```

you present

```
Certificate
Private Key
```

The server verifies them.

---

# Part 3: What is AD CS?

AD CS stands for

**Active Directory Certificate Services**

It is Microsoft's **Public Key Infrastructure (PKI)**.

Think of it as the department that issues digital IDs to everyone in the domain.

Without AD CS

```
No certificate authority
```

With AD CS

```
        Domain

            |
        Certificate Authority
             (CA)

      /        |        \
 User1      User2      Server
```

Everyone can request certificates.

---

# Part 4: What is a CA?

CA = **Certificate Authority**

The CA signs certificates.

Imagine a passport office.

You fill a form.

The government verifies you.

Then they stamp your passport.

The CA works exactly like this.

```
You
 |
 | Request certificate
 |
 V

Certificate Authority

 |
 | verifies identity
 |
 V

Signed Certificate
```

---

# Part 5: Public Key Cryptography

Every certificate has

```
Private Key
Public Key
```

Private key

```
Only you know it.
```

Public key

```
Everyone knows it.
```

The CA signs your public key.

---

# Part 6: AD CS Components

The major pieces are:

```
Certificate Authority

Certificate Template

Certificate

Private Key

Certificate Store

Enrollment Service
```

These all work together.

---

# Part 7: Certificate Templates

This is the most important concept for attackers.

A template defines

- Who can request
- What the certificate is used for
- Whether approval is required
- Whether users can choose another identity
- How long it lasts

Think of it as a form.

Example

```
User Template

Only Domain Users

Used for Login

Expires in 1 year
```

Another

```
Web Server Template

Only Servers

Server Authentication

2 years
```

---

# Part 8: Enrollment

Suppose you're Alice.

```
Alice

↓

"I want a certificate."

↓

CA checks permissions

↓

CA issues certificate

↓

Alice stores certificate
```

Simple.

---

# Part 9: Where are certificates stored?

Windows stores them in a certificate store.

For example

```
Current User

Personal

Trusted Root

Intermediate CA
```

You can view them with

```
certmgr.msc
```

or

```
certlm.msc
```

---

# Part 10: Authentication Using Certificates

Instead of

```
Password

↓

Domain Controller
```

we have

```
Certificate

↓

Domain Controller

↓

CA validates it

↓

Login successful
```

This is called **PKINIT (Public Key Cryptography for Initial Authentication in Kerberos)**.

---

# Part 11: Why attackers love AD CS

Normally

```
Want Administrator?

↓

Need password

or

Need NTLM hash
```

With AD CS

```
Need Administrator?

↓

Steal or obtain Administrator certificate

↓

Authenticate

↓

Done
```

No password required.

---

# Part 12: Example

Suppose Administrator owns

```
Administrator.pfx
```

This file contains

```
Certificate

+

Private Key
```

If you steal it

```
Administrator.pfx

↓

Authenticate to AD

↓

Become Administrator
```

Even if you don't know the Administrator password.

---

# Part 13: What is a .PFX file?

You'll see these everywhere during AD CS attacks.

A PFX contains

```
Certificate

+

Private Key
```

Think of it as a ZIP archive containing your complete digital identity.

---

# Part 14: Why AD CS becomes vulnerable

The problem usually isn't AD CS itself—it's **misconfigured certificate templates**.

Examples include:

- Any authenticated user can request certificates.
- A template lets the requester specify any username (called the **Subject Alternative Name**, or SAN).
- Certificates can be used for client authentication.
- The CA issues certificates automatically without approval.

If all of these are true, a normal domain user might request a certificate that says "I am Administrator" and the CA signs it.

---

# Part 15: The ESC attacks

Researchers grouped common AD CS misconfigurations into attack paths called **ESC** (Enterprise Security Configuration) vulnerabilities.

The most common include:

- **ESC1** – Enrollable template allows supplying another identity (the classic "request a cert as Administrator" attack).
- **ESC2** – Misconfigured certificate application policies.
- **ESC3** – Abuse of Enrollment Agent certificates.
- **ESC4** – Dangerous template permissions.
- **ESC6** – SAN abuse through CA configuration.
- **ESC8** – NTLM relay to the CA's web enrollment service.

These are among the most frequently encountered AD CS attack techniques.