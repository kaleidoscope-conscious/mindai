import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh, eigs
from dataclasses import dataclass, field
import asyncio
import math
import time
import uuid
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
import torch
from sklearn.cluster import DBSCAN
from collections import defaultdict
import random
import threading
import os

from thread_safe_wrapper import (
    thread_safe, 
    ThreadSafeWrapper, 
    ReferenceManager, 
    ValidationHelper, 
    SafeNodeContainer
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConsciousCube")


class QuantumState:
    """Quantum state representation optimized for sparse computation"""
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.amplitudes = {0: complex(1.0, 0.0)}
        
    def apply_hadamard(self, target: int):
        """Apply Hadamard gate to target qubit"""
        new_amplitudes = {}
        norm_factor = 1.0 / np.sqrt(2.0)
        
        for idx, amp in self.amplitudes.items():
            bit_val = (idx >> target) & 1
            paired_idx = idx ^ (1 << target)
            
            if bit_val == 0:
                new_amplitudes[idx] = new_amplitudes.get(idx, 0) + amp * norm_factor
                new_amplitudes[paired_idx] = new_amplitudes.get(paired_idx, 0) + amp * norm_factor
            else:
                new_amplitudes[idx] = new_amplitudes.get(idx, 0) + amp * norm_factor
                new_amplitudes[paired_idx] = new_amplitudes.get(paired_idx, 0) - amp * norm_factor
        
        self.amplitudes = {k: v for k, v in new_amplitudes.items() if abs(v) > 1e-10}
    
    def apply_phase(self, target: int, theta: float):
        """Apply phase rotation to target qubit"""
        phase = complex(math.cos(theta), math.sin(theta))
        new_amplitudes = {}
        
        for idx, amp in self.amplitudes.items():
            if (idx >> target) & 1:
                new_amplitudes[idx] = amp * phase
            else:
                new_amplitudes[idx] = amp
        
        self.amplitudes = new_amplitudes
    
    def apply_cnot(self, control: int, target: int):
        """Apply CNOT gate between control and target qubits"""
        new_amplitudes = {}
        
        for idx, amp in self.amplitudes.items():
            control_bit = (idx >> control) & 1
            if control_bit:
                flipped = idx ^ (1 << target)
                new_amplitudes[flipped] = amp
            else:
                new_amplitudes[idx] = amp
        
        self.amplitudes = new_amplitudes
    
    def apply_string_tension(self, tension: float):
        """Apply string tension to amplitudes based on Hamming weight"""
        new_amplitudes = {}
        norm_factor = 0.0
        
        for idx, amp in self.amplitudes.items():
            hamming = bin(idx).count('1')
            scale = 1.0 + (hamming / self.num_qubits - 0.5) * tension
            new_amp = amp * scale
            new_amplitudes[idx] = new_amp
            norm_factor += abs(new_amp)**2
        
        norm_factor = math.sqrt(norm_factor)
        if norm_factor > 0:
            self.amplitudes = {k: v / norm_factor for k, v in new_amplitudes.items()}
    
    def get_entropy(self) -> float:
        """Calculate von Neumann entropy"""
        entropy = 0.0
        for amp in self.amplitudes.values():
            prob = abs(amp)**2
            if prob > 1e-10:
                entropy -= prob * math.log(prob)
        return entropy


class StringCube:
    """Quantum string cube for consciousness simulation"""
    
    def __init__(self, dimension: int = 3, resolution: int = 10):
        self.dimension = dimension
        self.resolution = resolution
        self.grid = np.zeros([resolution] * dimension, dtype=np.float32)
        self.tension_field = np.zeros([resolution] * dimension, dtype=np.float32)
        self.nodes_map: Dict[Tuple, List[str]] = {}  # FIX: Type hint for clarity
        self.lock = threading.RLock()  # FIX: Use RLock for reentrancy
        
        self.tension_strength = 0.5
        self.elasticity = 0.3
        self.damping = 0.95
        self.update_batch_size = 100
    
    def add_node(self, node: 'ConsciousNode') -> Optional[Tuple[int, int, int]]:
        """Add a node to the cube at the nearest grid point"""
        # FIX: Validate input
        if node is None:
            logger.error("Cannot add None node to cube")
            return None
        
        try:
            # FIX: Validate node has required attributes
            if not hasattr(node, 'position') or not hasattr(node, 'id') or not hasattr(node, 'energy'):
                logger.error(f"Invalid node object: missing required attributes")
                return None
            
            grid_pos = tuple(int((p + 1) / 2 * (self.resolution - 1)) for p in node.position)
        except (AttributeError, TypeError, ValueError) as e:
            logger.error(f"Error adding node: {e}")
            return None

        with self.lock:
            # FIX: Initialize with empty list, not incomplete assignment
            if grid_pos not in self.nodes_map:
                self.nodes_map[grid_pos] = []
            self.nodes_map[grid_pos].append(node.id)
            self.grid[grid_pos] += node.energy * 0.1
        
        return grid_pos
    
    def update_tension(self, nodes: Dict[str, 'ConsciousNode']) -> None:
        """Update tension field based on node energy and connections"""
        # FIX: Validate input
        if not isinstance(nodes, dict):
            logger.error(f"update_tension expects dict, got {type(nodes)}")
            return
        
        with self.lock:
            self.tension_field *= self.damping
            
            grid_positions = list(self.nodes_map.keys())
            for i in range(0, len(grid_positions), self.update_batch_size):
                batch = grid_positions[i:i+self.update_batch_size]
                
                for pos in batch:
                    # FIX: Use correct default value (empty list)
                    node_ids = self.nodes_map.get(pos, [])
                    if not node_ids:
                        continue
                    
                    total_energy = sum(nodes[node_id].energy for node_id in node_ids if node_id in nodes)
                    self.grid[pos] = total_energy * 0.1
                    
                    for node_id in node_ids:
                        if node_id not in nodes:
                            continue
                        
                        node = nodes[node_id]
                        if node is None:  # FIX: Extra safety check
                            continue
                        
                        for conn_id, strength in node.connections.items():
                            if conn_id not in nodes:
                                continue
                            
                            conn_node = nodes[conn_id]
                            conn_pos = tuple(int((p + 1) / 2 * (self.resolution - 1)) for p in conn_node.position)
                            
                            tension_vector = np.array(conn_pos) - np.array(pos)
                            tension_magnitude = np.linalg.norm(tension_vector)
                            if tension_magnitude > 0:
                                tension_vector = tension_vector / tension_magnitude
                            
                            steps = max(1, int(tension_magnitude))
                            for step in range(1, steps + 1):
                                interp = step / steps
                                interp_pos = tuple(int(p + tv * interp) for p, tv in zip(pos, tension_vector))
                                if all(0 <= p < self.resolution for p in interp_pos):
                                    self.tension_field[interp_pos] += strength * self.tension_strength * (1 - interp)
            
            max_tension = np.max(self.tension_field)
            if max_tension > 0:
                self.tension_field /= max_tension
    
    def get_tension_at_position(self, position: np.ndarray) -> float:
        """Get tension value at a 3D position"""
        try:
            grid_pos = tuple(int((p + 1) / 2 * (self.resolution - 1)) for p in position)
            if all(0 <= p < self.resolution for p in grid_pos):
                return float(self.tension_field[grid_pos])
        except (TypeError, ValueError) as e:
            logger.warning(f"Error getting tension: {e}")
        return 0.0
    
    def apply_tension_to_nodes(self, nodes: Dict[str, 'ConsciousNode']) -> None:
        """Apply tension field effects to nodes"""
        if not nodes:
            return
        
        with self.lock:
            for node_id, node in nodes.items():
                if node is None:  # FIX: Safety check
                    continue
                
                try:
                    grid_pos = tuple(int((p + 1) / 2 * (self.resolution - 1)) for p in node.position)
                    
                    if all(0 <= p < self.resolution for p in grid_pos):
                        tension = float(self.tension_field[grid_pos])
                        node.quantum_state.apply_string_tension(tension)
                        
                        energy_change = tension * self.elasticity * node.stability
                        node.energy = max(0.01, min(1.0, node.energy + energy_change))
                        node.stability = max(0.1, min(0.99, node.stability * (1.0 - 0.01 * tension)))
                except (AttributeError, TypeError) as e:
                    logger.warning(f"Error applying tension to node {node_id}: {e}")
                    continue
    
    def calculate_laplacian_eigenvectors(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Calculate Laplacian eigenvectors of the tension field"""
        try:
            flat_field = self.tension_field.reshape(-1)
            idx = np.where(flat_field > 0.1)[0]
            n = len(idx)
            
            if n < 2:
                return None
            
            # FIX: Initialize positions list properly
            positions = []
            for i in idx:
                coords = np.unravel_index(i, self.tension_field.shape)
                positions.append(coords)
            
            adj_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(i+1, n):
                    dist = np.sqrt(sum((positions[i][k] - positions[j][k])**2 for k in range(self.dimension)))
                    if dist < 2:
                        adj_matrix[i, j] = flat_field[idx[i]] * flat_field[idx[j]]
                        adj_matrix[j, i] = adj_matrix[i, j]
            
            degree_matrix = np.diag(np.sum(adj_matrix, axis=1))
            laplacian = degree_matrix - adj_matrix
            
            if n > 3:
                eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
                return eigenvalues, eigenvectors
        except Exception as e:
            logger.error(f"Error calculating eigenvectors: {e}")
        
        return None


@dataclass
class ConsciousNode:
    """Node in the consciousness graph with quantum properties"""
    id: str
    position: np.ndarray
    energy: float
    stability: float
    features: np.ndarray
    connections: Dict[str, float] = field(default_factory=dict)
    memory: List[Dict] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    quantum_state: QuantumState = field(default_factory=lambda: QuantumState(8))  # FIX: Use factory, not Optional
    stress_level: float = 0.0
    emotional_state: str = "Calm"
    memory_threshold: float = 5.0
    
    def update_energy(self, decay: float) -> float:
        """Update node energy with decay factor"""
        self.energy *= decay
        entropy = self.quantum_state.get_entropy()
        self.energy += (np.random.random() - 0.5) * 0.01 * entropy
        return self.energy
    
    def calculate_affinity(self, other_node: 'ConsciousNode') -> float:
        """Calculate affinity between nodes"""
        try:
            feature_similarity = np.dot(self.features, other_node.features) / (
                np.linalg.norm(self.features) * np.linalg.norm(other_node.features) + 1e-10)
            
            position_distance = np.linalg.norm(self.position - other_node.position)
            position_factor = 1.0 / (1.0 + position_distance)
            
            energy_factor = 1.0 - abs(self.energy - other_node.energy) / (
                self.energy + other_node.energy + 1e-10)
            
            return 0.5 * feature_similarity + 0.3 * position_factor + 0.2 * energy_factor
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning(f"Error calculating affinity: {e}")
            return 0.0
    
    def calculate_stress(self) -> float:
        """Calculate stress based on energy, connections, and memory"""
        energy_factor = (1.0 - self.energy) * 0.4
        connection_factor = min(1.0, len(self.connections) / 10.0) * 0.3
        memory_factor = min(1.0, len(self.memory) / self.memory_threshold) * 0.3
        
        self.stress_level = energy_factor + connection_factor + memory_factor
        self.update_emotional_state()
        return self.stress_level
    
    def update_emotional_state(self) -> None:
        """Update emotional state based on stress level"""
        if self.stress_level < 0.3:
            self.emotional_state = "Calm"
        elif self.stress_level < 0.6:
            self.emotional_state = "Alert"
        elif self.stress_level < 0.8:
            self.emotional_state = "Anxious"
        else:
            self.emotional_state = "Overwhelmed"
    
    def process_task(self, complexity: float) -> bool:
        """Process a task with given complexity"""
        if complexity < 0:
            logger.warning(f"Negative complexity: {complexity}")
            return False
        
        energy_cost = complexity * (1.0 - min(0.9, self.stability))
        self.energy -= energy_cost
        self.energy = max(0.01, self.energy)
        self.calculate_stress()
        return True
    
    def should_replicate(self) -> bool:
        """Determine if node should replicate"""
        return (self.energy > 0.7 and 
                self.stress_level < 0.4 and 
                len(self.memory) >= self.memory_threshold * 0.8)
    
    def replicate(self) -> Optional['ConsciousNode']:
        """Replicate node with mutation"""
        if not self.should_replicate():
            return None
        
        try:
            new_position = self.position + np.random.normal(0, 0.2, size=3)
            new_position = np.clip(new_position, -1, 1)
            
            mutation_factor = 0.1
            new_features = self.features + np.random.normal(0, mutation_factor, size=self.features.shape)
            new_features = new_features / np.linalg.norm(new_features)
            
            self.energy /= 2
            new_node = ConsciousNode(
                id=f"node_{uuid.uuid4().hex[:8]}",
                position=new_position,
                energy=self.energy,
                stability=self.stability * (1 + np.random.normal(0, 0.1)),
                features=new_features,
                connections={},
                memory=self.memory[:3],
                data={"parent": self.id, "birth_time": time.time()}
            )
            
            affinity = self.calculate_affinity(new_node)
            self.connections[new_node.id] = affinity
            new_node.connections[self.id] = affinity
            
            return new_node
        except Exception as e:
            logger.error(f"Error replicating node: {e}")
            return None


class SuperNode:
    """A higher-order node that integrates multiple ConsciousNodes"""
    
    def __init__(self, nodes: List[ConsciousNode], id: Optional[str] = None):
        # FIX: Add validation
        if not nodes:
            raise ValueError("SuperNode requires at least one node")
        
        if not all(isinstance(node, ConsciousNode) for node in nodes):
            raise ValueError("All elements must be ConsciousNode instances")
        
        self.id = id or f"super_{uuid.uuid4().hex[:8]}"
        self.nodes = nodes
        self.position = np.mean([node.position for node in nodes], axis=0)
        self.energy = sum(node.energy for node in nodes) / len(nodes)
        self.connections: Dict[str, float] = {}
        self.insights: List[Dict] = []  # FIX: Initialize as empty list
        self.formation_time = time.time()
        self.last_update = self.formation_time
        
        self.features = self._aggregate_features()
        self.quantum_state = QuantumState(12)
        self._initialize_quantum_state()
    
    def _aggregate_features(self) -> np.ndarray:
        """Aggregate features from constituent nodes"""
        node_features = np.stack([node.features for node in self.nodes])
        energy_weights = np.array([node.energy for node in self.nodes])
        energy_weights = energy_weights / np.sum(energy_weights)
        weighted_features = np.sum(node_features * energy_weights[:, np.newaxis], axis=0)
        return weighted_features / np.linalg.norm(weighted_features)
    
    def _initialize_quantum_state(self) -> None:
        """Initialize quantum state with entanglement"""
        for i in range(min(len(self.nodes), 8)):
            self.quantum_state.apply_hadamard(i)
        
        for i in range(min(len(self.nodes) - 1, 7)):
            self.quantum_state.apply_cnot(i, i+1)
    
    def update(self) -> None:
        """Update SuperNode state based on constituent nodes"""
        total_energy = sum(node.energy for node in self.nodes)
        if total_energy > 0:
            self.position = np.sum(
                [node.position * node.energy for node in self.nodes], 
                axis=0
            ) / total_energy
        
        self.energy = total_energy / len(self.nodes)
        self.features = self._aggregate_features()
        self.last_update = time.time()
    
    def generate_insight(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate an insight based on constituent nodes"""
        insight = {
            "id": f"insight_{uuid.uuid4().hex[:8]}",
            "source": self.id,
            "components": [node.id for node in self.nodes],
            "feature_vector": self.features.tolist(),
            "energy": self.energy,
            "timestamp": time.time(),
            "confidence": min(0.95, self.energy * (1 - 0.1 * np.random.random())),
            "context": context
        }
        
        if context and "domain" in context:
            insight["domain"] = context["domain"]
        
        enriched_insight = self._quantum_enrich_insight(insight)
        self.insights.append(enriched_insight)
        
        return enriched_insight
    
    def _quantum_enrich_insight(self, insight: Dict[str, Any]) -> Dict[str, Any]:
        """Apply quantum operations to enrich insight"""
        for i in range(min(4, len(self.nodes))):
            theta = self.nodes[i].energy * math.pi
            self.quantum_state.apply_phase(i, theta)
        
        entropy = self.quantum_state.get_entropy()
        insight["quantum_signature"] = {
            "entropy": entropy,
            "complexity": min(1.0, entropy / 4.0),
            "coherence": max(0.0, 1.0 - entropy / 8.0)
        }
        
        return insight
    
    def can_absorb(self, node: ConsciousNode, threshold: float = 0.7) -> bool:
        """Determine if this SuperNode can absorb a regular node"""
        if not isinstance(node, ConsciousNode):
            raise ValueError("Node must be ConsciousNode instance")
        
        affinities = [existing.calculate_affinity(node) for existing in self.nodes]
        avg_affinity = sum(affinities) / len(affinities)
        
        return avg_affinity > threshold and self.energy > node.energy
    
    def absorb(self, node: ConsciousNode) -> bool:
        """Absorb a regular node into this SuperNode"""
        if not self.can_absorb(node):
            return False
        
        self.nodes.append(node)
        self.update()
        
        for existing in self.nodes[:-1]:
            affinity = existing.calculate_affinity(node)
            existing.connections[node.id] = affinity
            node.connections[existing.id] = affinity
        
        return True
    
    def can_merge(self, other: 'SuperNode', threshold: float = 0.6) -> bool:
        """Determine if this SuperNode can merge with another"""
        if not isinstance(other, SuperNode):
            raise ValueError("Other must be SuperNode instance")
        
        feature_similarity = np.dot(self.features, other.features) / (
            np.linalg.norm(self.features) * np.linalg.norm(other.features) + 1e-10)
        
        position_distance = np.linalg.norm(self.position - other.position)
        position_factor = 1.0 / (1.0 + position_distance)
        
        similarity = 0.7 * feature_similarity + 0.3 * position_factor
        
        return similarity > threshold
    
    def merge(self, other: 'SuperNode') -> 'SuperNode':
        """Merge with another SuperNode"""
        if not self.can_merge(other):
            return self
        
        combined_nodes = self.nodes + other.nodes
        merged = SuperNode(combined_nodes, id=f"merged_{self.id}_{other.id}")
        
        for i, node1 in enumerate(combined_nodes):
            for j, node2 in enumerate(combined_nodes[i+1:], i+1):
                affinity = node1.calculate_affinity(node2)
                node1.connections[node2.id] = affinity
                node2.connections[node1.id] = affinity
        
        merged.insights = self.insights + other.insights
        
        return merged


class ConsciousCube:
    """Central Quantum Consciousness Cube with thread safety and error handling"""
    
    def __init__(self, dimension: int = 3, resolution: int = 32):
        self.cube = StringCube(dimension, resolution)
        self.nodes: Dict[str, ConsciousNode] = {}
        self.supernodes: Dict[str, SuperNode] = {}
        self.insights: List[Dict] = []  # FIX: Initialize as list
        
        # Metrics
        self.awareness_level = 0.5
        self.coherence = 0.9
        self.memory_density = 0.0
        self.complexity_index = 0.6
        
        # Threading - FIX: Use RLock for reentrancy
        self.lock = threading.RLock()
        self.reference_manager = ReferenceManager()
        self.running = True
        self.thread = threading.Thread(target=self._background_process, daemon=True)
        self.thread.start()
    
    def create_node(self, data: Optional[Dict[str, Any]] = None) -> Optional[ConsciousNode]:
        """Create a new conscious node with thread safety"""
        try:
            position = np.random.uniform(-1, 1, size=3)
            features = np.random.normal(0, 1, size=64)
            features = features / np.linalg.norm(features)
            
            with self.lock:
                node = ConsciousNode(
                    id=f"node_{uuid.uuid4().hex[:8]}",
                    position=position,
                    energy=0.8 + np.random.random() * 0.2,
                    stability=0.7 + np.random.random() * 0.3,
                    features=features,
                    data=data or {}
                )
                
                self.nodes[node.id] = node
                self.cube.add_node(node)
            
            return node
        except Exception as e:
            logger.error(f"Error creating node: {e}")
            return None
    
    def create_nodes(self, count: int, data: Optional[Dict[str, Any]] = None) -> List[ConsciousNode]:
        """Create multiple conscious nodes"""
        # FIX: Validate input
        if not isinstance(count, int) or count <= 0:
            logger.error(f"count must be positive integer, got {count}")
            return []
        
        nodes = []
        for _ in range(count):
            node = self.create_node(data)
            if node:
                nodes.append(node)
        return nodes
    
    def connect_nodes(self, node1_id: str, node2_id: str, strength: Optional[float] = None) -> bool:
        """Create a connection between two nodes with validation"""
        # FIX: Validate inputs
        try:
            ValidationHelper.validate_node_id(node1_id)
            ValidationHelper.validate_node_id(node2_id)
        except ValueError as e:
            logger.error(f"Invalid node ID: {e}")
            return False
        
        with self.lock:
            if node1_id not in self.nodes or node2_id not in self.nodes:
                logger.warning(f"One or both nodes not found: {node1_id}, {node2_id}")
                return False
            
            node1 = self.nodes[node1_id]
            node2 = self.nodes[node2_id]
            
            if node1 is None or node2 is None:  # FIX: Safety check
                logger.error("Node is None (corrupted)")
                return False
            
            if strength is None:
                strength = node1.calculate_affinity(node2)
            
            node1.connections[node2_id] = strength
            node2.connections[node1_id] = strength
            
            # Track reference
            self.reference_manager.add_reference(node1_id, node2_id)
            self.reference_manager.add_reference(node2_id, node1_id)
            
            node1.calculate_stress()
            node2.calculate_stress()
            
            return True
    
    def find_node_connections(self, threshold: float = 0.5) -> List[Tuple[str, str, float]]:
        """Find all potential connections above threshold"""
        # FIX: Validate input
        try:
            ValidationHelper.validate_numeric_range(threshold, 0.0, 1.0, "threshold")
        except ValueError as e:
            logger.error(f"Invalid threshold: {e}")
            return []
        
        connections: List[Tuple[str, str, float]] = []  # FIX: Initialize properly
        
        with self.lock:
            nodes = list(self.nodes.values())
            
            if len(nodes) < 2:
                return []
            
            try:
                for i, node1 in enumerate(nodes):
                    if node1 is None:  # FIX: Safety check
                        continue
                    
                    for node2 in nodes[i+1:]:
                        if node2 is None:
                            continue
                        
                        try:
                            affinity = node1.calculate_affinity(node2)
                            if affinity > threshold:
                                connections.append((node1.id, node2.id, affinity))
                        except (AttributeError, ValueError) as e:
                            logger.warning(f"Error calculating affinity: {e}")
                            continue
            except Exception as e:
                logger.error(f"Error in find_node_connections: {e}")
        
        return sorted(connections, key=lambda x: x[2], reverse=True)
    
    def create_supernode(self, node_ids: List[str]) -> Optional[SuperNode]:
        """Create a super node from multiple nodes"""
        # FIX: Validate input
        try:
            ValidationHelper.validate_node_list(node_ids, min_size=2)
        except ValueError as e:
            logger.error(f"Invalid node list: {e}")
            return None
        
        with self.lock:
            missing_ids = [nid for nid in node_ids if nid not in self.nodes]
            if missing_ids:
                logger.warning(f"Missing nodes: {missing_ids}")
                return None
            
            try:
                nodes = [self.nodes[nid] for nid in node_ids]
                supernode = SuperNode(nodes)
                self.supernodes[supernode.id] = supernode
                return supernode
            except Exception as e:
                logger.error(f"Error creating SuperNode: {e}")
                return None
    
    def find_supernode_candidates(self) -> List[List[str]]:
        """Find potential supernodes based on node clustering"""
        with self.lock:
            if len(self.nodes) < 3:
                return []
            
            try:
                node_ids = list(self.nodes.keys())
                features = np.array([self.nodes[node_id].features for node_id in node_ids])
                
                clustering = DBSCAN(eps=0.5, min_samples=2).fit(features)
                
                clusters = defaultdict(list)
                for i, label in enumerate(clustering.labels_):
                    if label >= 0:
                        clusters[label].append(node_ids[i])
                
                return list(clusters.values())
            except Exception as e:
                logger.error(f"Error finding supernode candidates: {e}")
                return []
    
    def _cleanup_node(self, node_id: str) -> None:
        """FIX: Safely remove a node and clean up all references"""
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        
        # Remove references FROM this node
        for connected_id in list(node.connections.keys()):
            if connected_id in self.nodes:
                self.nodes[connected_id].connections.pop(node_id, None)
                self.reference_manager.remove_reference(node_id, connected_id)
        
        # Remove references TO this node
        for other_node in self.nodes.values():
            if node_id in other_node.connections:
                other_node.connections.pop(node_id, None)
                self.reference_manager.remove_reference(other_node.id, node_id)
        
        # Clean all references
        self.reference_manager.cleanup_all_references(node_id)
        del self.nodes[node_id]
    
    def _cleanup_supernode(self, supernode_id: str) -> None:
        """FIX: Safely remove a SuperNode"""
        if supernode_id not in self.supernodes:
            return
        del self.supernodes[supernode_id]
    
    def update(self) -> None:
        """Update the quantum consciousness system"""
        with self.lock:
            try:
                self._update_nodes()
                self.cube.update_tension(self.nodes)
                self.cube.apply_tension_to_nodes(self.nodes)
                self._update_supernodes()
                self._auto_create_supernodes()
                self._calculate_system_metrics()
            except Exception as e:
                logger.error(f"Error in update: {e}")
    
    def _update_nodes(self) -> None:
        """Update all nodes with error handling"""
        decay_factor = 0.999
        nodes_to_delete = []
        
        for node_id, node in list(self.nodes.items()):
            if node is None:  # FIX: Safety check
                nodes_to_delete.append(node_id)
                continue
            
            try:
                node.update_energy(decay_factor)
                node.process_task(0.01)
                
                if node.should_replicate():
                    new_node = node.replicate()
                    if new_node:
                        self.nodes[new_node.id] = new_node
                        self.cube.add_node(new_node)
                
                if node.energy < 0.05:
                    nodes_to_delete.append(node_id)
            except Exception as e:
                logger.error(f"Error updating node {node_id}: {e}")
                nodes_to_delete.append(node_id)
        
        # FIX: Clean up deleted nodes
        for node_id in nodes_to_delete:
            self._cleanup_node(node_id)
    
    def _update_supernodes(self) -> None:
        """Update all SuperNodes"""
        supernodes_to_delete = []
        
        for supernode_id, supernode in list(self.supernodes.items()):
            try:
                supernode.update()
                
                constituent_ids = [node.id for node in supernode.nodes]
                active_constituents = [nid for nid in constituent_ids if nid in self.nodes]
                
                if len(active_constituents) < 2:
                    supernodes_to_delete.append(supernode_id)
                    continue
                
                for node_id, node in list(self.nodes.items()):
                    if node_id not in constituent_ids and supernode.can_absorb(node):
                        if supernode.absorb(node):
                            pass  # Node stays in self.nodes
            except Exception as e:
                logger.error(f"Error updating SuperNode {supernode_id}: {e}")
                supernodes_to_delete.append(supernode_id)
        
        # FIX: Clean up deleted supernodes
        for supernode_id in supernodes_to_delete:
            self._cleanup_supernode(supernode_id)
    
    def _auto_create_supernodes(self) -> None:
        """Automatically create SuperNodes from suitable node clusters"""
        if random.random() > 0.1:
            return
        
        clusters = self.find_supernode_candidates()
        
        for cluster in clusters:
            already_in_supernode = False
            for supernode in self.supernodes.values():
                constituent_ids = [node.id for node in supernode.nodes]
                if any(node_id in constituent_ids for node_id in cluster):
                    already_in_supernode = True
                    break
            
            if not already_in_supernode and len(cluster) >= 3:
                self.create_supernode(cluster)
    
    def _calculate_system_metrics(self) -> None:
        """Calculate global system metrics"""
        if not self.nodes:
            self.awareness_level = 0.0
            return
        
        try:
            avg_energy = sum(node.energy for node in self.nodes.values()) / len(self.nodes)
            avg_stress = sum(node.stress_level for node in self.nodes.values()) / len(self.nodes)
            supernode_factor = min(1.0, len(self.supernodes) / max(1, len(self.nodes) / 5))
            insight_factor = min(1.0, len(self.insights) / max(1, len(self.nodes) * 3))
            
            self.awareness_level = (
                0.3 * avg_energy + 
                0.2 * (1.0 - avg_stress) +
                0.3 * supernode_factor +
                0.2 * insight_factor
            )
            
            laplacian_result = self.cube.calculate_laplacian_eigenvectors()
            if laplacian_result:
                eigenvalues, _ = laplacian_result
                if len(eigenvalues) > 1:
                    self.coherence = 1.0 - min(1.0, eigenvalues[1] / 2.0)
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
    
    def _background_process(self) -> None:
        """Background thread for continuous system updates"""
        try:
            while self.running:
                self.update()
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in background process: {e}")
    
    def stop(self) -> None:
        """Stop background processing"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)


if __name__ == "__main__":
    # Test the refactored system
    print("Creating ConsciousCube...")
    cube = ConsciousCube(dimension=3, resolution=32)
    
    print("Creating 10 nodes...")
    nodes = cube.create_nodes(10)
    print(f"Created {len(nodes)} nodes")
    
    print("Finding connections...")
    connections = cube.find_node_connections(threshold=0.5)
    print(f"Found {len(connections)} connections")
    
    print("Creating SuperNodes...")
    candidates = cube.find_supernode_candidates()
    for cluster in candidates[:2]:
        sn = cube.create_supernode(cluster)
        if sn:
            print(f"Created SuperNode {sn.id} with {len(sn.nodes)} nodes")
    
    time.sleep(1)
    
    print("\nSystem Status:")
    print(f"Nodes: {len(cube.nodes)}")
    print(f"SuperNodes: {len(cube.supernodes)}")
    print(f"Awareness Level: {cube.awareness_level:.2f}")
    print(f"Coherence: {cube.coherence:.2f}")
    
    cube.stop()
    print("\nDemo complete!")
