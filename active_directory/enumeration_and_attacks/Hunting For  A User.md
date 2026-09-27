# Hunting For A User

## Password Spraying Overview

***

Password spraying can result in gaining access to systems and potentially gaining a foothold on a target network. The attack involves attempting to log into an exposed service using one common password and a longer list of usernames or email addresses. The usernames and emails may have been gathered during the OSINT phase of the penetration test or our initial enumeration attempts. Remember that a penetration test is not static, but we are constantly iterating through several techniques and repeating processes as we uncover new data. Often we will be working in a team or executing multiple TTPs at once to utilize our time effectively. As we progress through our career, we will find that many of our tasks like scanning, attempting to crack hashes, and others take quite a bit of time. We need to make sure we are using our time effectively and creatively because most assessments are time-boxed. So while we have our poisoning attempts running, we can also utilize the info we have to attempt to gain access via Password Spraying. Now let's cover some of the considerations for Password spraying and how to make our target list from the information we have.

***

### Story Time

Password spraying can be a very effective way to gain a foothold internally. There are many times that this technique has helped me land a foothold during my assessments. Keep in mind that these examples come from non-evasive "grey box" assessments where I had internal network access with a Linux VM and a list of in-scope IP ranges and nothing else.

#### Scenario 1

In this first example, I performed all my standard checks and could not find anything useful like an SMB NULL session or LDAP anonymous bind that could allow me to retrieve a list of valid users. So I decided to use the `Kerbrute` tool to build a target username list by enumerating valid domain users (a technique we will cover later in this section). To create this list, I took the `jsmith.txt` username list from the [statistically-likely-usernames](https://github.com/insidetrust/statistically-likely-usernames) GitHub repo and combined this with results that I got from scraping LinkedIn. With this combined list in hand, I enumerated valid users with `Kerbrute` and then used the same tool to password spray with the common password `Welcome1`. I got two hits with this password for very low privileged users, but this gave me enough access within the domain to run BloodHound and eventually identify attack paths that led to domain compromise.

#### Scenario 2

In the second assessment, I was faced with a similar setup, but enumerating valid domain users with common username lists, and results from LinkedIn did not yield any results. I turned to Google and searched for PDFs published by the organization. My search generated many results, and I confirmed in the document properties of 4 of them that the internal username structure was in the format of `F9L8`, randomly generated GUIDs using just capital letters and numbers (`A-Z and 0-9`). This information was published with the document in the `Author` field and shows the importance of scrubbing document metadata before posting anything online. From here, a short Bash script could be used to generate 1,679,616 possible username combinations.

```
    bash
```

`#!/bin/bash for x in {{A..Z},{0..9}}{{A..Z},{0..9}}{{A..Z},{0..9}}{{A..Z},{0..9}} do echo $x; done`

I then used the generated username list with `Kerbrute` to enumerate every single user account in the domain. This attempt to make it more difficult to enumerate usernames ended up with me being able to enumerate every single account in the domain because of the predictable GUID in use combined with the PDF metadata I could locate and greatly facilitated the attack. Typically, I can only identify 40-60% of valid accounts using a list such as `jsmith.txt`. In this example, I significantly increased my chances of a successful password spraying attack by starting the attack with ALL domain accounts in my target list. From here, I obtained valid passwords for a few accounts. Eventually, I was able to follow a complicated attack chain involving [Resource-Based Constrained Delegation (RBCD)](https://posts.specterops.io/another-word-on-delegation-10bdbe3cd94a) and the [Shadow Credentials](https://web.archive.org/web/20250703081952/https://www.fortalicesolutions.com/posts/shadow-credentials-workstation-takeover-edition) attack to ultimately gain control over the domain.

***

### Password Spraying Considerations

While password spraying is useful for a penetration tester or red teamer, careless use may cause considerable harm, such as locking out hundreds of production accounts. One example is brute-forcing attempts to identify the password for an account using a long list of passwords. In contrast, password spraying is a more measured attack, utilizing very common passwords across multiple industries. The below table visualizes a password spray.

**Password Spray Visualization**

| **Attack** | **Username**                                                          | **Password** |
| ---------- | --------------------------------------------------------------------- | ------------ |
| 1          | [bob.smith@inlanefreight.local](mailto:bob.smith@inlanefreight.local) | Welcome1     |
| 1          | [john.doe@inlanefreight.local](mailto:john.doe@inlanefreight.local)   | Welcome1     |
| 1          | [jane.doe@inlanefreight.local](mailto:jane.doe@inlanefreight.local)   | Welcome1     |
| DELAY      |                                                                       |              |
| 2          | [bob.smith@inlanefreight.local](mailto:bob.smith@inlanefreight.local) | Passw0rd     |
| 2          | [john.doe@inlanefreight.local](mailto:john.doe@inlanefreight.local)   | Passw0rd     |
| 2          | [jane.doe@inlanefreight.local](mailto:jane.doe@inlanefreight.local)   | Passw0rd     |
| DELAY      |                                                                       |              |
| 3          | [bob.smith@inlanefreight.local](mailto:bob.smith@inlanefreight.local) | Winter2022   |
| 3          | [john.doe@inlanefreight.local](mailto:john.doe@inlanefreight.local)   | Winter2022   |
| 3          | [jane.doe@inlanefreight.local](mailto:jane.doe@inlanefreight.local)   | Winter2022   |

It involves sending fewer login requests per username and is less likely to lock out accounts than a brute force attack. However, password spraying still presents a risk of lockouts, so it is essential to introduce a delay between login attempts. Internal password spraying can be used to move laterally within a network, and the same considerations regarding account lockouts apply. However, it may be possible to obtain the domain password policy with internal access, significantly lowering this risk.

It’s common to find a password policy that allows five bad attempts before locking out the account, with a 30-minute auto-unlock threshold. Some organizations configure more extended account lockout thresholds, even requiring an administrator to unlock the accounts manually. If you don’t know the password policy, a good rule of thumb is to wait a few hours between attempts, which should be long enough for the account lockout threshold to reset. It is best to obtain the password policy before attempting the attack during an internal assessment, but this is not always possible.

## Enumerating & Retrieving Password Policies

***

### Enumerating the Password Policy - from Linux - Credentialed

As stated in the previous section, we can pull the domain password policy in several ways, depending on how the domain is configured and whether or not we have valid domain credentials. With valid domain credentials, the password policy can also be obtained remotely using tools such as [CrackMapExec](https://github.com/byt3bl33d3r/CrackMapExec) or `rpcclient`.

###

### Enumerating the Password Policy - from Linux - SMB NULL Sessions

Without credentials, we may be able to obtain the password policy via an SMB NULL session or LDAP anonymous bind. The first is via an SMB NULL session. SMB NULL sessions allow an unauthenticated attacker to retrieve information from the domain, such as a complete listing of users, groups, computers, user account attributes, and the domain password policy. SMB NULL session misconfigurations are often the result of legacy Domain Controllers being upgraded in place, ultimately bringing along insecure configurations, which existed by default in older versions of Windows Server.

When creating a domain in earlier versions of Windows Server, anonymous access was granted to certain shares, which allowed for domain enumeration. An SMB NULL session can be enumerated easily. For enumeration, we can use tools such as `enum4linux`, `CrackMapExec`, `rpcclient`, etc.

We can use [rpcclient](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html) to check a Domain Controller for SMB NULL session access.

Once connected, we can issue an RPC command such as `querydominfo` to obtain information about the domain and confirm NULL session access.

**Using rpcclient**

We can also obtain the password policy. We can see that the password policy is relatively weak, allowing a minimum password of 8 characters.

**Obtaining the Password Policy using rpcclient**

***

Let's try this using [enum4linux](https://labs.portcullis.co.uk/tools/enum4linux). `enum4linux` is a tool built around the [Samba suite of tools](https://www.samba.org/samba/docs/current/man-html/samba.7.html) `nmblookup`, `net`, `rpcclient` and `smbclient` to use for enumeration of windows hosts and domains. It can be found pre-installed on many different penetration testing distros, including Parrot Security Linux. Below we have an example output displaying information that can be provided by `enum4linux`. Here are some common enumeration tools and the ports they use:

| Tool      | Ports                                             |
| --------- | ------------------------------------------------- |
| nmblookup | 137/UDP                                           |
| nbtstat   | 137/UDP                                           |
| net       | 139/TCP, 135/TCP, TCP and UDP 135 and 49152-65535 |
| rpcclient | 135/TCP                                           |
| smbclient | 445/TCP                                           |

**Using enum4linux**

The tool [enum4linux-ng](https://github.com/cddmp/enum4linux-ng) is a rewrite of `enum4linux` in Python, but has additional features such as the ability to export data as YAML or JSON files which can later be used to process the data further or feed it to other tools. It also supports colored output, among other features

**Using enum4linux-ng**

&#x20;Enum4linux-ng provided us with a bit clearer output and handy JSON and YAML output using the `-oA` flag.

**Displaying the contents of ilfreight.json**

### Enumerating Null Session - from Windows

It is less common to do this type of null session attack from Windows, but we could use the command `net use \\host\ipc$ "" /u:""` to establish a null session from a windows machine and confirm if we can perform more of this type of attack.

**Establish a null session from windows**

```cmd
C:\htb> net use \\DC01\ipc$ "" /u:"" The command completed successfully.
```

We can also use a username/password combination to attempt to connect. Let's see some common errors when trying to authenticate:

**Error: Account is Disabled**

```cmd
C:\htb> net use \\DC01\ipc$ "" /u:guest System error 1331 has occurred. This user can't sign in because this account is currently disabled.
```

**Error: Password is Incorrect**

```cmd
C:\htb> net use \\DC01\ipc$ "password" /u:guest System error 1326 has occurred. The user name or password is incorrect.
```

**Error: Account is locked out (Password Policy)**

```cmd
C:\htb> net use \\DC01\ipc$ "password" /u:guest System error 1909 has occurred. The referenced account is currently locked out and may not be logged on to.
```

### Enumerating the Password Policy - from Linux - LDAP Anonymous Bind

[LDAP anonymous binds](https://docs.microsoft.com/en-us/troubleshoot/windows-server/identity/anonymous-ldap-operations-active-directory-disabled) allow unauthenticated attackers to retrieve information from the domain, such as a complete listing of users, groups, computers, user account attributes, and the domain password policy. This is a legacy configuration, and as of Windows Server 2003, only authenticated users are permitted to initiate LDAP requests. We still see this configuration from time to time as an admin may have needed to set up a particular application to allow anonymous binds and given out more than the intended amount of access, thereby giving unauthenticated users access to all objects in AD.

With an LDAP anonymous bind, we can use LDAP-specific enumeration tools such as `windapsearch.py`, `ldapsearch`, `ad-ldapdomaindump.py`, etc., to pull the password policy. With [ldapsearch](https://linux.die.net/man/1/ldapsearch), it can be a bit cumbersome but doable. One example command to get the password policy is as follows:

**Using ldapsearch**

Note: In newer versions of `ldapsearch`, the `-h` parameter was deprecated in favor for `-H`.

Here we can see the minimum password length of 8, lockout threshold of 5, and password complexity is set (`pwdProperties` set to `1`).

***

### Enumerating the Password Policy - from Windows

If we can authenticate to the domain from a Windows host, we can use built-in Windows binaries such as `net.exe` to retrieve the password policy. We can also use various tools such as PowerView, CrackMapExec ported to Windows, SharpMapExec, SharpView, etc.

Using built-in commands is helpful if we land on a Windows system and cannot transfer tools to it, or we are positioned on a Windows system by the client, but have no way of getting tools onto it. One example using the built-in net.exe binary is:

**Using net.exe**

&#x20;Here we can glean the following information:

* Passwords never expire (Maximum password age set to Unlimited)
* The minimum password length is 8 so weak passwords are likely in use
* The lockout threshold is 5 wrong passwords
* Accounts remained locked out for 30 minutes

This password policy is excellent for password spraying. The eight-character minimum means that we can try common weak passwords such as `Welcome1`. The lockout threshold of 5 means that we can attempt 2-3 (to be safe) sprays every 31 minutes without the risk of locking out any accounts. If an account has been locked out, it will automatically unlock (without manual intervention from an admin) after 30 minutes, but we should avoid locking out `ANY` accounts at all costs.

PowerView is also quite handy for this:

**Using PowerView**

PowerView gave us the same output as our `net accounts` command, just in a different format but also revealed that password complexity is enabled (`PasswordComplexity=1`).

As with Linux, we have many tools at our disposal to retrieve the password policy while on a Windows system, whether it is our attack system or a system provided by the client. PowerView/SharpView are always good bets, as are CrackMapExec, SharpMapExec, and others. The choice of tools depends on the goal of the assessment, stealth considerations, any anti-virus or EDR in place, and other potential restrictions on the target host. Let's cover a few examples.

***

### Analyzing the Password Policy

We've now pulled the password policy in numerous ways. Let's go through the policy for the INLANEFREIGHT.LOCAL domain piece by piece.

* The minimum password length is 8 (8 is very common, but nowadays, we are seeing more and more organizations enforce a 10-14 character password, which can remove some password options for us, but does not mitigate the password spraying vector completely)
* The account lockout threshold is 5 (it is not uncommon to see a lower threshold such as 3 or even no lockout threshold set at all)
* The lockout duration is 30 minutes (this may be higher or lower depending on the organization), so if we do accidentally lockout (avoid!!) an account, it will unlock after the 30-minute window passes
* Accounts unlock automatically (in some organizations, an admin must manually unlock the account). We never want to lockout accounts while performing password spraying, but we especially want to avoid locking out accounts in an organization where an admin would have to intervene and unlock hundreds (or thousands) of accounts by hand/script
* Password complexity is enabled, meaning that a user must choose a password with 3/4 of the following: an uppercase letter, lowercase letter, number, special character (`Password1` or `Welcome1` would satisfy the "complexity" requirement here, but are still clearly weak passwords).

The default password policy when a new domain is created is as follows, and there have been plenty of organizations that never changed this policy:

| Policy                                      | Default Value |
| ------------------------------------------- | ------------- |
| Enforce password history                    | 24 days       |
| Maximum password age                        | 42 days       |
| Minimum password age                        | 1 day         |
| Minimum password length                     | 7             |
| Password must meet complexity requirements  | Enabled       |
| Store passwords using reversible encryption | Disabled      |
| Account lockout duration                    | Not set       |
| Account lockout threshold                   | 0             |
| Reset account lockout counter after         | Not set       |

***

### Next Steps

Now that we have the password policy in hand, we need to create a target user list to perform our password spraying attack. Remember that sometimes we will not be able to obtain the password policy if we are performing external password spraying (or if we are on an internal assessment and cannot retrieve the policy using any of the methods shown here). In these cases, we `MUST` exercise extreme caution not to lock out accounts. We can always ask our client for their password policy if the goal is as comprehensive an assessment as possible. If asking for the policy does not fit the expectations of the assessment or the client does not want to provide it, we should run one, max two, password spraying attempts (regardless of whether we are internal or external) and wait over an hour between attempts if we indeed decide to attempt two. While most organizations will have a lockout threshold of 5 bad password attempts, a lockout duration of 30 minutes and accounts will automatically unlock, we cannot always count on this being normal. I have seen plenty of organizations with a lockout threshold of 3, requiring an admin to intervene and unlock accounts manually.

`We do not want to be the pentester that locks out every account in the organization!`

## Password Spraying - Making a Target User List

***

### Detailed User Enumeration

To mount a successful password spraying attack, we first need a list of valid domain users to attempt to authenticate with. There are several ways that we can gather a target list of valid users:

* By leveraging an SMB NULL session to retrieve a complete list of domain users from the domain controller
* Utilizing an LDAP anonymous bind to query LDAP anonymously and pull down the domain user list
* Using a tool such as `Kerbrute` to validate users utilizing a word list from a source such as the [statistically-likely-usernames](https://github.com/insidetrust/statistically-likely-usernames) GitHub repo, or gathered by using a tool such as [linkedin2username](https://github.com/initstring/linkedin2username) to create a list of potentially valid users
* Using a set of credentials from a Linux or Windows attack system either provided by our client or obtained through another means such as LLMNR/NBT-NS response poisoning using `Responder` or even a successful password spray using a smaller wordlist

No matter the method we choose, it is also vital for us to consider the domain password policy. If we have an SMB NULL session, LDAP anonymous bind, or a set of valid credentials, we can enumerate the password policy. Having this policy in hand is very useful because the minimum password length and whether or not password complexity is enabled can help us formulate the list of passwords we will try in our spray attempts. Knowing the account lockout threshold and bad password timer will tell us how many spray attempts we can do at a time without locking out any accounts and how many minutes we should wait between spray attempts.

Again, if we do not know the password policy, we can always ask our client, and, if they won't provide it, we can either try one very targeted password spraying attempt as a "hail mary" if all other options for a foothold have been exhausted. We could also try one spray every few hours in an attempt to not lock out any accounts. Regardless of the method we choose, and if we have the password policy or not, we must always keep a log of our activities, including, but not limited to:

* The accounts targeted
* Domain Controller used in the attack
* Time of the spray
* Date of the spray
* Password(s) attempted

This will help us ensure that we do not duplicate efforts. If an account lockout occurs or our client notices suspicious logon attempts, we can supply them with our notes to crosscheck against their logging systems and ensure nothing nefarious was going on in the network.

***

### SMB NULL Session to Pull User List

If you are on an internal machine but don’t have valid domain credentials, you can look for SMB NULL sessions or LDAP anonymous binds on Domain Controllers. Either of these will allow you to obtain an accurate list of all users within Active Directory and the password policy. If you already have credentials for a domain user or `SYSTEM` access on a Windows host, then you can easily query Active Directory for this information.

It’s possible to do this using the SYSTEM account because it can `impersonate` the computer. A computer object is treated as a domain user account (with some differences, such as authenticating across forest trusts). If you don’t have a valid domain account, and SMB NULL sessions and LDAP anonymous binds are not possible, you can create a user list using external resources such as email harvesting and LinkedIn. This user list will not be as complete, but it may be enough to provide you with access to Active Directory.

Some tools that can leverage SMB NULL sessions and LDAP anonymous binds include [enum4linux](https://github.com/portcullislabs/enum4linux), [rpcclient](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html), and [CrackMapExec](https://github.com/byt3bl33d3r/CrackMapExec), among others. Regardless of the tool, we'll have to do a bit of filtering to clean up the output and obtain a list of only usernames, one on each line. We can do this with `enum4linux` with the `-U` flag.

**Using enum4linux**

We can use the `enumdomusers` command after connecting anonymously using `rpcclient`.

**Using rpcclient**

Finally, we can use `CrackMapExec` with the `--users` flag. This is a useful tool that will also show the `badpwdcount` (invalid login attempts), so we can remove any accounts from our list that are close to the lockout threshold. It also shows the `baddpwdtime`, which is the date and time of the last bad password attempt, so we can see how close an account is to having its `badpwdcount` reset. In an environment with multiple Domain Controllers, this value is maintained separately on each one. To get an accurate total of the account's bad password attempts, we would have to either query each Domain Controller and use the sum of the values or query the Domain Controller with the PDC Emulator FSMO role.

**Using CrackMapExec --users Flag**

###

### Gathering Users with LDAP Anonymous

We can use various tools to gather users when we find an LDAP anonymous bind. Some examples include [windapsearch](https://github.com/ropnop/windapsearch) and [ldapsearch](https://linux.die.net/man/1/ldapsearch). If we choose to use `ldapsearch` we will need to specify a valid LDAP search filter. We can learn more about these search filters in the [Active Directory LDAP](https://academy.hackthebox.com/course/preview/active-directory-ldap) module.

**Using ldapsearch**

Tools such as `windapsearch` make this easier (though we should still understand how to create our own LDAP search filters). Here we can specify anonymous access by providing a blank username with the `-u` flag and the `-U` flag to tell the tool to retrieve just users.

**Using windapsearch**

***

### Enumerating Users with Kerbrute

As mentioned in the `Initial Enumeration of The Domain` section, if we have no access at all from our position in the internal network, we can use `Kerbrute` to enumerate valid AD accounts and for password spraying.

This tool uses [Kerberos Pre-Authentication](https://ldapwiki.com/wiki/Wiki.jsp?page=Kerberos%20Pre-Authentication), which is a much faster and potentially stealthier way to perform password spraying. This method does not generate Windows event ID [4625: An account failed to log on](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4625), or a logon failure which is often monitored for. The tool sends TGT requests to the domain controller without Kerberos Pre-Authentication to perform username enumeration. If the KDC responds with the error `PRINCIPAL UNKNOWN`, the username is invalid. Whenever the KDC prompts for Kerberos Pre-Authentication, this signals that the username exists, and the tool will mark it as valid. This method of username enumeration does not cause logon failures and will not lock out accounts. However, once we have a list of valid users and switch gears to use this tool for password spraying, failed Kerberos Pre-Authentication attempts will count towards an account's failed login accounts and can lead to account lockout, so we still must be careful regardless of the method chosen.

Let's try out this method using the [jsmith.txt](https://github.com/insidetrust/statistically-likely-usernames/blob/master/jsmith.txt) wordlist of 48,705 possible common usernames in the format `flast`. The [statistically-likely-usernames](https://github.com/insidetrust/statistically-likely-usernames) GitHub repo is an excellent resource for this type of attack and contains a variety of different username lists that we can use to enumerate valid usernames using `Kerbrute`.

**Kerbrute User Enumeration**

We've checked over 48,000 usernames in just over 12 seconds and discovered 50+ valid ones. Using Kerbrute for username enumeration will generate event ID [4768: A Kerberos authentication ticket (TGT) was requested](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768). This will only be triggered if [Kerberos event logging](https://docs.microsoft.com/en-us/troubleshoot/windows-server/identity/enable-kerberos-event-logging) is enabled via Group Policy. Defenders can tune their SIEM tools to look for an influx of this event ID, which may indicate an attack. If we are successful with this method during a penetration test, this can be an excellent recommendation to add to our report.

If we are unable to create a valid username list using any of the methods highlighted above, we could turn back to external information gathering and search for company email addresses or use a tool such as [linkedin2username](https://github.com/initstring/linkedin2username) to mash up possible usernames from a company's LinkedIn page.

***

### Credentialed Enumeration to Build our User List

With valid credentials, we can use any of the tools stated previously to build a user list. A quick and easy way is using CrackMapExec.

**Using CrackMapExec with Valid Credentials**

### Now for the Fun

Now that we've covered creating a target user list for spraying and discussed password policies, let's get our hands dirty performing password spraying attacks a few ways from a Linux attack host and then from a Windows host.
