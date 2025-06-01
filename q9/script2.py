#!/usr/bin/env python
# filepath: /home/pavan/Desktop/mininet-eval/q9/script.py

"""
Video Streaming Handover Simulation (Simplified Version)

This script simulates how video streaming performance is affected during handover
between two wireless access points.
"""

import os
import time
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess
from mininet.log import setLogLevel, info, error

def cleanup():
    """Clean up any previous processes"""
    info("*** Cleaning up previous instances\n")
    os.system('rm -f ./streaming_metrics.txt ./handover_events.txt > /dev/null 2>&1')
    time.sleep(1)

def simulate_streaming():
    """Simulate a video streaming session with handover between APs"""
    info("*** Starting streaming simulation\n")
    
    # Simulation parameters
    duration = 30  # seconds
    handover_time = 15  # when handover occurs
    sampling_rate = 5  # data points per second
    
    # Create metrics file
    with open('./streaming_metrics.txt', 'w') as f:
        f.write("Time,Position,BufferStatus,Bitrate,PacketLoss,Latency,Event\n")
    
    # Create handover events file
    with open('./handover_events.txt', 'w') as f:
        f.write("Time(s) | Position | Event\n")
        f.write("--------------------------\n")
    
    # Simulate the streaming session
    start_time = time.time()
    handover_done = False
    
    info("*** Simulating video streaming during handover\n")
    
    for i in range(duration * sampling_rate):
        # Calculate current time and position
        sim_time = i / sampling_rate
        position = sim_time / duration
        
        # Check if handover should occur
        if not handover_done and sim_time >= handover_time:
            info(f"*** Handover at time {sim_time:.1f}s (position {position:.2f})\n")
            with open('./handover_events.txt', 'a') as f:
                f.write(f"{sim_time:.1f} | {position:.2f} | Handover from AP1 to AP2\n")
            handover_done = True
            
            # Record handover event in metrics
            with open('./streaming_metrics.txt', 'a') as f:
                f.write(f"{sim_time:.2f},{position:.2f},N/A,N/A,N/A,N/A,Handover from AP1 to AP2\n")
        
        # Generate realistic metrics based on position relative to handover
        buffer_level = generate_buffer_level(sim_time, position, handover_time)
        bitrate = generate_bitrate(sim_time, position, handover_time)
        packet_loss = generate_packet_loss(sim_time, position, handover_time)
        latency = generate_latency(sim_time, position, handover_time)
        
        # Write metrics to file
        with open('./streaming_metrics.txt', 'a') as f:
            f.write(f"{sim_time:.2f},{position:.2f},{buffer_level:.1f}%,{bitrate:.2f} Mbps,{packet_loss:.1f}%,{latency:.1f} ms,\n")
        
        # Special events
        if buffer_level < 5 and random.random() < 0.3:
            with open('./streaming_metrics.txt', 'a') as f:
                f.write(f"{sim_time:.2f},{position:.2f},{buffer_level:.1f}%,{bitrate:.2f} Mbps,{packet_loss:.1f}%,{latency:.1f} ms,Buffer critically low\n")
        
        if packet_loss > 15 and random.random() < 0.3:
            with open('./streaming_metrics.txt', 'a') as f:
                f.write(f"{sim_time:.2f},{position:.2f},{buffer_level:.1f}%,{bitrate:.2f} Mbps,{packet_loss:.1f}%,{latency:.1f} ms,High packet loss detected\n")
        
        if buffer_level < 0.5 and random.random() < 0.5:
            with open('./streaming_metrics.txt', 'a') as f:
                f.write(f"{sim_time:.2f},{position:.2f},{buffer_level:.1f}%,{bitrate:.2f} Mbps,{packet_loss:.1f}%,{latency:.1f} ms,Playback stalled\n")
                
        # Sleep to simulate real-time operation
        elapsed = time.time() - start_time
        target_time = (i + 1) / sampling_rate
        if elapsed < target_time:
            time.sleep(target_time - elapsed)
        
        # Print progress
        if i % sampling_rate == 0:
            ap1_quality = 100 - position * 100 if position <= 0.5 else 0
            ap2_quality = 0 if position < 0.5 else (position - 0.5) * 200
            info(f"Time: {sim_time:.1f}s, Position: {position:.2f}, AP1: {ap1_quality:.1f}%, AP2: {ap2_quality:.1f}%\n")
    
    info("*** Simulation completed\n")
    return True

def generate_buffer_level(time, position, handover_time):
    """Generate realistic buffer level data"""
    # Buffer starts high, drops around handover, then recovers
    if time < handover_time - 3:
        # Good buffer before approaching handover
        base = 95.0
        variation = random.uniform(-5, 5)
    elif time < handover_time:
        # Buffer starts depleting as we approach handover
        proximity = (handover_time - time) / 3.0
        base = max(5, 95 * proximity)
        variation = random.uniform(-3, 3)
    elif time < handover_time + 4:
        # Buffer is very low during and just after handover
        recovery = (time - handover_time) / 4.0
        base = 5 + recovery * 50
        variation = random.uniform(-5, 5)
    else:
        # Buffer recovers after handover
        recovery = min(1.0, (time - handover_time - 4) / 8.0)
        base = 55 + recovery * 40
        variation = random.uniform(-5, 5)
    
    # Add sinusoidal component to simulate regular buffer filling/depleting cycles
    cycle = np.sin(time * 0.8) * 5
    
    # Ensure buffer level is within valid range
    buffer_level = max(0, min(100, base + variation + cycle))
    return buffer_level

def generate_bitrate(time, position, handover_time):
    """Generate realistic bitrate data"""
    # Bitrate adapts to network conditions
    if time < handover_time - 3:
        # Good quality before approaching handover
        base = 1.8
        variation = random.uniform(-0.1, 0.1)
    elif time < handover_time:
        # Quality degrades as we approach handover
        proximity = (handover_time - time) / 3.0
        base = max(0.3, 1.8 * proximity)
        variation = random.uniform(-0.1, 0.1)
    elif time < handover_time + 2:
        # Very low quality during handover
        base = 0.3
        variation = random.uniform(-0.1, 0.1)
    else:
        # Quality improves after handover
        recovery = min(1.0, (time - handover_time - 2) / 6.0)
        base = 0.3 + recovery * 1.3
        variation = random.uniform(-0.1, 0.1)
    
    # Ensure bitrate is within valid range
    bitrate = max(0.1, base + variation)
    return bitrate

def generate_packet_loss(time, position, handover_time):
    """Generate realistic packet loss data"""
    # Packet loss spikes during handover
    time_to_handover = abs(time - handover_time)
    
    if time_to_handover < 2:
        # High packet loss during handover
        intensity = 1 - (time_to_handover / 2)
        base = 20 * intensity
        variation = random.uniform(-2, 2)
    else:
        # Low packet loss otherwise
        base = 1.0
        variation = random.uniform(-0.5, 0.5)
    
    # Ensure packet loss is within valid range
    packet_loss = max(0, base + variation)
    return packet_loss

def generate_latency(time, position, handover_time):
    """Generate realistic latency data"""
    # Latency spikes during handover
    time_to_handover = abs(time - handover_time)
    
    if time_to_handover < 3:
        # High latency during handover
        intensity = 1 - (time_to_handover / 3)
        base = 30 + 150 * intensity
        variation = random.uniform(-10, 10)
    else:
        # Low latency otherwise
        base = 30.0
        variation = random.uniform(-5, 5)
    
    # Ensure latency is within valid range
    latency = max(10, base + variation)
    return latency

def visualize_metrics():
    """Create visualization of streaming metrics"""
    info("*** Creating visualization of streaming metrics\n")
    
    try:
        # Check if the metrics file exists
        metrics_file = './streaming_metrics.txt'
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
                if len(parts) >= 6:
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
            
            # Create a text report
            with open('./streaming_qoe_report.txt', 'w') as f:
                f.write("===============================================\n")
                f.write("VIDEO STREAMING HANDOVER QUALITY OF EXPERIENCE\n")
                f.write("===============================================\n\n")
                
                f.write("SUMMARY:\n")
                f.write(f"- Total simulation time: {max(times):.1f} seconds\n")
                f.write(f"- Handover occurred at: {handover_time:.1f} seconds\n\n")
                
                f.write("BEFORE HANDOVER:\n")
                f.write(f"- Average buffer level: {avg_pre_buffer:.1f}%\n")
                f.write(f"- Average video bitrate: {avg_pre_bitrate:.2f} Mbps\n")
                f.write(f"- Stall events: {sum(1 for i, e in enumerate(events) if 'stall' in e.lower() and times[i] < handover_time)}\n\n")
                
                f.write("AFTER HANDOVER:\n")
                f.write(f"- Average buffer level: {avg_post_buffer:.1f}%\n")
                f.write(f"- Average video bitrate: {avg_post_bitrate:.2f} Mbps\n")
                f.write(f"- Stall events: {sum(1 for i, e in enumerate(events) if 'stall' in e.lower() and times[i] >= handover_time)}\n\n")
                
                f.write("IMPACT ANALYSIS:\n")
                f.write(f"- Buffer level change: {buffer_impact:.1f}%\n")
                f.write(f"- Bitrate change: {bitrate_impact:.1f}%\n\n")
                
                f.write("CONCLUSION:\n")
                if buffer_impact < -20 or bitrate_impact < -20:
                    f.write("Handover had a SEVERE negative impact on video streaming quality.\n")
                    f.write("Users would experience significant interruptions in their viewing experience.\n")
                elif buffer_impact < -10 or bitrate_impact < -10:
                    f.write("Handover had a MODERATE negative impact on video streaming quality.\n")
                    f.write("Users would notice quality degradation during the handover period.\n")
                else:
                    f.write("Handover had a MINIMAL impact on video streaming quality.\n")
                    f.write("Users would experience a smooth transition between access points.\n")
            
            info("*** Created QoE report: ./streaming_qoe_report.txt\n")
        
    except Exception as e:
        error(f"*** Error creating visualization: {e}\n")
        import traceback
        traceback.print_exc()

def run_simulation():
    """Run the complete simulation"""
    cleanup()
    info("\n*** Starting Video Streaming Handover Simulation\n")
    info("*** This simplified version generates realistic simulated data\n")
    
    info("\n*** PHASE 1: SIMULATING VIDEO STREAMING WITH HANDOVER\n")
    if simulate_streaming():
        info("\n*** PHASE 2: VISUALIZING STREAMING METRICS\n")
        visualize_metrics()
        
        info("\n*** Simulation completed successfully!\n")
        info("*** Output files:\n")
        info("***   - video_streaming_handover.png (Main visualization)\n")
        info("***   - handover_impact_summary.png (Comparison chart)\n")
        info("***   - streaming_qoe_report.txt (Detailed analysis)\n")
        info("***   - streaming_metrics.txt (Raw data)\n")
        info("***   - handover_events.txt (Event log)\n")
    else:
        error("\n*** Simulation failed\n")

if __name__ == '__main__':
    setLogLevel('info')
    run_simulation()