#!/usr/bin/env python
# filepath: /home/pavan/Desktop/mininet-eval/q6/script.py

"""
Handover Simulation using Standard Mininet
Simulates a station moving between two access points without specialized WiFi modules
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
import os
import time
import subprocess
import sys
import threading

def cleanup():
    """Clean up previous Mininet instances"""
    info("*** Cleaning up previous instances\n")
    os.system('sudo mn -c > /dev/null 2>&1')
    os.system('sudo pkill -f iperf > /dev/null 2>&1')
    time.sleep(1)

def adjust_link_quality(net, sta, ap1, ap2, step_count=20):
    """Simulate movement by gradually changing link quality"""
    info("*** Starting station mobility simulation\n")
    
    # Initial link qualities - sta starts near ap1
    ap1_quality = {'bw': 20, 'delay': '1ms', 'loss': 0.1}
    ap2_quality = {'bw': 1, 'delay': '20ms', 'loss': 50}
    
    # Parameters to track current state
    current_link = 1  # 1 = connected to ap1, 2 = connected to ap2
    
    # Create TCLink connections to both APs
    # Start with good connection to AP1, poor connection to AP2
    link1 = net.addLink(sta, ap1, cls=TCLink, bw=ap1_quality['bw'], 
                       delay=ap1_quality['delay'], loss=ap1_quality['loss'])
    link2 = net.addLink(sta, ap2, cls=TCLink, bw=ap2_quality['bw'], 
                       delay=ap2_quality['delay'], loss=ap2_quality['loss'])
    
    # Set up initial routing to use AP1
    sta.cmd(f'ip route add default via {ap1.IP()}')
    
    # Open the ping output file for writing
    with open('/tmp/ping_output.txt', 'w') as f:
        f.write("*** Ping results during simulated movement ***\n")
        f.write("Time | Position | Connected AP | RTT (ms) | Packet Loss\n")
        f.write("---------------------------------------------------------\n")
        
        # Start the movement simulation
        for step in range(step_count + 1):
            position = step / step_count  # 0.0 to 1.0 representing position
            
            # Calculate new link qualities based on position
            # As sta moves from AP1 to AP2, quality of AP1 link decreases and AP2 improves
            ap1_new_bw = max(1, 20 - position * 19)  # 20 down to 1
            ap1_new_delay = f"{1 + position * 19}ms"  # 1ms up to 20ms
            ap1_new_loss = min(99, position * 50)  # 0% up to 50%
            
            ap2_new_bw = max(1, 1 + position * 19)  # 1 up to 20
            ap2_new_delay = f"{20 - position * 19}ms"  # 20ms down to 1ms
            ap2_new_loss = min(99, 50 - position * 50)  # 50% down to 0%
            
            # Update link qualities to simulate movement
            link1_name = f"{sta.name}-eth0"
            link2_name = f"{sta.name}-eth1"
            
            # Update AP1 link quality
            sta.cmd(f'tc qdisc change dev {link1_name} root netem rate {ap1_new_bw}Mbit delay {ap1_new_delay} loss {ap1_new_loss}%')
            # Update AP2 link quality
            sta.cmd(f'tc qdisc change dev {link2_name} root netem rate {ap2_new_bw}Mbit delay {ap2_new_delay} loss {ap2_new_loss}%')
            
            # Determine if handover should occur (when AP2 becomes better than AP1)
            should_use_ap2 = (ap2_new_bw > ap1_new_bw and ap2_new_loss < ap1_new_loss)
            
            # If we need to change APs, simulate a handover
            if should_use_ap2 and current_link == 1:
                info(f"*** Handover at position {position:.2f}: STA changing from AP1 to AP2\n")
                # Change default route to use AP2
                sta.cmd(f'ip route del default')
                sta.cmd(f'ip route add default via {ap2.IP()}')
                current_link = 2
                
                # Record the handover event
                f.write(f"{step} | {position:.2f} | Handover to AP2 | - | -\n")
                
            elif not should_use_ap2 and current_link == 2:
                info(f"*** Handover at position {position:.2f}: STA changing from AP2 to AP1\n")
                # Change default route to use AP1
                sta.cmd(f'ip route del default')
                sta.cmd(f'ip route add default via {ap1.IP()}')
                current_link = 1
                
                # Record the handover event
                f.write(f"{step} | {position:.2f} | Handover to AP1 | - | -\n")
            
            # Run a ping test to the Internet (simulated by a server node)
            if current_link == 1:
                ping_target = ap1.IP()
                connected_ap = "AP1"
            else:
                ping_target = ap2.IP()
                connected_ap = "AP2"
                
            # Run ping and extract RTT and loss
            ping_result = sta.cmd(f'ping -c 3 -q {ping_target}')
            
            # Parse ping results
            rtt = "timeout"
            loss = 100.0
            
            for line in ping_result.split('\n'):
                if 'min/avg/max' in line:
                    try:
                        rtt = line.split('=')[1].split('/')[1].strip()
                    except:
                        pass
                if 'packets transmitted' in line:
                    try:
                        packets_sent = int(line.split(' ')[0])
                        packets_received = int(line.split(' ')[3])
                        if packets_sent > 0:
                            loss = 100.0 - (packets_received / packets_sent * 100.0)
                    except:
                        pass
            
            # Record the ping result
            f.write(f"{step} | {position:.2f} | {connected_ap} | {rtt} | {loss:.1f}%\n")
            
            # Sleep to simulate real-time movement
            time.sleep(1)
    
    info("*** Movement simulation completed\n")
    info("*** Check /tmp/ping_output.txt for detailed results\n")

def topology():
    """Create a simple network to simulate a station moving between APs"""
    cleanup()
    
    net = None
    try:
        # Create a standard Mininet network with TCLinks to simulate wireless
        net = Mininet(switch=OVSSwitch, link=TCLink, controller=None)

        info("*** Creating nodes\n")
        
        # Create two switches to act as access points with explicit dpids
        ap1 = net.addSwitch('s1', dpid='1000000000000001')  # Renamed to s1 with explicit dpid
        ap2 = net.addSwitch('s2', dpid='1000000000000002')  # Renamed to s2 with explicit dpid
        
        # Create a switch to represent the core network with explicit dpid
        core = net.addSwitch('s3', dpid='1000000000000003')  # Renamed to s3 with explicit dpid
        
        # Create a station
        sta = net.addHost('sta', ip='10.0.0.10/24')
        
        # Create a server in the core network
        server = net.addHost('server', ip='10.0.0.100/24')
        
        # Connect APs to the core
        net.addLink(ap1, core, cls=TCLink, bw=100, delay='1ms')
        net.addLink(ap2, core, cls=TCLink, bw=100, delay='1ms')
        
        # Connect server to the core
        net.addLink(server, core, cls=TCLink, bw=100, delay='1ms')
        
        # Set IP addresses for APs
        ap1.cmd('ifconfig s1-eth0 10.0.0.1/24')
        ap2.cmd('ifconfig s2-eth0 10.0.0.2/24')

        # Start the network
        info("*** Building and starting network\n")
        net.build()
        net.start()
        
        # Configure switches to act as learning switches
        for sw in [ap1, ap2, core]:
            sw.cmd(f'ovs-ofctl add-flow {sw.name} action=normal')
        
        # Allow some time for the network to initialize
        time.sleep(2)
        
        # Run ping test to check initial connectivity
        info("*** Testing initial connectivity\n")
        ping_result = sta.cmd(f'ping -c 3 {ap1.IP()}')
        if '3 received' in ping_result:
            info("Initial connectivity successful\n")
        else:
            error("Initial connectivity failed, continuing anyway\n")
        
        # Run the link quality adjustment in a separate thread to simulate movement
        info("*** Setting up mobility simulation\n")
        adjust_link_quality(net, sta, ap1, ap2)
        
        # Start CLI for network exploration
        info("\n*** Starting CLI for network exploration (type 'exit' when done)\n")
        CLI(net)
        
    except Exception as e:
        error(f"*** Error: {e}\n")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if net:
            info("\n*** Stopping network\n")
            net.stop()

def analyze_results():
    """Analyze and visualize the handover results"""
    try:
        # Check if the results file exists
        if not os.path.exists('/tmp/ping_output.txt'):
            error("*** Results file '/tmp/ping_output.txt' not found\n")
            return
            
        # Process the results
        info("*** Analyzing handover results\n")
        with open('/tmp/ping_output.txt', 'r') as f:
            lines = f.readlines()[3:]  # Skip header lines
            
        positions = []
        rtts = []
        losses = []
        handovers = []
        
        for line in lines:
            parts = line.strip().split('|')
            if len(parts) >= 5:
                try:
                    position = float(parts[1].strip())
                    positions.append(position)
                    
                    # Check if this is a handover line
                    if "Handover" in parts[2]:
                        handovers.append(position)
                        rtts.append(None)
                        losses.append(None)
                    else:
                        # Try to parse RTT
                        rtt_str = parts[3].strip()
                        if rtt_str == "timeout":
                            rtts.append(1000)  # Use 1000ms for timeouts
                        else:
                            rtts.append(float(rtt_str))
                            
                        # Parse loss
                        loss_str = parts[4].strip().replace('%', '')
                        losses.append(float(loss_str))
                except Exception as e:
                    error(f"Error parsing line: {line.strip()}, Error: {e}\n")
        
        # Generate a simple text-based visualization
        info("\n*** Handover Analysis Results ***\n")
        info("Position | RTT (ms) | Packet Loss | Status\n")
        info("------------------------------------------\n")
        
        for i, pos in enumerate(positions):
            if i < len(rtts) and rtts[i] is None:  # Handover point
                info(f"{pos:.2f}    | -------- | ---------- | *** HANDOVER ***\n")
            elif i < len(rtts) and i < len(losses):
                status = "GOOD" if rtts[i] < 100 and losses[i] < 10 else "POOR"
                info(f"{pos:.2f}    | {rtts[i]:.1f}     | {losses[i]:.1f}%       | {status}\n")
        
        # Try to create a plot if matplotlib is available
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Create positions for plotting, filtering out handover points
            plot_positions = []
            plot_rtts = []
            plot_losses = []
            
            for i, pos in enumerate(positions):
                if i < len(rtts) and rtts[i] is not None:
                    plot_positions.append(pos)
                    plot_rtts.append(min(rtts[i], 500))  # Cap RTT at 500ms for visibility
                    plot_losses.append(losses[i])
            
            # Create a figure with two subplots
            plt.figure(figsize=(10, 8))
            
            # Ensure we have data to plot
            if len(plot_positions) > 0 and len(plot_rtts) > 0:
                # RTT subplot
                plt.subplot(2, 1, 1)
                plt.plot(plot_positions, plot_rtts, 'b-o', linewidth=2)
                
                # Mark handover points with vertical lines
                for h_pos in handovers:
                    plt.axvline(x=h_pos, color='r', linestyle='--', alpha=0.7)
                    if len(plot_rtts) > 0:  # Ensure there are RTT values
                        plt.text(h_pos, max(plot_rtts)/2, 'Handover', rotation=90, 
                                verticalalignment='center')
                
                plt.title('RTT vs. Position during Handover Simulation', fontsize=14)
                plt.ylabel('RTT (ms)', fontsize=12)
                plt.grid(True, alpha=0.3)
                
                # Packet loss subplot
                plt.subplot(2, 1, 2)
                plt.plot(plot_positions, plot_losses, 'g-o', linewidth=2)
                
                # Mark handover points with vertical lines
                for h_pos in handovers:
                    plt.axvline(x=h_pos, color='r', linestyle='--', alpha=0.7)
                    if len(plot_losses) > 0:  # Ensure there are loss values
                        plt.text(h_pos, max(plot_losses)/2, 'Handover', rotation=90, 
                                verticalalignment='center')
                
                plt.title('Packet Loss vs. Position during Handover Simulation', fontsize=14)
                plt.xlabel('Position (0.0 = near AP1, 1.0 = near AP2)', fontsize=12)
                plt.ylabel('Packet Loss (%)', fontsize=12)
                plt.grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.savefig('./handover_analysis.png', dpi=300)
                info("\n*** Created visualization: ./handover_analysis.png\n")
            else:
                error("*** Not enough data points to create a plot\n")
            
        except ImportError:
            info("\n*** Could not create visualization: matplotlib not available\n")
        except Exception as e:
            error(f"\n*** Error creating visualization: {e}\n")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        error(f"*** Error analyzing results: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
    analyze_results()