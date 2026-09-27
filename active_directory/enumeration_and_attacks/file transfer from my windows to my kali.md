# Method 1: Using Secure Copy Protocol (SCP)

This is the cleanest built-in CLI method if the SSH service is active on your Kali Linux machine. Windows 10 and 11 have a native OpenSSH client pre-installed.

- **Enable SSH on Kali** (if it is not already running):
    
    bash
    ```bash
    sudo systemctl start ssh
    ```

- **Find your Kali IP address** by running `ip a` or `ifconfig` in the Kali terminal. 
- **Execute the SCP command** in Windows PowerShell or Command Prompt:
  
    **`scp C:\path\to\your\file.txt kali_username@KALI_IP:/home/kali/DestinationFolder`**

