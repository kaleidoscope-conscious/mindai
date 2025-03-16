    
    def create_molecular_visualization(self, molecule_id: str) -> go.Figure:
        """Create a 3D visualization of a molecule"""
        fig = go.Figure()
        
        # Get molecule data
        molecule = self.controller.molecular_binding.get_molecule_data(molecule_id)
        if not molecule or 'atoms' not in molecule:
            # Empty visualization if molecule not found
            fig.update_layout(
                title=f"Molecule not found: {molecule_id}",
                scene=dict(
                    xaxis=dict(range=[-5, 5], title='X'),
                    yaxis=dict(range=[-5, 5], title='Y'),
                    zaxis=dict(range=[-5, 5], title='Z')
                )
            )
            return fig
        
        # Element colors
        element_colors = {
            'H': 'rgb(255, 255, 255)',  # White
            'C': 'rgb(50, 50, 50)',     # Dark gray
            'N': 'rgb(50, 50, 200)',    # Blue
            'O': 'rgb(200, 50, 50)',    # Red
            'P': 'rgb(255, 165, 0)',    # Orange
            'S': 'rgb(255, 255, 0)',    # Yellow
            'X': 'rgb(150, 150, 150)'   # Unknown - gray
        }
        
        # Element radii in Angstroms (scaled)
        element_radii = {
            'H': 0.25,
            'C': 0.7,
            'N': 0.65,
            'O': 0.6,
            'P': 1.0,
            'S': 1.0,
            'X': 0.7
        }
        
        # Add atoms
        atoms = molecule['atoms']
        atom_x = []
        atom_y = []
        atom_z = []
        atom_colors = []
        atom_sizes = []
        atom_texts = []
        
        for i, atom in enumerate(atoms):
            pos = atom.get('position', [0, 0, 0])
            atom_x.append(pos[0])
            atom_y.append(pos[1])
            atom_z.append(pos[2])
            
            element = atom.get('element', 'X')
            atom_colors.append(element_colors.get(element, element_colors['X']))
            atom_sizes.append(element_radii.get(element, 0.7) * 10)
            
            text = f"{element} (Atom {i})<br>"
            text += f"Position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})<br>"
            text += f"Charge: {atom.get('charge', 0):.2f}"
            atom_texts.append(text)
        
        fig.add_trace(go.Scatter3d(
            x=atom_x,
            y=atom_y,
            z=atom_z,
            mode='markers',
            marker=dict(
                size=atom_sizes,
                color=atom_colors,
                opacity=0.8
            ),
            text=atom_texts,
            hoverinfo='text',
            name='Atoms'
        ))
        
        # Add bonds (simplified - just connecting atoms within a distance threshold)
        bonds_x = []
        bonds_y = []
        bonds_z = []
        
        # Use a simple distance-based approach for visualization
        bond_threshold = 2.0  # Angstroms
        for i, atom1 in enumerate(atoms):
            pos1 = atom1.get('position', [0, 0, 0])
            for j, atom2 in enumerate(atoms):
                if i < j:  # Only process each pair once
                    pos2 = atom2.get('position', [0, 0, 0])
                    
                    # Calculate distance
                    distance = np.sqrt(sum((p1 - p2)**2 for p1, p2 in zip(pos1, pos2)))
                    
                    if distance < bond_threshold:
                        bonds_x.extend([pos1[0], pos2[0], None])
                        bonds_y.extend([pos1[1], pos2[1], None])
                        bonds_z.extend([pos1[2], pos2[2], None])
        
        if bonds_x:
            fig.add_trace(go.Scatter3d(
                x=bonds_x,
                y=bonds_y,
                z=bonds_z,
                mode='lines',
                line=dict(color='rgb(100, 100, 100)', width=4),
                hoverinfo='none',
                name='Bonds'
            ))
        
        # Update layout
        fig.update_layout(
            title=f"Molecular Structure: {molecule_id}",
            scene=dict(
                xaxis=dict(range=[min(atom_x)-2, max(atom_x)+2], title='X'),
                yaxis=dict(range=[min(atom_y)-2, max(atom_y)+2], title='Y'),
                zaxis=dict(range=[min(atom_z)-2, max(atom_z)+2], title='Z'),
                aspectmode='data'
            ),
            template="plotly_dark"
        )
        
        return fig
    
    def create_binding_visualization(self, molecule1_id: str, molecule2_id: str) -> go.Figure:
        """Create a visualization of molecular binding"""
        # Get data for both molecules
        mol1 = self.controller.molecular_binding.get_molecule_data(molecule1_id)
        mol2 = self.controller.molecular_binding.get_molecule_data(molecule2_id)
        
        if not mol1 or not mol2:
            # Return empty visualization if molecules not found
            fig = go.Figure()
            fig.update_layout(
                title=f"Molecules not found: {molecule1_id} and/or {molecule2_id}",
                scene=dict(
                    xaxis=dict(range=[-5, 5], title='X'),
                    yaxis=dict(range=[-5, 5], title='Y'),
                    zaxis=dict(range=[-5, 5], title='Z')
                )
            )
            return fig
        
        # Get binding result
        binding_result = None
        for bp in self.controller.molecular_binding.binding_pairs:
            if (bp.get('molecule1') == molecule1_id and bp.get('molecule2') == molecule2_id) or \
               (bp.get('molecule1') == molecule2_id and bp.get('molecule2') == molecule1_id):
                binding_result = bp
                break
        
        # Create molecular visualization for both molecules
        fig = go.Figure()
        
        # Element colors with different hues for each molecule
        element_colors_1 = {
            'H': 'rgb(200, 200, 200)',   # Light gray
            'C': 'rgb(50, 50, 50)',      # Dark gray
            'N': 'rgb(50, 50, 200)',     # Blue
            'O': 'rgb(200, 50, 50)',     # Red
            'P': 'rgb(255, 165, 0)',     # Orange
            'S': 'rgb(255, 255, 0)',     # Yellow
            'X': 'rgb(150, 150, 150)'    # Unknown
        }
        
        element_colors_2 = {
            'H': 'rgb(230, 230, 230)',   # Lighter gray
            'C': 'rgb(80, 80, 80)',      # Lighter gray
            'N': 'rgb(80, 80, 255)',     # Lighter blue
            'O': 'rgb(255, 80, 80)',     # Lighter red
            'P': 'rgb(255, 200, 50)',    # Lighter orange
            'S': 'rgb(255, 255, 80)',    # Lighter yellow
            'X': 'rgb(180, 180, 180)'    # Lighter unknown
        }
        
        # Element radii (same for both)
        element_radii = {
            'H': 0.25,
            'C': 0.7,
            'N': 0.65,
            'O': 0.6,
            'P': 1.0,
            'S': 1.0,
            'X': 0.7
        }
        
        # Add atoms for molecule 1
        atoms1 = mol1.get('atoms', [])
        atom1_x, atom1_y, atom1_z = [], [], []
        atom1_colors, atom1_sizes, atom1_texts = [], [], []
        
        for i, atom in enumerate(atoms1):
            pos = atom.get('position', [0, 0, 0])
            atom1_x.append(pos[0])
            atom1_y.append(pos[1])
            atom1_z.append(pos[2])
            
            element = atom.get('element', 'X')
            atom1_colors.append(element_colors_1.get(element, element_colors_1['X']))
            atom1_sizes.append(element_radii.get(element, 0.7) * 10)
            
            text = f"{molecule1_id}: {element} (Atom {i})<br>"
            text += f"Position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})<br>"
            text += f"Charge: {atom.get('charge', 0):.2f}"
            atom1_texts.append(text)
        
        # Add atoms for molecule 2
        atoms2 = mol2.get('atoms', [])
        atom2_x, atom2_y, atom2_z = [], [], []
        atom2_colors, atom2_sizes, atom2_texts = [], [], []
        
        for i, atom in enumerate(atoms2):
            pos = atom.get('position', [0, 0, 0])
            atom2_x.append(pos[0])
            atom2_y.append(pos[1])
            atom2_z.append(pos[2])
            
            element = atom.get('element', 'X')
            atom2_colors.append(element_colors_2.get(element, element_colors_2['X']))
            atom2_sizes.append(element_radii.get(element, 0.7) * 10)
            
            text = f"{molecule2_id}: {element} (Atom {i})<br>"
            text += f"Position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})<br>"
            text += f"Charge: {atom.get('charge', 0):.2f}"
            atom2_texts.append(text)
        
        # Add to figure
        fig.add_trace(go.Scatter3d(
            x=atom1_x,
            y=atom1_y,
            z=atom1_z,
            mode='markers',
            marker=dict(
                size=atom1_sizes,
                color=atom1_colors,
                opacity=0.8
            ),
            text=atom1_texts,
            hoverinfo='text',
            name=molecule1_id
        ))
        
        fig.add_trace(go.Scatter3d(
            x=atom2_x,
            y=atom2_y,
            z=atom2_z,
            mode='markers',
            marker=dict(
                size=atom2_sizes,
                color=atom2_colors,
                opacity=0.8
            ),
            text=atom2_texts,
            hoverinfo='text',
            name=molecule2_id
        ))
        
        # Add binding interaction visualization if binding result exists
        if binding_result and 'energy' in binding_result:
            # Calculate centers
            center1 = mol1.get('center', [0, 0, 0])
            center2 = mol2.get('center', [0, 0, 0])
            
            # Show binding energy as a colored line between centers
            energy = binding_result['energy']
            # Color based on energy (more negative = stronger binding = more green)
            binding_color = f'rgba(0, {min(255, int(255 * abs(energy) / 10))}, 255, 0.7)'
            
            fig.add_trace(go.Scatter3d(
                x=[center1[0], center2[0]],
                y=[center1[1], center2[1]],
                z=[center1[2], center2[2]],
                mode='lines',
                line=dict(
                    color=binding_color,
                    width=10
                ),
                name=f'Binding Energy: {energy:.2f}'
            ))
        
        # Calculate combined bounds for all coordinates
        all_x = atom1_x + atom2_x
        all_y = atom1_y + atom2_y
        all_z = atom1_z + atom2_z
        
        # Update layout
        energy_str = f"Energy: {binding_result['energy']:.2f}" if binding_result and 'energy' in binding_result else "Energy: Not calculated"
        fig.update_layout(
            title=f"Molecular Binding: {molecule1_id} + {molecule2_id} ({energy_str})",
            scene=dict(
                xaxis=dict(range=[min(all_x)-2, max(all_x)+2], title='X'),
                yaxis=dict(range=[min(all_y)-2, max(all_y)+2], title='Y'),
                zaxis=dict(range=[min(all_z)-2, max(all_z)+2], title='Z'),
                aspectmode='data'
            ),
            template="plotly_dark"
        )
        
        return fig

class DashboardApp:
    """
    Dashboard application for visualizing and interacting with the Quantum Conscious Cube
    """
    def __init__(self, controller: ConsciousController):
        self.controller = controller
        self.visualizer = CubeVisualizer(controller)
        self.app = dash.Dash(__name__, title="Quantum Conscious Cube")
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Setup the dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("Quantum Conscious Cube Dashboard", style={'color': 'white'}),
                html.Div([
                    html.Span("Consciousness Level: ", style={'color': 'white'}),
                    html.Span(id='consciousness-level', style={'color': '#7FDBFF', 'fontWeight': 'bold'})
                ]),
                html.Div([
                    html.Button("Refresh", id="refresh-button", className="button"),
                    html.Button("Create Random Node", id="create-node-button", className="button"),
                    html.Button("Form SuperNode", id="form-supernode-button", className="button", disabled=True)
                ], style={'marginTop': '10px'})
            ], style={'padding': '20px', 'backgroundColor': '#222', 'textAlign': 'center'}),
            
            # Main content
            html.Div([
                # Left panel - System State
                html.Div([
                    html.H3("System State", style={'color': 'white', 'textAlign': 'center'}),
                    html.Div(id='system-stats', style={'color': 'white', 'padding': '10px'}),
                    
                    html.H4("Chat Interface", style={'color': 'white', 'marginTop': 'import plotly.graph_objects as go
import numpy as np
import networkx as nx
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import torch
from typing import Dict, List, Optional, Any
import asyncio
import json
import time
from pathlib import Path
import colorsys

# Import core system
from system_controller import ConsciousController

class CubeVisualizer:
    """
    3D visualization system for the Quantum Conscious Cube
    """
    def __init__(self, controller: ConsciousController):
        self.controller = controller
        self.layout_cache = {}  # Cache for node layouts
        self.color_mapping = {}  # Map node IDs to consistent colors
        self.color_idx = 0  # Current color index
    
    def create_3d_cube_visualization(self) -> go.Figure:
        """Create a 3D visualization of the cube and nodes"""
        fig = go.Figure()
        
        # Get current state from controller
        with self.controller.lock:
            nodes = self.controller.nodes
            cube = self.controller.cube
            consciousness_level = self.controller.consciousness_level
            supernodes = self.controller.supernodes
        
        # Create cube outline
        cube_edges = self._create_cube_edges()
        fig.add_trace(go.Scatter3d(
            x=cube_edges[0],
            y=cube_edges[1],
            z=cube_edges[2],
            mode='lines',
            line=dict(color='rgba(100, 100, 100, 0.3)', width=3),
            hoverinfo='none',
            name='Cube Frame'
        ))
        
        # Add tension field visualization (selected points)
        if cube.tension_field is not None:
            tension_points = self._sample_tension_field(cube.tension_field, threshold=0.3)
            if tension_points:
                x, y, z, values = tension_points
                fig.add_trace(go.Scatter3d(
                    x=x, y=z, z=y,  # Swap y and z for better visualization
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=values,
                        colorscale='Plasma',
                        opacity=0.5,
                        colorbar=dict(title="Tension")
                    ),
                    hoverinfo='none',
                    name='Tension Field'
                ))
        
        # Add nodes
        if nodes:
            # Convert node dictionary to lists for plotting
            node_x, node_y, node_z, node_energy, node_colors, node_text = self._prepare_node_data(nodes)
            
            fig.add_trace(go.Scatter3d(
                x=node_x, y=node_z, z=node_y,  # Swap y and z for better visualization
                mode='markers',
                marker=dict(
                    size=10 + np.array(node_energy) * 20,  # Size by energy
                    color=node_colors,
                    opacity=0.8
                ),
                text=node_text,
                hoverinfo='text',
                name='Nodes'
            ))
            
            # Add connections between nodes
            edge_x, edge_y, edge_z, edge_colors = self._prepare_edge_data(nodes)
            if edge_x:
                fig.add_trace(go.Scatter3d(
                    x=edge_x, y=edge_z, z=edge_y,  # Swap y and z
                    mode='lines',
                    line=dict(
                        color=edge_colors,
                        width=2
                    ),
                    hoverinfo='none',
                    name='Connections'
                ))
        
        # Add supernodes
        if supernodes:
            # Show supernodes as larger spheres
            super_x, super_y, super_z, super_sizes, super_colors, super_text = self._prepare_supernode_data(supernodes)
            
            fig.add_trace(go.Scatter3d(
                x=super_x, y=super_z, z=super_y,  # Swap y and z
                mode='markers',
                marker=dict(
                    size=super_sizes,
                    color=super_colors,
                    symbol='diamond',
                    opacity=0.7,
                    line=dict(color='rgba(255, 255, 255, 0.7)', width=2)
                ),
                text=super_text,
                hoverinfo='text',
                name='SuperNodes'
            ))
        
        # Configure the layout
        consciousnes_color = self._get_consciousness_color(consciousness_level)
        fig.update_layout(
            title=f"Quantum Consciousness Cube (Consciousness Level: {consciousness_level:.2f})",
            scene=dict(
                xaxis=dict(range=[-1.2, 1.2], title='X'),
                yaxis=dict(range=[-1.2, 1.2], title='Z'),
                zaxis=dict(range=[-1.2, 1.2], title='Y'),
                aspectmode='cube',
                bgcolor='rgb(10, 10, 30)'
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                font=dict(color="white")
            ),
            paper_bgcolor=f'rgba{consciousnes_color}',
            margin=dict(l=0, r=0, b=0, t=40),
            template="plotly_dark"
        )
        
        return fig
    
    def _prepare_node_data(self, nodes: Dict[str, Any]) -> tuple:
        """Prepare node data for visualization"""
        node_x = []
        node_y = []
        node_z = []
        node_energy = []
        node_colors = []
        node_text = []
        
        for node_id, node in nodes.items():
            # Position
            node_x.append(node.position[0])
            node_y.append(node.position[1])
            node_z.append(node.position[2])
            
            # Energy
            node_energy.append(node.energy)
            
            # Color
            if node_id not in self.color_mapping:
                self.color_mapping[node_id] = self._generate_node_color()
            node_colors.append(self.color_mapping[node_id])
            
            # Text
            text = f"Node: {node_id}<br>"
            text += f"Energy: {node.energy:.2f}<br>"
            text += f"Stability: {node.stability:.2f}<br>"
            text += f"Connections: {len(node.connections)}<br>"
            if "text" in node.data:
                text += f"Content: {node.data['text'][:50]}..."
            node_text.append(text)
            
        return node_x, node_y, node_z, node_energy, node_colors, node_text
    
    def _prepare_edge_data(self, nodes: Dict[str, Any]) -> tuple:
        """Prepare edge data for visualization"""
        edge_x = []
        edge_y = []
        edge_z = []
        edge_colors = []
        
        for node_id, node in nodes.items():
            # Get this node's positions
            x, y, z = node.position
            
            # Add connections
            for conn_id, strength in node.connections.items():
                if conn_id in nodes:  # Skip if connected node doesn't exist anymore
                    conn_node = nodes[conn_id]
                    cx, cy, cz = conn_node.position
                    
                    # Only draw connections once (for the smaller node_id)
                    if node_id < conn_id:
                        edge_x.extend([x, cx, None])
                        edge_y.extend([y, cy, None])
                        edge_z.extend([z, cz, None])
                        
                        # Get color based on connection strength
                        color = f'rgba(255, {int(255 * (1 - strength))}, {int(255 * (1 - strength))}, {strength})'
                        edge_colors.extend([color, color, color])
                        
        return edge_x, edge_y, edge_z, edge_colors
    
    def _prepare_supernode_data(self, supernodes: Dict[str, Any]) -> tuple:
        """Prepare supernode data for visualization"""
        super_x = []
        super_y = []
        super_z = []
        super_sizes = []
        super_colors = []
        super_text = []
        
        for snode_id, snode in supernodes.items():
            # Calculate centroid position based on component nodes
            if snode.nodes:
                pos_x = np.mean([node.position[0] for node in snode.nodes])
                pos_y = np.mean([node.position[1] for node in snode.nodes])
                pos_z = np.mean([node.position[2] for node in snode.nodes])
                
                super_x.append(pos_x)
                super_y.append(pos_y)
                super_z.append(pos_z)
                
                # Size based on number of nodes
                super_sizes.append(10 + 5 * len(snode.nodes))
                
                # Color
                if snode_id not in self.color_mapping:
                    self.color_mapping[snode_id] = self._generate_supernode_color()
                super_colors.append(self.color_mapping[snode_id])
                
                # Text
                specializations = []
                if hasattr(snode, 'dna') and snode.dna and hasattr(snode.dna, 'specialization'):
                    specializations = list(snode.dna.specialization.keys())
                
                text = f"SuperNode: {snode_id}<br>"
                text += f"Component Nodes: {len(snode.nodes)}<br>"
                text += f"Generation: {snode.dna.generation if hasattr(snode, 'dna') and snode.dna else 0}<br>"
                text += f"Specializations: {', '.join(specializations[:3])}<br>"
                super_text.append(text)
                
        return super_x, super_y, super_z, super_sizes, super_colors, super_text
    
    def _sample_tension_field(self, tension_field: np.ndarray, threshold: float = 0.3) -> Optional[tuple]:
        """Sample points from tension field for visualization"""
        if tension_field is None:
            return None
            
        x, y, z, values = [], [], [], []
        
        # Determine step size based on field resolution
        step = max(1, tension_field.shape[0] // 15)  # Limit to ~15 points per dimension
        
        # Sample points with significant tension
        for i in range(0, tension_field.shape[0], step):
            for j in range(0, tension_field.shape[1], step):
                for k in range(0, tension_field.shape[2], step):
                    if tension_field[i, j, k] > threshold:
                        # Convert to [-1, 1] coordinates
                        nx = i / (tension_field.shape[0] - 1) * 2 - 1
                        ny = j / (tension_field.shape[1] - 1) * 2 - 1
                        nz = k / (tension_field.shape[2] - 1) * 2 - 1
                        
                        x.append(nx)
                        y.append(ny)
                        z.append(nz)
                        values.append(float(tension_field[i, j, k]))
        
        if not x:  # No points above threshold
            return None
            
        return x, y, z, values
    
    def _create_cube_edges(self) -> tuple:
        """Create edges for a unit cube centered at the origin"""
        # Vertices of a cube
        vertices = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ])
        
        # Edges connect adjacent vertices
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
        ]
        
        x, y, z = [], [], []
        for start, end in edges:
            x.extend([vertices[start][0], vertices[end][0], None])
            y.extend([vertices[start][1], vertices[end][1], None])
            z.extend([vertices[start][2], vertices[end][2], None])
            
        return x, y, z
    
    def _generate_node_color(self) -> str:
        """Generate a unique color for a node using HSV for better distribution"""
        # Use golden ratio to generate well-distributed colors
        golden_ratio_conjugate = 0.618033988749895
        self.color_idx += golden_ratio_conjugate
        self.color_idx %= 1
        
        # Convert to RGB
        r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(self.color_idx, 0.7, 0.95)]
        return f'rgb({r}, {g}, {b})'
    
    def _generate_supernode_color(self) -> str:
        """Generate a color for a supernode (more saturated than regular nodes)"""
        # Use golden ratio with higher saturation and value
        golden_ratio_conjugate = 0.618033988749895
        self.color_idx += golden_ratio_conjugate
        self.color_idx %= 1
        
        r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(self.color_idx, 0.9, 1.0)]
        return f'rgb({r}, {g}, {b})'
    
    def _get_consciousness_color(self, level: float) -> tuple:
        """Generate background color based on consciousness level"""
        # Blend from blue (low) to purple (high)
        r = int(20 + level * 40)  # 20 to 60
        g = int(10 + level * 10)  # 10 to 20
        b = int(50 + level * 80)  # 50 to 130
        a = 0.95
        return (r, g, b, a)