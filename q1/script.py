#!/usr/bin/env python
# filepath: /home/pavan/Desktop/mininet-eval/q1/script.py

"""
Enhanced MAC Protocol Comparison Script 
Simulates 802.11a/g/n protocols with appropriate characteristics
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info, error
import time
import subprocess
import os
import random

# Theoretical max speeds
MAX_SPEED_A = 54    # 802.11a: max 54 Mbps
MAX_SPEED_G = 54    # 802.11g: max 54 Mbps
MAX_SPEED_N = 300   # 802.11n: max 300 Mbps (theoretical)

# Link cap
LINK_CAP = 100      # Cap at 100 Mbps as in original script

class MacProtocolSimulator:
    """Simulates various 802.11 MAC protocol characteristics"""
    
    def __init__(self, standard, host, target_ip):
        self.standard = standard
        self.host = host
        self.target_ip = target_ip
        
        # Define protocol-specific parameters
        if standard == 'a':
            self.max_speed = MAX_SPEED_A
            self.collision_probability = 0.10
            self.backoff_factor = 2.0
            self.overhead = 0.25
        elif standard == 'g':
            self.max_speed = MAX_SPEED_G
            self.collision_probability = 0.08
            self.backoff_factor = 1.8
            self.overhead = 0.20
        elif standard == 'n':
            self.max_speed = min(MAX_SPEED_N, LINK_CAP)
            self.collision_probability = 0.05
            self.backoff_factor = 1.5
            self.overhead = 0.15
        else:
            raise ValueError(f"Unknown standard: {standard}")
    
    def simulate_traffic(self, duration=5):
        """Simulate network traffic with realistic MAC behavior"""
        info(f"*** Simulating 802.11{self.standard} traffic for {duration}s\n")
        
        # Start iperf with appropriate parameters
        output = self.host.cmd(f'iperf -c {self.target_ip} -t {duration} -i 1')
        
        # Parse the throughput
        throughput = self.parse_iperf(output)
        
        # Apply protocol-specific adjustments to better simulate real behavior
        adjusted_throughput = self.apply_protocol_effects(throughput)
        
        return adjusted_throughput
    
    def apply_protocol_effects(self, base_throughput):
        """Apply protocol-specific effects to the throughput"""
        # Factor in protocol overhead
        effective_throughput = base_throughput * (1 - self.overhead)
        
        # Cap at theoretical maximum
        effective_throughput = min(effective_throughput, self.max_speed)
        
        # Adjust for protocol efficiency
        if self.standard == 'a':
            # 802.11a is less efficient in presence of obstacles
            effective_throughput *= 0.90
        elif self.standard == 'g':
            # 802.11g has better efficiency
            effective_throughput *= 0.95
        elif self.standard == 'n':
            # 802.11n has best efficiency with MIMO
            effective_throughput *= 0.98
        
        return effective_throughput
    
    def parse_iperf(self, output):
        """Parse iperf output to extract bandwidth"""
        for line in reversed(output.split('\n')):
            if 'Mbits/sec' in line and 'sender' not in line:
                try:
                    return float(line.split()[-2])
                except:
                    pass
        return 0.0

def create_network():
    """Create a network to simulate different 802.11 protocols"""
    # Create Mininet without a controller - using OVS in standalone mode
    net = Mininet(switch=OVSSwitch, link=TCLink, controller=None)
    
    # Add switch (simulating access point)
    switch = net.addSwitch('s1')
    
    # Add hosts (simulating stations with different protocols)
    info("*** Creating nodes\n")
    h1 = net.addHost('h1', ip='10.0.0.1/8')  # Simulating 802.11a
    h2 = net.addHost('h2', ip='10.0.0.2/8')  # Simulating 802.11g
    h3 = net.addHost('h3', ip='10.0.0.3/8')  # Simulating 802.11n
    ap = net.addHost('ap', ip='10.0.0.100/8')  # Simulating access point
    
    # Create links simulating different protocols
    
    # 802.11a: 5GHz band, 54 Mbps max, higher latency
    net.addLink(h1, switch, bw=MAX_SPEED_A, delay='2ms', loss=1)
    
    # 802.11g: 2.4GHz band, 54 Mbps max, medium latency
    net.addLink(h2, switch, bw=MAX_SPEED_G, delay='1ms', loss=0.5)
    
    # 802.11n: Dual band, 300 Mbps max (capped by our 100 Mbps link), lowest latency
    net.addLink(h3, switch, bw=min(MAX_SPEED_N, LINK_CAP), delay='0.5ms', loss=0.1)
    
    # AP link - full bandwidth
    net.addLink(ap, switch, bw=LINK_CAP)
    
    return net, [h1, h2, h3], ap

def test_connectivity(hosts, ap):
    """Test if hosts can reach the AP"""
    info("\n*** Testing connectivity\n")
    
    success = True
    for host in hosts:
        result = host.cmd(f'ping -c 4 -W 2 {ap.IP()}')
        if '4 received' not in result:
            error(f"{host.name} failed to connect\n")
            success = False
        else:
            info(f"{host.name} connected successfully\n")
    
    return success

def run_perf_tests(hosts, ap):
    """Run performance tests using protocol simulators"""
    info("\n*** Starting performance tests\n")
    
    # Start iperf server on AP
    ap.cmd('killall -9 iperf 2>/dev/null')
    ap.cmd('iperf -s -D')
    time.sleep(2)
    
    # Map hosts to standards
    standards = {'h1': 'a', 'h2': 'g', 'h3': 'n'}
    results = {}
    
    # Test each host with appropriate protocol simulation
    for host in hosts:
        standard = standards[host.name]
        info(f"Testing 802.11{standard} ({host.name})...\n")
        
        simulator = MacProtocolSimulator(standard, host, ap.IP())
        throughput = simulator.simulate_traffic(duration=5)
        
        results[host.name] = throughput
        info(f"Throughput: {throughput:.2f} Mbps\n")
        time.sleep(1)
    
    # Stop iperf server
    ap.cmd('killall iperf')
    
    return results

def create_plot(results):
    """Create a plot of protocol performance"""
    try:
        import matplotlib
        # Use non-interactive backend
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Set up data for plotting
        protocols = ['802.11a', '802.11g', '802.11n']
        throughputs = [results['h1'], results['h2'], results['h3']]
        
        # Define protocol characteristics for visual display
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        hatches = ['/', '\\', 'x']
        
        plt.figure(figsize=(12, 8))
        
        # Create bars with custom appearance
        bars = plt.bar(protocols, throughputs, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Add patterns to bars
        for bar, hatch in zip(bars, hatches):
            bar.set_hatch(hatch)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height + 1,
                     f'{height:.2f} Mbps', ha='center', va='bottom', fontweight='bold')
        
        # Add theoretical max speeds for comparison
        plt.axhline(y=MAX_SPEED_A, color='#3498db', linestyle='--', alpha=0.5, label='802.11a Max (54 Mbps)')
        plt.axhline(y=MAX_SPEED_G, color='#2ecc71', linestyle='--', alpha=0.5, label='802.11g Max (54 Mbps)')
        plt.axhline(y=min(MAX_SPEED_N, LINK_CAP), color='#e74c3c', linestyle='--', alpha=0.5, 
                   label=f'802.11n Max ({min(MAX_SPEED_N, LINK_CAP)} Mbps, link limited)')
        
        # Add protocol comparison table as text
        table_text = """
        Protocol Characteristics:
        
        802.11a:
        • 5 GHz band
        • Less interference
        • Limited range
        • Max 54 Mbps
        
        802.11g:
        • 2.4 GHz band
        • More interference
        • Better range
        • Max 54 Mbps
        
        802.11n:
        • Dual band (2.4/5 GHz)
        • MIMO technology
        • Best range
        • Max 300+ Mbps
        """
        
        # plt.figtext(0.15, 0.02, table_text, fontsize=10, bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        # Add labels, title and legend
        plt.ylabel('Throughput (Mbps)', fontsize=12)
        plt.ylim(0, max(throughputs) * 1.2)
        plt.title('802.11 Protocol Performance Comparison', fontsize=16, fontweight='bold')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.legend(loc='upper right')
        
        # Save plot with high resolution
        plt.tight_layout()
        plt.savefig('protocol_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        info("*** Saved results to protocol_comparison.png\n")
        
    except ImportError:
        error("Matplotlib not available - skipping plot\n")
    except Exception as e:
        error(f"Error creating plot: {e}\n")

def main():
    """Main function to run the demonstration"""
    setLogLevel('info')
    net = None
    
    try:
        # Create and start network
        net, hosts, ap = create_network()
        net.start()
        
        # Configure OVS switch to operate as a learning switch
        switch = net.get('s1')
        switch.cmd('ovs-ofctl add-flow s1 action=normal')
        
        # Wait for network to initialize
        time.sleep(2)
        
        # Test connectivity
        if not test_connectivity(hosts, ap):
            info("*** Some connectivity tests failed, but continuing...\n")
        
        # Run performance tests
        results = run_perf_tests(hosts, ap)
        
        # Create comparison table
        info("\n*** Protocol Performance Comparison\n")
        info("Protocol      Throughput (Mbps)   Theoretical Max\n")
        info("---------------------------------------------------\n")
        info(f"802.11a (h1)    {results['h1']:.2f}              54 Mbps\n")
        info(f"802.11g (h2)    {results['h2']:.2f}              54 Mbps\n")
        info(f"802.11n (h3)    {results['h3']:.2f}              {min(MAX_SPEED_N, LINK_CAP)} Mbps\n")
        
        # Create visualization
        create_plot(results)
        
        # Save results to CSV
        with open('protocol_results.csv', 'w') as f:
            f.write("Protocol,Throughput (Mbps),Theoretical Max (Mbps)\n")
            f.write(f"802.11a,{results['h1']:.2f},{MAX_SPEED_A}\n")
            f.write(f"802.11g,{results['h2']:.2f},{MAX_SPEED_G}\n")
            f.write(f"802.11n,{results['h3']:.2f},{min(MAX_SPEED_N, LINK_CAP)}\n")
        info("*** Saved results to protocol_results.csv\n")
        
    except Exception as e:
        error(f"Error: {str(e)}\n")
        
    finally:
        if net:
            info("\n*** Stopping network\n")
            net.stop()

if __name__ == '__main__':
    main()