In the context of **Active Directory (AD)**, **UAC** stands for ==**UserAccountControl**, a core attribute attached to user and computer objects that stores numerical flag values to define account properties and security settings==

What is the `UserAccountControl` Attribute?

The `UserAccountControl` attribute is a bitmask field in Active Directory. It uses specific numerical values to track account behaviors—such as whether an account is disabled, whether passwords can expire, or what type of object it is (normal user, computer, or domain controller). 

- **Cumulative Values:** The numbers add up. If an account has multiple properties enabled, AD combines their decimal values into a single number.
- **Default User Account:** A standard, active user account typically starts with a value of **512** (`NORMAL_ACCOUNT`).
- **Disabled Account:** If you disable that standard account, AD adds `2` (`ACCOUNTDISABLE`), changing the total value to **514** (`512 + 2`).

`To check UAC attributes:`
```powershell
Get-ADUser -Identity "jdoe" -Properties UserAccountControl
```

```powershell
DistinguishedName  : CN=John Doe,OU=Users,DC=company,DC=local
Enabled            : True
GivenName          : John
Name               : John Doe
ObjectClass        : user
ObjectGUID         : 1234abcd-56ef-78gh-90ij-1234567890kl
SamAccountName     : jdoe
Surname            : Doe
UserAccountControl : 66048 <--- RIGHT HERE (Normal Account + Password Never Expires)
```


---

# UAC bypass via the System Configuration utility (msconfig.exe)

The System Configuration utility (`msconfig.exe`) is a trusted Windows binary. By default, Windows allows it to automatically run with high administrative privileges **without triggering a User Account Control (UAC) prompt**, even if the user is a standard administrator in a split-token environment.

Its success depends entirely on the Windows environment and configuration settings:

- **UAC Settings Level:** This method only works if UAC is set to its **default setting** ("Notify me only when apps try to make changes to my computer").
- **"Always Notify" Prevents It:** If a system administrator has set UAC to the highest security setting (**Always Notify**), Windows will force a UAC prompt the moment the user tries to open System Configuration (`msconfig.exe`), breaking the chain immediately.
- **Modern Windows Mitigations:** In newer versions of Windows 10 and Windows 11, Microsoft has hardened many built-in utilities. In heavily patched environments, launching child processes from certain auto-elevated administrative panels will drop the privileges of the child process (`cmd.exe`) back down to medium integrity, rendering the bypass ineffective.
- **Account Type Matters:** The user running this must already belong to the **local Administrators group**. If a completely restricted standard user accounts runs this, they will be prompted for administrator credentials immediately upon opening `msconfig.exe`.


**`how to bypass:`**  

Just open msconfig.exe and go to tolls , select command prompt, and click on launch, u would have the elevated cmd, enjoy.
