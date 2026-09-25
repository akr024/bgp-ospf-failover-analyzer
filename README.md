# BGP/OSPF Convergence & Failover Analyzer
A Python-based tool for a multi-router topology (Containerlab + FRRouting) with OSPF inside the topology mimicing a data center fabric and BGP peering out to a simulated backbone to provide redundant paths. The tool polls routing state (via SSH/vtysh parsing), detects route flaps and path changes, simulates link failures, measures convergence time, and triggers automated remediation (backup static route injection, re-announcement, alerting).

## Project Features 
- A realistic multi-router lab (OSPF inside a fabric, BGP to a simulated backbone) using Containerlab + FRRouting 
- Automate router state polling and change detection with Python 
- Measure and graph convergence time under simulated failures 
- Implement automated remediation 

## Tech Stack 
- Containerlab + FRRouting (network emulation) 
- Python (automation, parsing, analysis) 
- Docker (container runtime underlying the lab)
