
Enum-ing users and saving into a file:
```bash
nxc smb dc01.x.x \
    -u '' -p '' \
    --users-export users.txt
```

To brute force `rid`:
```bash
nxc smb 10.129.1x.x -u '' -p '' --rid-brute
```

or u can use **`ldap instead of smb auth`**.
