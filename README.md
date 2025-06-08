# Mininet Labs - Wireless Network Simulation

This repository contains a comprehensive collection of Mininet-based experiments for evaluating various aspects of 802.11 wireless network protocols and performance characteristics.

## Project Overview

This project provides hands-on laboratory exercises for understanding wireless networking concepts through simulation using Mininet-WiFi. Each question (q1-q11) focuses on different aspects of wireless networking, from basic protocol comparisons to advanced mobility and handover scenarios.

## Lab Exercises

### Q1 - MAC Protocol Performance Comparison (802.11a vs 802.11g vs 802.11n)
- **Files**: [q1/script.py](q1/script.py), [q1/protocol_results.csv](q1/protocol_results.csv)
- **Output**: [q1/protocol_comparison.png](q1/protocol_comparison.png)
- **Description**: Simulate a wireless network where multiple stations connect to an access point using different IEEE 802.11 standards. Create three stations: sta1 (802.11a), sta2 (802.11g), sta3 (802.11n). Measure throughput between each station and an AP using iperf. Analyze the impact of each MAC protocol on performance and plot the results.

### Q2 - Hidden Terminal Problem Analysis with RTS/CTS
- **Files**: [q2/script1.py](q2/script1.py)
- **Output**: [q2/rts_cts_comparison.png](q2/rts_cts_comparison.png), [q2/output.md](q2/output.md)
- **Description**: Simulate a hidden terminal problem where two stations cannot hear each other but both send to the same AP. Create two stations and one AP with overlapping but non-mutual range. Enable RTS/CTS mechanism and disable it in another run. Compare performance with and without RTS/CTS and explain how the MAC protocol handles collisions.

### Q3 - Distance and Signal Strength Impact on MAC Performance
- **Files**: [q3/script.py](q3/script.py)
- **Output**: [q3/wireless_mac_performance.png](q3/wireless_mac_performance.png)
- **Description**: Simulate a wireless network where stations are at different distances from the AP. Place sta1 near the AP and sta2 far from the AP. Observe performance degradation over distance and analyze how MAC layer parameters like signal-to-noise ratio (SNR) affect throughput.

### Q4 - Load Impact on 802.11 MAC Protocol
- **Files**: [q4/script.py](q4/script.py)
- **Output**: [q4/mac_load_analysis.png](q4/mac_load_analysis.png), [q4/output.md](q4/output.md)
- **Description**: Evaluate how the MAC layer handles traffic when multiple users are active. Create 5 stations and 1 AP. Simulate concurrent downloads (using iperf) from AP to all stations. Measure individual and total throughput. Analyze fairness and delay introduced by the MAC protocol.

### Q5 - Bandwidth Sharing Between Stations Using the Same AP
- **Files**: [q5/script.py](q5/script.py)
- **Output**: [q5/wifi_simulation_results.txt](q5/wifi_simulation_results.txt), [q5/wifi_simulation_results-1.txt](q5/wifi_simulation_results-1.txt)
- **Description**: Simulate a scenario where two stations share bandwidth while connected to one AP. Configure the AP to support a fixed data rate (e.g., 54 Mbps). Measure how this bandwidth is shared among the stations using iperf. Observe MAC-layer retransmissions, collisions, and delays.

### Q6 - Basic Handover Between Two Access Points
- **Files**: [q6/script.py](q6/script.py)
- **Output**: [q6/handover_analysis.png](q6/handover_analysis.png)
- **Description**: Simulate a network where a mobile station moves from AP1's coverage area to AP2's coverage area. Create 2 Access Points (ap1 and ap2) and 1 mobile Station (sta1). Set a movement path where sta1 moves from ap1's range into ap2's range. Capture when the handover occurs and measure packet loss or delay during handover.

### Q7 - Handover Delay Measurement
- **Files**: [q7/script.py](q7/script.py)
- **Output**: [q7/handover_detail.png](q7/handover_detail.png), [q7/mobility_results.png](q7/mobility_results.png), [q7/handover_events.txt](q7/handover_events.txt), [q7/ping_output.txt](q7/ping_output.txt)
- **Description**: Measure how long it takes for a handover to complete when a station moves between two APs. Setup the network with 2 APs and 1 mobile Station. Start a continuous ping from the station to a remote server or another host. Track the time when packets start dropping and when communication resumes. Calculate the handover delay.

### Q8 - Throughput Degradation During Handover
- **Files**: [q8/script.py](q8/script.py)
- **Description**: Observe how the throughput between a mobile device and a server is affected during handover. Use iperf to measure TCP or UDP throughput between the mobile Station and a Server. Move the Station between AP1 and AP2 during the transmission. Record throughput over time and plot the results.

### Q9 - Impact of Handover on Video Streaming
- **Files**: [q9/script.py](q9/script.py)
- **Description**: Test how real-time applications (like video streaming) behave during handover. Setup a video streaming server (like VLC server) connected to the APs. Let the Station watch a video stream while moving across AP1 and AP2. Observe interruptions, buffering, or delay during handover.

### Q10 - Forced Handover by Manipulating Signal Strength
- **Files**: [q10/script.py](q10/script.py), [q10/op.md](q10/op.md)
- **Description**: Manually reduce the signal strength of the AP to force a handover. Create 2 APs and 1 Station. Decrease the transmit power (txpower) of AP1 gradually. Force the Station to roam to AP2 as signal strength drops. Log the events and measure the handover time.

### Q11 - Multi-AP Handover Analysis
- **Files**: [q11/script.py](q11/script.py)
- **Description**: Test roaming in a network of 3 APs laid out in a row. Setup 3 Access Points: ap1, ap2, ap3 along a path. Move the Station across all three APs. Capture handover points and any packet loss. Analyze whether the station always connects to the nearest AP.

## Prerequisites

- Python 3.12+ (with virtual environment support)
- Mininet-WiFi
- Root/sudo privileges (required for network simulation)
- Required Python packages (install in virtual environment)

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mininet-labs
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt  # If available
```

## Running Experiments

Each lab exercise can be run independently. Navigate to the specific question directory and execute the script:

```bash
cd q1
sudo python script.py
```

**Note**: Most scripts require sudo privileges due to Mininet's network manipulation requirements.

## Network Topologies

The experiments utilize various network topologies including:
- Basic AP-STA configurations
- Multi-AP environments for handover testing
- Variable link conditions (bandwidth, delay, packet loss)
- Dynamic quality adjustment scenarios

## Key Features

- **Protocol Evaluation**: Compare different wireless protocols and mechanisms
- **Load Testing**: Analyze performance under varying traffic conditions
- **Mobility Simulation**: Test handover scenarios and roaming behavior
- **Real-time Monitoring**: Track network metrics and performance indicators
- **Visualization**: Generate plots and charts for result analysis

## Output Analysis

Each experiment generates various outputs:
- **CSV files**: Raw performance data
- **PNG files**: Visualization plots and graphs
- **TXT files**: Detailed logs and results
- **MD files**: Formatted output summaries

## Troubleshooting

- Ensure you have proper permissions to run network simulations
- Check that Mininet-WiFi is properly installed
- Verify Python virtual environment is activated
- Some experiments may show HTB quantum warnings - these are typically non-critical

## Contributing

When adding new experiments:
1. Create a new directory (q##)
2. Include appropriate script files
3. Generate meaningful output files
4. Update this README with experiment description

## License
This project is for educational purposes as part of wireless networking coursework.
