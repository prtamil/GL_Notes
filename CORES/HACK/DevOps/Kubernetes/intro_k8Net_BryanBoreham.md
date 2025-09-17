# Intro to kubernetes Netowking Bryan Boreham[https://www.youtube.com/watch?v=7OFw3lgSb1Q]

IP to IP redirecting = NAT plays important role in k8s networking [iptables are important]

All things availble in kernel flannel, weave are making it easy.

Nodeport accepts outcoming and can redirect to any node any pod.
it should be nodesport.

Loadbalancer -> uses -> Nodeport for communicating.

Ingress is L7 [Applayer http]
Loadbalancer L4 [Transport]

k8s provide abstractions its declarative.
Inside happenings are highly hidden
it has linux internals and uses nat,iptables,virtual networking, user defined networking [flannel,weave] and cni plugins.
