# -sn

The **`-sn`** flag in Nmap stands for ==**"Ping Scan"**== (formerly known as `-sP`). Its primary purpose is to perform **host discovery** to determine which machines on a network are active, **without scanning any of their ports**. 

example:
scanning a whole subnet:
```bash
nmap -sn 192.168.1.0/24
```

`working`:
When you run a scan with `-sn`, Nmap sends a series of probe packets to the target network. If a host responds, Nmap marks it as **online**. It then immediately stops and moves to the next host rather than continuing to check for open TCP or UDP ports.

# -Pn

The **`-Pn`** flag in Nmap tells the tool to ==**skip the host discovery phase** and treat all target IP addresses as online==.

By default, Nmap pings a target first; if the target does not respond, Nmap assumes it is offline and skips port scanning. The `-Pn` flag forces Nmap to attempt a full port scan on every specified IP, whether it responds to a ping or not.

Why Use `-Pn`?

Many modern firewalls and operating systems (like Windows with its default firewall settings) block ICMP (ping) traffic and dropped uninvited packets. 

- **Without `-Pn`:** Nmap pings the target, gets no response, assumes the host is dead, and stops. You miss open ports on an active machine.
- **With `-Pn`:** Nmap ignores the lack of ping response and scans the ports anyway, successfully finding services hidden behind the firewall.

# Scanning a Host for all open ports there can be

```bash
nmap -p- --min-rate=2000 -T4 10.129.1x.xx -oG allports.txt
```


# Then scanning those ports

```bash
ports=$(grep -oP '\d+/open' allports.txt | cut -d'/' -f1 | tr '\n' ',' | sed 's/,$//')
nmap -p$ports -sC -sV 10.129.1x.xx -oA xx_full
```


# --min-rate(Speed Floor)

This flag tells Nmap to send packets at a **minimum rate of 2,000 packets per second**.

- **How it works:** Nmap usually starts scanning slowly and speeds up if the network seems stable. This flag forces Nmap to never drop below 2,000 packets per second, no matter what.
- **Why use it:** It dramatically cuts down scan times, allowing you to scan thousands of ports or entire subnets in seconds or minutes.
- **The Risk:** It completely overrides Nmap's congestion control. If the network or target cannot handle 2,000 packets per second, packets will drop, and you will get **inaccurate results** (missing open ports).

---


# -T4(Timing Templates)

This flag sets Nmap's overall timing policy to **Aggressive** on a scale from `-T0` (paranoid/slowest) to `-T5` (insane/fastest).

- **How it works:** `-T4` shortens the amount of time Nmap waits for a response (timeouts) and increases the number of ports it scans at the same time (parallelism). It assumes you are on a fast, reliable network (like a modern LAN or fast broadband).

- **Why use it:** It optimizes settings to make the scan run significantly faster than the default (`-T3`) without being so aggressive (`-T5`) that it breaks everything.


---

# Scanning a single port:

```bash
nmap -sSVC -p 1433 --open 10.129.2x.xx -Pn -oG <file_name>
```

---

# --open



The **`--open`** flag ==tells Nmap to **only show hosts that have at least one open port**, and to **only list the open ports** on those hosts==.

By default, Nmap clutter-scans your terminal by showing ports that are `filtered` (blocked by a firewall) or `closed`. When scanning large networks or all 65,535 ports, this default behavior can create thousands of lines of useless text. 

What it Filters Out

- **`closed` ports:** The port is accessible but no service is listening.
- **`filtered` ports:** Nmap cannot determine if the port is open because a firewall is dropping the packets.
- **`closed|filtered` ports:** Nmap cannot distinguish between the two states. 


# Nmap 2.0

```bash
ports=$(nmap -p- --min-rate=1000 -T4 10.129.2x.xx | grep ^[0-9] | cut -d '/' -f 1 | tr '\n' ',' | sed s/,$//)
```

```bash
nmap -p$ports -sCV 10.129.2x.xx -oA xx_nmap
```