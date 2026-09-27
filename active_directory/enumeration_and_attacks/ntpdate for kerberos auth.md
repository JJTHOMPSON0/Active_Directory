If running sudo ntpdate `ip` says no eleigible servers anytime then do this:
 change your krb5.conf file to:
 ```bash
 sudo tee /etc/krb5.conf << 'EOF'
[libdefaults]
    default_realm = SIGNED.HTB
    dns_lookup_realm = false
    dns_lookup_kdc = false
    rdns = false
[realms]
    SIGNED.HTB = {
        kdc = DC01.SIGNED.HTB
        admin_server = DC01.SIGNED.HTB
    }

[domain_realm]
    .signed.htb = SIGNED.HTB
    signed.htb = SIGNED.HTB
EOF
 ```
 
and when ew wanna use a differnt  DNS server to act as a gateway tehn do this:
```bash
sudo tee /etc/resolv.conf << 'EOF'
nameserver DCO1.SIGNED.HTB
search ip
```

and if u wanna know the date skew of KDC then do this 
```bash
sudo nmap -sV -p1433(ex) --script ssl-date ip
```

and then do this :
```bash
sudo date -u -s "2026-xx-xx 06:xx:xx"
```
