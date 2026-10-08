With administrative access to a Windows system, we can attempt to quickly dump the files associated with the SAM database, transfer them to our attack host, and begin cracking the hashes offline.

## Registry hives
There are three registry hives we can copy if we have local administrative access to a target system, each serving a specific purpose when it comes to dumping and cracking password hashes. A brief description of each is provided in the table below:

| Registry Hive   | Description                                                                                                                                                       |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `HKLM\SAM`      | Contains password hashes for local user accounts. These hashes can be extracted and cracked to reveal plaintext passwords.                                        |
| `HKLM\SYSTEM`   | Stores the system boot key, which is used to encrypt the SAM database. This key is required to decrypt the hashes.                                                |
| `HKLM\SECURITY` | Contains sensitive information used by the Local Security Authority (LSA), including cached domain credentials (DCC2), cleartext passwords, DPAPI keys, and more. |

If we're only interested in dumping the hashes of local users, we need only `HKLM\SAM` and `HKLM\SYSTEM`. However, it's often useful to save `HKLM\SECURITY` as well, since it can contain cached domain user credentials on domain-joined systems, along with other valuable data.

## Transfering files via smb server to the attack host
#### Creating a share with smbserver

To create the share, we simply run `smbserver.py -smb2support`, specify a name for the share (e.g., `CompData`), and point to the local directory on our attack host where the hive copies will be stored (e.g., `/home/ltnbob/Documents`). The `-smb2support` flag ensures compatibility with newer versions of SMB. If we do not include this flag, newer Windows systems may fail to connect to the share, as SMBv1 is disabled by default due to [numerous severe vulnerabilities](https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=smbv1) and publicly available exploits.

![](../../ZMEDIA/Pasted%20image%2020261008214556.png)

Once the share is running on our attack host, we can use the `move` command on the Windows target to transfer the hive copies to the share.

#### Moving hive copies to share

![](../../ZMEDIA/Pasted%20image%2020261008214619.png)

We can then confirm that our hive copies were successfully moved to the share by navigating to the shared directory on our attack host and using `ls` to list the files.

```       shellsession
hyehaph@htb[/htb]$ ls 
sam.save  security.save  system.save
```

## Dumping hashes with secretsdump

One particularly useful tool for dumping hashes offline is Impacket's `secretsdump`. 

![](../../ZMEDIA/Pasted%20image%2020261008214810.png)

Here we see that `secretsdump` successfully dumped the `local` SAM hashes, along with data from `hklm\security`, including cached domain logon information and LSA secrets such as the machine and user keys for DPAPI.

Notice that the first step `secretsdump` performs is retrieving the `system bootkey` before proceeding to dump the `local SAM hashes`. This is necessary because the bootkey is used to encrypt and decrypt the SAM database. Without it, the hashes cannot be decrypted — which is why having copies of the relevant registry hives, as discussed earlier, is crucial.
