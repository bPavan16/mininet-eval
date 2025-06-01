#!/usr/bin/env python
# filepath: /home/pavan/Desktop/mininet-eval/q10/script.py

"""
Handover Simulation with Standard Mininet

This script simulates a wireless handover by using standard Mininet with
TCLink to emulate wireless properties. It reduces the quality of one link
to force a "handover" to another link.
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch 
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

def topology():
    """Create a network topology that simulates wireless handover"""

    # Create network with OVS switches and TCLinks, but no controller
    net = Mininet(switch=OVSSwitch, link=TCLink, controller=None)

    info("*** Creating nodes\n")
    # Add switches to represent access points (using them in standalone mode)
    s1 = net.addSwitch('s1', failMode='standalone')  # Represents AP1
    s2 = net.addSwitch('s2', failMode='standalone')  # Represents AP2
    
    # Add a host to represent the mobile station
    sta1 = net.addHost('sta1')
    
    # Add another host as a server to test connectivity
    h1 = net.addHost('h1')

    info("*** Creating links\n")
    # Connect server to both "access points"
    net.addLink(h1, s1)
    net.addLink(h1, s2)
    
    # Connect station to both "access points" with special configurations
    # Initially link to s1 (AP1) has good quality
    link1 = net.addLink(sta1, s1, 
                      bw=10,  # 10 Mbps
                      delay='5ms',  # Low initial delay
                      loss=0,  # No packet loss initially
                      max_queue_size=1000)
    
    # Link to s2 (AP2) has stable quality
    link2 = net.addLink(sta1, s2, 
                      bw=8,   # 8 Mbps
                      delay='15ms',  # Higher delay
                      loss=1,  # 1% packet loss
                      max_queue_size=1000)

    info("*** Starting network\n")
    net.build()
    
    # Configure IP addresses
    sta1.cmd('ifconfig sta1-eth0 10.0.0.10/24')
    sta1.cmd('ifconfig sta1-eth1 10.0.0.11/24')
    h1.cmd('ifconfig h1-eth0 10.0.0.100/24')
    h1.cmd('ifconfig h1-eth1 10.0.0.101/24')
    
    # Set up routing: initially use s1 (AP1)
    sta1.cmd('ip route add default via 10.0.0.100 dev sta1-eth0')
    
    # Create directory for storing results
    if not os.path.exists('./results'):
        os.makedirs('./results')
    
    # Lists to store data for plotting
    times = []
    ap1_quality = []
    ap2_quality = []
    connected_ap = []
    
    # Function to check which AP is being used (based on routes)
    def get_current_ap():
        route_info = sta1.cmd('ip route get 10.0.0.100')
        if 'dev sta1-eth0' in route_info:
            return 's1'  # Connected to AP1
        elif 'dev sta1-eth1' in route_info:
            return 's2'  # Connected to AP2
        else:
            return 'None'
    
    # Function to check connection quality
    def check_connection_quality():
        # Ping h1 through the current route and measure latency
        result = sta1.cmd('ping -c 3 -q 10.0.0.100')
        
        # Parse ping output to get latency and packet loss
        try:
            if '% packet loss' in result:
                packet_loss = float(result.split('%')[0].split(' ')[-1])
            else:
                packet_loss = 100  # Assume 100% loss if output format is unexpected
                
            if 'min/avg/max' in result:
                avg_latency = float(result.split('min/avg/max')[1].split('=')[1].split('/')[1])
            else:
                avg_latency = 1000  # High latency if output format is unexpected
                
            # Calculate connection quality (lower is worse)
            # Formula: 100 - (normalized latency + packet loss)
            quality = max(0, 100 - (avg_latency / 5) - packet_loss)
            return quality
        except:
            return 0  # Return 0 quality if parsing fails
    
    # Wait for network to stabilize
    info("*** Waiting for network to stabilize\n")
    time.sleep(3)
    
    info("*** Starting AP quality reduction to force handover\n")
    start_time = time.time()
    handover_occurred = False
    handover_time = 0
    handover_step = 0
    current_ap = get_current_ap()
    
    # Initial measurement
    ap1_qual = check_connection_quality()
    sta1.cmd('ip route del default')
    sta1.cmd('ip route add default via 10.0.0.101 dev sta1-eth1')
    time.sleep(1)  # Give time for routing to update
    ap2_qual = check_connection_quality()
    # Restore original route
    sta1.cmd('ip route del default')
    sta1.cmd('ip route add default via 10.0.0.100 dev sta1-eth0')
    time.sleep(1)  # Give time for routing to update
    
    times.append(0)
    ap1_quality.append(ap1_qual)
    ap2_quality.append(ap2_qual)
    connected_ap.append(current_ap)
    
    info(f"Initial AP qualities - AP1: {ap1_qual:.1f}%, AP2: {ap2_qual:.1f}%\n")
    info(f"STA1 currently routed via: {current_ap}\n")
    
    # Gradually reduce quality of link to AP1
    for step in range(1, 21):  # 20 steps
        elapsed = time.time() - start_time
        
        # Increase delay and packet loss for link to AP1
        delay = 5 + step * 5  # 5ms to 105ms
        loss = step  # 1% to 20%
        
        # Update link parameters
        try:
            link1_intf = sta1.connectionsTo(s1)[0][0]
            cmd = f'tc qdisc replace dev {link1_intf.name} root netem delay {delay}ms loss {loss}%'
            sta1.cmd(cmd)
            
            info(f"Reduced quality of link to AP1 - delay: {delay}ms, loss: {loss}%\n")
            
            # Check connection quality for both APs
            ap1_qual = check_connection_quality()
            
            # Temporarily change route to check AP2 quality
            sta1.cmd('ip route del default')
            sta1.cmd('ip route add default via 10.0.0.101 dev sta1-eth1')
            time.sleep(1)  # Give time for routing to update
            ap2_qual = check_connection_quality()
            
            # Decide which AP to use based on quality
            if ap1_qual < ap2_qual - 15:  # Hysteresis of 15% to prevent oscillation
                if current_ap == 's1':
                    # Handover to AP2
                    info(f"\n*** Handover: Switching from AP1 to AP2\n")
                    current_ap = 's2'
                    # Keep the route via AP2
                    if not handover_occurred:
                        handover_time = elapsed
                        handover_step = step
                        handover_occurred = True
                else:
                    # Already using AP2, keep using it
                    pass
            else:
                # AP1 still good enough or already using AP2
                if current_ap == 's2':
                    # Already using AP2, keep using it
                    pass
                else:
                    # Switch back to AP1
                    sta1.cmd('ip route del default')
                    sta1.cmd('ip route add default via 10.0.0.100 dev sta1-eth0')
                    time.sleep(1)  # Give time for routing to update
            
            # Store data for plotting
            times.append(elapsed)
            ap1_quality.append(ap1_qual)
            ap2_quality.append(ap2_qual)
            connected_ap.append(current_ap)
            
            info(f"AP qualities - AP1: {ap1_qual:.1f}%, AP2: {ap2_qual:.1f}%\n")
            info(f"STA1 currently routed via: {current_ap}\n")
            
            # If handover occurred and we've collected enough data, break
            if handover_occurred and step > handover_step + 5:
                break
        except Exception as e:
            info(f"Error in step {step}: {e}\n")
            
        time.sleep(1)
    
    # Show handover summary
    if handover_occurred:
        info(f"\n*** Handover occurred at step {handover_step}, time: {handover_time:.2f} seconds\n")
        info(f"*** AP1 quality at handover: {ap1_quality[handover_step]:.1f}%\n")
        info(f"*** AP2 quality at handover: {ap2_quality[handover_step]:.1f}%\n")
    else:
        info("\n*** No handover occurred during simulation\n")
    
    # Create visualization
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(times, ap1_quality, 'b-', linewidth=2, label='AP1 Quality')
        plt.plot(times, ap2_quality, 'g-', linewidth=2, label='AP2 Quality')
        
        # Mark points where station is connected to each AP
        ap1_connected = [i for i, ap in enumerate(connected_ap) if ap == 's1']
        ap2_connected = [i for i, ap in enumerate(connected_ap) if ap == 's2']
        
        if ap1_connected:
            plt.scatter([times[i] for i in ap1_connected], [ap1_quality[i] for i in ap1_connected], 
                      color='blue', s=50, alpha=0.5, label='Connected to AP1')
                      
        if ap2_connected:
            plt.scatter([times[i] for i in ap2_connected], [ap2_quality[i] for i in ap2_connected], 
                      color='green', s=50, alpha=0.5, label='Connected to AP2')
        
        # Mark handover point
        if handover_occurred:
            plt.axvline(x=handover_time, color='r', linestyle='--', 
                      label=f'Handover at {handover_time:.1f}s')
        
        plt.title('Wireless Handover Simulation')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Connection Quality (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('./results/handover_simulation.png', dpi=300)
        
        info(f"\n*** Created visualization: ./results/handover_simulation.png\n")
    except Exception as e:
        info(f"Error creating visualization: {e}\n")
    
    # Create a basic text report
    try:
        with open('./results/handover_report.txt', 'w') as f:
            f.write("WIRELESS HANDOVER SIMULATION REPORT\n")
            f.write("===================================\n\n")
            
            f.write("SIMULATION SETUP:\n")
            f.write(f"- AP1 (s1): Initial quality link (10Mbps, 5ms delay, 0% loss)\n")
            f.write(f"- AP2 (s2): Stable quality link (8Mbps, 15ms delay, 1% loss)\n\n")
            
            f.write("SIMULATION RESULTS:\n")
            if handover_occurred:
                f.write(f"- Handover occurred at {handover_time:.2f} seconds\n")
                f.write(f"- AP1 quality at handover: {ap1_quality[handover_step]:.1f}%\n")
                f.write(f"- AP2 quality at handover: {ap2_quality[handover_step]:.1f}%\n")
                f.write(f"- AP1 parameters at handover: {5 + handover_step * 5}ms delay, {handover_step}% loss\n")
            else:
                f.write("- No handover occurred during simulation\n")
        
        info(f"\n*** Created report: ./results/handover_report.txt\n")
    except Exception as e:
        info(f"Error creating report: {e}\n")
    
    # Run CLI for further exploration
    info("\n*** Running CLI\n")
    CLI(net)
    
    # Clean up
    info("\n*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()