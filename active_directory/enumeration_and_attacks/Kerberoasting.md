# Kerberoasting - from Linux

---

Our enumeration up to this point has given us a broad picture of the domain and potential issues. We have enumerated user accounts and can see that some are configured with Service Principal Names. Let's see how we can leverage this to move laterally and escalate privileges in the target domain.

---

## Kerberoasting Overview

Kerberoasting is a lateral movement/privilege escalation technique in Active Directory environments. This attack targets [Service Principal Names (SPN)](https://docs.microsoft.com/en-us/windows/win32/ad/service-principal-names) accounts. SPNs are unique identifiers that Kerberos uses to map a service instance to a service account in whose context the service is running. Domain accounts are often used to run services to overcome the network authentication limitations of built-in accounts such as `NT AUTHORITY\LOCAL SERVICE`. Any domain user can request a Kerberos ticket for any service account in the same domain. This is also possible across forest trusts if authentication is permitted across the trust boundary. All you need to perform a Kerberoasting attack is an account's cleartext password (or NTLM hash), a shell in the context of a domain user account, or SYSTEM level access on a domain-joined host.

Domain accounts running services are often local administrators, if not highly privileged domain accounts. Due to the distributed nature of systems, interacting services, and associated data transfers, service accounts may be granted administrator privileges on multiple servers across the enterprise. Many services require elevated privileges on various systems, so service accounts are often added to privileged groups, such as Domain Admins, either directly or via nested membership. Finding SPNs associated with highly privileged accounts in a Windows environment is very common. Retrieving a Kerberos ticket for an account with an SPN does not by itself allow you to execute commands in the context of this account. However, the ticket (TGS-REP) is encrypted with the service account’s NTLM hash, so the cleartext password can potentially be obtained by subjecting it to an offline brute-force attack with a tool such as Hashcat.

Service accounts are often configured with weak or reused password to simplify administration, and sometimes the password is the same as the username. If the password for a domain SQL Server service account is cracked, you are likely to find yourself as a local admin on multiple servers, if not Domain Admin. Even if cracking a ticket obtained via a Kerberoasting attack gives a low-privilege user account, we can use it to craft service tickets for the service specified in the SPN. For example, if the SPN is set to MSSQL/SRV01, we can access the MSSQL service as sysadmin, enable the xp_cmdshell extended procedure and gain code execution on the target SQL server.

For an interesting look at the origin of this technique, check out the [talk](https://youtu.be/PUyhlN-E5MU) Tim Medin gave at Derbycon 2014, showcasing Kerberoasting to the world.

---

## Kerberoasting - Performing the Attack

Depending on your position in a network, this attack can be performed in multiple ways:

- From a non-domain joined Linux host using valid domain user credentials.
- From a domain-joined Linux host as root after retrieving the keytab file.
- From a domain-joined Windows host authenticated as a domain user.
- From a domain-joined Windows host with a shell in the context of a domain account.
- As SYSTEM on a domain-joined Windows host.
- From a non-domain joined Windows host using [runas](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc771525\(v=ws.11\)) /netonly.

Several tools can be utilized to perform the attack:

- Impacket’s [GetUserSPNs.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/GetUserSPNs.py) from a non-domain joined Linux host.
- A combination of the built-in setspn.exe Windows binary, PowerShell, and Mimikatz.
- From Windows, utilizing tools such as PowerView, [Rubeus](https://github.com/GhostPack/Rubeus), and other PowerShell scripts.

Obtaining a TGS ticket via Kerberoasting does not guarantee you a set of valid credentials, and the ticket must still be `cracked` offline with a tool such as Hashcat to obtain the cleartext password. TGS tickets take longer to crack than other formats such as NTLM hashes, so often, unless a weak password is set, it can be difficult or impossible to obtain the cleartext using a standard cracking rig.

---

## Efficacy of the Attack

While it can be a great way to move laterally or escalate privileges in a domain, Kerberoasting and the presence of SPNs do not guarantee us any level of access. We might be in an environment where we crack a TGS ticket and obtain Domain Admin access straightway or obtain credentials that help us move down the path to domain compromise. Other times we may perform the attack and retrieve many TGS tickets, some of which we can crack, but none of the ones that crack are for privileged users, and the attack does not gain us any additional access. I would likely write up the finding as high-risk in my report in the first two cases. In the third case, we may Kerberoast and end up unable to crack a single TGS ticket, even after days of cracking attempts with Hashcat on a powerful GPU password cracking rig. In this scenario, I would still write up the finding, but I would drop it down to a medium-risk issue to make the client aware of the risk of SPNs in the domain (these strong passwords could always be changed to something weaker or a very determined attacker may be able to crack the tickets using Hashcat), but take into account the fact that I was unable to take control of any domain accounts using the attack. It is vital to make these types of distinctions in our reports and know when it's ok to lower the risk of a finding when mitigating controls (such as very strong passwords) are in place.

---

## Performing the Attack

Kerberoasting attacks are easily done now using automated tools and scripts. We will cover performing this attack in various ways, both from a Linux and a Windows attack host. Let's first go through how to do this from a Linux host. The following section will walk through a "semi-manual" way of performing the attack and two quick, automated attacks using common open-source tools, all from a Windows attack host.

---

## Kerberoasting with GetUserSPNs.py

A prerequisite to performing Kerberoasting attacks is either domain user credentials (cleartext or just an NTLM hash if using Impacket), a shell in the context of a domain user, or account such as SYSTEM. Once we have this level of access, we can start. We must also know which host in the domain is a Domain Controller so we can query it.

Let's start by installing the Impacket toolkit, which we can grab from [Here](https://github.com/SecureAuthCorp/impacket). After cloning the repository, we can cd into the directory and install it as follows:

#### Installing Impacket using Pip

![](../../ZMEDIA/Pasted%20image%2020260707084410.png)
This will install all Impacket tools and place them in our PATH so we can call them from any directory on our attack host. Impacket is already installed on the attack host that we can spawn at the end of this section to follow along and work through the exercises. Running the tool with the `-h` flag will bring up the help menu.

#### Listing GetUserSPNs.py Help Options

![](../../ZMEDIA/Pasted%20image%2020260707084427.png)

We can start by just gathering a listing of SPNs in the domain. To do this, we will need a set of valid domain credentials and the IP address of a Domain Controller. We can authenticate to the Domain Controller with a cleartext password, NT password hash, or even a Kerberos ticket. For our purposes, we will use a password. Entering the below command will generate a credential prompt and then a nicely formatted listing of all SPN accounts. From the output below, we can see that several accounts are members of the Domain Admins group. If we can retrieve and crack one of these tickets, it could lead to domain compromise. It is always worth investigating the group membership of all accounts because we may find an account with an easy-to-crack ticket that can help us further our goal of moving laterally/vertically in the target domain.

#### Listing SPN Accounts with GetUserSPNs.py
![](../../ZMEDIA/Pasted%20image%2020260707084443.png)

We can now pull all TGS tickets for offline processing using the `-request` flag. The TGS tickets will be output in a format that can be readily provided to Hashcat or John the Ripper for offline password cracking attempts.

#### Requesting all TGS Tickets

![](../../ZMEDIA/Pasted%20image%2020260707084515.png)
We can also be more targeted and request just the TGS ticket for a specific account. Let's try requesting one for just the `sqldev` account.

#### Requesting a Single TGS ticket

![](../../ZMEDIA/Pasted%20image%2020260707084536.png)

With this ticket in hand, we could attempt to crack the user's password offline using Hashcat. If we are successful, we may end up with Domain Admin rights.

To facilitate offline cracking, it is always good to use the `-outputfile` flag to write the TGS tickets to a file that can then be run using Hashcat on our attack system or moved to a GPU cracking rig.

#### Saving the TGS Ticket to an Output File
![](../../ZMEDIA/Pasted%20image%2020260707084549.png)

Here we've written the TGS ticket for the `sqldev` user to a file named `sqldev_tgs`. Now we can attempt to crack the ticket offline using Hashcat hash mode `13100`.

#### Cracking the Ticket Offline with Hashcat

![](../../ZMEDIA/Pasted%20image%2020260707084610.png)

![GIF showcasing the usage of hashcat to crack the obtained hash.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/hashcat_tgs.png)

We've successfully cracked the user's password as `database!`. As the last step, we can confirm our access and see that we indeed have Domain Admin rights as we can authenticate to the target DC in the INLANEFREIGHT.LOCAL domain. From here, we could perform post-exploitation and continue to enumerate the domain for other paths to compromise and other notable flaws and misconfigurations.

#### Testing Authentication against a Domain Controller
![](../../ZMEDIA/Pasted%20image%2020260707084621.png)

---

## More Roasting

Now that we've covered Kerberoasting from a Linux attack host, we'll go through the process from a Windows host. We may decide to perform part, or all, of our testing from a Windows host, our client may provide us with a Windows host to test from, or we may compromise a host and need to use it as a jump-off point for further attacks. Regardless of how we are using Windows hosts during our assessments, to remain versatile, it is essential to understand how to perform as many attacks as possible from both Linux and Windows hosts, because we never know what we will have thrown at us from one assessment to another.


# Kerberoasting - from Windows

---

## Kerberoasting - Semi Manual method

Before tools such as `Rubeus` existed, stealing or forging Kerberos tickets was a complex, manual process. As the tactic and defenses have evolved, we can now perform Kerberoasting from Windows in multiple ways. To start down this path, we will explore the manual route and then move into more automated tooling. Let's begin with the built-in [setspn](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc731241\(v=ws.11\)) binary to enumerate SPNs in the domain.

#### Enumerating SPNs with setspn.exe
![](../../ZMEDIA/Pasted%20image%2020260707084837.png)

We will notice many different SPNs returned for the various hosts in the domain. We will focus on `user accounts` and ignore the computer accounts returned by the tool. Next, using PowerShell, we can request TGS tickets for an account in the shell above and load them into memory. Once they are loaded into memory, we can extract them using `Mimikatz`. Let's try this by targeting a single user:

#### Targeting a Single User
![](../../ZMEDIA/Pasted%20image%2020260707084852.png)

Before moving on, let's break down the commands above to see what we are doing (which is essentially what is used by [Rubeus](https://posts.specterops.io/kerberoasting-revisited-d434351bd4d1) when using the default Kerberoasting method):

- The [Add-Type](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/add-type?view=powershell-7.2) cmdlet is used to add a .NET framework class to our PowerShell session, which can then be instantiated like any .NET framework object
- The `-AssemblyName` parameter allows us to specify an assembly that contains types that we are interested in using
- [System.IdentityModel](https://docs.microsoft.com/en-us/dotnet/api/system.identitymodel?view=netframework-4.8) is a namespace that contains different classes for building security token services
- We'll then use the [New-Object](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/new-object?view=powershell-7.2) cmdlet to create an instance of a .NET Framework object
- We'll use the [System.IdentityModel.Tokens](https://docs.microsoft.com/en-us/dotnet/api/system.identitymodel.tokens?view=netframework-4.8) namespace with the [KerberosRequestorSecurityToken](https://docs.microsoft.com/en-us/dotnet/api/system.identitymodel.tokens.kerberosrequestorsecuritytoken?view=netframework-4.8) class to create a security token and pass the SPN name to the class to request a Kerberos TGS ticket for the target account in our current logon session

We can also choose to retrieve all tickets using the same method, but this will also pull all computer accounts, so it is not optimal.

#### Retrieving All Tickets Using setspn.exe
![](../../ZMEDIA/Pasted%20image%2020260707084905.png)

The above command combines the previous command with `setspn.exe` to request tickets for all accounts with SPNs set.

Now that the tickets are loaded, we can use `Mimikatz` to extract the ticket(s) from `memory`.

## Extracting Tickets from Memory with Mimikatz

 ![](../../ZMEDIA/Pasted%20image%2020260707084942.png)

If we do not specify the `base64 /out:true` command, Mimikatz will extract the tickets and write them to `.kirbi` files. Depending on our position on the network and if we can easily move files to our attack host, this can be easier when we go to crack the tickets. Let's take the base64 blob retrieved above and prepare it for cracking.

Next, we can take the base64 blob and remove new lines and white spaces since the output is column wrapped, and we need it all on one line for the next step.

#### Preparing the Base64 Blob for Cracking

![](../../ZMEDIA/Pasted%20image%2020260707085001.png)

We can place the above single line of output into a file and convert it back to a `.kirbi` file using the `base64` utility.

#### Placing the Output into a File as .kirbi

```shellsession
haphestus@htb[/htb]$ cat encoded_file | base64 -d > sqldev.kirbi
```

Next, we can use [this](https://raw.githubusercontent.com/nidem/kerberoast/907bf234745fe907cf85f3fd916d1c14ab9d65c0/kirbi2john.py) version of the `kirbi2john.py` tool to extract the Kerberos ticket from the TGS file.

#### Extracting the Kerberos Ticket using kirbi2john.py

```shellsession
haphestus@htb[/htb]$ python2.7 kirbi2john.py sqldev.kirbi
```

This will create a file called `crack_file`. We then must modify the file a bit to be able to use Hashcat against the hash.

#### Modifiying crack_file for Hashcat

```shellsession
haphestus@htb[/htb]$ sed 's/\$krb5tgs\$\(.*\):\(.*\)/\$krb5tgs\$23\$\*\1\*\$\2/' crack_file > sqldev_tgs_hashcat
```

Now we can check and confirm that we have a hash that can be fed to Hashcat.

#### Viewing the Prepared Hash
![](../../ZMEDIA/Pasted%20image%2020260707085124.png)

We can then run the ticket through Hashcat again and get the cleartext password `database!`.

#### Cracking the Hash with Hashcat
![](../../ZMEDIA/Pasted%20image%2020260707085150.png)

If we decide to skip the base64 output with Mimikatz and type `mimikatz # kerberos::list /export`, the .kirbi file (or files) will be written to disk. In this case, we can download the file(s) and run `kirbi2john.py` against them directly, skipping the base64 decoding step.

Now that we have seen the older, more manual way to perform Kerberoasting from a Windows machine and offline processing, let's look at some quicker ways. Most assessments are time-boxed, and we often need to work as quickly and efficiently as possible, so the above method will likely not be our go-to every time. That being said, it can be useful for us to have other tricks up our sleeves and methodologies in case our automated tools fail or are blocked.

---

## Automated / Tool Based Route

Next, we'll cover two much quicker ways to perform Kerberoasting from a Windows host. First, let's use [PowerView](https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1) to extract the TGS tickets and convert them to Hashcat format. We can start by enumerating SPN accounts.

#### Using PowerView to Enumerate SPN Accounts
![](../../ZMEDIA/Pasted%20image%2020260707085206.png)

From here, we could target a specific user and retrieve the TGS ticket in Hashcat format.

#### Using PowerView to Target a Specific User

![](../../ZMEDIA/Pasted%20image%2020260707085300.png)

Finally, we can export all tickets to a CSV file for offline processing.

#### Exporting All Tickets to a CSV File

```powershell
PS C:\htb> Get-DomainUser * -SPN | Get-DomainSPNTicket -Format Hashcat | Export-Csv .\ilfreight_tgs.csv -NoTypeInformation
```

#### Viewing the Contents of the .CSV File
![](../../ZMEDIA/Pasted%20image%2020260707085336.png)

We can also use [Rubeus](https://github.com/GhostPack/Rubeus) from GhostPack to perform Kerberoasting even faster and easier. Rubeus provides us with a variety of options for performing Kerberoasting.

#### Using Rubeus
![](../../ZMEDIA/Pasted%20image%2020260707085401.png)
As we can see from scrolling the Rubeus help menu, the tool has a vast number of options for interacting with Kerberos, most of which are out of the scope of this module and will be covered in-depth in later modules on advanced Kerberos attacks. It is worth scrolling through the menu, familiarizing yourself with the options, and reading up on the various other possible tasks. Some options include:

- Performing Kerberoasting and outputting hashes to a file
- Using alternate credentials
- Performing Kerberoasting combined with a pass-the-ticket attack
- Performing "opsec" Kerberoasting to filter out AES-enabled accounts
- Requesting tickets for accounts passwords set between a specific date range
- Placing a limit on the number of tickets requested
- Performing AES Kerberoasting

#### Viewing Rubeus's Capabilities

![GIF showcasing the commands supported by Rubeus in a PowerShell terminal.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/rubeus_help.png)

We can first use Rubeus to gather some stats. From the output below, we can see that there are nine Kerberoastable users, seven of which support RC4 encryption for ticket requests and two of which support AES 128/256. More on encryption types later. We also see that all nine accounts had their password set this year (2022 at the time of writing). If we saw any SPN accounts with their passwords set 5 or more years ago, they could be promising targets as they could have a weak password that was set and never changed when the organization was less mature.

#### Using the /stats Flag
![](../../ZMEDIA/Pasted%20image%2020260707085419.png)

Let's use Rubeus to request tickets for accounts with the `admincount` attribute set to `1`. These would likely be high-value targets and worth our initial focus for offline cracking efforts with Hashcat. Be sure to specify the `/nowrap` flag so that the hash can be more easily copied down for offline cracking using Hashcat. Per the documentation, the ""/nowrap" flag prevents any base64 ticket blobs from being column wrapped for any function"; therefore, we won't have to worry about trimming white space or newlines before cracking with Hashcat.

#### Using the /nowrap Flag
![](../../ZMEDIA/Pasted%20image%2020260707085435.png)

---

## A Note on Encryption Types

Kerberoasting tools typically request `RC4 encryption` when performing the attack and initiating TGS-REQ requests. This is because RC4 is [weaker](https://www.stigviewer.com/stigs/microsoft_windows_10/2025-02-25/finding/V-220936) and easier to crack offline using tools such as Hashcat than other encryption algorithms such as AES-128 and AES-256. When performing Kerberoasting in most environments, we will retrieve hashes that begin with `$krb5tgs$23$*`, an RC4 (type 23) encrypted ticket. Sometimes we will receive an AES-256 (type 18) encrypted hash or hash that begins with `$krb5tgs$18$*`. While it is possible to crack AES-128 (type 17) and AES-256 (type 18) TGS tickets using [Hashcat](https://github.com/hashcat/hashcat/pull/1955), it will typically be significantly more time consuming than cracking an RC4 (type 23) encrypted ticket, but still possible especially if a weak password is chosen. Let's walk through an example.

Let's start by creating an SPN account named `testspn` and using Rubeus to Kerberoast this specific user to test this out. As we can see, we received the TGS ticket RC4 (type 23) encrypted.

![](../../ZMEDIA/Pasted%20image%2020260707085527.png)
Checking with PowerView, we can see that the `msDS-SupportedEncryptionTypes` attribute is set to `0`. The chart [here](https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/decrypting-the-selection-of-supported-kerberos-encryption-types/ba-p/1628797) tells us that a decimal value of `0` means that a specific encryption type is not defined and set to the default of `RC4_HMAC_MD5`.

```powershell
PS C:\htb> Get-DomainUser testspn -Properties samaccountname,serviceprincipalname,msds-supportedencryptiontypes

serviceprincipalname                   msds-supportedencryptiontypes samaccountname 
--------------------                   ----------------------------- -------------- testspn/kerberoast.inlanefreight.local                            0 testspn
```

Next, let's crack this ticket using Hashcat and note how long it took. The account is set with a weak password found in the `rockyou.txt` wordlist for our purposes. Running this through Hashcat, we see that it took four seconds to crack on a CPU, and therefore it would crack almost instantly on a powerful GPU cracking rig and probably even on a single GPU.

#### Cracking the Ticket with Hashcat & rockyou.txt

 ![](../../ZMEDIA/Pasted%20image%2020260707085626.png)
Let's assume that our client has set SPN accounts to support AES 128/256 encryption.

![Active Directory Users and Computers window showing properties for user 'testspn' with account options and logon settings.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/aes_kerberoast.png)

If we check this with PowerView, we'll see that the `msDS-SupportedEncryptionTypes attribute` is set to `24`, meaning that AES 128/256 encryption types are the only ones supported.

#### Checking Supported Encryption Types

```powershell
PS C:\htb> Get-DomainUser testspn -Properties samaccountname,serviceprincipalname,msds-supportedencryptiontypes

serviceprincipalname                   msds-supportedencryptiontypes samaccountname --------------------                   ----------------------------- -------------- 
testspn/kerberoast.inlanefreight.local                            24 testspn
```

Requesting a new ticket with Rubeus will show us that the account name is using AES-256 (type 18) encryption.

#### Requesting a New Ticket

![](../../ZMEDIA/Pasted%20image%2020260707085725.png)

To run this through Hashcat, we need to use hash mode `19700`, which is `Kerberos 5, etype 18, TGS-REP (AES256-CTS-HMAC-SHA1-96)` per the handy Hashcat [example_hashes](https://hashcat.net/wiki/doku.php?id=example_hashes) table. We run the AES hash as follows and check the status, which shows it should take over 23 minutes to run through the entire rockyou.txt wordlist by typing `s` to see the status of the cracking job.

#### Running Hashcat & Checking the Status of the Cracking Job
![](../../ZMEDIA/Pasted%20image%2020260707085816.png)
When the hash finally cracks, we see that it took 4 minutes 36 seconds for a relatively simple password on a CPU. This would be greatly magnified with a stronger/longer password.

#### Viewing the Length of Time it Took to Crack
![](../../ZMEDIA/Pasted%20image%2020260707085830.png)
We can use Rubeus with the `/tgtdeleg` flag to specify that we want only RC4 encryption when requesting a new service ticket. The tool does this by specifying RC4 encryption as the only algorithm we support in the body of the TGS request. This may be a failsafe built-in to Active Directory for backward compatibility. By using this flag, we can request an RC4 (type 23) encrypted ticket that can be cracked much faster.

#### Using the /tgtdeleg Flag

![Rubeus tool output showing kerberoasting action for user 'testspn' with RC4_HMAC and AES encryption types, displaying hash details.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/kerb_tgs_18.png)

In the above image, we can see that when supplying the `/tgtdeleg` flag, the tool requested an RC4 ticket even though the supported encryption types are listed as AES 128/256. This simple example shows the importance of detailed enumeration and digging deeper when performing attacks such as Kerberoasting. Here we could downgrade from AES to RC4 and cut cracking time down by over 4 minutes and 30 seconds. In a real-world engagement where we have a strong GPU password cracking rig at our disposal, this type of downgrade could result in a hash cracking in a few hours instead of a few days and could make or break our assessment.

Note: This does not work against a Windows Server 2019 Domain Controller, regardless of the domain functional level. It will always return a service ticket encrypted with the highest level of encryption supported by the target account. This being said, if we find ourselves in a domain with Domain Controllers running on Server 2016 or earlier (which is quite common), enabling AES will not partially mitigate Kerberoasting by only returning AES encrypted tickets, which are much more difficult to crack, but rather will allow an attacker to request an RC4 encrypted service ticket. In Windows Server 2019 DCs, enabling AES encryption on an SPN account will result in us receiving an AES-256 (type 18) service ticket, which is substantially more difficult (but not impossible) to crack, especially if a relatively weak dictionary password is in use.

It is possible to edit the encryption types used by Kerberos. This can be done by opening Group Policy, editing the Default Domain Policy, and choosing: `Computer Configuration > Policies > Windows Settings > Security Settings > Local Policies > Security Options`, then double-clicking on `Network security: Configure encryption types allowed for Kerberos` and selecting the desired encryption type allowed for Kerberos. Removing all other encryption types except for `RC4_HMAC_MD5` would allow for the above downgrade example to occur in 2019. Removing support for AES would introduce a security flaw into AD and should likely never be done. Furthermore, removing support for RC4 regardless of the Domain Controller Windows Server version or domain functional level could have operational impacts and should be thoroughly tested before implementation.

![Group Policy Management Editor showing security settings for Kerberos encryption types, including DES, RC4, and AES options.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/kerb_encrypt_types.png)

---

## Mitigation & Detection

An important mitigation for non-managed service accounts is to set a long and complex password or passphrase that does not appear in any word list and would take far too long to crack. However, it is recommended to use [Managed Service Accounts (MSA)](https://techcommunity.microsoft.com/t5/ask-the-directory-services-team/managed-service-accounts-understanding-implementing-best/ba-p/397009), and [Group Managed Service Accounts (gMSA)](https://docs.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview), which use very complex passwords, and automatically rotate on a set interval (like machine accounts) or accounts set up with LAPS.

Kerberoasting requests Kerberos TGS tickets with RC4 encryption, which should not be the majority of Kerberos activity within a domain. When Kerberoasting is occurring in the environment, we will see an abnormal number of `TGS-REQ` and `TGS-REP` requests and responses, signaling the use of automated Kerberoasting tools. Domain controllers can be configured to log Kerberos TGS ticket requests by selecting [Audit Kerberos Service Ticket Operations](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/audit-kerberos-service-ticket-operations) within Group Policy.

![Group Policy Management Editor showing audit settings for Kerberos Authentication Service with success and failure events configured.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/kerb_audit.png)

Doing so will generate two separate event IDs: [4769](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769): A Kerberos service ticket was requested, and [4770](https://docs.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4770): A Kerberos service ticket was renewed. 10-20 Kerberos TGS requests for a given account can be considered normal in a given environment. A large amount of 4769 event IDs from one account within a short period may indicate an attack.

Below we can see an example of a Kerberoasting attack being logged. We see many event ID 4769 being logged in succession, which appears to be anomalous behavior. Clicking into one, we can see that a Kerberos service ticket was requested by the `htb-student` user (attacker) for the `sqldev` account (target). We can also see that the ticket encryption type is `0x17`, which is the hex value for 23 (`DES_CBC_CRC, DES_CBC_MD5, RC4, AES 256`), meaning that the requested ticket was RC4, so if the password was weak, there is a good chance that the attacker would be able to crack it and gain control of the `sqldev` account.

![Event Viewer showing Security logs with Event ID 4769 for Kerberos Service Ticket Operations, detailing account and service information for htb-student@INLANEFREIGHT.LOCAL.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/4769.png)

Some other remediation steps include restricting the use of the RC4 algorithm, particularly for Kerberos requests by service accounts. This must be tested to make sure nothing breaks within the environment. Furthermore, Domain Admins and other highly privileged accounts should not be used as SPN accounts (if SPN accounts must exist in the environment).

This excellent [post](https://adsecurity.org/?p=3458) by Sean Metcalf highlights some mitigation and detection strategies for Kerberoasting.

---

## Continuing Onwards

Now that we have a set of (hopefully privileged) credentials, we can move on to see where we can use the credentials. We may be able to:

- Access a host via RDP or WinRM as a local user or a local admin
- Authenticate to a remote host as an admin using a tool such as PsExec
- Gain access to a sensitive file share
- Gain MSSQL access to a host as a DBA user, which can then be leveraged to escalate privileges

Regardless of our access, we will also want to dig deeper into the domain for other flaws and misconfigurations that can help us expand our access and add to our report to provide more value to our clients.