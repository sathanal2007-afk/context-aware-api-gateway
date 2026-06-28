# context-aware-api-gateway
# Context-Aware API Gateway & Mitigation Engine

A high-performance, security-focused API Gateway built with Python and FastAPI. This project solves critical blind spots in traditional rate limiters by evaluating the physical and behavioral context of incoming requests rather than relying solely on static IP tracking.

## 🚨 The Core Problem (Drawbacks Solved)
1. **Distributed IP Botnets:** Traditional rate limiters only track requests per IP. Attackers rotate thousands of residential IPs to perform Brute-Force attacks or scraping without hitting single-IP threshold blocks.
2. **Context Blindness:** Standard validation frameworks allow requests as long as credentials match, ignoring impossible physical displacements of user sessions.

## 🛠️ Advanced Security Implementations
Our system acts as an **Adaptive Firewall Layer** by running two unified security pipelines:

* **Impossible Travel Detection (Geospatial Velocity Check):** Tracks consecutive user actions. Calculates real-time displacement speed using geospatial coordinate telemetry (`geopy.distance.geodesic`). If a session registers an impossible speed transition ($>900\text{ km/h}$ - Commercial Flight limit), the gateway immediately tags the profile state as compromised and freezes access.
* **Dynamic Sliding-Window Throttling (Rate Limiter):** Limits maximum transaction requests to a constraint of **5 Requests Per Minute (RPM)**. Automatically cleanses stale metrics from cache memory inline.

## 🏗️ Core Architecture & Flow
