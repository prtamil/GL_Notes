# Understanding K8s Networking series - Depth [https://www.youtube.com/watch?v=B6FsWNUnRo0&t=53s]

## Policy vs Mechanism

Kubernetes [Service,Ingress,Egress,CNI] => Policy
iptables,NAT,TunTap, Virtual Networks => Mechanism

## Layers

5 -> App ->Messages -> N/A
4 -> Transport -> Segment -> Port
3 -> Network -> DataGram -> IP Address
2 -> Link -> Frames -> MAC Addr
1 -> Physical -> Bits -> N/A

Devices

NetAdapter/Interface -> Layer 2
Switch (MAC Bridge) -> Layer 2
Router/Default Gateway -> Layer 3

Home Network

Interner = firewall = nat = router = switch ->pc

pc -> Virtual Switch -> virtual adapter,

## Network Namespaces and Virtual Ethernet (veth) Interface.

NetNamespaces isolates

1. Network devices
2. v4 and v6 protocol stacks
3. ip routing tables.
4. Firewall Rules.
5. PortNumbers (sockets)
6. veth devices

Veth devices

1. What goes in one end will come out the other.
2. virtual patch cable.

example:

Ubuntu1 VM
Network namespace 1

1. veth11 172.16.0.2
2. veth10
3. Br0 [172.16.0.1] [Virtual bridge]
4. eth0 [192.168.0.10] [Actual NIC Inteface]

Connection between 2 vm -> Switch/Tunnel.

This video has server1.sh file to create namespace/bride download and use it.
(https://github.com/gary-RR/myYouTube_video_container_networking)

## Overlay Networks

1. Overlay network is a virtual network which is routed on top of underlay network infrastructure, Routing decision would take place with help of software.
2. Some overlay network provider operate on Layer 2 (flannel uses VXLAN to encapsulate layer2 ethernet inside a UDP Packet)
3. Some overlay network provider in Layer 3 (Calico uses IP in IP proptocol)

Tunnel:

1. Useful virtual interface meant for routing
2. Routed tunnels.

TAP -> Layer 2
TUN -> Layer 3

TAP = NIC -> virtual bridge -> tap interface (create virtual tap iface) -> Get packet in userspace -> Do what u want
