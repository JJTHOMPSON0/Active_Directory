An **RODC** (Read-Only Domain Controller) is ==a specialized type of Windows Server Active Directory Domain Controller that holds a read-only copy of the Active Directory database==. Unlike a standard writable domain controller, it cannot create, change, or delete any directory objects locally. All modifications must be made on a standard writable domain controller and then replicated inbound to the RODC.

---

Why Are RODCs Used?

Organizations deploy RODCs primarily for **security** and **performance** in remote environments where full writable domain controllers pose a risk. 

- **Poor Physical Security:** Branch offices, retail stores, or warehouses often lack locked server rooms or dedicated on-site IT staff. If someone steals or breaks into an RODC, they do not get a fully writable database.

- **Password Protection (Password Replication Policy):** By default, an RODC does not store user passwords. Using a [Password Replication Policy (PRP)](https://rostantechnologies.com/blog/technology/active-directory-domain-controllers-adc-rodc-cdc-guide), administrators can choose to cache credentials only for local users who actually work at that specific office, preventing a mass compromise of enterprise passwords if the server is breached.

- **Unidirectional (One-Way) Replication:** Data flows in only one direction—from a writable domain controller down to the RODC. If an attacker compromises the RODC and injects malicious changes, those changes cannot replicate back to the rest of the corporate forest. 

- **Filtered Attribute Set (FAS):** Sensitive attributes (such as local administrator passwords or specific cryptographic keys) are stripped out and never replicated to an RODC. 

- **Local Authentication & Bandwidth Savings:** Instead of remote branch users having to authenticate over a slow or expensive Wide Area Network (WAN) link back to corporate headquarters every time they log in, the RODC handles local logins and DNS lookups quickly. 

- **Administrative Delegation:** Local IT staff or trusted local workers can be given limited administrative rights just for that specific server without granting them power over the entire domain. 