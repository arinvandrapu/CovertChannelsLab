# Covert Channels 

# Overview
This project demonstrates the design, implementation, and analysis of covert communication channels capable of exfiltrating data while evading Data Loss Prevention (DLP) conrtrols. Two covert channels were implemented: a Timing Channel and a Storage Channel. The project evaluates throughput, reliability, detectability, and security trade-offs using real-world network measurements and statistical analysis. 

# Objectives
- **Implement covert timing and storage channels**
- **Measure channel throughput and accuracy**
- **Perform statistical analysis (SNR, T-test, Chi-square, entropy)**
- **Evaluate detectability vs. reliability tradeoffs**
- **Analyze feasibility of covert channels in real networks**

# Environment
- **OS: Kali Linux**
- **Languages: Python**
- **Libraries: Scapy, Pandas, NumPy, Matplotlib**
- **Tools: Wireshark, Jupyter Notebook**

# Threat Model
The simulated network enforced strict DLP controls:
- No SSH/RDP access
- All HTTP payloads inspected
- Data exfiltration blocked at application layer

# Skills & Knowledge Gained

**Systems and Network Security:**
- Designed and implemented covert timing and storage channels
- Understood real-world data exfiltration techniques
- Analyzed network traffic using Wireshark
- Identified covert channel detection signatures
- Evaluated attack vs. defense tradeoffs

**Networking & Protocols:**
- Manipulated IPv4 header fields for covert storage
- Measured packet inter-arrival timing behavior
- Understood effects of network jitter and scheduling noise
- Explored real-world limitations of covert channels

**Data Analysis and Experimentation:**
- Designed controlled timing experiments
- Collected and analyzed real timing data
- Used Jupyter Notebook for statistical analysis
- Interpreted distributions, noise, and detection metrics
- Compared reliability vs stealth performance

# The Experiment
Assumption: The attacker has code execution on an internal machine, but cannot send visible data externally.

Goal: Hide the message inside network metadata not inspected by DLP/

Message exfiltrated: "Help! I need somebody. Help! Not just anybody."

# Covert Channel Designs
The Timing Channel encodes bits using packet delay differences: 
- bit 0 -> short delay
- bit 1 -> long delay

The receiver decodes bits by comparing observed inter-arrival time against a threshold. 

The Storage Channel encodes data in the IPv4 Identification field of packets. Each packet embeds a byte of hidden data without modifying payload content.

# Experiments
**Baseline Validation**

Baseline Timing Channel:

<img width="475" height="318" alt="image" src="https://github.com/user-attachments/assets/b20d7969-7f5e-4b08-88d9-c3b59fb47746" />

Baseline Storage Channel:

<img width="475" height="311" alt="image" src="https://github.com/user-attachments/assets/b8e6f2ee-2a34-4c19-a08f-19f99308b29b" />


Both channels successfully transmitted the hidden message across the loopback network.
- Timing Channel Throughput: ~6–8 bits/sec
- Storage Channel: Near-instant transmission

Wireshark confirmed:
- Timing channel shows bimodal packet spacing
- Storage channel modifies IPv4 Identification field

# Timing Optimization Study
Ten timing configurations were tested (3 trials each) o maximize throughput while preserving accuracy.

**Configurations Used:**

| Bit0_delay | Bit1_delay | Threshold | Trials | Successes | BPS (Bits/Second) | Notes |
|-----------|-----------|-----------|--------|-----------|-------------------|-------|
| 0.10 | 0.15 | 0.125 | 3 | 3 | 7.9 | Works |
| 0.08 | 0.12 | 0.10 | 3 | 3 | 9.8 | Works |
| 0.06 | 0.10 | 0.08 | 3 | 3 | 12.2 | Works |
| 0.05 | 0.08 | 0.065 | 3 | 3 | 14.8 | Works |
| 0.04 | 0.07 | 0.055 | 3 | 3 | 17.2667 | Works, 1 trial had a different BPS |
| 0.03 | 0.06 | 0.045 | 3 | 3 | 21.9333 | Works, 1 trial had a different BPS |
| 0.025 | 0.05 | 0.0375 | 3 | 3 | 24.5333 | Works, 1 trial had a different BPS |
| 0.08 | 0.09 | 0.085 | 3 | 1 | 11.2667 | 2 Errors |
| 0.04 | 0.045 | 0.0425 | 3 | 0 | 21.4333 | 3 Errors |
| 0.01 | 0.02 | 0.015 | 3 | 2 | 55.0667 | 1 Error |


# Statistical Analysis
Statistical Analysis was performed by using Jupyter.

Most Successful Experiment Results:

<img width="473" height="157" alt="image" src="https://github.com/user-attachments/assets/ccf11dc6-3553-45f2-9797-334bc5dbfc17" />

<img width="477" height="123" alt="image" src="https://github.com/user-attachments/assets/5c4e52c9-639d-4d2e-84d7-d451f108b4c3" />

<img width="477" height="154" alt="image" src="https://github.com/user-attachments/assets/f4c0388f-137a-4ca7-8d50-b0d525c2615b" />

Least Successful Experiment Results:

<img width="479" height="157" alt="image" src="https://github.com/user-attachments/assets/4a68b42d-e10d-445a-89f0-1deca69f78e8" />

<img width="476" height="131" alt="image" src="https://github.com/user-attachments/assets/90da0781-7940-43d5-99f6-23294adb34db" />

<img width="476" height="150" alt="image" src="https://github.com/user-attachments/assets/3e1f85a2-b5ec-45ed-a040-29df4f8b7777" />


**Overall Findings:**

| Metric             | Best Run         | Worst Run                |
| ------------------ | ---------------- | ------------------------ |
| SNR                | 10.12            | 2.19                     |
| T-Test p-value     | < 0.05           | < 0.05                   |
| Chi-Square p-value | < 0.05           | < 0.05                   |
| Entropy            | Low (detectable) | Higher (less detectable) |
| Robustness         | σ ≤ 0.005 s      | Fails under small noise  |

**Key Interpretation:**
- Higher SNR → reliable decoding but easier to detect
- Lower SNR → stealthier but less reliable
- Timing channels require balance between performance and stealth

**Security Trade-off**

| Reliable Channel         | Stealthy Channel     |
| ------------------------ | -------------------- |
| High SNR                 | Lower SNR            |
| Accurate decoding        | More decoding errors |
| Statistically detectable | Harder to detect     |
| Low entropy              | Higher entropy       |

**Real-World Feasability**

| Network                      | Result         |
| ---------------------------- | -------------- |
| Local network (<5 ms jitter) | Works reliably |
| Internet (10–50 ms jitter)   | Unreliable     |

Factors limiting covert channels:

- Network jitter
- Traffic shaping
- Packet batching
- Clock drift
- IDS statistical detection
- Header normalization by firewalls
