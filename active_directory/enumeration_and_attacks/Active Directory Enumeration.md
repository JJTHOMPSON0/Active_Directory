# Initial Enumeration
## External Recon and Enumeration Principles

Before kicking off any pentest, it can be beneficial to perform `external reconnaissance` of your target. This can serve many different functions, such as:

- Validating information provided to you in the scoping document from the client
- Ensuring you are taking actions against the appropriate scope when working remotely
- Looking for any information that is publicly accessible that can affect the outcome of your test, such as leaked credentials

Think of it like this; we are trying to get the `lay of the land` to ensure we provide the most comprehensive test possible for our customer. That also means identifying any potential information leaks and breach data out in the world. This can be as simple as gleaning a username format from the customer's main website or social media. We may also dive as deep as scanning GitHub repositories for credentials left in code pushes, hunting in documents for links to an intranet or remotely accessible sites, and just looking for any information that can key us in on how the enterprise environment is configured.

---

### What Are We Looking For?

When conducting our external reconnaissance, there are several key items that we should be looking for. This information may not always be publicly accessible, but it would be prudent to see what is out there. If we get stuck during a penetration test, looking back at what could be obtained through passive recon can give us that nudge needed to move forward, such as password breach data that could be used to access a VPN or other externally facing service. The table below highlights the "`What`" in what we would be searching for during this phase of our engagement.

|**Data Point**|**Description**|
|---|---|
|`IP Space`|Valid ASN for our target, netblocks in use for the organization's public-facing infrastructure, cloud presence and the hosting providers, DNS record entries, etc.|
|`Domain Information`|Based on IP data, DNS, and site registrations. Who administers the domain? Are there any subdomains tied to our target? Are there any publicly accessible domain services present? (Mailservers, DNS, Websites, VPN portals, etc.) Can we determine what kind of defenses are in place? (SIEM, AV, IPS/IDS in use, etc.)|
|`Schema Format`|Can we discover the organization's email accounts, AD usernames, and even password policies? Anything that will give us information we can use to build a valid username list to test external-facing services for password spraying, credential stuffing, brute forcing, etc.|
|`Data Disclosures`|For data disclosures we will be looking for publicly accessible files ( .pdf, .ppt, .docx, .xlsx, etc. ) for any information that helps shed light on the target. For example, any published files that contain `intranet` site listings, user metadata, shares, or other critical software or hardware in the environment (credentials pushed to a public GitHub repo, the internal AD username format in the metadata of a PDF, for example.)|
|`Breach Data`|Any publicly released usernames, passwords, or other critical information that can help an attacker gain a foothold.|

We have addressed the `why` and `what` of external reconnaissance; let's dive into the `where` and `how`.

---

### Where Are We Looking?

Our list of data points above can be gathered in many different ways. There are many different websites and tools that can provide us with some or all of the information above that we could use to obtain information vital to our assessment. The table below lists a few potential resources and examples that can be used.

|**Resource**|**Examples**|
|---|---|
|`ASN / IP registrars`|[IANA](https://www.iana.org/), [arin](https://www.arin.net/) for searching the Americas, [RIPE](https://www.ripe.net/) for searching in Europe, [BGP Toolkit](https://bgp.he.net/)|
|`Domain Registrars & DNS`|[Domaintools](https://www.domaintools.com/), [PTRArchive](http://ptrarchive.com/), [ICANN](https://lookup.icann.org/lookup), manual DNS record requests against the domain in question or against well known DNS servers, such as `8.8.8.8`.|
|`Social Media`|Searching Linkedin, Twitter, Facebook, your region's major social media sites, news articles, and any relevant info you can find about the organization.|
|`Public-Facing Company Websites`|Often, the public website for a corporation will have relevant info embedded. News articles, embedded documents, and the "About Us" and "Contact Us" pages can also be gold mines.|
|`Cloud & Dev Storage Spaces`|[GitHub](https://github.com/), [AWS S3 buckets & Azure Blog storage containers](https://grayhatwarfare.com/), [Google searches using "Dorks"](https://www.exploit-db.com/google-hacking-database)|
|`Breach Data Sources`|[HaveIBeenPwned](https://haveibeenpwned.com/) to determine if any corporate email accounts appear in public breach data, [Dehashed](https://www.dehashed.com/) to search for corporate emails with cleartext passwords or hashes we can try to crack offline. We can then try these passwords against any exposed login portals (Citrix, RDS, OWA, 0365, VPN, VMware Horizon, custom applications, etc.) that may use AD authentication.|

### Finding Address Spaces

![Welcome to Hurricane Electric BGP Toolkit. Displays visitor IP 72.185.168.230, announced as 72.184.0.0/14, ISP AS33363 (Charter Communications).](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/bgp-toolkit.png)

The `BGP-Toolkit` hosted by [Hurricane Electric](http://he.net/) is a fantastic resource for researching what address blocks are assigned to an organization and what ASN they reside within. Just punch in a domain or IP address, and the toolkit will search for any results it can. We can glean a lot from this info. Many large corporations will often self-host their infrastructure, and since they have such a large footprint, they will have their own ASN. This will typically not be the case for smaller organizations or fledgling companies. As you research, keep this in mind since smaller organizations will often host their websites and other infrastructure in someone else's space (Cloudflare, Google Cloud, AWS, or Azure, for example). Understanding where that infrastructure resides is extremely important for our testing. We have to ensure we are not interacting with infrastructure out of our scope. If we are not careful while pentesting against a smaller organization, we could end up inadvertently causing harm to another organization sharing that infrastructure. 

In some cases, your client may need to get written approval from a third-party hosting provider before you can test. Others, such as AWS, have specific [guidelines](https://aws.amazon.com/security/penetration-testing/) for performing penetration tests and do not require prior approval for testing some of their services. Others, such as Oracle, ask you to submit a [Cloud Security Testing Notification](https://docs.oracle.com/en-us/iaas/Content/Security/Concepts/security_testing-policy_notification.htm).

### DNS

DNS is a great way to validate our scope and find out about reachable hosts the customer did not disclose in their scoping document. Sites like [domaintools](https://whois.domaintools.com/), and [viewdns.info](https://viewdns.info/) are great spots to start. We can get back many records and other data ranging from DNS resolution to testing for DNSSEC and if the site is accessible in more restricted countries. Sometimes we may find additional hosts out of scope, but look interesting. In that case, we could bring this list to our client to see if any of them should indeed be included in the scope. We may also find interesting subdomains that were not listed in the scoping documents, but reside on in-scope IP addresses and therefore are fair game.

#### Viewdns.info

![ViewDNS.info tools page with options for Reverse IP Lookup, Reverse Whois Lookup, IP History, DNS Report, Reverse MX Lookup, Reverse NS Lookup, IP Location Finder, Chinese Firewall Test, DNS Propagation Checker, Is My Site Down, Iran Firewall Test, and Domain/IP Whois.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/viewdnsinfo.png)

This is also a great way to validate some of the data found from our IP/ASN searches. Not all information about the domain found will be current, and running checks that can validate what we see is always good practice.

### Public Data

Social media can be a treasure trove of interesting data that can clue us in to how the organization is structured, what kind of equipment they operate, potential software and security implementations, their schema, and more. On top of that list are job-related sites like LinkedIn, Indeed.com, and Glassdoor. Simple job postings often reveal a lot about a company. For example, take a look at the job listing below. It's for a `SharePoint Administrator` and can key us in on many things. We can tell from the listing that the company has been using SharePoint for a while and has a mature program since they are talking about security programs, backup & disaster recovery, and more. What is interesting to us in this posting is that we can see the company likely uses SharePoint 2013 and SharePoint 2016. That means they may have upgraded in place, potentially leaving vulnerabilities in play that may not exist in newer versions. This also means we may run into different versions of SharePoint during our engagements.

### Sharepoint Admin Job Listing

![Job description for a remote SharePoint Administrator with 8+ years experience, requiring skills in application deployment, SharePoint, Azure, PHP, teamwork, and enterprise applications.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/spjob2.png)

Don't discount public information such as job postings or social media. You can learn a lot about an organization just from what they post, and a well-intentioned post could disclose data relevant to us as penetration testers.

Websites hosted by the organization are also great places to dig for information. We can gather contact emails, phone numbers, organizational charts, published documents, etc. These sites, specifically the embedded documents, can often have links to internal infrastructure or intranet sites that you would not otherwise know about. Checking any publicly accessible information for those types of details can be quick wins when trying to formulate a picture of the domain structure. With the growing use of sites such as GitHub, AWS cloud storage, and other web-hosted platforms, data can also be leaked unintentionally. For example, a dev working on a project may accidentally leave some credentials or notes hardcoded into a code release. If you know where to look for that data, it can give you an easy win. It could mean the difference between having to password spray and brute-force credentials for hours or days or gaining a quick foothold with developer credentials, which may also have elevated permissions. Tools like [Trufflehog](https://github.com/trufflesecurity/truffleHog) and sites like [Greyhat Warfare](https://buckets.grayhatwarfare.com/) are fantastic resources for finding these breadcrumbs.


---

### Overarching Enumeration Principles

Keeping in mind that our goal is to understand our target better, we are looking for every possible avenue we can find that will provide us with a potential route to the inside. Enumeration itself is an iterative process we will repeat several times throughout a penetration test. Besides the customer's scoping document, this is our primary source of information, so we want to ensure we are leaving no stone unturned. When starting our enumeration, we will first use `passive` resources, starting wide in scope and narrowing down. Once we exhaust our initial run of passive enumeration, we will need to examine the results and then move into our active enumeration phase.

---

### Example Enumeration Process

We have already covered quite a few concepts pertaining to enumeration. Let's start putting it all together. We will practice our enumeration tactics on the `inlanefreight.com` domain without performing any heavy scans (such as Nmap or vulnerability scans which are out of scope). We will start first by checking our Netblocks data and seeing what we can find.

#### Check for ASN/IP & Domain Data

![DNS info for inlanefreight.com: Start of Authority with AWS DNS, nameservers ns1 and ns2.inlanefreight.com, mail exchanger mail1.inlanefreight.com, A record 134.209.24.248, and AAAA record 2A03:B0C0:1:E0::32C:B001.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/BGPhe-inlane.png)

From this first look, we have already gleaned some interesting info. BGP.he is reporting:

- IP Address: 134.209.24.248
- Mail Server: mail1.inlanefreight.com
- Nameservers: NS1.inlanefreight.com & NS2.inlanefreight.com

For now, this is what we care about from its output. Inlanefreight is not a large corporation, so we didn't expect to find that it had its own ASN. Now let's validate some of this information.

#### Viewdns Results

![Reverse IP results for inlanefreight.com showing two domains: inlanefreight.com and lycjg.us, with last resolved dates.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/viewdns-results.png)

In the request above, we utilized `viewdns.info` to validate the IP address of our target. Both results match, which is a good sign. Now let's try another route to validate the two nameservers in our results.
```shell
haphestus@htb[/htb]$ nslookup ns1.inlanefreight.com Server:     192.168.186.1 Address:    192.168.186.1#53 Non-authoritative answer: Name:   ns1.inlanefreight.com Address: 178.128.39.165 nslookup ns2.inlanefreight.com Server:     192.168.86.1 Address:    192.168.86.1#53 Non-authoritative answer: Name:   ns2.inlanefreight.com Address: 206.189.119.186
```

We now have `two` new IP addresses to add to our list for validation and testing. Before taking any further action with them, ensure they are in-scope for your test. For our purposes, the actual IP addresses would not be in scope for scanning, but we could passively browse any websites to hunt for interesting data. For now, that is it with enumerating domain information from DNS. Let's take a look at the publicly available information.

Inlanefreight is a fictitious company that we are using for this module, so there is no real social media presence. However, we would check sites like LinkedIn, Twitter, Instagram, and Facebook for helpful info if it were real. Instead, we will move on to examining the website `inlanefreight.com`.

The first check we ran was looking for any documents. Using `filetype:pdf inurl:inlanefreight.com` as a search, we are looking for PDFs.

#### Hunting For Files

![Google search result for 'filetype:pdf inurl:inlanefreight.com' showing a PDF titled 'corporate goals and strategy - Inlanefreight' from inlanefreight.com.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/google-dorks.png)

One document popped up, so we need to ensure we note the document and its location and download a copy locally to dig through. It is always best to save files, screenshots, scan output, tool output, etc., as soon as we come across them or generate them. This helps us keep as comprehensive a record as possible and not risk forgetting where we saw something or losing critical data. Next, let's look for any email addresses we can find.

#### Hunting E-mail Addresses

![Google search for 'intext:"@inlanefreight.com" inurl:inlanefreight.com' showing results for Inlanefreight's homepage and contact page.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/intext-dork.png)

Using the dork `intext:"@inlanefreight.com" inurl:inlanefreight.com`, we are looking for any instance that appears similar to the end of an email address on the website. One promising result came up with a contact page. When we look at the page (pictured below), we can see a large list of employees and contact info for them. This information can be helpful since we can determine that these people are at least most likely active and still working with the company.

#### E-mail Dork Results

Browsing the [contact page](https://www.inlanefreight.com/index.php/contact/), we can see several emails for staff in different offices around the globe. We now have an idea of their email naming convention (first.last) and where some people work in the organization. This could be handy in later password spraying attacks or if social engineering/phishing were part of our engagement scope.

![Contact information for Inlanefreight sales executives in the United States: Emma Williams, John Smith, and David Jones with their respective email addresses.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/ilfreightemails.png)

#### Username Harvesting

We can use a tool such as [linkedin2username](https://github.com/initstring/linkedin2username) to scrape data from a company's LinkedIn page and create various mashups of usernames (flast, first.last, f.last, etc.) that can be added to our list of potential password spraying targets.

#### Credential Hunting

[Dehashed](http://dehashed.com/) is an excellent tool for hunting for cleartext credentials and password hashes in breach data. We can search either on the site or using a script that performs queries via the API. Typically we will find many old passwords for users that do not work on externally-facing portals that use AD auth (or internal), but we may get lucky! This is another tool that can be useful for creating a user list for external or internal password spraying.

Note: For our purposes, the sample data below is fictional.

```shell
haphestus@htb[/htb]$ sudo python3 dehashed.py -q inlanefreight.local -p id : 5996447501 email : roger.grimes@inlanefreight.local username : rgrimes password : Ilovefishing! hashed_password :  name : Roger Grimes vin :  address :  phone :  database_name : ModBSolutions id : 7344467234 email : jane.yu@inlanefreight.local username : jyu password : Starlight1982_! hashed_password :  name : Jane Yu vin :  address :  phone :  database_name : MyFitnessPal
```

## Initial Enumeration of the Domain

### Tasks

Our tasks to accomplish for this section are:

- Enumerate the internal network, identifying hosts, critical services, and potential avenues for a foothold.
- This can include active and passive measures to identify users, hosts, and vulnerabilities we may be able to take advantage of to further our access.
- Document any findings we come across for later use. Extremely important!

#### Key Data Points

|**Data Point**|**Description**|
|---|---|
|`AD Users`|We are trying to enumerate valid user accounts we can target for password spraying.|
|`AD Joined Computers`|Key Computers include Domain Controllers, file servers, SQL servers, web servers, Exchange mail servers, database servers, etc.|
|`Key Services`|Kerberos, NetBIOS, LDAP, DNS|
|`Vulnerable Hosts and Services`|Anything that can be a quick win. ( a.k.a an easy host to exploit and gain a foothold)|

---

### TTPs

We will start with `passive` identification of any hosts in the network, followed by `active` validation of the results to find out more about each host (what services are running, names, potential vulnerabilities, etc.). Once we know what hosts exist, we can proceed with probing those hosts, looking for any interesting data we can glean from them. After we have accomplished these tasks, we should stop and regroup and look at what info we have. At this time, we'll hopefully have a set of credentials or a user account to target for a foothold onto a domain-joined host or have the ability to begin credentialed enumeration from our Linux attack host.

Let's look at a few tools and techniques to help us with this enumeration.

### Identifying Hosts

First, let's take some time to listen to the network and see what's going on. We can use `Wireshark` and `TCPDump` to "put our ear to the wire" and see what hosts and types of network traffic we can capture. This is particularly helpful if the assessment approach is "black box." We notice some [ARP](https://en.wikipedia.org/wiki/Address_Resolution_Protocol) requests and replies, [MDNS](https://en.wikipedia.org/wiki/Multicast_DNS), and other basic [layer two](https://www.juniper.net/documentation/us/en/software/junos/multicast-l2/topics/topic-map/layer-2-understanding.html) packets (since we are on a switched network, we are limited to the current broadcast domain) some of which we can see below. This is a great start that gives us a few bits of information about the customer's network setup.

#### Start Wireshark on ea-attack01

```bash
┌─[htb-student@ea-attack01]─[~] └──╼ $sudo -E wireshark 11:28:20.487     Main Warn QStandardPaths: runtime directory '/run/user/1001' is not owned by UID 0, but a directory permissions 0700 owned by UID 1001 GID 1002 <SNIP>
```

#### Wireshark Output

![Wireshark capture showing ARP requests from VMware sources to broadcast, querying IP addresses in the 172.16.5.x range.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/ea-wireshark.png)

- ARP packets make us aware of the hosts: 172.16.5.5, 172.16.5.25 172.16.5.50, 172.16.5.100, and 172.16.5.125.

  

![Wireshark window showing MDNS queries from source IP 172.16.5.125 to destination 224.0.0.251, protocol MDNS, querying 'AAAA ACADEMY-EA-WEB0.local'.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/ea-wireshark-mdns.png)

- MDNS makes us aware of the ACADEMY-EA-WEB01 host.

  
If we are on a host without a GUI (which is typical), we can use [tcpdump](https://linux.die.net/man/8/tcpdump), [net-creds](https://github.com/DanMcInerney/net-creds), and [NetMiner](https://www.netminer.com/en/product/netminer.php), etc., to perform the same functions. We can also use tcpdump to save a capture to a .pcap file, transfer it to another host, and open it in Wireshark.

#### Tcpdump Output

```bash
haphestus@htb[/htb]$ sudo tcpdump -i ens224
```

![GIF showcasing the traffic seen by tcpdump on the ens224 interface.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/tcpdump-example.png)

There is no one right way to listen and capture network traffic. There are plenty of tools that can process network data. Wireshark and tcpdump are just a few of the easiest to use and most widely known. Depending on the host you are on, you may already have a network monitoring tool built-in, such as `pktmon.exe`, which was added to all editions of Windows 10. As a note for testing, it's always a good idea to save the PCAP traffic you capture. You can review it again later to look for more hints, and it makes for great additional information to include while writing your reports.

Our first look at network traffic pointed us to a couple of hosts via `MDNS` and `ARP`. Now let's utilize a tool called `Responder` to analyze network traffic and determine if anything else in the domain pops up.

[Responder](https://github.com/lgandx/Responder-Windows) is a tool built to listen, analyze, and poison `LLMNR`, `NBT-NS`, and `MDNS` requests and responses. It has many more functions, but for now, all we are utilizing is the tool in its Analyze mode. This will passively listen to the network and not send any poisoned packets. We'll cover this tool more in-depth in later sections.

#### Starting Responder

```bash
sudo responder -I ens224 -A
```

#### Responder Results

![GIF showcasing and analyzing the traffic captured by responder on the ens224 interface.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/143/responder-example.gif)

As we start Responder with passive analysis mode enabled, we will see requests flow in our session. Notice below that we found a few unique hosts not previously mentioned in our Wireshark captures. It's worth noting these down as we are starting to build a nice target list of IPs and DNS hostnames.

Our passive checks have given us a few hosts to note down for a more in-depth enumeration. Now let's perform some active checks starting with a quick ICMP sweep of the subnet using `fping`.

[Fping](https://fping.org/) provides us with a similar capability as the standard ping application in that it utilizes ICMP requests and replies to reach out and interact with a host. Where fping shines is in its ability to issue ICMP packets against a list of multiple hosts at once and its scriptability. Also, it works in a round-robin fashion, querying hosts in a cyclical manner instead of waiting for multiple requests to a single host to return before moving on. These checks will help us determine if anything else is active on the internal network. ICMP is not a one-stop-shop, but it is an easy way to get an initial idea of what exists. Other open ports and active protocols may point to new hosts for later targeting. Let's see it in action.

#### FPing Active Checks

Here we'll start `fping` with a few flags: `a` to show targets that are alive, `s` to print stats at the end of the scan, `g` to generate a target list from the CIDR network, and `q` to not show per-target results.

```bash
haphestus@htb[/htb]$ fping -asgq 172.16.5.0/23 172.16.5.5 172.16.5.25 172.16.5.50 172.16.5.100 172.16.5.125 172.16.5.200 172.16.5.225 172.16.5.238 172.16.5.240      510 targets       9 alive     501 unreachable       0 unknown addresses     2004 timeouts (waiting for response)    2013 ICMP Echos sent       9 ICMP Echo Replies received    2004 other ICMP received  0.029 ms (min round trip time) 0.396 ms (avg round trip time) 0.799 ms (max round trip time)       15.366 sec (elapsed real time)
```

The command above validates which hosts are active in the `/23` network and does it quietly instead of spamming the terminal with results for each IP in the target list. We can combine the successful results and the information we gleaned from our passive checks into a list for a more detailed scan with Nmap. From the `fping` command, we can see 9 "live hosts," including our attack host.

#### Nmap Scanning

Now that we have a list of active hosts within our network, we can enumerate those hosts further. We are looking to determine what services each host is running, identify critical hosts such as `Domain Controllers` and `web servers`, and identify potentially vulnerable hosts to probe later. With our focus on AD, after doing a broad sweep, it would be wise of us to focus on standard protocols typically seen accompanying AD services, such as DNS, SMB, LDAP, and Kerberos name a few. Below is a quick example of a simple Nmap scan.

```bash
sudo nmap -v -A -iL hosts.txt -oN /home/htb-student/Documents/host-enum
```

#### NMAP Result Highlights

```shell
Nmap scan report for inlanefreight.local (172.16.5.5) Host is up (0.069s latency). Not shown: 987 closed tcp ports (conn-refused) PORT     STATE SERVICE       VERSION 53/tcp   open  domain        Simple DNS Plus 88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-04-04 15:12:06Z) 135/tcp  open  msrpc         Microsoft Windows RPC 139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn 389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name) |_ssl-date: 2022-04-04T15:12:53+00:00; -1s from scanner time. | ssl-cert: Subject: | Subject Alternative Name: DNS:ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL | Issuer: commonName=INLANEFREIGHT-CA | Public Key type: rsa | Public Key bits: 2048 | Signature Algorithm: sha256WithRSAEncryption | Not valid before: 2022-03-30T22:40:24 | Not valid after:  2023-03-30T22:40:24 | MD5:   3a09 d87a 9ccb 5498 2533 e339 ebe3 443f |_SHA-1: 9731 d8ec b219 4301 c231 793e f913 6868 d39f 7920 445/tcp  open  microsoft-ds? 464/tcp  open  kpasswd5? 593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0 636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name) <SNIP>   3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name) 3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: INLANEFREIGHT.LOCAL0., Site: Default-First-Site-Name) 3389/tcp open  ms-wbt-server Microsoft Terminal Services | rdp-ntlm-info: |   Target_Name: INLANEFREIGHT |   NetBIOS_Domain_Name: INLANEFREIGHT |   NetBIOS_Computer_Name: ACADEMY-EA-DC01 |   DNS_Domain_Name: INLANEFREIGHT.LOCAL |   DNS_Computer_Name: ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL |   DNS_Tree_Name: INLANEFREIGHT.LOCAL |   Product_Version: 10.0.17763 |_  System_Time: 2022-04-04T15:12:45+00:00 <SNIP> 5357/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP) |_http-title: Service Unavailable |_http-server-header: Microsoft-HTTPAPI/2.0 Service Info: Host: ACADEMY-EA-DC01; OS: Windows; CPE: cpe:/o:microsoft:windows
```

Our scans have provided us with the naming standard used by NetBIOS and DNS, we can see some hosts have RDP open, and they have pointed us in the direction of the primary `Domain Controller` for the INLANEFREIGHT.LOCAL domain (ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL). The results below show some interesting results surrounding a possibly outdated host (not in our current lab).

```shell
haphestus@htb[/htb]$ nmap -A 172.16.5.100 Starting Nmap 7.92 ( https://nmap.org ) at 2022-04-08 13:42 EDT Nmap scan report for 172.16.5.100 Host is up (0.071s latency). Not shown: 989 closed tcp ports (conn-refused) PORT      STATE SERVICE      VERSION 80/tcp    open  http         Microsoft IIS httpd 7.5 |_http-title: Site doesn't have a title (text/html). |_http-server-header: Microsoft-IIS/7.5 | http-methods:  |_  Potentially risky methods: TRACE 135/tcp   open  msrpc        Microsoft Windows RPC 139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn 443/tcp   open  https? 445/tcp   open  microsoft-ds Windows Server 2008 R2 Standard 7600 microsoft-ds 1433/tcp  open  ms-sql-s     Microsoft SQL Server 2008 R2 10.50.1600.00; RTM | ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback | Not valid before: 2022-04-08T17:38:25 |_Not valid after:  2052-04-08T17:38:25 |_ssl-date: 2022-04-08T17:43:53+00:00; 0s from scanner time. | ms-sql-ntlm-info:  |   Target_Name: INLANEFREIGHT |   NetBIOS_Domain_Name: INLANEFREIGHT |   NetBIOS_Computer_Name: ACADEMY-EA-CTX1 |   DNS_Domain_Name: INLANEFREIGHT.LOCAL |   DNS_Computer_Name: ACADEMY-EA-CTX1.INLANEFREIGHT.LOCAL |_  Product_Version: 6.1.7600 Host script results: | smb2-security-mode:  |   2.1:  |_    Message signing enabled but not required | ms-sql-info:  |   172.16.5.100:1433:  |     Version:  |       name: Microsoft SQL Server 2008 R2 RTM |       number: 10.50.1600.00 |       Product: Microsoft SQL Server 2008 R2 |       Service pack level: RTM |       Post-SP patches applied: false |_    TCP port: 1433 |_nbstat: NetBIOS name: ACADEMY-EA-CTX1, NetBIOS user: <unknown>, NetBIOS MAC: 00:50:56:b9:c7:1c (VMware) | smb-os-discovery:  |   OS: Windows Server 2008 R2 Standard 7600 (Windows Server 2008 R2 Standard 6.1) |   OS CPE: cpe:/o:microsoft:windows_server_2008::- |   Computer name: ACADEMY-EA-CTX1 |   NetBIOS computer name: ACADEMY-EA-CTX1\x00 |   Domain name: INLANEFREIGHT.LOCAL |   Forest name: INLANEFREIGHT.LOCAL |   FQDN: ACADEMY-EA-CTX1.INLANEFREIGHT.LOCAL |_  System time: 2022-04-08T10:43:48-07:00 <SNIP>
```

We can see from the output above that we have a potential host running an outdated operating system ( Windows 7, 8, or Server 2008 based on the output). This is of interest to us since it means there are legacy operating systems running in this AD environment. It also means there is potential for older exploits like EternalBlue, MS08-067, and others to work and provide us with a SYSTEM level shell. As weird as it sounds to have hosts running legacy software or end-of-life operating systems, it is still common in large enterprise environments. You will often have some process or equipment such as a production line or the HVAC built on the older OS and has been in place for a long time. Taking equipment like that offline is costly and can hurt an organization, so legacy hosts are often left in place. They will likely try to build a hard outer shell of Firewalls, IDS/IPS, and other monitoring and protection solutions around those systems. If you can find your way into one, it is a big deal and can be a quick and easy foothold. Before exploiting legacy systems, however, we should alert our client and get their approval in writing in case an attack results in system instability or brings a service or the host down. They may prefer that we just observe, report, and move on without actively exploiting the system.

The results of these scans will clue us into where we will start looking for potential domain enumeration avenues, not just host scanning. We need to find our way to a domain user account. Looking at our results, we found several servers that host domain services ( DC01, MX01, WS01, etc.). Now that we know what exists and what services are running, we can poll those servers and attempt to enumerate users. 

We need to be aware of what scans we run and how they work. Some of the Nmap scripted scans run active vulnerability checks against a host that could cause system instability or take it offline, causing issues for the customer or worse. For example, running a large discovery scan against a network with devices such as sensors or logic controllers could potentially overload them and disrupt the customer's industrial equipment causing a loss of product or capability. Take the time to understand the scans you use before running them in a customer's environment.

---

### Identifying Users

If our client does not provide us with a user to start testing with (which is often the case), we will need to find a way to establish a foothold in the domain by either obtaining clear text credentials or an NTLM password hash for a user, a SYSTEM shell on a domain-joined host, or a shell in the context of a domain user account. Obtaining a valid user with credentials is critical in the early stages of an internal penetration test. This access (even at the lowest level) opens up many opportunities to perform enumeration and even attacks. Let's look at one way we can start gathering a list of valid users in a domain to use later in our assessment.

#### Kerbrute - Internal AD Username Enumeration

[Kerbrute](https://github.com/ropnop/kerbrute) can be a stealthier option for domain account enumeration. It takes advantage of the fact that Kerberos pre-authentication failures often will not trigger logs or alerts. We will use Kerbrute in conjunction with the `jsmith.txt` or `jsmith2.txt` user lists from [Insidetrust](https://github.com/insidetrust/statistically-likely-usernames). This repository contains many different user lists that can be extremely useful when attempting to enumerate users when starting from an unauthenticated perspective. We can point Kerbrute at the DC we found earlier and feed it a wordlist. The tool is quick, and we will be provided with results letting us know if the accounts found are valid or not, which is a great starting point for launching attacks such as password spraying, which we will cover in-depth later in this module.

To get started with Kerbrute, we can download [precompiled binaries](https://github.com/ropnop/kerbrute/releases/latest) for the tool for testing from Linux, Windows, and Mac, or we can compile it ourselves. This is generally the best practice for any tool we introduce into a client environment. To compile the binaries to use on the system of our choosing, we first clone the repo:

#### Cloning Kerbrute GitHub Repo

```shell
haphestus@htb[/htb]$ sudo git clone https://github.com/ropnop/kerbrute.git Cloning into 'kerbrute'... remote: Enumerating objects: 845, done. remote: Counting objects: 100% (47/47), done. remote: Compressing objects: 100% (36/36), done. remote: Total 845 (delta 18), reused 28 (delta 10), pack-reused 798 Receiving objects: 100% (845/845), 419.70 KiB | 2.72 MiB/s, done. Resolving deltas: 100% (371/371), done.
```

Typing `make help` will show us the compiling options available.

#### Listing Compiling Options

```shell
haphestus@htb[/htb]$ make help help:            Show this help. windows:  Make Windows x86 and x64 Binaries linux:  Make Linux x86 and x64 Binaries mac:  Make Darwin (Mac) x86 and x64 Binaries clean:  Delete any binaries all:  Make Windows, Linux and Mac x86/x64 Binaries
```

We can choose to compile just one binary or type `make all` and compile one each for use on Linux, Windows, and Mac systems (an x86 and x64 version for each).

#### Compiling for Multiple Platforms and Architectures

```shell
haphestus@htb[/htb]$ sudo make all go: downloading github.com/spf13/cobra v1.1.1 go: downloading github.com/op/go-logging v0.0.0-20160315200505-970db520ece7 go: downloading github.com/ropnop/gokrb5/v8 v8.0.0-20201111231119-729746023c02 go: downloading github.com/spf13/pflag v1.0.5 go: downloading github.com/jcmturner/gofork v1.0.0 go: downloading github.com/hashicorp/go-uuid v1.0.2 go: downloading golang.org/x/crypto v0.0.0-20201016220609-9e8e0b390897 go: downloading github.com/jcmturner/rpc/v2 v2.0.2 go: downloading github.com/jcmturner/dnsutils/v2 v2.0.0 go: downloading github.com/jcmturner/aescts/v2 v2.0.0 go: downloading golang.org/x/net v0.0.0-20200114155413-6afb5195e5aa cd /tmp/kerbrute rm -f kerbrute kerbrute.exe kerbrute kerbrute.exe kerbrute.test kerbrute.test.exe kerbrute.test kerbrute.test.exe main main.exe rm -f /root/go/bin/kerbrute Done. Building for windows amd64.. <SNIP>
```

The newly created `dist` directory will contain our compiled binaries.

#### Listing the Compiled Binaries in dist

```shell
haphestus@htb[/htb]$ ls dist/ kerbrute_darwin_amd64  kerbrute_linux_386  kerbrute_linux_amd64  kerbrute_windows_386.exe  kerbrute_windows_amd64.exe
```

We can then test out the binary to make sure it works properly. We will be using the x64 version on the supplied Parrot Linux attack host in the target environment.

#### Testing the kerbrute_linux_amd64 Binary

```bash
haphestus@htb[/htb]$ ./kerbrute_linux_amd64      __             __               __   / /_____  _____/ /_  _______  __/ /____  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \ / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/ /_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                         Version: dev (9cfb81e) - 02/17/22 - Ronnie Flathers @ropnop This tool is designed to assist in quickly bruteforcing valid Active Directory accounts through Kerberos Pre-Authentication. It is designed to be used on an internal Windows domain with access to one of the Domain Controllers. Warning: failed Kerberos Pre-Auth counts as a failed login and WILL lock out accounts Usage:   kerbrute [command]     <SNIP>
```

We can add the tool to our PATH to make it easily accessible from anywhere on the host.

#### Adding the Tool to our Path

```bash
haphestus@htb[/htb]$ echo $PATH /home/htb-student/.local/bin:/snap/bin:/usr/sandbox/:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/usr/share/games:/usr/local/sbin:/usr/sbin:/sbin:/snap/bin:/usr/local/sbin:/usr/sbin:/sbin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/home/htb-student/.dotnet/tools
```

#### Moving the Binary

```shell
haphestus@htb[/htb]$ sudo mv kerbrute_linux_amd64 /usr/local/bin/kerbrute
```

We can now type `kerbrute` from any location on the system and will be able to access the tool. Feel free to follow along on your system and practice the above steps. Now let's run through an example of using the tool to gather an initial username list.

#### Enumerating Users with Kerbrute

```shell
haphestus@htb[/htb]$ kerbrute userenum -d INLANEFREIGHT.LOCAL --dc 172.16.5.5 jsmith.txt -o valid_ad_users 2021/11/17 23:01:46 >  Using KDC(s): 2021/11/17 23:01:46 >   172.16.5.5:88 2021/11/17 23:01:46 >  [+] VALID USERNAME:       jjones@INLANEFREIGHT.LOCAL 2021/11/17 23:01:46 >  [+] VALID USERNAME:       sbrown@INLANEFREIGHT.LOCAL 2021/11/17 23:01:46 >  [+] VALID USERNAME:       tjohnson@INLANEFREIGHT.LOCAL 2021/11/17 23:01:50 >  [+] VALID USERNAME:       evalentin@INLANEFREIGHT.LOCAL  <SNIP>  2021/11/17 23:01:51 >  [+] VALID USERNAME:       sgage@INLANEFREIGHT.LOCAL 2021/11/17 23:01:51 >  [+] VALID USERNAME:       jshay@INLANEFREIGHT.LOCAL 2021/11/17 23:01:51 >  [+] VALID USERNAME:       jhermann@INLANEFREIGHT.LOCAL 2021/11/17 23:01:51 >  [+] VALID USERNAME:       whouse@INLANEFREIGHT.LOCAL 2021/11/17 23:01:51 >  [+] VALID USERNAME:       emercer@INLANEFREIGHT.LOCAL 2021/11/17 23:01:52 >  [+] VALID USERNAME:       wshepherd@INLANEFREIGHT.LOCAL 2021/11/17 23:01:56 >  Done! Tested 48705 usernames (56 valid) in 9.940 seconds
```

We can see from our output that we validated 56 users in the INLANEFREIGHT.LOCAL domain and it took only a few seconds to do so. Now we can take these results and build a list for use in targeted password spraying attacks.



  

