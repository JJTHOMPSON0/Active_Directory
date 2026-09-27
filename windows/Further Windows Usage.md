# Microsoft Management Console (MMC)

---

The MMC can be used to group snap-ins, or administrative tools, to manage hardware, software, and network components within a Windows host. It has been around since Windows Server 2000 and runs on all Windows versions. We can also use MMC to create custom tools and distribute them to users. MMC works with the concept of snap-ins, allowing administrators to create a customized console with only the administrative tools needed to manage several services. These snap-ins can be added to manage both local and remote systems.

We can open MMC by just typing `mmc` in the Start menu. When we open MMC for the first time, it will be blank.

![Console window with no items displayed, showing Console Root and Actions pane.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/MMC.png)

From here, we can browse to File --> `Add or Remove Snap-ins`, and begin customizing our administrative console.

![Add or Remove Snap-ins window showing available snap-ins like ActiveX Control and selected snap-ins as Console Root.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/MMC_add_remove.png)

As we begin adding snap-ins, we will be asked if we want to add the snap-in to manage just the local computer or if it will be used to manage another computer on the network.

![Services snap-in selection window with options to manage local or another computer.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/MMC_services.png)

Once we have finished adding snap-ins, they will appear on the left-hand side of MMC. From here, we can save the set of snap-ins as a .msc file, so they will all be loaded the next time we open MMC. By default, they are saved in the Windows Administrative Tools directory under the Start menu. Next time we open MMC, we can choose to load any of the views that we have created.

![Open dialog showing Windows Administrative Tools folder with management.msc file.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/49/saved_msc.png)

# Windows Subsystem for Linux (WSL)

---

[WSL](https://docs.microsoft.com/en-us/windows/wsl/) is a feature that allows Linux binaries to be run natively on Windows 10 and Windows Server 2019. It was originally intended for developers who needed to run Bash, Ruby, and native Linux command-line tools such as `sed`, `awk`, `grep`, etc., directly on their Windows workstation. The second version of WSL, released in May 2019, introduced a real Linux kernel utilizing a subset of Hyper-V features.

WSL can be installed by running the PowerShell command `Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux` as an Administrator. Once this feature is enabled, we can either download a Linux distro from the Microsoft Store and install it or manually download the Linux distro of our choice and unpack and install it from the command line.

WSL installs an application called `Bash.exe`, which can be run by merely typing `bash` into a Windows console to spawn a Bash shell. We have the full look and feel of a Linux host from this shell, including the standard Linux directory structure.

```powershell
PS C:\htb> ls / bin dev home lib lLib64 media opt root sbin srv tmp var boot etc init 1lib32 Libx32 mnt proc run Snap sys usr
```

We can access the C$ volume and other volumes on the host operating system via the `mnt` directory, making the transition from the WSL host and the Windows host OS seamless. Once in this bash shell, we can interact with WSL as we would interact with any Linux-based operating system: running commands, installing updates/packages, etc.

```powershell
PS C:\htb> uname -a Linux WS01 4.4.0-18362-Microsoft #476-Microsoft Frit Nov 01 16:53:00 PST 2019 x86_64 x86 _64 x86_64 GNU/Linux
```