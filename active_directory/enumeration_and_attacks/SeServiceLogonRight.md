
if we see this enabled for an account, then that account can log on as a service account, we can just do, so to get the shell as that service privileged account we can just do:
```bash
Invoke-RunasCs -Username svc_sql -Password '<account_passwd' -LogonType 5 -BypassUAC -Command 'whoami /priv'
```

obviously  we would need `plain-text password` to achieve this, so if u dont know the plain-text, if u have a shell, just do `rubeus` and `get a TGT`, `request a user template certificate` to get .pfx files, then request `RC4 hash` of the account,then use `impacket-changepasswd` to `change the hash of the account to a known hash`, then u can validate teh change with nxc smb auth, and just use `RunasCs`  to get LOGON TYPE 5 session, and enjoy the privileges.