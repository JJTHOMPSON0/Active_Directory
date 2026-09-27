# AD CS ESC8

**`NTLM relay to the CA's web enrollment service`** ==But where NTLM is disabled, u can still use kerberos relaying over smb instead using `krbrealyx`==

\==SOURCE==**`LAB:VulnCicada`**

#### Part 1: What is AD CS, and why does it exist?

Active Directory Certificate Services is Microsoft's PKI (Public Key Infrastructure) system bolted onto AD. Its job is to issue **digital certificates** to users, computers, and services — for things like smart card login, HTTPS, code signing, VPN auth, etc.

The key fact that makes AD CS attackable: **in AD, a certificate can be used as proof of identity, exactly like a password.** If you have a valid certificate that says "I am DC-JPQ225$", you can walk up to the KDC (the Kerberos server) and say "give me a TGT for this identity" — and if the cert is valid and trusted, it will, **without knowing any password or hash.**

This is called **PKINIT** (public key cryptography for initial authentication in Kerberos). It's exactly what `certipy-ad auth -pfx unknown6960.pfx` did in your run — it took a `.pfx` (a certificate + private key bundle) and traded it for a Kerberos TGT.

#### Part 2: Certificate Templates

A **template** is a blueprint AD CS uses to decide: who can request this kind of certificate, and what identity/permissions does the resulting certificate grant?

Example templates:

* `User` — normal employee cert for signing emails, etc. Low privilege.
* `DomainController` — a special template meant _only_ for domain controllers to prove their own machine identity to each other. Extremely high privilege, because a cert from this template says "I am a Domain Controller" — which is basically as powerful as being Domain Admin.

In your command:

```bash
--template DomainController
```

You told the CA "please issue me a certificate using the DomainController blueprint." Normally, only an actual DC's machine account is _allowed_ to request that template. You couldn't request it yourself as `Rosie.Powell` — that request would just be denied. This is the whole reason the attack needed **relaying**: you needed to make the _request_ actually come from the DC's own identity, not yours.

#### Part 3: Why relaying? What is "relaying," concretely?

Authentication protocols like NTLM and Kerberos work by proving identity via a **challenge/response exchange** — some cryptographic proof that's tied to a specific network session.

**Relaying abuses this**: instead of cracking or forging that proof, you sit in the middle and _forward_ a real authentication attempt from Victim → to a different target service, "borrowing" the victim's identity for that one transaction.

**NTLM relay (the classic version):**

1. You trick a victim machine into authenticating to you (attacker) over SMB.
2. The victim sends an NTLM challenge-response.
3. You immediately forward ("relay") that exact response to a _different_ target server (e.g., the AD CS web enrollment page) before it expires.
4. The target server thinks it's talking to the victim, and grants whatever the victim was allowed to do — e.g., "please issue me a DomainController certificate."

This only works because NTLM auth isn't (by default) tied to _which_ server the client thinks it's talking to. That's the vulnerability. Modern hardened domains disable NTLM entirely (like Cicada.vl did — remember all your `STATUS_NOT_SUPPORTED` errors) specifically to kill this attack class.

**Kerberos relay (what you actually did):**

Kerberos tickets _are_ normally tied to a specific target service (the SPN — Service Principal Name — is baked into the ticket request). So naively, Kerberos should be relay-proof. But there's a trick:

1. You add a **DNS record** (`attacker.cicada.vl → your IP`) — this is the `bloodyAD ... add dnsRecord` command you ran. Now your attacker box has a legitimate-looking hostname inside the domain.
2. You **coerce** the DC into authenticating to that hostname (explained in Part 4 below).
3. Because the DC thinks it's authenticating to `attacker.cicada.vl` for an SMB session, it requests a Kerberos service ticket for `cifs/attacker.cicada.vl` — and sends the resulting AP-REQ to _you_.
4. Here's the actual "trick": AD CS's HTTP enrollment endpoint doesn't validate that the Kerberos ticket's target SPN matches the _HTTP_ service properly (missing Extended Protection for Authentication / channel binding) — so `krbrelayx` takes that DC-authenticated ticket and replays it against `http://dc-jpq225.cicada.vl/certsrv/` instead. AD CS is fooled into thinking the DC itself is submitting the certificate request over HTTP.
5. The CA happily issues a `DomainController` template cert — because as far as it can tell, the Domain Controller is asking for it.

That's ESC8 exactly: **"Web Enrollment is enabled over HTTP"** is dangerous specifically because HTTP enrollment lacks the strong channel-binding protections that would normally stop a relayed ticket from being accepted for the wrong purpose.

#### Part 4: Coercion — how do you make the DC authenticate to you at all?

Domain controllers don't just randomly connect out to a random attacker box. You have to _trigger_ it. This is what **PetitPotam** and its cousins do — they abuse legitimate Windows RPC functions that were never meant for this purpose.

`PetitPotam` specifically abuses **EFSRPC** (Encrypting File System Remote Protocol) — a legitimate Windows API for managing encrypted files remotely. One of its functions, `EfsRpcOpenFileRaw` (or `EfsRpcAddUsersToFile`, which is what your nxc output showed: `Exploit Success, efsrpc\EfsRpcAddUsersToFile`), takes a filename parameter. If you pass it a UNC path like `\\attacker.cicada.vl\share\file`, the DC will try to _open that file_, which means it needs to authenticate to `attacker.cicada.vl` over SMB to do so.

So the "attack" is essentially: _"Hey DC, please go check this file for me: `\\attacker.cicada.vl\whatever`"_ — and the DC, trying to be helpful, authenticates to your machine to fetch it. That authentication attempt is the thing krbrelayx catches and relays.

This requires you to already have _some_ valid domain credentials (Rosie.Powell's) to even call the EFSRPC function in the first place — coercion isn't unauthenticated, it just doesn't require _privileged_ creds.&#x20;

#### Part 5: Tying your whole session together, step by step

| Step                                                                         | What happened                                                                | Why                                                                                                  |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| DNS record add                                                               | `attacker.cicada.vl → 10.10.14.32`                                           | Gives your box a legit-looking domain hostname, required because Kerberos tickets are hostname-bound |
| `krbrelayx.py -t http://.../certfnsh.asp --adcs --template DomainController` | Starts listening on SMB (445) _and_ proxies to the CA's HTTP enrollment page | Sets the trap and the relay target simultaneously                                                    |
| `nxc ... coerce_plus ... PetitPotam`                                         | Told the DC "go open this file at `\\attacker.cicada.vl\...`"                | Forces the DC to authenticate to your listener                                                       |
| DC authenticates via Kerberos to your fake host                              | krbrelayx captures the AP-REQ                                                | This is literally the DC's own identity being used                                                   |
| krbrelayx relays that AP-REQ to `certsrv/certfnsh.asp`                       | AD CS issues a cert for `DC-JPQ225$` under the `DomainController` template   | ESC8: HTTP enrollment doesn't validate the ticket was meant for it                                   |
| `certipy-ad auth -pfx ...`                                                   | Cert → PKINIT → Kerberos TGT as `DC-JPQ225$`                                 | Cert = provable identity                                                                             |
| `secretsdump.py -k ... DC-JPQ225$`                                           | DCSync — DC machine accounts have replication rights by design               | Now you have _every_ domain account's hash, including Administrator                                  |

The elegant/nasty part of this chain: every individual step (DNS write, EFSRPC call, cert request, DCSync as a DC) is something a _real_ DC or admin tool does routinely — the attack is entirely about tricking legitimate mechanisms into cooperating in the wrong order, not exploiting a memory-corruption bug.

Blog:

```cardlink
url: https://www.synacktiv.com/publications/relaying-kerberos-over-smb-using-krbrelayx.html
title: "Relaying Kerberos over SMB using krbrelayx"
description: "Relaying Kerberos over SMB using krbrelayx"
host: www.synacktiv.com
image: https://www.synacktiv.com/sites/default/files/styles/blog_grid_view/public/2024-11/9azn60_copy_660x330.jpg
```

#### ESC8 specifically

ESC1 through ESC11+ (the naming comes from SpecterOps' original AD CS research) are a taxonomy of distinct AD CS misconfigurations. Each number is a _different_ root cause — they're not escalating severity levels, just an enumerated list of separate bugs/misconfigs. ESC8 is specifically about a **transport-layer weakness**, not a template misconfiguration.

**The core issue:** AD CS can optionally expose a web-based enrollment interface at `/certsrv/` (this is the "Web Enrollment" feature you saw in your Certipy output: `Web Enrollment: HTTP Enabled: True`). This is a legacy feature — an actual webpage where you log in and click buttons to request a certificate, instead of using the native RPC-based enrollment protocol.

Here's the problem: **HTTP authentication in Windows (NTLM or Kerberos over HTTP) does not, by default, cryptographically bind the authentication to the TLS channel it travels over — and if it's plain HTTP, there's no TLS channel to bind to at all.**

There's a real protection for this called **EPA — Extended Protection for Authentication** (a.k.a. channel binding tokens). When EPA is enabled, the server checks: "does this authentication ticket/response actually match a hash of _this specific_ connection?" If a ticket got relayed from a different connection (like an SMB session, as in your attack), the channel binding fails and the server rejects it.

**ESC8 = "the CA's web enrollment endpoint doesn't enforce EPA (or is plain HTTP with no TLS at all)."** That's it — that's the entire vulnerability. Nothing about the certificate template itself is broken; a totally reasonable, low-privilege template could still be abused via ESC8 as long as _some_ enrollable template exists and the attacker can get a higher-privilege identity's ticket to relay.

In your case, the CA's own permissions actually made this even worse than a normal ESC8 case: recall the CA config showed

```
Enroll : CICADA.VL\Authenticated Users
```

So _any_ authenticated user (like Rosie.Powell) could reach the enrollment endpoint and request a cert using _whatever identity got relayed to it_ — including a Domain Controller's, once you relayed the DC's own Kerberos ticket there.

If EPA had been enabled on that web enrollment endpoint, your relayed AP-REQ would've been rejected outright, because it was authenticated on a _different_ connection (the SMB session with the DC) than the one submitting the HTTP cert request.

#### What is an AP-REQ?

This is Kerberos internals, so let's build it from the ground up.

Kerberos authentication (simplified) has three main message exchanges:

1. **AS-REQ / AS-REP** (Authentication Service exchange) — you send your username to the KDC, prove you know your password (or, in your ESC8 finale, prove it via a certificate through PKINIT), and get back a **TGT** (Ticket Granting Ticket). This is what `impacket-getTGT` and `certipy-ad auth` produce.
2. **TGS-REQ / TGS-REP** (Ticket Granting Service exchange) — you present your TGT to the KDC and say "I want to talk to _this specific service_" (e.g., `cifs/attacker.cicada.vl` or `HTTP/dc-jpq225.cicada.vl`). The KDC checks your TGT is valid and issues you a **service ticket** — encrypted specifically so _only that target service_ can decrypt it (using a key derived from that service's own account password/keytab).
3. **AP-REQ / AP-REP** (Application exchange) — this is the actual moment of "logging in" to the target service. The client packages up the service ticket it got in step 2, plus a fresh **authenticator** (a timestamp encrypted with a session key, to prove this isn't a replayed old ticket), and sends this bundle — the **AP-REQ** — directly to the target application/service. The service decrypts the ticket with its own key, checks the authenticator's timestamp is fresh, and if all checks out, sends back an AP-REP confirming "yes, you're authenticated," and grants access.

**So an AP-REQ is literally: "here is my Kerberos service ticket for a specific service, plus proof I'm the one who was just issued it, right now."** It's the actual credential-presentation packet — the thing you hand over at the door, not the ticket-office receipt.

**Why relaying an AP-REQ works here specifically:** In step 2 above, the DC requested a service ticket for `cifs/attacker.cicada.vl` (an SMB service, because PetitPotam coerced it to open a file over SMB). That ticket is cryptographically valid _only_ for talking to an SMB service under that name — the KDC encrypted it with (effectively) your attacker box's key material for that SPN, since DNS said `attacker.cicada.vl` was a real, resolvable hostname you controlled.

krbrelayx, sitting there pretending to be an SMB server, receives that AP-REQ. Normally the story would end there — an SMB ticket shouldn't be usable anywhere else. But the HTTP enrollment endpoint at `/certsrv/`, lacking EPA/channel binding, doesn't actually verify _which specific TCP/TLS session_ an AP-REQ arrived on, or cross-check it was meant for HTTP rather than SMB. So krbrelayx just forwards that same AP-REQ bundle to the CA's HTTP endpoint, and the endpoint's Kerberos/SSPI stack decrypts it, sees "yep, this decrypts fine, this is DC-JPQ225$," and authenticates the HTTP session as the DC — even though that specific ticket was technically minted for a completely different service.

That gap — "a valid AP-REQ for service A gets accepted by service B because nothing checks the transport/service binding" — is the entire mechanical core of Kerberos relay, and EPA/channel-binding is precisely the fix that would close it.
