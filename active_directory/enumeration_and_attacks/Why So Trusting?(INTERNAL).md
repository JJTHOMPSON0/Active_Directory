# Domain Trusts Primer

---

## Scenario

Many large organizations will acquire new companies over time and bring them into the fold. One way this is done for ease of use is to establish a trust relationship with the new domain. In doing so, you can avoid migrating all the established objects, making integration much quicker. This trust can also introduce weaknesses into the customer's environment if they are not careful. A subdomain with an exploitable flaw or vulnerability can provide us with a quick route into the target domain. Companies may also establish trusts with other companies (such as an MSP), a customer, or other business units of the same company (such as a division of the company in another geographical region). Let's explore domain trusts more and how we can abuse built-in functionality during our assessments.

---

## Domain Trusts Overview

A [trust](https://social.technet.microsoft.com/wiki/contents/articles/50969.active-directory-forest-trust-attention-points.aspx) is used to establish forest-forest or domain-domain (intra-domain) authentication, which allows users to access resources in (or perform administrative tasks) another domain, outside of the main domain where their account resides. A trust creates a link between the authentication systems of two domains and may allow either one-way or two-way (bidirectional) communication. An organization can create various types of trusts:

- `Parent-child`: Two or more domains within the same forest. The child domain has a two-way transitive trust with the parent domain, meaning that users in the child domain `corp.inlanefreight.local` could authenticate into the parent domain `inlanefreight.local`, and vice-versa.
- `Cross-link`: A trust between child domains to speed up authentication.
- `External`: A non-transitive trust between two separate domains in separate forests which are not already joined by a forest trust. This type of trust utilizes [SID filtering](https://www.serverbrain.org/active-directory-2008/sid-history-and-sid-filtering.html) or filters out authentication requests (by SID) not from the trusted domain.
- `Tree-root`: A two-way transitive trust between a forest root domain and a new tree root domain. They are created by design when you set up a new tree root domain within a forest.
- `Forest`: A transitive trust between two forest root domains.
- [ESAE](https://docs.microsoft.com/en-us/security/compass/esae-retirement): A bastion forest used to manage Active Directory.

When establishing a trust, certain elements can be modified depending on the business case.

Trusts can be transitive or non-transitive.

- A `transitive` trust means that trust is extended to objects that the child domain trusts. For example, let's say we have three domains. In a transitive relationship, if `Domain A` has a trust with `Domain B`, and `Domain B` has a `transitive` trust with `Domain C`, then `Domain A` will automatically trust `Domain C`.
- In a `non-transitive trust`, the child domain itself is the only one trusted.

![Diagram of servers A, B, C representing domains a.com, b.com, c.com, illustrating A=B, B=C, thus A=C.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/transitive-trusts.png)

Adapted from [here](https://zindagitech.com/wp-content/uploads/2021/09/Picture2-Deepak-4.png.webp)

#### Trust Table Side By Side

|Transitive|Non-Transitive|
|---|---|
|Shared, 1 to many|Direct trust|
|The trust is shared with anyone in the forest|Not extended to next level child domains|
|Forest, tree-root, parent-child, and cross-link trusts are transitive|Typical for external or custom trust setups|

An easy comparison to make can be package delivery to your house. For a `transitive` trust, you have extended the permission to anyone in your household (forest) to accept a package on your behalf. For a `non-transitive` trust, you have given strict orders with the package that no one other than the delivery service and you can handle the package, and only you can sign for it.

Trusts can be set up in two directions: one-way or two-way (bidirectional).

- `One-way trust`: Users in a `trusted` domain can access resources in a trusting domain, not vice-versa.
- `Bidirectional trust`: Users from both trusting domains can access resources in the other domain. For example, in a bidirectional trust between `INLANEFREIGHT.LOCAL` and `FREIGHTLOGISTICS.LOCAL`, users in `INLANEFREIGHT.LOCAL` would be able to access resources in `FREIGHTLOGISTICS.LOCAL`, and vice-versa.

Domain trusts are often set up incorrectly and can provide us with critical unintended attack paths. Also, trusts set up for ease of use may not be reviewed later for potential security implications if security is not considered before establishing the trust relationship. A Merger & Acquisition (M&A) between two companies can result in bidirectional trusts with acquired companies, which can unknowingly introduce risk into the acquiring company’s environment if the security posture of the acquired company is unknown and untested. If someone wanted to target your organization, they could also look at the other company you acquired for a potentially softer target to attack, allowing them to get into your organization indirectly. It is not uncommon to be able to perform an attack such as Kerberoasting against a domain outside the principal domain and obtain a user that has administrative access within the principal domain. I have performed many penetration tests where this was the case: I was unable to find a foothold in the principal domain, but was able to find a flaw in a trusted domain which, in turn, gave me a foothold, or even full admin rights in the principal domain. This type of "end-around" attack could be prevented if security is considered as paramount before establishing any kind of domain trust. As we examine trust relationships, keep these thoughts in mind for reporting. Often, we will find that the larger organization is unaware that a trust relationship exists with one or more domains.

Below is a graphical representation of the various trust types.

![Diagram of Inlanefreight Forest showing trust types: Parent-child, Cross-link, External, Tree-root, and Forest between domains.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/trusts-diagram.png)

---

## Enumerating Trust Relationships

We can use the [Get-ADTrust](https://docs.microsoft.com/en-us/powershell/module/activedirectory/get-adtrust?view=windowsserver2022-ps) cmdlet to enumerate domain trust relationships. This is especially helpful if we are limited to just using built-in tools.

#### Using Get-ADTrust

 ![](../../../ZMEDIA/Pasted%20image%2020260707144958.png)

The above output shows that our current domain `INLANEFREIGHT.LOCAL` has two domain trusts. The first is with `LOGISTICS.INLANEFREIGHT.LOCAL`, and the `IntraForest` property shows that this is a child domain, and we are currently positioned in the root domain of the forest. The second trust is with the domain `FREIGHTLOGISTICS.LOCAL,` and the `ForestTransitive` property is set to `True`, which means that this is a forest trust or external trust. We can see that both trusts are set up to be bidirectional, meaning that users can authenticate back and forth across both trusts. This is important to note down during an assessment. If we cannot authenticate across a trust, we cannot perform any enumeration or attacks across the trust.

Aside from using built-in AD tools such as the Active Directory PowerShell module, both PowerView and BloodHound can be utilized to enumerate trust relationships, the type of trusts established, and the authentication flow. After importing PowerView, we can use the [Get-DomainTrust](https://powersploit.readthedocs.io/en/latest/Recon/Get-DomainTrust/) function to enumerate what trusts exist, if any.

#### Checking for Existing Trusts using Get-DomainTrust

![](../../../ZMEDIA/Pasted%20image%2020260707145016.png)

PowerView can be used to perform a domain trust mapping and provide information such as the type of trust (parent/child, external, forest) and the direction of the trust (one-way or bidirectional). This information is beneficial once a foothold is obtained, and we plan to compromise the environment further.

#### Using Get-DomainTrustMapping

![](../../../ZMEDIA/Pasted%20image%2020260707145029.png)

From here, we could begin performing enumeration across the trusts. For example, we could look at all users in the child domain:

#### Checking Users in the Child Domain using Get-DomainUser

![](../../../ZMEDIA/Pasted%20image%2020260707145103.png)

Another tool we can use to get Domain Trust is `netdom`. The `netdom query` sub-command of the `netdom` command-line tool in Windows can retrieve information about the domain, including a list of workstations, servers, and domain trusts.

#### Using netdom to query domain trust

![](../../../ZMEDIA/Pasted%20image%2020260707145051.png)

#### Using netdom to query domain controllers

![](../../../ZMEDIA/Pasted%20image%2020260707145115.png)

#### Using netdom to query workstations and servers

 ![](../../../ZMEDIA/Pasted%20image%2020260707145126.png)

We can also use BloodHound to visualize these trust relationships by using the `Map Domain Trusts` pre-built query. Here we can easily see that two bidirectional trusts exist.

#### Visualizing Trust Relationships in BloodHound

![Graph showing domain relationships: INLANEFREIGHT.LOCAL connected to LOGISTICS.INLANEFREIGHT.LOCAL and FREIGHT.LOGISTICS.LOCAL. Sidebar with pre-built analytics queries.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/BH_trusts.png)

---

## Onwards

In the following few sections, we will cover common attacks that we can perform against child --> parent domain trusts and across bidirectional forest trusts. These types of attacks should not be overlooked, but we should always check with our client to ensure that any trusts we uncover during our enumeration are in scope for the assessment and we are not going outside the Rules of Engagement.

# Attacking Domain Trusts - Child -> Parent Trusts - from Windows

---

## SID History Primer

The [sidHistory](https://docs.microsoft.com/en-us/windows/win32/adschema/a-sidhistory) attribute is used in migration scenarios. If a user in one domain is migrated to another domain, a new account is created in the second domain. The original user's SID will be added to the new user's SID history attribute, ensuring that the user can still access resources in the original domain.

SID history is intended to work across domains, but can work in the same domain. Using Mimikatz, an attacker can perform SID history injection and add an administrator account to the SID History attribute of an account they control. When logging in with this account, all of the SIDs associated with the account are added to the user's token.

This token is used to determine what resources the account can access. If the SID of a Domain Admin account is added to the SID History attribute of this account, then this account will be able to perform DCSync and create a [Golden Ticket](https://attack.mitre.org/techniques/T1558/001/) or a Kerberos ticket-granting ticket (TGT), which will allow for us to authenticate as any account in the domain of our choosing for further persistence.

---

## ExtraSids Attack - Mimikatz

This attack allows for the compromise of a parent domain once the child domain has been compromised. Within the same AD forest, the [sidHistory](https://docs.microsoft.com/en-us/windows/win32/adschema/a-sidhistory) property is respected due to a lack of [SID Filtering](https://web.archive.org/web/20220812183844/https://www.serverbrain.org/active-directory-2008/sid-history-and-sid-filtering.html) protection. SID Filtering is a protection put in place to filter out authentication requests from a domain in another forest across a trust. Therefore, if a user in a child domain that has their sidHistory set to the `Enterprise Admins group` (which only exists in the parent domain), they are treated as a member of this group, which allows for administrative access to the entire forest. In other words, we are creating a Golden Ticket from the compromised child domain to compromise the parent domain. In this case, we will leverage the `SIDHistory` to grant an account (or non-existent account) Enterprise Admin rights by modifying this attribute to contain the SID for the Enterprise Admins group, which will give us full access to the parent domain without actually being part of the group.

To perform this attack after compromising a child domain, we need the following:

- The KRBTGT hash for the child domain
- The SID for the child domain
- The name of a target user in the child domain (does not need to exist!)
- The FQDN of the child domain.
- The SID of the Enterprise Admins group of the root domain.
- With this data collected, the attack can be performed with Mimikatz.

Now we can gather each piece of data required to perform the ExtraSids attack. First, we need to obtain the NT hash for the [KRBTGT](https://adsecurity.org/?p=483) account, which is a service account for the Key Distribution Center (KDC) in Active Directory. The account KRB (Kerberos) TGT (Ticket Granting Ticket) is used to encrypt/sign all Kerberos tickets granted within a given domain. Domain controllers use the account's password to decrypt and validate Kerberos tickets. The KRBTGT account can be used to create Kerberos TGT tickets that can be used to request TGS tickets for any service on any host in the domain. This is also known as the Golden Ticket attack and is a well-known persistence mechanism for attackers in Active Directory environments. The only way to invalidate a Golden Ticket is to change the password of the KRBTGT account, which should be done periodically and definitely after a penetration test assessment where full domain compromise is reached.

Since we have compromised the child domain, we can log in as a Domain Admin or similar and perform the DCSync attack to obtain the NT hash for the KRBTGT account.

#### Obtaining the KRBTGT Account's NT Hash using Mimikatz

![](../../../ZMEDIA/Pasted%20image%2020260707145226.png)

We can use the PowerView `Get-DomainSID` function to get the SID for the child domain, but this is also visible in the Mimikatz output above.

#### Using Get-DomainSID

```powershell
PS C:\htb> Get-DomainSID 
S-1-5-21-2806153819-209893948-922872689
```

Next, we can use `Get-DomainGroup` from PowerView to obtain the SID for the Enterprise Admins group in the parent domain. We could also do this with the [Get-ADGroup](https://docs.microsoft.com/en-us/powershell/module/activedirectory/get-adgroup?view=windowsserver2022-ps) cmdlet with a command such as `Get-ADGroup -Identity "Enterprise Admins" -Server "INLANEFREIGHT.LOCAL"`.

#### Obtaining Enterprise Admins Group's SID using Get-DomainGroup
![](../../../ZMEDIA/Pasted%20image%2020260707145302.png)

At this point, we have gathered the following data points:

- The KRBTGT hash for the child domain: `9d765b482771505cbe97411065964d5f`
- The SID for the child domain: `S-1-5-21-2806153819-209893948-922872689`
- The name of a target user in the child domain (does not need to exist to create our Golden Ticket!): We'll choose a fake user: `hacker`
- The FQDN of the child domain: `LOGISTICS.INLANEFREIGHT.LOCAL`
- The SID of the Enterprise Admins group of the root domain: `S-1-5-21-3842939050-3880317879-2865463114-519`

Before the attack, we can confirm no access to the file system of the DC in the parent domain.

#### Using ls to Confirm No Access

![](../../../ZMEDIA/Pasted%20image%2020260707145316.png)

Using Mimikatz and the data listed above, we can create a Golden Ticket to access all resources within the parent domain.

#### Creating a Golden Ticket with Mimikatz

![](../../../ZMEDIA/Pasted%20image%2020260707145327.png)

We can confirm that the Kerberos ticket for the non-existent hacker user is residing in memory.

#### Confirming a Kerberos Ticket is in Memory Using klist
![](../../../ZMEDIA/Pasted%20image%2020260707145338.png)

From here, it is possible to access any resources within the parent domain, and we could compromise the parent domain in several ways.

#### Listing the Entire C: Drive of the Domain Controller
![](../../../ZMEDIA/Pasted%20image%2020260707145350.png)

---

## ExtraSids Attack - Rubeus

We can also perform this attack using Rubeus. First, again, we'll confirm that we cannot access the parent domain Domain Controller's file system.

#### Using ls to Confirm No Access Before Running Rubeus
![](../../../ZMEDIA/Pasted%20image%2020260707145401.png)

Next, we will formulate our Rubeus command using the data we retrieved above. The `/rc4` flag is the NT hash for the KRBTGT account. The `/sids` flag will tell Rubeus to create our Golden Ticket giving us the same rights as members of the Enterprise Admins group in the parent domain.

#### Creating a Golden Ticket using Rubeus

![](../../../ZMEDIA/Pasted%20image%2020260707145424.png)
![](../../../ZMEDIA/Pasted%20image%2020260707145441.png)
Once again, we can check that the ticket is in memory using the `klist` command.

#### Confirming the Ticket is in Memory Using klist
![](../../../ZMEDIA/Pasted%20image%2020260707145500.png)
Finally, we can test this access by performing a DCSync attack against the parent domain, targeting the `lab_adm` Domain Admin user.

#### Performing a DCSync Attack

![](../../../ZMEDIA/Pasted%20image%2020260707145517.png)

When dealing with multiple domains and our target domain is not the same as the user's domain, we will need to specify the exact domain to perform the DCSync operation on the particular domain controller. The command for this would look like the following:

![](../../../ZMEDIA/Pasted%20image%2020260707145529.png)

---

## Next Steps

Now that we've walked through child --> parent domain compromise from a Windows attack box, we'll cover a few ways to achieve the same if we are constrained to a Linux attack host.


# Attacking Domain Trusts - Child -> Parent Trusts - from Linux

---

We can also perform the attack shown in the previous section from a Linux attack host. To do so, we'll still need to gather the same bits of information:

- The KRBTGT hash for the child domain
- The SID for the child domain
- The name of a target user in the child domain (does not need to exist!)
- The FQDN of the child domain
- The SID of the Enterprise Admins group of the root domain

Once we have complete control of the child domain, `LOGISTICS.INLANEFREIGHT.LOCAL`, we can use `secretsdump.py` to DCSync and grab the NTLM hash for the KRBTGT account.

#### Performing DCSync with secretsdump.py

![](../../../ZMEDIA/Pasted%20image%2020260707145619.png)

Next, we can use [lookupsid.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/lookupsid.py) from the Impacket toolkit to perform SID brute forcing to find the SID of the child domain. In this command, whatever we specify for the IP address (the IP of the domain controller in the child domain) will become the target domain for a SID lookup. The tool will give us back the SID for the domain and the RIDs for each user and group that could be used to create their SID in the format `DOMAIN_SID-RID`. For example, from the output below, we can see that the SID of the `lab_adm` user would be `S-1-5-21-2806153819-209893948-922872689-1001`.

#### Performing SID Brute Forcing using lookupsid.py

![](../../../ZMEDIA/Pasted%20image%2020260707145634.png)

We can filter out the noise by piping the command output to grep and looking for just the domain SID.

#### Looking for the Domain SID

 ![](../../../ZMEDIA/Pasted%20image%2020260707145647.png)

Next, we can rerun the command, targeting the INLANEFREIGHT Domain Controller (DC01) at 172.16.5.5 and grab the domain `SID S-1-5-21-3842939050-3880317879-2865463114` and attach the RID of the Enterprise Admins group. [Here](https://adsecurity.org/?p=1001) is a handy list of well-known SIDs.

#### Grabbing the Domain SID & Attaching to Enterprise Admin's RID

![](../../../ZMEDIA/Pasted%20image%2020260707145700.png)

We have gathered the following data points to construct the command for our attack. Once again, we will use the non-existent user `hacker` to forge our Golden Ticket.

- The KRBTGT hash for the child domain: `9d765b482771505cbe97411065964d5f`
- The SID for the child domain: `S-1-5-21-2806153819-209893948-922872689`
- The name of a target user in the child domain (does not need to exist!): `hacker`
- The FQDN of the child domain: `LOGISTICS.INLANEFREIGHT.LOCAL`
- The SID of the Enterprise Admins group of the root domain: `S-1-5-21-3842939050-3880317879-2865463114-519`

Next, we can use [ticketer.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/ticketer.py) from the Impacket toolkit to construct a Golden Ticket. This ticket will be valid to access resources in the child domain (specified by `-domain-sid`) and the parent domain (specified by `-extra-sid`).

#### Constructing a Golden Ticket using ticketer.py

![](../../../ZMEDIA/Pasted%20image%2020260707145715.png)

The ticket will be saved down to our system as a [credential cache (ccache)](https://web.mit.edu/kerberos/krb5-1.12/doc/basic/ccache_def.html) file, which is a file used to hold Kerberos credentials. Setting the `KRB5CCNAME` environment variable tells the system to use this file for Kerberos authentication attempts.

#### Setting the KRB5CCNAME Environment Variable

```shellsession
haphestus@htb[/htb]$ export KRB5CCNAME=hacker.ccache
```

We can check if we can successfully authenticate to the parent domain's Domain Controller using [Impacket's version of Psexec](https://github.com/SecureAuthCorp/impacket/blob/master/examples/psexec.py). If successful, we will be dropped into a SYSTEM shell on the target Domain Controller.

#### Getting a SYSTEM shell using Impacket's psexec.py
![](../../../ZMEDIA/Pasted%20image%2020260707145738.png)

Impacket also has the tool [raiseChild.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/raiseChild.py), which will automate escalating from child to parent domain. We need to specify the target domain controller and credentials for an administrative user in the child domain; the script will do the rest. If we walk through the output, we see that it starts by listing out the child and parent domain's fully qualified domain names (FQDN). It then:

- Obtains the SID for the Enterprise Admins group of the parent domain
- Retrieves the hash for the KRBTGT account in the child domain
- Creates a Golden Ticket
- Logs into the parent domain
- Retrieves credentials for the Administrator account in the parent domain

Finally, if the `target-exec` switch is specified, it authenticates to the parent domain's Domain Controller via Psexec.

#### Performing the Attack with raiseChild.py

![](../../../ZMEDIA/Pasted%20image%2020260707145754.png)

The script lists out the workflow and process in a comment as follows:
![](../../../ZMEDIA/Pasted%20image%2020260707145818.png)`

Though tools such as `raiseChild.py` can be handy and save us time, it is essential to understand the process and be able to perform the more manual version by gathering all of the required data points. In this case, if the tool fails, we are more likely to understand why and be able to troubleshoot what is missing, which we would not be able to if blindly running this tool. In a client production environment, we should **`always`** be careful when running any sort of "autopwn" script like this, and always remain cautious and construct commands manually when possible. Other tools exist which can take in data from a tool such as BloodHound, identify attack paths, and perform an "autopwn" function that can attempt to perform each action in an attack chain to elevate us to Domain Admin (such as a long ACL attack path). I would recommend avoiding tools such as these and work with tools that you understand fully, and will also give you the greatest degree of control throughout the process.

`We don't want to tell the client that something broke because we used an "autopwn" script!`

---

## More Fun

In the next section, we will briefly discuss some techniques that can be used for cross-forest trust abuse when we find ourselves in an environment with a bidirectional forest trust (meaning we can authenticate into another forest). We will not cover all possible cross-forest trust attacks, as those will be covered in great detail in later modules.