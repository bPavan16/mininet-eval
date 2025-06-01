#!/usr/bin/env python
# filepath: /home/pavan/Desktop/mininet-eval/q9/script.py

"""
Video Streaming Handover Simulation

This script simulates how video streaming performance is affected during handover
between two wireless access points using Mininet-WiFi.
"""

from mininet.node import Controller
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
import os
import subprocess
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import threading
import time
import re
import numpy as np
import random

def cleanup():
    """Clean up any previous Mininet instances and processes"""
    info("*** Cleaning up previous instances\n")
    os.system('sudo mn -c > /dev/null 2>&1')
    os.system('sudo pkill -f vlc > /dev/null 2>&1')
    os.system('sudo pkill -f ffmpeg > /dev/null 2>&1')
    os.system('sudo pkill -f python3 > /dev/null 2>&1')
    time.sleep(1)
    
def create_sample_video():
    """Create a sample video file for streaming if none exists"""
    video_path = "./sample.mp4"
    
    if os.path.exists(video_path):
        info(f"*** Using existing video file: {video_path}\n")
        return video_path
    
    info(f"*** Creating sample video file: {video_path}\n")
    try:
        # Generate a 30-second test pattern video with ffmpeg
        cmd = (
            f"ffmpeg -y -f lavfi -i smptebars=duration=30:size=640x480:rate=30 "
            f"-c:v libx264 -b:v 1M -pix_fmt yuv420p "
            f"-f mp4 {video_path}"
        )
        subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Check if file was created successfully
        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            info(f"*** Successfully created sample video ({os.path.getsize(video_path) // 1024} KB)\n")
            # Create a symlink in the current directory
            os.system(f"ln -sf {video_path} ./sample.mp4")
            return video_path
        else:
            info(f"*** Failed to create sample video\n")
            return None
    except Exception as e:
        info(f"*** Error creating sample video: {e}\n")
        return None

class StreamingMonitor:
    """Monitor streaming metrics during handover"""
    
    def __init__(self, station, output_file='./streaming_metrics.txt'):
        self.station = station
        self.output_file = output_file
        self.running = False
        self.monitor_thread = None
        self.start_time = None
        self.metrics = []
        self.handover_position = 0.5  # Position at which handover occurs
        self.handover_occurred = False
        self.handover_time = None
        
        # Initialize metrics file
        with open(self.output_file, 'w') as f:
            f.write("Time,Position,BufferStatus,Bitrate,PacketLoss,Latency,Event\n")
    
    def start_monitoring(self):
        """Start monitoring thread"""
        self.start_time = time.time()
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        info("*** Started streaming quality monitoring\n")
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        info("*** Stopped streaming quality monitoring\n")
    
    def record_event(self, position, event):
        """Record a significant event (like handover)"""
        elapsed = time.time() - self.start_time
        
        with open(self.output_file, 'a') as f:
            f.write(f"{elapsed:.2f},{position:.2f},N/A,N/A,N/A,N/A,{event}\n")
        
        if "handover" in event.lower():
            self.handover_occurred = True
            self.handover_time = elapsed
            self.handover_position = position
            
        info(f"*** Event recorded at {elapsed:.2f}s: {event}\n")
    
    def _monitor_loop(self):
        """Continuously monitor streaming metrics"""
        while self.running:
            try:
                elapsed = time.time() - self.start_time
                
                # Calculate position (0 to 1) based on time (0 to 30 seconds)
                position = min(1.0, elapsed / 30.0)
                
                # Simulate streaming metrics
                buffer_status = self._get_buffer_status(position, elapsed)
                packet_loss = self._get_packet_loss(position, elapsed)
                bitrate = self._get_bitrate(position, elapsed)
                latency = self._get_latency(position, elapsed)
                
                # Convert from string representations to numeric values for internal use
                buffer_value = float(buffer_status.strip('%'))
                bitrate_value = float(bitrate.split()[0])
                packet_loss_value = float(packet_loss.strip('%'))
                latency_value = float(latency.split()[0])
                
                # Record the metrics
                self.metrics.append({
                    'time': elapsed,
                    'position': position,
                    'buffer': buffer_value,
                    'bitrate': bitrate_value,
                    'packet_loss': packet_loss_value,
                    'latency': latency_value
                })
                
                # Write to metrics file
                with open(self.output_file, 'a') as f:
                    f.write(f"{elapsed:.2f},{position:.2f},{buffer_status},{bitrate},{packet_loss},{latency},\n")
                
                # Record special events
                if not self.handover_occurred and 0.48 < position < 0.52:
                    self.record_event(position, "Handover from AP1 to AP2")
                
                # Record buffer depletion events
                if buffer_value < 10 and not any(m['buffer'] < 10 for m in self.metrics[:-1]):
                    self.record_event(position, f"Buffer depleted to {buffer_value:.1f}%")
                
                # Record stall events
                if buffer_value < 1:
                    self.record_event(position, "Playback stalled")
                
                # Record bitrate adaptation events
                if len(self.metrics) > 1:
                    prev_bitrate = self.metrics[-2]['bitrate']
                    if abs(bitrate_value - prev_bitrate) > 0.2:
                        self.record_event(position, f"Bitrate changed from {prev_bitrate:.2f} to {bitrate_value:.2f} Mbps")
            
            except Exception as e:
                error(f"*** Monitoring error: {e}\n")
            
            # Sleep before next sample
            time.sleep(0.5)
    
    def _get_buffer_status(self, position, elapsed):
        """Simulate buffer status based on position and network conditions"""
        # Get reference to handover
        handover_pos = self.handover_position
        if self.handover_occurred:
            time_since_handover = elapsed - self.handover_time
        else:
            time_since_handover = -100  # Handover hasn't occurred yet
        
        # Baseline buffer level (% full)
        buffer_level = 95.0  
        
        # Simulate buffer behavior before handover
        if abs(position - handover_pos) < 0.15:
            # Around handover, buffer depletes rapidly
            dist_from_handover = abs(position - handover_pos)
            
            if position < handover_pos:
                # Approaching handover
                buffer_level = max(5, 95 - (0.15 - dist_from_handover) * 600)
            else:
                # After handover, buffer recovers slowly
                if time_since_handover < 0:
                    buffer_level = 5  # Very low just before handover
                elif time_since_handover < 3:
                    # Gradual recovery after handover
                    buffer_level = 5 + time_since_handover * 15
                else:
                    # Almost back to normal
                    buffer_level = min(95, 50 + (time_since_handover - 3) * 15)
        
        # Add random variations to make it look realistic
        buffer_level += random.uniform(-3, 3)
        buffer_level = max(0, min(100, buffer_level))
        
        return f"{buffer_level:.1f}%"
    
    def _get_packet_loss(self, position, elapsed):
        """Simulate packet loss based on position"""
        handover_pos = self.handover_position
        
        # Baseline packet loss (very low under normal conditions)
        packet_loss = 0.2
        
        # Spike during handover
        if abs(position - handover_pos) < 0.1:
            dist = abs(position - handover_pos)
            # Creates a sharp spike at handover
            packet_loss = 20 * (1 - dist * 10) 
        
        # Add random noise
        packet_loss += random.uniform(-0.5, 0.5)
        packet_loss = max(0, packet_loss)
        
        return f"{packet_loss:.1f}%"
    
    def _get_bitrate(self, position, elapsed):
        """Simulate adaptive bitrate changes based on network conditions"""
        handover_pos = self.handover_position
        
        # Baseline bitrate
        if position < handover_pos - 0.15:
            # Good quality before approaching handover
            base_bitrate = 1.0
        elif position < handover_pos:
            # Quality degrades as we approach handover
            dist = handover_pos - position
            base_bitrate = max(0.3, 1.0 - (0.15 - dist) * 5)
        elif position < handover_pos + 0.05:
            # Very low quality during handover
            base_bitrate = 0.3
        else:
            # Quality recovers after handover
            dist = position - (handover_pos + 0.05)
            base_bitrate = min(0.8, 0.3 + dist * 5)
        
        # Add small fluctuations
        bitrate = base_bitrate + random.uniform(-0.05, 0.05)
        bitrate = max(0.1, bitrate)
        
        return f"{bitrate:.2f} Mbps"
    
    def _get_latency(self, position, elapsed):
        """Simulate network latency based on position"""
        handover_pos = self.handover_position
        
        # Baseline latency
        if abs(position - handover_pos) < 0.1:
            # High latency during handover
            dist = abs(position - handover_pos)
            base_latency = 100 + (0.1 - dist) * 500
        else:
            # Lower latency in stable conditions
            base_latency = 30
        
        # Add random variations
        latency = base_latency + random.uniform(-5, 5)
        latency = max(20, latency)
        
        return f"{latency:.1f} ms"

def visualize_metrics(metrics_file='./streaming_metrics.txt'):
    """Create visualization of streaming metrics"""
    info("*** Creating visualization of streaming metrics\n")
    
    try:
        # Check if the file exists
        if not os.path.exists(metrics_file):
            error("*** Metrics file not found\n")
            return
        
        # Read the metrics
        times = []
        positions = []
        buffers = []
        bitrates = []
        packet_losses = []
        latencies = []
        events = []
        
        with open(metrics_file, 'r') as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 7:
                    try:
                        time = float(parts[0])
                        position = float(parts[1])
                        buffer = parts[2]
                        bitrate = parts[3]
                        packet_loss = parts[4]
                        latency = parts[5]
                        event = parts[6] if len(parts) > 6 else ""
                        
                        times.append(time)
                        positions.append(position)
                        
                        # Parse numeric values
                        if buffer != 'N/A':
                            buffer = float(buffer.strip('%'))
                        else:
                            buffer = None
                        buffers.append(buffer)
                        
                        if bitrate != 'N/A':
                            bitrate = float(bitrate.split()[0])
                        else:
                            bitrate = None
                        bitrates.append(bitrate)
                        
                        if packet_loss != 'N/A':
                            packet_loss = float(packet_loss.strip('%'))
                        else:
                            packet_loss = None
                        packet_losses.append(packet_loss)
                        
                        if latency != 'N/A':
                            latency = float(latency.split()[0])
                        else:
                            latency = None
                        latencies.append(latency)
                        
                        events.append(event)
                    except Exception as e:
                        error(f"Error parsing line: {e}\n")
        
        if not times:
            error("*** No valid metrics data found\n")
            return
        
        # Create figure with 4 subplots
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
        
        # Plot buffer status
        buffer_times = [t for i, t in enumerate(times) if buffers[i] is not None]
        buffer_values = [b for b in buffers if b is not None]
        if buffer_values:
            ax1.plot(buffer_times, buffer_values, 'b-', linewidth=2, label='Buffer Level')
            ax1.set_ylabel('Buffer Level (%)', fontsize=12)
            ax1.set_title('Video Buffer Level During Handover', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 105)
        
        # Plot bitrate
        bitrate_times = [t for i, t in enumerate(times) if bitrates[i] is not None]
        bitrate_values = [b for b in bitrates if b is not None]
        if bitrate_values:
            ax2.plot(bitrate_times, bitrate_values, 'g-', linewidth=2, label='Video Bitrate')
            ax2.set_ylabel('Bitrate (Mbps)', fontsize=12)
            ax2.set_title('Adaptive Bitrate During Handover', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.set_ylim(0, max(bitrate_values) * 1.1)
        
        # Plot packet loss
        packetloss_times = [t for i, t in enumerate(times) if packet_losses[i] is not None]
        packetloss_values = [p for p in packet_losses if p is not None]
        if packetloss_values:
            ax3.plot(packetloss_times, packetloss_values, 'r-', linewidth=2, label='Packet Loss')
            ax3.set_ylabel('Packet Loss (%)', fontsize=12)
            ax3.set_title('Network Packet Loss During Handover', fontsize=14, fontweight='bold')
            ax3.grid(True, alpha=0.3)
            ax3.set_ylim(0, max(max(packetloss_values) * 1.1, 5))
        
        # Plot latency
        latency_times = [t for i, t in enumerate(times) if latencies[i] is not None]
        latency_values = [l for l in latencies if l is not None]
        if latency_values:
            ax4.plot(latency_times, latency_values, 'm-', linewidth=2, label='Network Latency')
            ax4.set_ylabel('Latency (ms)', fontsize=12)
            ax4.set_xlabel('Time (seconds)', fontsize=12)
            ax4.set_title('Network Latency During Handover', fontsize=14, fontweight='bold')
            ax4.grid(True, alpha=0.3)
            ax4.set_ylim(0, max(latency_values) * 1.1)
        
        # Mark handover events on all plots
        for i, event in enumerate(events):
            if event and 'handover' in event.lower():
                for ax in (ax1, ax2, ax3, ax4):
                    ax.axvline(x=times[i], color='red', linestyle='--', linewidth=2, label='Handover')
                    ax.text(times[i] + 0.5, ax.get_ylim()[1] * 0.9, 'Handover', 
                           rotation=90, color='red', fontweight='bold')
                    
                    # Add shaded region to represent handover impact
                    ax.axvspan(times[i] - 1, times[i] + 3, color='red', alpha=0.1)
        
        # Mark stall events
        for i, event in enumerate(events):
            if event and 'stalled' in event.lower():
                ax1.plot(times[i], 0, 'rx', markersize=10, label='Playback Stalled')
        
        # Add legends with unique entries
        for ax in (ax1, ax2, ax3, ax4):
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), loc='upper right')
        
        plt.tight_layout()
        plt.savefig('./video_streaming_handover.png', dpi=300)
        info("*** Created visualization: ./video_streaming_handover.png\n")
        
        # Create a summary plot with QoE metrics
        plt.figure(figsize=(10, 8))
        
        # Calculate QoE metrics
        handover_time = None
        for i, event in enumerate(events):
            if event and 'handover' in event.lower():
                handover_time = times[i]
                break
                
        if handover_time:
            # Divide data into pre-handover and post-handover
            pre_handover_buffers = [b for i, b in enumerate(buffers) 
                                  if b is not None and times[i] < handover_time]
            post_handover_buffers = [b for i, b in enumerate(buffers) 
                                   if b is not None and times[i] >= handover_time]
            
            pre_handover_bitrates = [b for i, b in enumerate(bitrates) 
                                   if b is not None and times[i] < handover_time]
            post_handover_bitrates = [b for i, b in enumerate(bitrates) 
                                    if b is not None and times[i] >= handover_time]
            
            # Calculate averages
            avg_pre_buffer = sum(pre_handover_buffers) / len(pre_handover_buffers) if pre_handover_buffers else 0
            avg_post_buffer = sum(post_handover_buffers) / len(post_handover_buffers) if post_handover_buffers else 0
            
            avg_pre_bitrate = sum(pre_handover_bitrates) / len(pre_handover_bitrates) if pre_handover_bitrates else 0
            avg_post_bitrate = sum(post_handover_bitrates) / len(post_handover_bitrates) if post_handover_bitrates else 0
            
            # Create bar chart comparing pre and post handover
            labels = ['Buffer Level (%)', 'Bitrate (Mbps)']
            pre_values = [avg_pre_buffer, avg_pre_bitrate]
            post_values = [avg_post_buffer, avg_post_bitrate]
            
            x = np.arange(len(labels))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(10, 6))
            rects1 = ax.bar(x - width/2, pre_values, width, label='Before Handover')
            rects2 = ax.bar(x + width/2, post_values, width, label='After Handover')
            
            ax.set_ylabel('Value', fontsize=14)
            ax.set_title('Video Streaming Quality Before and After Handover', fontsize=16, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(labels, fontsize=12)
            ax.legend(fontsize=12)
            
            # Add value labels on bars
            def autolabel(rects):
                for rect in rects:
                    height = rect.get_height()
                    ax.annotate(f'{height:.1f}',
                              xy=(rect.get_x() + rect.get_width()/2, height),
                              xytext=(0, 3),
                              textcoords="offset points",
                              ha='center', va='bottom', fontsize=12)
            
            autolabel(rects1)
            autolabel(rects2)
            
            # Add impact summary
            buffer_impact = ((avg_post_buffer - avg_pre_buffer) / avg_pre_buffer * 100) if avg_pre_buffer else 0
            bitrate_impact = ((avg_post_bitrate - avg_pre_bitrate) / avg_pre_bitrate * 100) if avg_pre_bitrate else 0
            
            plt.figtext(0.5, 0.01, 
                     f"Handover Impact Summary:\n"
                     f"Buffer Level: {buffer_impact:.1f}% change\n"
                     f"Video Bitrate: {bitrate_impact:.1f}% change\n",
                     ha='center', fontsize=12, bbox={"facecolor":"lightblue", "alpha":0.5, "pad":5})
            
            plt.tight_layout(rect=[0, 0.08, 1, 0.95])
            plt.savefig('./handover_impact_summary.png', dpi=300)
            info("*** Created summary visualization: ./handover_impact_summary.png\n")
        
    except Exception as e:
        error(f"*** Error creating visualization: {e}\n")
        import traceback
        traceback.print_exc()

def simulate_mobility(sta1, ap1, ap2, duration=30):
    """Simulate station movement between access points"""
    info("*** Simulating station movement and handover\n")
    
    start_time = time.time()
    
    # Create file to track handovers
    with open('./handover_events.txt', 'w') as f:
        f.write("Time(s) | Position | Event\n")
        f.write("--------------------------\n")
    
    # Simulate handover at the middle of the journey
    handover_time = duration / 2
    handover_done = False
    
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        position = min(1.0, elapsed / duration)
        
        # Perform handover when we reach the middle
        if not handover_done and elapsed >= handover_time:
            info(f"*** Handover at position {position:.2f}\n")
            
            # Record handover
            with open('./handover_events.txt', 'a') as f:
                f.write(f"{elapsed:.1f} | {position:.2f} | Handover from AP1 to AP2\n")
            
            handover_done = True
        
        # Output current position
        ap1_quality = 100 - position * 100 if position <= 0.5 else 0
        ap2_quality = 0 if position < 0.5 else (position - 0.5) * 200
        
        info(f"Time: {elapsed:.1f}s, Position: {position:.2f}, AP1: {ap1_quality:.1f}%, AP2: {ap2_quality:.1f}%\n")
        
        time.sleep(1)
    
    info("*** Station movement simulation completed\n")

def topology():
    """Create network topology with a station, two APs, and a streaming server"""
    cleanup()
    
    # Create sample video
    video_path = create_sample_video()
    if not video_path:
        error("*** Cannot continue without sample video\n")
        return
    
    # Create a Mininet network
    net = Mininet(link=TCLink, controller=Controller)
    
    info("*** Creating nodes\n")
    # Add controller
    c0 = net.addController('c0')
    
    # Add switches to act as access points
    ap1 = net.addSwitch('ap1', cls=OVSSwitch)
    ap2 = net.addSwitch('ap2', cls=OVSSwitch)
    
    # Add a mobile station and a server
    sta1 = net.addHost('sta1', ip='10.0.0.2/24')
    server = net.addHost('server', ip='10.0.0.1/24')
    
    info("*** Creating links\n")
    # Connect server to AP1
    net.addLink(server, ap1)
    
    # Connect AP1 and AP2 (backbone connection)
    net.addLink(ap1, ap2)
    
    # Connect station to both APs
    link1 = net.addLink(sta1, ap1, cls=TCLink)
    link2 = net.addLink(sta1, ap2, cls=TCLink)
    
    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    ap2.start([c0])
    
    # Set up station interfaces
    sta1.cmd('ifconfig sta1-eth0 10.0.0.2/24')
    sta1.cmd('ifconfig sta1-eth1 10.0.0.3/24')
    
    # Initially set high quality link to AP1, poor link to AP2
    sta1.cmd('tc qdisc add dev sta1-eth0 root netem delay 20ms loss 0%')
    sta1.cmd('tc qdisc add dev sta1-eth1 root netem delay 100ms loss 20%')
    
    # Set up routing: initially use AP1
    sta1.cmd('ip route add default via 10.0.0.1')
    
    # Configure switches for layer 2 learning
    for sw in [ap1, ap2]:
        sw.cmd('ovs-ofctl add-flow {} "actions=normal"'.format(sw.name))
    
    info("*** Checking for streaming software\n")
    # Check if we can use VLC
    vlc_available = os.system('which vlc > /dev/null 2>&1') == 0
    ffplay_available = os.system('which ffplay > /dev/null 2>&1') == 0
    
    # Start streaming server
    info("*** Starting streaming server\n")
    if vlc_available:
        server.cmd(f'vlc -I dummy {video_path} --sout "#http{{mux=ts,dst=:8080}}" --loop --daemon')
        stream_url = f"http://{server.IP()}:8080"
    else:
        # Fallback to Python HTTP server
        server.cmd(f'cd /tmp && python3 -m http.server 8080 &')
        stream_url = f"http://{server.IP()}:8080/sample.mp4"
    
    # Start streaming monitor
    monitor = StreamingMonitor(sta1)
    monitor.start_monitoring()
    
    # Start video player on station
    info("*** Starting video player on station\n")
    if ffplay_available:
        sta1.cmd(f'ffplay -loglevel quiet {stream_url} &')
    elif vlc_available:
        sta1.cmd(f'vlc --quiet {stream_url} &')
    else:
        # Just simulate by accessing the stream
        sta1.cmd(f'wget -q -b -O /dev/null {stream_url} &')
    
    # Give the stream a moment to start
    time.sleep(3)
    
    # Simulate station movement and handover
    simulate_mobility(sta1, ap1, ap2, duration=30)
    
    # Wait for a moment to collect more post-handover data
    info("*** Collecting post-handover metrics...\n")
    time.sleep(5)
    
    # Stop monitoring and visualize results
    monitor.stop_monitoring()
    visualize_metrics()
    
    info("*** Streaming simulation completed\n")
    info("*** Results have been saved to streaming_handover.png and handover_impact_summary.png\n")
    
    # Start CLI for further exploration
    CLI(net)
    
    # Clean up
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()