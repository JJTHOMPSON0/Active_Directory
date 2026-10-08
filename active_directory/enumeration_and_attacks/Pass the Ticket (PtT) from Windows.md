## Pass the Ticket (PtT) attack

We need a valid Kerberos ticket to perform a `Pass the Ticket (PtT)` attack. It can be:

- Service Ticket (TGS) to allow access to a particular resource.
- Ticket Granting Ticket (TGT), which we use to request service tickets to access any resource the user has privileges.

Before we perform a `Pass the Ticket (PtT)` attack, let's see some methods to get a ticket using `Mimikatz` and `Rubeus`.

## Harvesting Kerberos tickets from Windows

On Windows, tickets are processed and stored by the LSASS (Local Security Authority Subsystem Service) process. Therefore, to get a ticket from a Windows system, you must communicate with LSASS and request it. As a non-administrative user, you can only get your tickets, but as a local administrator, you can collect everything.

We can harvest all tickets from a system using the `Mimikatz` module `sekurlsa::tickets /export`. The result is a list of files with the extension `.kirbi`, which contain the tickets.

#### Mimikatz - Export tickets

![](../../ZMEDIA/Pasted%20image%2020261008223740.png)
The tickets that end with `$` correspond to the computer account, which needs a ticket to interact with the Active Directory. User tickets have the user's name, followed by an `@` that separates the service name and the domain, for example: `[randomvalue]-username@service-domain.local.kirbi`.

**Note:** If you pick a ticket with the service krbtgt, it corresponds to the TGT of that account.

We can also export tickets using `Rubeus` and the option `dump`. This option can be used to dump all tickets (if running as a local administrator). `Rubeus dump`, instead of giving us a file, will print the ticket encoded in Base64 format. We are adding the option `/nowrap` for easier copy-paste.


#### Rubeus - Export tickets

![](../../ZMEDIA/Pasted%20image%2020261008223821.png)
**Note:** To collect all tickets we need to execute Mimikatz or Rubeus as an administrator.

This is a common way to retrieve tickets from a computer. Another advantage of abusing Kerberos tickets is the ability to forge our own tickets. Let's see how we can do this using the `Pass the Key` aka. `OverPass the Hash` technique.

## Pass the Key aka. OverPass the Hash

The traditional `Pass the Hash` (`PtH`) technique involves reusing an NTLM password hash that doesn't touch Kerberos. The `Pass the Key` aka. `OverPass the Hash` approach converts a hash/key (rc4_hmac, aes256_cts_hmac_sha1, etc.) for a domain-joined user into a full `Ticket Granting Ticket` (`TGT`). This technique was developed by Benjamin Delpy and Skip Duckwall in their presentation [Abusing Microsoft Kerberos - Sorry you guys don't get it](https://www.slideshare.net/gentilkiwi/abusing-microsoft-kerberos-sorry-you-guys-dont-get-it/18). Also [Will Schroeder](https://twitter.com/harmj0y) adapted their project to create the [Rubeus](https://github.com/GhostPack/Rubeus) tool.

To forge our tickets, we need to have the user's hash; we can use Mimikatz to dump all users Kerberos encryption keys using the module `sekurlsa::ekeys`. This module will enumerate all key types present for the Kerberos package.

#### Mimikatz - Extract Kerberos keys

 ![](../../ZMEDIA/Pasted%20image%2020261008223853.png)
Now that we have access to the `AES256_HMAC` and `RC4_HMAC` keys, we can perform the OverPass the Hash aka. Pass the Key attack using `Mimikatz` and `Rubeus`.

#### Mimikatz - Pass the Key aka. OverPass the Hash

![](../../ZMEDIA/Pasted%20image%2020261008223912.png)
This will create a new `cmd.exe` window that we can use to request access to any service we want in the context of the target user.

To forge a ticket using `Rubeus`, we can use the module `asktgt` with the username, domain, and hash which can be `/rc4`, `/aes128`, `/aes256`, or `/des`. In the following example, we use the AES-256 hash from the information we collect using Mimikatz `sekurlsa::ekeys`.

#### Rubeus - Pass the Key aka. OverPass the Hash

 ![](../../ZMEDIA/Pasted%20image%2020261008223938.png)

**Note:** Mimikatz requires administrative rights to perform the Pass the Key/OverPass the Hash attacks, while Rubeus doesn't.

To learn more about the difference between Mimikatz `sekurlsa::pth` and Rubeus `asktgt`, consult the Rubeus tool documentation [Example for OverPass the Hash](https://github.com/GhostPack/Rubeus#example-over-pass-the-hash).

## Pass the Ticket (PtT)

Now that we have some Kerberos tickets, we can use them to move laterally within an environment.

With `Rubeus` we performed an OverPass the Hash attack and retrieved the ticket in Base64 format. Instead, we could use the flag `/ptt` to submit the ticket (TGT or TGS) to the current logon session.

#### Rubeus - Pass the Ticket

![](../../ZMEDIA/Pasted%20image%2020261008224041.png)
Note that now it displays `Ticket successfully imported!`.

Another way is to import the ticket into the current session using the `.kirbi` file from the disk.

Let's use a ticket exported from Mimikatz and import it using Pass the Ticket.

#### Rubeus - Pass the Ticket

![](../../ZMEDIA/Pasted%20image%2020261008224112.png)

We can also use the Base64 output from Rubeus or convert a .kirbi to Base64 to perform the Pass the Ticket attack. We can use PowerShell to convert a .kirbi to Base64.

#### Convert .kirbi to Base64 Format

![](../../ZMEDIA/Pasted%20image%2020261008224141.png)

Using Rubeus, we can perform a Pass the Ticket providing the Base64 string instead of the file name.

#### Pass the Ticket - Base64 Format

![](../../ZMEDIA/Pasted%20image%2020261008224155.png)

Finally, we can also perform the Pass the Ticket attack using the Mimikatz module `kerberos::ptt` and the .kirbi file that contains the ticket we want to import.

#### Mimikatz - Pass the Ticket

![](../../ZMEDIA/Pasted%20image%2020261008224217.png)

**Note:** Instead of opening mimikatz.exe with cmd.exe and exiting to get the ticket into the current command prompt, we can use the Mimikatz module `misc` to launch a new command prompt window with the imported ticket using the `misc::cmd` command.

## Pass The Ticket with PowerShell Remoting (Windows)

[PowerShell Remoting](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/running-remote-commands?view=powershell-7.2) allows us to run scripts or commands on a remote computer. Administrators often use PowerShell Remoting to manage remote computers on the network. Enabling PowerShell Remoting creates both HTTP and HTTPS listeners. The listener runs on standard port TCP/5985 for HTTP and TCP/5986 for HTTPS.

To create a PowerShell Remoting session on a remote computer, you must have administrative permissions, be a member of the Remote Management Users group, or have explicit PowerShell Remoting permissions in your session configuration.

Suppose we find a user account that doesn't have administrative privileges on a remote computer but is a member of the Remote Management Users group. In that case, we can use PowerShell Remoting to connect to that computer and execute commands.

## Mimikatz - PowerShell Remoting with Pass the Ticket

To use PowerShell Remoting with Pass the Ticket, we can use Mimikatz to import our ticket and then open a PowerShell console and connect to the target machine. Let's open a new `cmd.exe` and execute `mimikatz.exe`, then import the ticket we collected using `kerberos::ptt`. Once the ticket is imported into our `cmd.exe` session, we can launch a PowerShell command prompt from the same `cmd.exe` and use the command `Enter-PSSession` to connect to the target machine.

#### Mimikatz - Pass the Ticket for lateral movement.

![](../../ZMEDIA/Pasted%20image%2020261008224332.png)
## Rubeus - PowerShell Remoting with Pass the Ticket

Rubeus has the option `createnetonly`, which creates a sacrificial process/logon session ([Logon type 9](https://eventlogxp.com/blog/logon-type-what-does-it-mean/)). The process is hidden by default, but we can specify the flag `/show` to display the process, and the result is the equivalent of `runas /netonly`. This prevents the erasure of existing TGTs for the current logon session.

#### Create a sacrificial process with Rubeus

![](../../ZMEDIA/Pasted%20image%2020261008224428.png)

The above command will open a new cmd window. From that window, we can execute Rubeus to request a new TGT with the option `/ptt` to import the ticket into our current session and connect to the DC using PowerShell Remoting.

#### Rubeus - Pass the Ticket for lateral movement

![](../../ZMEDIA/Pasted%20image%2020261008224452.png)