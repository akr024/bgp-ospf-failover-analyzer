# Topology Design

## Overview
The topology is a DC fabric with a backbone attached to it acting as the edge routers towards the internet. The intention of the topology is to mimic a small-scale data center network which has two leaf routers, two spine routers and two backbone routers. Following Spine-Leaf datacenter architecture, the two leaf routers are connected to both spine routers and each of the spine routers is connected to a backbone router. This provides redundancy in the connection to the backbone while also providing redundancy to the leaf routers and allowing for equal-cost multi-path (ECMP) routing. The DC fabric (2 leaf routers + 2 spine routers) runs OSPF as the routing protocol, while eBGP is used to connect the DC fabric with the backbone and the backbone internally runs iBGP to connect the two edge routers such that information about external networks can be shared amongst them. Using a routing protocol between these two edge routers in the backbone is not necessary as they’re directly connected to each other.

## Why a single OSPF area
A single OSPF area is utilised because the topology consists of 6 routers in total (2 leaf nodes, 2 spine nodes and 2 backbone nodes). Having multiple OSPF areas configured in such a small-scale topology would be over-engineering because multiple OSPF areas are beneficial when there is a large scale topology, as OSPF relies on maintaining a global LSDB on each router; thus having a single area for hundreds or thousands of routers would make the protocol largely inefficient and also increase the convergence time. This is why a larger topology is divided into multiple OSPF areas. However, as mentioned, this project is focused on a small topology consisting of 6 routers and hence a single OSPF area suffices.

## Addressing plan

| Link                  | Subnet        | Purpose |
|-----------------------|---------------|---------|
| leaf1 – spine1        | `10.0.13.0/30` | OSPF    |
| leaf1 – spine2        | `10.0.14.0/30` | OSPF    |
| leaf2 – spine1        | `10.0.23.0/30` | OSPF    |
| leaf2 – spine2        | `10.0.24.0/30` | OSPF    |
| spine1 – backbone1    | `10.0.35.0/30` | eBGP    |
| spine2 – backbone2    | `10.0.46.0/30` | eBGP    |
| backbone1 – backbone2 | `10.0.56.0/30` | iBGP    |

| Router    | Loopback        | Notes                                      |
|-----------|-----------------|--------------------------------------------|
| leaf1     | `10.255.0.1/32` | + simulated service subnet `192.168.1.0/24` |
| leaf2     | `10.255.0.2/32` | + simulated service subnet `192.168.2.0/24` |
| spine1    | `10.255.0.3/32` |                                            |
| spine2    | `10.255.0.4/32` |                                            |
| backbone1 | `10.255.0.5/32` |                                            |
| backbone2 | `10.255.0.6/32` |                                            |

## Future considerations
A future consideration to extend this project could include enabling multi-area OSPF as the topology gets larger and intends to cover a realistic data center network consisting of hundreds of routers. Another consideration can be to utilise eBGP as the internal routing protocol between all nodes as it scales much better in a larger environment, according to RFC 7938. Lastly, the backbone can be extended by adding more than 2 backbone nodes which allows for greater redundancy and a more realistic backbone network showcasing the benefits of using eBGP as an internal routing protocol over a standard routing protocol such as OSPF.

