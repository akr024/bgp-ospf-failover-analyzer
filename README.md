A Python-based tool that monitors a multi-router network fabric running OSPF and BGP, detects link/route failures, measures reconvergence time, and can trigger automated remediation - built as a hands-on demonstration of routing protocol behavior and network automation. 

## Status 
Under active development (Day 1 of 17 — environment setup complete). 

## Project Goals 
- Build a realistic multi-router lab (OSPF inside a fabric, BGP to a simulated backbone) using Containerlab + FRRouting 
- Automate router state polling and change detection with Python 
- Measure and graph convergence time under simulated failures 
- Implement basic automated remediation 
- Produce a final report summarizing findings 

## Tech Stack 
- Containerlab + FRRouting (network emulation) 
- Python (automation, parsing, analysis) 
- Docker (container runtime underlying the lab)
