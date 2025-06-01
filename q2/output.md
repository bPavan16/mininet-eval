```plaintext
(.venv) 
Desktop/mininet-eval/q2 via 🐍 v3.12.3 (.venv) took 38s 
❯ sudo python script1.py


====== STARTING TEST WITHOUT RTS/CTS ======

*** Creating nodes
(10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 1ms delay) (10.00Mbit 1ms delay) *** Configuring hosts
sta1 sta2 ap 
*** Starting controller

*** Starting 1 switches
s1 (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 1ms delay) ...(10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 1ms delay) 
*** Configuring RTS/CTS simulation
*** Running test: WITHOUT RTS CTS
*** Simulating simultaneous access (no RTS/CTS, collision prone)
*** Analyzing results for WITHOUT RTS CTS

*** Results for WITHOUT RTS CTS:
Station 1: 8.41 Mbps, 21.9% loss
Station 2: 8.41 Mbps, 26.3% loss
Total throughput: 16.82 Mbps
Average packet loss: 24.1%

*** Starting CLI for network exploration (type "exit" when done)
*** Starting CLI:
mininet> exit
*** Stopping 0 controllers

*** Stopping 3 links
...
*** Stopping 1 switches
s1 
*** Stopping 3 hosts
sta1 sta2 ap 
*** Done


====== STARTING TEST WITH RTS/CTS ======

*** Creating nodes
(10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 1ms delay) (10.00Mbit 1ms delay) *** Configuring hosts
sta1 sta2 ap 
*** Starting controller

*** Starting 1 switches
s1 (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 1ms delay) ...(10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 2ms delay 1.00000% loss) (10.00Mbit 1ms delay) 
*** Configuring RTS/CTS simulation
*** Running test: WITH RTS CTS
*** Simulating coordinated access (RTS/CTS behavior)
*** First client done, starting second client
*** Analyzing results for WITH RTS CTS

*** Results for WITH RTS CTS:
Station 1: 13.60 Mbps, 0.0% loss
Station 2: 12.60 Mbps, 0.0% loss
Total throughput: 26.20 Mbps
Average packet loss: 0.0%

*** Starting CLI for network exploration (type "exit" when done)
*** Starting CLI:
mininet> exit
*** Stopping 0 controllers

*** Stopping 3 links
...
*** Stopping 1 switches
s1 
*** Stopping 3 hosts
sta1 sta2 ap 
*** Done

*** Comparing RTS/CTS vs. No RTS/CTS Performance ***
*** Results comparison:
=== WITH RTS/CTS ===
Station 1: 13.60 Mbps, 0.0% loss
Station 2: 12.60 Mbps, 0.0% loss
Total throughput: 26.20 Mbps
Average packet loss: 0.0%

=== WITHOUT RTS/CTS ===
Station 1: 8.41 Mbps, 21.9% loss
Station 2: 8.41 Mbps, 26.3% loss
Total throughput: 16.82 Mbps
Average packet loss: 24.1%

*** Key observations:
1. RTS/CTS reduces collisions by coordinating transmissions
2. Without RTS/CTS, hidden terminals cause collisions and packet loss
3. Total network throughput is usually better with RTS/CTS
4. RTS/CTS trades individual station throughput for fairness

*** Saved comparison plot to ./rts_cts_comparison.png

*** All tests completed. Results saved to /tmp/
(.venv) 
Desktop/mininet-eval/q2 via 🐍 v3.12.3 (.venv) took 43s 
```