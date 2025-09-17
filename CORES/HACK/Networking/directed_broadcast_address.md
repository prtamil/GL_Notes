What is Directed Broadcast Address ?
-----------------------------------
    - Host sends data to all devices on a specific network.
    - Host part has all '1's .
    - for ex: 172.16.255.255 is broadcast address for 172.16.x.x network
    - Routers can route directed broadcast address.
    - bydefault routers disable direct broadcast address by default.
    - inorder to stop DOS (Denial of Service Attack) it is disabled.
    - hacking tools like smurf will use broadcast address for DOS

Is Directed Broadcast Address is enabled by default ?
---------------------------------------------------
No it is Disabled by default in Cisco Router and Switches

How does one do DOS attack using Broadcast Address ?
--------------------------------------------------
1. Attacker Log into a machine where he wants to dos.
2. From that machine he sends packets to Broadcase address
3. for example: 192.1.0.3 ip he sends packets to 192.1.0.255.
4. So all Computers in this network send packet to source address
5. Which causes Denial Of Service Attack to the host
