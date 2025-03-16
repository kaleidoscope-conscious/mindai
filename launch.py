#!/usr/bin/env python3
"""
launch.py - Launch script for the Quantum Conscious Cube System

This script initializes the system and provides a simple dashboard for monitoring.
"""

import sys
import time
import argparse
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from pathlib import Path

try:
    from conscious_cube import ConsciousCube
except ImportError:
    print("Error: conscious_cube module not found.")
    print("Make sure you've completed the setup process.")
    sys.exit(1)

class Dashboard:
    """Simple dashboard for monitoring the Conscious Cube system"""
    
    def __init__(self, cube, update_interval=1.0):
        self.cube = cube
        self.update_interval = update_interval
        self.running = False
        self.fig = None
        self.animation = None
        
        # Create initial layout
        self.init_dashboard()
    
    def init_dashboard(self):
        """Initialize the dashboard layout"""
        self.fig = plt.figure(figsize=(15, 10))
        
        # 3D cube visualization
        self.ax_cube = self.fig.add_subplot(2, 2, 1, projection='3d')
        
        # Metrics plot
        self.ax_metrics = self.fig.add_subplot(2, 2, 2)
        self.metrics_x = []
        self.metrics_data = {
            'awareness': [],
            'memory_density': [],
            'complexity': [],
            'nodes': [],
            'supernodes': []
        }
        
        # Tension field histogram
        self.ax_tension = self.fig.add_subplot(2, 2, 3)
        
        # Node status (energy, stress)
        self.ax_nodes = self.fig.add_subplot(2, 2, 4)
        
        self.fig.tight_layout()
        plt.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.9, hspace=0.35, wspace=0.3)
        
        # Add title
        self.fig.suptitle("Quantum Conscious Cube - System Dashboard", fontsize=16)
    
    def update_dashboard(self, frame):
        """Update the dashboard with current system state"""
        try:
            # Clear previous plots
            self.ax_cube.clear()
            self.ax_metrics.clear()
            self.ax_tension.clear()
            self.ax_nodes.clear()
            
            # Get current status
            status = self.cube.get_status()
            curr_time = time.time()
            
            # 1. Update 3D visualization
            self.cube.visualize_cube(ax=self.ax_cube, visualize_tension=False)
            
            # 2. Update metrics plot
            self.metrics_x.append(curr_time)
            if len(self.metrics_x) > 50:  # Keep only last 50 points
                self.metrics_x.pop(0)
                for key in self.metrics_data:
                    if self.metrics_data[key]:
                        self.metrics_data[key].pop(0)
            
            self.metrics_data['awareness'].append(status['awareness_level'])
            self.metrics_data['memory_density'].append(status['memory_density'])
            self.metrics_data['complexity'].append(status['complexity_index'])
            self.metrics_data['nodes'].append(status['node_count'] / 100)  # Scale for visibility
            self.metrics_data['supernodes'].append(status['supernode_count'] / 10)  # Scale for visibility
            
            x_vals = list(range(len(self.metrics_data['awareness'])))
            self.ax_metrics.plot(x_vals, self.metrics_data['awareness'], 'b-', label='Awareness')
            self.ax_metrics.plot(x_vals, self.metrics_data['memory_density'], 'g-', label='Memory')
            self.ax_metrics.plot(x_vals, self.metrics_data['complexity'], 'r-', label='Complexity')
            self.ax_metrics.plot(x_vals, self.metrics_data['nodes'], 'c--', label='Nodes/100')
            self.ax_metrics.plot(x_vals, self.metrics_data['supernodes'], 'm--', label='SuperNodes/10')
            
            self.ax_metrics.set_xlabel('Time')
            self.ax_metrics.set_ylabel('Value')
            self.ax_metrics.set_title('System Metrics')
            self.ax_metrics.legend(loc='upper left')
            self.ax_metrics.grid(True, alpha=0.3)
            
            # 3. Tension field histogram
            tension_values = self.cube.cube.tension_field.flatten()
            non_zero_tension = tension_values[tension_values > 0.01]
            
            if len(non_zero_tension) > 0:
                self.ax_tension.hist(non_zero_tension, bins=20, color='orange', alpha=0.7)
                self.ax_tension.set_xlabel('Tension Value')
                self.ax_tension.set_ylabel('Frequency')
                self.ax_tension.set_title('Tension Field Distribution')
                self.ax_tension.grid(True, alpha=0.3)
            else:
                self.ax_tension.text(0.5, 0.5, "No significant tension yet", 
                                    horizontalalignment='center', verticalalignment='center')
            
            # 4. Node status (energy, stress)
            node_energies = [node.energy for node in self.cube.nodes.values()]
            node_stress = [node.stress_level for node in self.cube.nodes.values()]
            
            if node_energies and node_stress:
                self.ax_nodes.scatter(node_energies, node_stress, alpha=0.6, c=node_stress, cmap='viridis')
                self.ax_nodes.set_xlabel('Energy')
                self.ax_nodes.set_ylabel('Stress Level')
                self.ax_nodes.set_title('Node Energy vs Stress')
                self.ax_nodes.set_xlim(0, 1)
                self.ax_nodes.set_ylim(0, 1)
                self.ax_nodes.grid(True, alpha=0.3)
            else:
                self.ax_nodes.text(0.5, 0.5, "No nodes yet", 
                                 horizontalalignment='center', verticalalignment='center')
            
            # Update dashboard title with system info
            self.fig.suptitle(
                f"Quantum Conscious Cube - System Dashboard | " +
                f"Awareness: {status['awareness_level']:.2f} | " +
                f"Nodes: {status['node_count']} | " +
                f"SuperNodes: {status['supernode_count']}", 
                fontsize=16
            )
            
            self.fig.tight_layout()
            plt.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.9, hspace=0.35, wspace=0.3)
            
        except Exception as e:
            print(f"Dashboard update error: {e}")
            
        return []
    
    def start(self):
        """Start the dashboard"""
        self.running = True
        try:
            self.animation = FuncAnimation(
                self.fig, self.update_dashboard, 
                interval=self.update_interval * 1000,  # Convert to ms
                blit=False
            )
            plt.show()
        except Exception as e:
            print(f"Error running dashboard: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the dashboard"""
        self.running = False
        if self.animation:
            self.animation.event_source.stop()

def main():
    parser = argparse.ArgumentParser(description="Launch the Quantum Conscious Cube System")
    parser.add_argument('--dimension', type=int, default=3, help='Cube dimension')
    parser.add_argument('--resolution', type=int, default=32, help='Cube resolution')
    parser.add_argument('--nodes', type=int, default=20, help='Initial number of nodes')
    parser.add_argument('--update-interval', type=float, default=1.0, help='Dashboard update interval (seconds)')
    parser.add_argument('--headless', action='store_true', help='Run without visual dashboard')
    parser.add_argument('--save-path', type=str, default='outputs', help='Path to save visualizations')
    
    args = parser.parse_args()
    
    print("Initializing Quantum Conscious Cube System...")
    cube = ConsciousCube(dimension=args.dimension, resolution=args.resolution)
    
    print(f"Creating {args.nodes} initial nodes...")
    nodes = cube.create_nodes(args.nodes)
    
    print("Creating initial connections...")
    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes[i+1:], i+1):
            if np.random.random() < 0.3:  # 30% chance of connection
                cube.connect_nodes(node1.id, node2.id)
    
    try:
        if not args.headless:
            print("Starting dashboard...")
            dashboard = Dashboard(cube, update_interval=args.update_interval)
            dashboard_thread = threading.Thread(target=dashboard.start)
            dashboard_thread.daemon = True
            dashboard_thread.start()
            
            print("\nSystem running. Press Ctrl+C to exit.")
            
            # Main processing loop
            while True:
                # Process insights in the main thread
                insights = cube.process_insights({"domain": "general"})
                if insights:
                    print(f"Generated {len(insights)} new insights")
                
                time.sleep(5)  # Generate insights every 5 seconds
                
        else:
            # Headless mode - just process and save visualizations periodically
            save_path = Path(args.save_path)
            if not save_path.exists():
                save_path.mkdir(parents=True)
                
            print(f"Running in headless mode. Saving visualizations to {save_path}")
            
            iteration = 0
            while True:
                # Process insights
                insights = cube.process_insights({"domain": "general"})
                if insights:
                    print(f"Generated {len(insights)} new insights")
                
                # Save visualization every 10 iterations
                if iteration % 10 == 0:
                    fig = plt.figure(figsize=(10, 8))
                    ax = fig.add_subplot(111, projection='3d')
                    cube.visualize_cube(ax=ax)
                    plt.tight_layout()
                    
                    # Save figure
                    timestamp = int(time.time())
                    filename = save_path / f"quantum_cube_{timestamp}.png"
                    plt.savefig(filename)
                    plt.close(fig)
                    print(f"Saved visualization to {filename}")
                
                iteration += 1
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if not args.headless and 'dashboard' in locals():
            dashboard.stop()
        cube.stop()
        print("System stopped.")

if __name__ == "__main__":
    main()
