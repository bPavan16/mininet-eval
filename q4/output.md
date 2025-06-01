```plaintext
Desktop/mininet-eval/ps4 via 🐍 v3.12.3 (.venv) 
❯ sudo python script.py
============================================================
802.11 MAC PROTOCOL LOAD IMPACT EVALUATOR
============================================================
This tool evaluates how the 802.11 MAC layer handles
traffic when multiple users are active simultaneously
============================================================
🚀 Starting 802.11 MAC Protocol Load Impact Evaluation
📡 Analyzing how MAC layer handles multiple concurrent users
------------------------------------------------------------
*** Creating 802.11 MAC load evaluation topology
(54.00Mbit 1ms delay 0.5ms jitter 0.10000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(54.00Mbit 1ms delay 0.5ms jitter 0.10000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(54.00Mbit 1ms delay 0.5ms jitter 0.10000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(54.00Mbit 1ms delay 0.5ms jitter 0.10000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(48.00Mbit 2ms delay 0.5ms jitter 0.50000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(48.00Mbit 2ms delay 0.5ms jitter 0.50000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(48.00Mbit 2ms delay 0.5ms jitter 0.50000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(48.00Mbit 2ms delay 0.5ms jitter 0.50000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(36.00Mbit 3ms delay 0.5ms jitter 1.00000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(36.00Mbit 3ms delay 0.5ms jitter 1.00000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
*** Starting network
*** Configuring hosts
sta1 sta2 sta3 sta4 sta5 
(54.00Mbit 1ms delay 0.5ms jitter 0.10000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(54.00Mbit 1ms delay 0.5ms jitter 0.10000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(48.00Mbit 2ms delay 0.5ms jitter 0.50000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(48.00Mbit 2ms delay 0.5ms jitter 0.50000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
(36.00Mbit 3ms delay 0.5ms jitter 1.00000% loss) *** Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change.
*** Waiting for network to stabilize
*** Testing connectivity
*** Ping: testing ping reachability
sta1 -> X X X X 
sta2 -> X X X X 
sta3 -> X X X X 
sta4 -> X X X X 
sta5 -> X X X X 
*** Results: 100% dropped (0/20 received)

🔍 Starting comprehensive MAC performance evaluation...
*** Starting comprehensive MAC performance analysis

============================================================
PHASE 1: BASELINE PERFORMANCE MEASUREMENT
============================================================
*** Measuring baseline throughput for sta1
*** Cleaning up existing processes
*** Cleaning up existing processes
*** Measuring baseline throughput for sta2
*** Cleaning up existing processes
*** Cleaning up existing processes
*** Measuring baseline throughput for sta3
*** Cleaning up existing processes
*** Cleaning up existing processes
*** Measuring baseline throughput for sta4
*** Cleaning up existing processes
*** Cleaning up existing processes
*** Measuring baseline throughput for sta5
*** Cleaning up existing processes
*** Cleaning up existing processes

============================================================
PHASE 2: CONCURRENT LOAD TESTING
============================================================
*** Starting concurrent throughput measurement
*** Cleaning up existing processes
sta1 concurrent throughput: 0.00 Mbps, delay: 0.05 ms
sta3 concurrent throughput: 0.00 Mbps, delay: 0.05 ms
sta5 concurrent throughput: 0.00 Mbps, delay: 0.05 ms
sta2 concurrent throughput: 0.00 Mbps, delay: 0.05 ms
sta4 concurrent throughput: 0.00 Mbps, delay: 0.06 ms
*** Cleaning up existing processes

============================================================
PHASE 3: PERFORMANCE ANALYSIS
============================================================

📊 Generating analysis plots and reports...
*** Generating comprehensive MAC performance analysis plots ***
Using simulated baseline throughput values for visualization
Using simulated concurrent throughput values for visualization

*** MAC load analysis plot saved to: /home/pavan/Desktop/mininet-eval/mac_load_analysis.png ***
*** Backup plot saved to: ./mac_load_analysis.png ***

================================================================================
802.11 MAC PROTOCOL LOAD IMPACT ANALYSIS REPORT
================================================================================

TEST CONFIGURATION:
--------------------
Number of Stations: 5
Test Duration: 20 seconds
MAC Protocol: CSMA/CA (802.11)
Topology: Star (All stations connected to single AP)

PERFORMANCE COMPARISON:
-------------------------
Station  Baseline     Concurrent   Degradation  Delay     
------------------------------------------------------------
sta1     0.00         0.00         0.0         % 0.05      
sta2     0.00         0.00         0.0         % 0.05      
sta3     0.00         0.00         0.0         % 0.05      
sta4     0.00         0.00         0.0         % 0.06      
sta5     0.00         0.00         0.0         % 0.05      

SUMMARY STATISTICS:
--------------------
Total Baseline Throughput: 0.00 Mbps
Total Concurrent Throughput: 0.00 Mbps
MAC Protocol Efficiency: 0.0%
Efficiency Loss: 100.0%

FAIRNESS ANALYSIS:
------------------
Jain's Fairness Index: 0.000
Fairness Rating: Poor
Perfect Fairness: 1.000

DELAY STATISTICS:
-----------------
Average Delay: 0.05 ms
Maximum Delay: 0.06 ms
Minimum Delay: 0.05 ms
Delay Variation: 0.01 ms

DETAILED ANALYSIS:
------------------

MAC Protocol Behavior Under Load:

1. MEDIUM ACCESS CONTROL:
   • CSMA/CA coordinates access to shared medium
   • Stations must wait for clear channel before transmission
   • Backoff algorithms prevent collisions
   • ACK mechanism ensures reliable delivery

2. CONTENTION AND OVERHEAD:
   • 5 stations compete for channel access
   • Increased contention leads to longer backoff times
   • RTS/CTS overhead for collision avoidance
   • Inter-frame spacing (SIFS/DIFS) reduces efficiency

3. PERFORMANCE IMPACT:
   • Individual capacity: 0.0 Mbps (sum of individual tests)
   • Shared capacity: 0.0 Mbps (concurrent access)
   • Overhead: 0.0 Mbps (100.0%)

4. FAIRNESS EVALUATION:
   • Fairness Index: 0.000
   • All stations get relatively equal access to the medium
   • Some variation due to different signal conditions
   • MAC protocol provides good fairness overall

5. DELAY CHARACTERISTICS:
   • Average MAC delay: 0.1 ms
   • Delay increases with network load
   • Backoff and contention contribute to latency
   • Jitter affects real-time applications
        

KEY FINDINGS:
-------------
• MAC efficiency decreases with increasing load
• 100.0% capacity lost to protocol overhead
• Average performance degradation: 0.0%
• Fairness index of 0.000 indicates poor fairness
• MAC layer introduces 0.1 ms average delay

RECOMMendations:
---------------
• Consider load balancing across multiple APs
• Implement QoS mechanisms for prioritization
• Optimize station placement for better signal quality
• Consider fair queuing algorithms
• Monitor network performance under varying loads
• Consider 802.11n/ac for higher efficiency
• Implement proper channel management

============================================================
✅ MAC LOAD EVALUATION COMPLETED!
============================================================
📈 Key Results:
   • MAC Efficiency: 0.0%
   • Fairness Index: 0.000
   • Average Delay: 0.1 ms
   • Performance Loss: 100.0%

Press Enter to open Mininet CLI for additional testing...
Available commands:
  sta1 iperf -c ap1 -t 10
  sta2 ping -c 20 ap1
  pingall
```