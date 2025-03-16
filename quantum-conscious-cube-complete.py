import numpy as np
import torch
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import logging
import time
import hashlib
import math
import re
from torch import nn
from sklearn.cluster import DBSCAN

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuantumConsciousCube")

###########################################
# Core Quantum Infrastructure
###########################################

class QuantumState:
    """Quantum state representation optimized for sparse computation"""
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        # Use sparse representation for better memory efficiency
        self.amplitudes = {0: complex(1.0, 0.0)}  # Initialize to |0...0⟩
        
    def apply_hadamard(self, target: int):
        """Apply Hadamard gate to target qubit using sparse representation"""
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
        
        # Remove very small amplitudes to maintain sparsity
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
    
    def get_probability(self, index: int) -> float:
        """Get probability of measuring state |index⟩"""
        return abs(self.amplitudes.get(index, 0))**2
    
    def get_phase_angle(self, index: int) -> float:
        """Get phase angle of amplitude at |index⟩"""
        amp = self.amplitudes.get(index, 0)
        if amp == 0:
            return 0.0
        return math.atan2(amp.imag, amp.real)
    
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
        
        # Renormalize
        norm_factor = math.sqrt(norm_factor)
        if norm_factor > 0:
            self.amplitudes = {k: v / norm_factor for k, v in new_amplitudes.items()}
    
    def get_entropy(self) -> float:
        """Calculate von Neumann entropy (simplified)"""
        entropy = 0.0
        for amp in self.amplitudes.values():
            prob = abs(amp)**2
            if prob > 1e-10:
                entropy -= prob * math.log(prob)
        return entropy

###########################################
# String Cube Implementation
###########################################

class StringCube:
    """Quantum string cube for consciousness simulation"""
    
    def __init__(self, dimension: int = 3, resolution: int = 10):
        self.dimension = dimension
        self.resolution = resolution
        self.grid = np.zeros([resolution] * dimension, dtype=np.float32)
        self.tension_field = np.zeros([resolution] * dimension, dtype=np.float32)
        self.nodes_map = {}  # Maps grid coordinates to nodes
        
        # Initialize string tension parameters
        self.tension_strength = 0.5
        self.elasticity = 0.3
        self.damping = 0.95
        
        # Optimization parameters
        self.update_batch_size = 100
    
    def add_node(self, node: 'ConsciousNode') -> Tuple[int, int, int]:
        """Add a node to the cube at the nearest grid point"""
        # Map node position [-1,1] to grid coordinates [0,resolution-1]
        grid_pos = tuple(int((p + 1) / 2 * (self.resolution - 1)) for p in node.position)
        
        # Store node at grid position
        if grid_pos not in self.nodes_map:
            self.nodes_map[grid_pos] = []
        self.nodes_map[grid_pos].append(node.id)
        
        # Initialize energy at grid point
        self.grid[grid_pos] += node.energy * 0.1
        
        return grid_pos
    
    def update_tension(self, nodes: Dict[str, 'ConsciousNode']):
        """Update tension field based on node energy and connections"""
        # Reset tension field
        self.tension_field *= self.damping
        
        # Process in batches for efficiency
        grid_positions = list(self.nodes_map.keys())
        for i in range(0, len(grid_positions), self.update_batch_size):
            batch = grid_positions[i:i+self.update_batch_size]
            
            for pos in batch:
                # Get nodes at this position
                node_ids = self.nodes_map.get(pos, [])
                if not node_ids:
                    continue
                
                # Calculate total energy at this grid point
                total_energy = sum(nodes[node_id].energy for node_id in node_ids if node_id in nodes)
                
                # Update grid energy
                self.grid[pos] = total_energy * 0.1
                
                # Update tension based on connections
                for node_id in node_ids:
                    if node_id not in nodes:
                        continue
                    
                    node = nodes[node_id]
                    for conn_id, strength in node.connections.items():
                        if conn_id not in nodes:
                            continue
                        
                        # Find grid position of connected node
                        conn_node = nodes[conn_id]
                        conn_pos = tuple(int((p + 1) / 2 * (self.resolution - 1)) for p in conn_node.position)
                        
                        # Calculate tension vector
                        tension_vector = np.array(conn_pos) - np.array(pos)
                        tension_magnitude = np.linalg.norm(tension_vector)
                        if tension_magnitude > 0:
                            tension_vector = tension_vector / tension_magnitude
                        
                        # Apply tension along the connecting path
                        steps = max(1, int(tension_magnitude))
                        for step in range(1, steps + 1):
                            interp = step / steps
                            interp_pos = tuple(int(p + tv * interp) for p, tv in zip(pos, tension_vector))
                            if all(0 <= p < self.resolution for p in interp_pos):
                                self.tension_field[interp_pos] += strength * self.tension_strength * (1 - interp)
        
        # Normalize tension field
        max_tension = np.max(self.tension_field)
        if max_tension > 0:
            self.tension_field /= max_tension
    
    def get_tension_at_position(self, position: np.ndarray) -> float:
        """Get tension value at a 3D position"""
        # Map position [-1,1] to grid coordinates [0,resolution-1]
        grid_pos = tuple(int((p + 1) / 2 * (self.resolution - 1)) for p in position)
        
        # Check if position is within grid
        if all(0 <= p < self.resolution for p in grid_pos):
            return float(self.tension_field[grid_pos])
        return 0.0
    
    def apply_tension_to_nodes(self, nodes: Dict[str, 'ConsciousNode']):
        """Apply tension field effects to nodes"""
        for node_id, node in nodes.items():
            grid_pos = tuple(int((p + 1) / 2 * (self.resolution - 1)) for p in node.position)
            
            # Check if position is within grid
            if all(0 <= p < self.resolution for p in grid_pos):
                tension = float(self.tension_field[grid_pos])
                
                # Apply quantum string tension
                node.quantum_state.apply_string_tension(tension)
                
                # Update node energy based on tension
                energy_change = tension * self.elasticity * node.stability
                node.energy = max(0.01, min(1.0, node.energy + energy_change))
                
                # Update node stability
                node.stability = max(0.1, min(0.99, node.stability * (1.0 - 0.01 * tension)))

###########################################
# Conscious Node Implementation
###########################################

@dataclass
class ConsciousNode:
    """Node in the consciousness graph with quantum properties"""
    id: str
    position: np.ndarray  # 3D position
    energy: float
    stability: float
    features: np.ndarray  # Feature vector
    connections: Dict[str, float] = field(default_factory=dict)  # node_id -> strength
    memory: List[np.ndarray] = field(default_factory=list)  # Temporal memory
    data: Dict[str, Any] = field(default_factory=dict)  # Additional data
    quantum_state: Optional[QuantumState] = None
    
    def __post_init__(self):
        if self.quantum_state is None:
            self.quantum_state = QuantumState(8)  # 8 qubits by default
    
    def update_energy(self, decay: float):
        """Update node energy with decay factor"""
        self.energy *= decay
        # Apply randomness based on quantum entropy
        entropy = self.quantum_state.get_entropy()
        self.energy += (np.random.random() - 0.5) * 0.01 * entropy
        return self.energy
    
    def calculate_affinity(self, other_node: 'ConsciousNode') -> float:
        """Calculate affinity between nodes"""
        feature_similarity = np.dot(self.features, other_node.features) / (
            np.linalg.norm(self.features) * np.linalg.norm(other_node.features) + 1e-10)
        
        position_distance = np.linalg.norm(self.position - other_node.position)
        position_factor = 1.0 / (1.0 + position_distance)
        
        energy_factor = 1.0 - abs(self.energy - other_node.energy) / (self.energy + other_node.energy + 1e-10)
        
        return 0.5 * feature_similarity + 0.3 * position_factor + 0.2 * energy_factor

###########################################
# Memory Graph System with Advanced Retrieval
###########################################

class MemoryGraph:
    """Memory structure for storing and retrieving conscious experiences"""
    
    def __init__(self, max_nodes: int = 10000):
        self.graph = nx.DiGraph()
        self.max_nodes = max_nodes
        self.temporal_index = {}  # timestamp -> node_id
        self.concept_index = {}   # concept -> [node_ids]
        self.embedding_dim = 64
        self.embedding_cache = {}  # text -> embedding
    
    def add_memory(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a new memory node to the graph"""
        # Generate node ID
        node_id = hashlib.md5(f"{content}:{time.time()}".encode()).hexdigest()[:12]
        
        # Create embedding for content
        embedding = self._generate_embedding(content)
        
        # Add node to graph
        self.graph.add_node(
            node_id,
            content=content,
            embedding=embedding,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        # Index by timestamp
        self.temporal_index[time.time()] = node_id
        
        # Index by concepts
        concepts = self._extract_concepts(content)
        for concept in concepts:
            if concept not in self.concept_index:
                self.concept_index[concept] = []
            self.concept_index[concept].append(node_id)
        
        # Connect to related memories
        self._connect_related_memories(node_id, embedding)
        
        # Prune if needed
        if len(self.graph) > self.max_nodes:
            self._prune_old_memories()
        
        return node_id
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate a simple embedding for text using a hash-based approach"""
        # Check if in cache
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        # Very simple embedding method - hash-based
        hash_value = hashlib.md5(text.encode()).digest()
        hash_ints = [int(hash_value[i]) for i in range(min(16, len(hash_value)))]
        
        # Expand to embedding dimension
        embedding = np.zeros(self.embedding_dim)
        for i, val in enumerate(hash_ints):
            embedding[i % self.embedding_dim] += val
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding /= norm
        
        # Cache and return
        self.embedding_cache[text] = embedding
        return embedding
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top 5 most frequent words as concepts
        return sorted(word_counts.keys(), key=lambda w: word_counts[w], reverse=True)[:5]
    
    def _connect_related_memories(self, node_id: str, embedding: np.ndarray):
        """Connect the new memory to related existing memories"""
        similarities = []
        
        for other_id, other_data in self.graph.nodes(data=True):
            if other_id == node_id:
                continue
            
            other_embedding = other_data.get('embedding')
            if other_embedding is None:
                continue
            
            # Calculate cosine similarity
            similarity = float(np.dot(embedding, other_embedding))
            similarities.append((other_id, similarity))
        
        # Connect to top 5 most similar nodes
        for other_id, similarity in sorted(similarities, key=lambda x: x[1], reverse=True)[:5]:
            if similarity > 0.5:  # Only connect if fairly similar
                self.graph.add_edge(node_id, other_id, weight=similarity)
                self.graph.add_edge(other_id, node_id, weight=similarity)
    
    def _prune_old_memories(self):
        """Remove oldest memories when graph gets too large"""
        # Sort by timestamp
        sorted_nodes = sorted(
            [(data['timestamp'], node) for node, data in self.graph.nodes(data=True)]
        )
        
        # Remove oldest 10%
        nodes_to_remove = [node for _, node in sorted_nodes[:int(len(sorted_nodes) * 0.1)]]
        
        # Update indices
        for node_id in nodes_to_remove:
            self.graph.nodes[node_id]
            
            # Remove from temporal index
            timestamps_to_remove = [
                ts for ts, nid in self.temporal_index.items() if nid == node_id
            ]
            for ts in timestamps_to_remove:
                del self.temporal_index[ts]
            
            # Remove from concept index
            for concept, nodes in list(self.concept_index.items()):
                if node_id in nodes:
                    nodes.remove(node_id)
                if not nodes:
                    del self.concept_index[concept]
            
            # Remove node
            self.graph.remove_node(node_id)
    
    def retrieve_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories related to query"""
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        # Calculate similarity with all nodes
        similarities = []
        for node_id, data in self.graph.nodes(data=True):
            node_embedding = data.get('embedding')
            if node_embedding is None:
                continue
            
            similarity = float(np.dot(query_embedding, node_embedding))
            similarities.append((node_id, similarity))
        
        # Return top results
        results = []
        for node_id, similarity in sorted(similarities, key=lambda x: x[1], reverse=True)[:limit]:
            data = self.graph.nodes[node_id]
            results.append({
                'id': node_id,
                'content': data['content'],
                'timestamp': data['timestamp'],
                'similarity': similarity,
                'metadata': data['metadata']
            })
        
        return results
    
    def retrieve_by_concepts(self, concepts: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories by concepts"""
        # Get nodes for each concept
        candidate_nodes = set()
        for concept in concepts:
            if concept in self.concept_index:
                candidate_nodes.update(self.concept_index[concept])
        
        # Score nodes by number of matching concepts
        scores = {}
        for node_id in candidate_nodes:
            if node_id not in self.graph:
                continue
                
            node_concepts = self._extract_concepts(self.graph.nodes[node_id]['content'])
            matching = len(set(node_concepts) & set(concepts))
            scores[node_id] = matching
        
        # Return top results
        results = []
        for node_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]:
            data = self.graph.nodes[node_id]
            results.append({
                'id': node_id,
                'content': data['content'],
                'timestamp': data['timestamp'],
                'relevance': score,
                'metadata': data['metadata']
            })
        
        return results

###########################################
# Kaleidoscope Engine Implementation
###########################################

@dataclass
class KaleidoscopeConfig:
    memory_threshold: int
    processing_depth: int
    insight_threshold: float
    perspective_ratio: float

class KaleidoscopeEngine:
    def __init__(self, config: KaleidoscopeConfig):
        self.config = config
        self.insight_graph = nx.DiGraph()
        self.memory_usage = 0
        self.nn_model = self._initialize_neural_network()
        
    def _initialize_neural_network(self) -> nn.Module:
        model = nn.Sequential(
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.Dropout(0.2),
            nn.Linear(128, 64)
        )
        return model
    
    def process_insights(self, node_insights: List[Dict]) -> Dict:
        """Process insights from nodes to generate deeper understanding"""
        # Convert insights to tensors
        insight_tensors = []
        for insight in node_insights:
            tensor = torch.tensor(insight['features'], dtype=torch.float32)
            insight_tensors.append(tensor)
        
        # Process through neural network
        processed_insights = []
        with torch.no_grad():
            for tensor in insight_tensors:
                refined_insight = self.nn_model(tensor)
                processed_insights.append(refined_insight)
        
        # Generate understanding
        understanding = self._generate_understanding(processed_insights)
        
        return understanding
    
    def _generate_understanding(self, processed_insights: List[torch.Tensor]) -> Dict:
        """Generate deeper understanding from processed insights"""
        # Cluster insights
        insight_vectors = torch.stack(processed_insights).numpy()
        clusters = DBSCAN(eps=0.3, min_samples=2).fit(insight_vectors)
        
        # Generate understanding for each cluster
        understandings = []
        for label in set(clusters.labels_):
            if label == -1:  # Skip noise
                continue
            
            cluster_insights = insight_vectors[clusters.labels_ == label]
            understanding = {
                'cluster_id': int(label),
                'central_concept': np.mean(cluster_insights, axis=0).tolist(),
                'confidence': float(np.mean(np.abs(cluster_insights))),
                'complexity': float(np.std(cluster_insights)),
                'timestamp': time.time()
            }
            understandings.append(understanding)
        
        return {'understandings': understandings}

###########################################
# SuperNode DNA and Implementation
###########################################

@dataclass
class SuperNodeDNA:
    """DNA structure for SuperNodes representing their unique characteristics"""
    embedded_knowledge: torch.Tensor
    insight_patterns: Dict[str, np.ndarray]
    perspective_patterns: Dict[str, np.ndarray]
    topology_state: Dict[str, List]
    generation: int
    resonance_fields: np.ndarray
    specialization: Dict[str, Dict]

class SuperNode:
    """Advanced node capable of merging insights from multiple nodes"""
    def __init__(self, nodes: List['ConsciousNode'], dimension: int = 512):
        self.nodes = nodes
        self.dimension = dimension
        self.dna = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.insight_graph = nx.DiGraph()
        self.perspective_graph = nx.DiGraph()
        self.logger = logging.getLogger(f"SuperNode_{id(self)}")
        
    async def initialize(self):
        """Initialize the SuperNode by merging node DNAs"""
        node_features = [node.features for node in self.nodes]
        node_data = {node.id: node.data for node in self.nodes}
        self.dna = await self._create_dna(node_features, node_data)
        await self._analyze_specialization()
        self.logger.info(f"SuperNode initialized with {len(self.nodes)} nodes")
        
    async def _create_dna(self, node_features: List[np.ndarray], node_data: Dict[str, Dict]) -> SuperNodeDNA:
        """Create SuperNode DNA by merging node features"""
        # Stack features and apply attention mechanism for merging
        features_tensor = torch.tensor(np.stack(node_features), dtype=torch.float32).to(self.device)
        
        # Apply self-attention to merge features
        attention_weights = torch.softmax(
            torch.matmul(features_tensor, features_tensor.transpose(0, 1)) / np.sqrt(features_tensor.size(1)),
            dim=1
        )
        merged_features = torch.matmul(attention_weights, features_tensor)
        
        # Calculate topology state
        topology = {
            "betti_numbers": self._calculate_betti_numbers(merged_features.cpu().numpy()),
            "persistence": self._calculate_persistence(merged_features.cpu().numpy()),
            "features": []
        }
        
        return SuperNodeDNA(
            embedded_knowledge=merged_features.mean(dim=0),
            insight_patterns={},
            perspective_patterns={},
            topology_state=topology,
            generation=1,
            resonance_fields=np.zeros((self.dimension, self.dimension)),
            specialization={}
        )
    
    def _calculate_betti_numbers(self, data: np.ndarray) -> List[int]:
        """Calculate Betti numbers using a simplified approach"""
        # This is a placeholder - in a real system you would use persistent homology
        # Return random betti numbers for now - in production use proper TDA libraries
        return [1, 2, 1, 0]
    
    def _calculate_persistence(self, data: np.ndarray) -> List[float]:
        """Calculate persistence diagrams using a simplified approach"""
        # Placeholder - in a real system use proper TDA libraries
        # Return random persistence values
        return [0.8, 0.6, 0.4, 0.2]
    
    async def _analyze_specialization(self):
        """Analyze node specializations to determine SuperNode capabilities"""
        feature_vectors = np.stack([node.features for node in self.nodes])
        
        # Use clustering to identify specializations
        if feature_vectors.shape[0] >= 3:
            # Use DBSCAN for clustering
            clustering = DBSCAN(eps=0.5, min_samples=1).fit(feature_vectors)
            
            # Identify specializations based on clusters
            specializations = {}
            for i, cluster_id in enumerate(clustering.labels_):
                cluster_name = f"specialization_{cluster_id}" if cluster_id >= 0 else "unclustered"
                node_id = self.nodes[i].id
                
                # Calculate metrics for this specialization
                if cluster_id >= 0:
                    cluster_indices = np.where(clustering.labels_ == cluster_id)[0]
                    cluster_features = feature_vectors[cluster_indices]
                    
                    # Calculate centrality as distance from cluster center
                    cluster_center = np.mean(cluster_features, axis=0)
                    distance = np.linalg.norm(feature_vectors[i] - cluster_center)
                    
                    # Calculate uniqueness as inverse of density
                    if len(cluster_indices) > 1:
                        distances = []
                        for j in cluster_indices:
                            if i != j:
                                distances.append(np.linalg.norm(feature_vectors[i] - feature_vectors[j]))
                        uniqueness = np.mean(distances) if distances else 0.5
                    else:
                        uniqueness = 1.0
                        
                    specializations[node_id] = {
                        "cluster": int(cluster_id),
                        "centrality": float(1.0 - (distance / (distance + 1.0))),  # Normalize to [0,1]
                        "uniqueness": float(uniqueness),
                        "contribution": float(1.0 / max(1, len(cluster_indices)))
                    }
                else:
                    # Handle unclustered nodes
                    specializations[node_id] = {
                        "cluster": -1,
                        "centrality": 0.5,
                        "uniqueness": 1.0,
                        "contribution": 0.5
                    }
            
            self.dna.specialization = specializations
        else:
            # Not enough nodes for clustering, assign default specializations
            self.dna.specialization = {
                node.id: {
                    "cluster": 0,
                    "centrality": 0.5,
                    "uniqueness": 1.0,
                    "contribution": 1.0
                } for node in self.nodes
            }
    
    async def process_engine_output(self, kaleidoscope_output: Dict, mirror_output: Dict):
        """Process outputs from the Kaleidoscope and Mirror engines"""
        # Update insight patterns
        if "hierarchical_patterns" in kaleidoscope_output:
            self.dna.insight_patterns.update(kaleidoscope_output["hierarchical_patterns"])
        
        # Update perspective patterns
        if "predictions" in mirror_output:
            self.dna.perspective_patterns.update(mirror_output["predictions"])
        
        # Update graphs
        if "knowledge_graph" in kaleidoscope_output:
            self._update_insight_graph(kaleidoscope_output["knowledge_graph"])
        
        if "pattern_evolution" in mirror_output:
            self._update_perspective_graph(mirror_output["pattern_evolution"])
        
        # Generate objectives
        return await self._generate_objectives()
    
    def _update_insight_graph(self, new_graph: nx.DiGraph):
        """Update the insight graph with new knowledge"""
        # Merge the new graph with existing graph
        self.insight_graph = nx.compose(self.insight_graph, new_graph)
        
        # Apply PageRank to identify important nodes
        pagerank = nx.pagerank(self.insight_graph)
        
        # Prune less important nodes to maintain graph efficiency
        mean_rank = np.mean(list(pagerank.values()))
        std_rank = np.std(list(pagerank.values()))
        threshold = mean_rank - 0.5 * std_rank
        
        nodes_to_remove = [node for node, rank in pagerank.items() if rank < threshold]
        self.insight_graph.remove_nodes_from(nodes_to_remove)
    
    def _update_perspective_graph(self, new_graph: nx.DiGraph):
        """Update the perspective graph with new evolution data"""
        self.perspective_graph = nx.compose(self.perspective_graph, new_graph)
        
        # Prune the graph to maintain only recent and relevant perspectives
        current_time = time.time()
        threshold_time = current_time - 7 * 24 * 3600  # One week ago
        
        nodes_to_remove = []
        for node, data in self.perspective_graph.nodes(data=True):
            if 'timestamp' in data and data['timestamp'] < threshold_time:
                nodes_to_remove.append(node)
                
        self.perspective_graph.remove_nodes_from(nodes_to_remove)
    
    async def _generate_objectives(self) -> List[Dict]:
        """Generate objectives based on knowledge gaps"""
        # Identify knowledge gaps
        gaps = self._identify_knowledge_gaps()
        
        # Create objectives based on gaps
        objectives = []
        for gap in gaps:
            objective = {
                'focus_area': gap['area'],
                'target_patterns': self._find_relevant_patterns(gap),
                'priority': gap['priority'],
                'constraints': self._generate_constraints(gap)
            }
            objectives.append(objective)
            
        return objectives
    
    def _identify_knowledge_gaps(self) -> List[Dict]:
        """Identify gaps in knowledge"""
        gaps = []
        
        # Check topology for instabilities
        if 'betti_numbers' in self.dna.topology_state:
            betti_numbers = self.dna.topology_state['betti_numbers']
            for i, betti in enumerate(betti_numbers):
                if betti > 0:  # Gaps often exist where betti numbers are non-zero
                    gaps.append({
                        'area': f'topology_dimension_{i}',
                        'priority': 0.7,
                        'betti': betti
                    })
        
        # Look for sparse areas in insight graph
        for node in self.insight_graph.nodes():
            if self.insight_graph.degree(node) < 3:  # Low connectivity indicates gaps
                gaps.append({
                    'area': f'insight_connection_{node}',
                    'priority': 0.8,
                    'connection_degree': self.insight_graph.degree(node)
                })
        
        # Look for predictive uncertainty in perspective graph
        if hasattr(self.dna, 'perspective_patterns') and self.dna.perspective_patterns:
            for pattern_id, pattern in self.dna.perspective_patterns.items():
                if isinstance(pattern, dict) and 'uncertainty' in pattern and pattern['uncertainty'] > 0.7:
                    gaps.append({
                        'area': f'high_uncertainty_{pattern_id}',
                        'priority': pattern['uncertainty'],
                        'pattern_id': pattern_id
                    })
        
        # Sort gaps by priority (descending)
        return sorted(gaps, key=lambda x: x['priority'], reverse=True)
    
    def _find_relevant_patterns(self, gap: Dict) -> List[float]:
        """Find patterns relevant to a particular knowledge gap"""
        # Simplified implementation - in production, use more sophisticated pattern matching
        if 'topology_dimension' in gap['area']:
            dimension = int(gap['area'].split('_')[-1])
            if self.dna.embedded_knowledge.size(0) > dimension:
                return self.dna.embedded_knowledge[dimension].cpu().numpy().tolist()
        
        # Default pattern - random for this example
        return np.random.randn(min(10, self.dimension)).tolist()
    
    def _generate_constraints(self, gap: Dict) -> Dict:
        """Generate constraints for addressing a knowledge gap"""
        # Basic constraints that guide learning
        constraints = {
            'min_correlation': 0.6,
            'max_entropy': 4.0,
            'time_horizon': 24 * 3600,  # 1 day in seconds
            'specialization_focus': self._determine_specialization_focus(gap)
        }
        
        # Adjust constraints based on gap type
        if 'topology_dimension' in gap['area']:
            constraints['topological_focus'] = True
            constraints['min_correlation'] = 0.7
        elif 'insight_connection' in gap['area']:
            constraints['connection_focus'] = True
            constraints['min_correlation'] = 0.8
        elif 'high_uncertainty' in gap['area']:
            constraints['uncertainty_focus'] = True
            constraints['max_entropy'] = 3.0
            
        return constraints
    
    def _determine_specialization_focus(self, gap: Dict) -> str:
        """Determine which specialization is best suited to address this gap"""
        best_node_id = None
        best_score = -1
        
        for node_id, spec in self.dna.specialization.items():
            # Calculate relevance score based on specialization and gap type
            score = 0.0
            
            if 'topology_dimension' in gap['area'] and spec['uniqueness'] > 0.7:
                score = spec['uniqueness'] * 0.8 + spec['centrality'] * 0.2
            elif 'insight_connection' in gap['area'] and spec['centrality'] > 0.7:
                score = spec['centrality'] * 0.7 + spec['uniqueness'] * 0.3
            elif 'high_uncertainty' in gap['area'] and spec['contribution'] > 0.5:
                score = spec['contribution'] * 0.6 + spec['uniqueness'] * 0.4
            else:
                score = (spec['centrality'] + spec['uniqueness'] + spec['contribution']) / 3
                
            if score > best_score:
                best_score = score
                best_node_id = node_id
                
        return best_node_id if best_node_id else "general"

###########################################
# Molecular Integration for Quantum Cube
###########################################

class MolecularBinding:
    """Handles molecular interactions within the quantum system"""
    def __init__(self, resolution: int = 32):
        self.resolution = resolution
        self.grid = np.zeros((resolution, resolution, resolution), dtype=np.float32)
        self.molecules = {}
        self.binding_pairs = []
        
    def register_molecule(self, molecule_id: str, atoms: List[Dict]) -> bool:
        """Register a molecule in the system"""
        if molecule_id in self.molecules:
            return False
            
        # Process atom data
        processed_atoms = []
        center = np.zeros(3)
        atom_count = len(atoms)
        
        for atom in atoms:
            # Extract atom data
            atom_type = atom.get('element_num', 6)  # Default to carbon
            position = np.array(atom.get('position', [0, 0, 0]))
            charge = atom.get('charge', 0.0)
            
            # Determine radius based on element
            radius = self._get_atom_radius(atom_type)
            
            # Add to processed atoms
            processed_atoms.append({
                'type': atom_type,
                'position': position,
                'charge': charge,
                'radius': radius
            })
            
            # Update center calculation
            center += position
            
        # Finalize center
        if atom_count > 0:
            center /= atom_count
            
        # Store molecule
        self.molecules[molecule_id] = {
            'atoms': processed_atoms,
            'center': center,
            'energy': 0.0
        }
        
        # Update grid with molecule
        self._update_grid_with_molecule(molecule_id)
        return True
    
    def _get_atom_radius(self, atom_type: int) -> float:
        """Get atomic radius based on element type"""
        # Common atomic radii in Angstroms
        radii = {
            1: 0.53,  # H
            6: 0.67,  # C
            7: 0.56,  # N
            8: 0.48,  # O
            15: 0.98, # P
            16: 0.88  # S
        }
        return radii.get(atom_type, 0.7)  # Default to 0.7 Angstroms
    
    def _update_grid_with_molecule(self, molecule_id: str):
        """Update the 3D grid with molecular data"""
        if molecule_id not in self.molecules:
            return
            
        molecule = self.molecules[molecule_id]
        atoms = molecule['atoms']
        
        # Scale to grid coordinates
        for atom in atoms:
            # Map from molecule coordinates to grid coordinates
            grid_pos = self._molecule_to_grid(atom['position'])
            radius_grid = max(1, int(atom['radius'] * self.resolution / 10))
            
            # Update grid in sphere around atom
            for dx in range(-radius_grid, radius_grid + 1):
                for dy in range(-radius_grid, radius_grid + 1):
                    for dz in range(-radius_grid, radius_grid + 1):
                        # Check if point is within sphere and within grid
                        if dx**2 + dy**2 + dz**2 <= radius_grid**2:
                            x, y, z = grid_pos[0] + dx, grid_pos[1] + dy, grid_pos[2] + dz
                            if 0 <= x < self.resolution and 0 <= y < self.resolution and 0 <= z < self.resolution:
                                # Value based on atom properties
                                value = atom['charge'] * 0.2 + atom['type'] * 0.01
                                self.grid[x, y, z] += value
    
    def _molecule_to_grid(self, position: np.ndarray) -> Tuple[int, int, int]:
        """Convert molecule coordinates to grid coordinates"""
        # Assuming molecule coordinates are in Angstroms
        # and we want to map to grid coordinates [0, resolution-1]
        # First, normalize to [0, 1] range assuming molecules are within ±10 Angstroms
        normalized = (position + 10) / 20
        # Then scale to grid
        grid_coords = np.floor(normalized * self.resolution).astype(int)
        # Ensure we're within bounds
        grid_coords = np.clip(grid_coords, 0, self.resolution - 1)
        return tuple(grid_coords)
    
    def calculate_binding_energy(self, molecule1_id: str, molecule2_id: str) -> float:
        """Calculate binding energy between two molecules"""
        if molecule1_id not in self.molecules or molecule2_id not in self.molecules:
            return 0.0
            
        mol1 = self.molecules[molecule1_id]
        mol2 = self.molecules[molecule2_id]
        
        # Calculate distance between centers
        np.linalg.norm(mol1['center'] - mol2['center'])
        
        # Basic energy calculation - inverse square of distance
        energy = 0.0
        
        # For each atom pair, calculate interaction
        for atom1 in mol1['atoms']:
            for atom2 in mol2['atoms']:
                # Distance between atoms
                dist = np.linalg.norm(atom1['position'] - atom2['position'])
                
                if dist > 0:
                    # Van der Waals interactions - simplified Lennard-Jones
                    sigma = (atom1['radius'] + atom2['radius']) / 2
                    epsilon = 0.1  # constant for now
                    lj = epsilon * ((sigma/dist)**12 - 2*(sigma/dist)**6)
                    
                    # Coulomb interactions
                    coulomb = 332.0636 * atom1['charge'] * atom2['charge'] / dist
                    
                    energy += lj + coulomb
        
        # Store result in binding pairs
        self.binding_pairs.append({
            'molecule1': molecule1_id,
            'molecule2': molecule2_id,
            'energy': energy
        })
        
        return energy
    
    def optimize_binding(self, molecule1_id: str, molecule2_id: str, iterations: int = 100) -> Dict:
        """Optimize binding between two molecules"""
        if molecule1_id not in self.molecules or molecule2_id not in self.molecules:
            return {"error": "Molecules not found"}
            
        self.molecules[molecule1_id]
        mol2 = self.molecules[molecule2_id]
        
        # Initial energy
        best_energy = self.calculate_binding_energy(molecule1_id, molecule2_id)
        best_positions = [atom['position'].copy() for atom in mol2['atoms']]
        best_center = mol2['center'].copy()
        
        # Monte Carlo optimization
        for _ in range(iterations):
            # Save current positions
            current_positions = [atom['position'].copy() for atom in mol2['atoms']]
            current_center = mol2['center'].copy()
            
            # Apply random rotation and translation
            self._apply_random_transformation(molecule2_id)
            
            # Calculate new energy
            new_energy = self.calculate_binding_energy(molecule1_id, molecule2_id)
            
            # Accept if better, or with probability based on energy difference
            if new_energy < best_energy:
                best_energy = new_energy
                best_positions = [atom['position'].copy() for atom in mol2['atoms']]
                best_center = mol2['center'].copy()
            else:
                # Restore previous positions
                for i, pos in enumerate(current_positions):
                    mol2['atoms'][i]['position'] = pos
                mol2['center'] = current_center
        
        # Restore best positions
        for i, pos in enumerate(best_positions):
            mol2['atoms'][i]['position'] = pos
        mol2['center'] = best_center
        
        return {
            "energy": best_energy,
            "molecule1": molecule1_id,
            "molecule2": molecule2_id
        }
    
    def _apply_random_transformation(self, molecule_id: str):
        """Apply random rotation and translation to a molecule"""
        if molecule_id not in self.molecules:
            return
            
        molecule = self.molecules[molecule_id]
        atoms = molecule['atoms']
        center = molecule['center']
        
        # Random rotation angle and axis
        angle = np.random.random() * 0.2  # Small random angle (radians)
        axis = np.random.random(3) * 2 - 1  # Random unit vector
        axis = axis / np.linalg.norm(axis)
        
        # Create rotation matrix (Rodrigues' rotation formula)
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])
        R = np.eye(3) + sin_a * K + (1 - cos_a) * (K @ K)
        
        # Random translation
        translation = (np.random.random(3) * 2 - 1) * 0.5  # Small random translation
        
        # Apply transformation to each atom
        for atom in atoms:
            # Translate to origin
            pos = atom['position'] - center
            # Rotate
            pos = R @ pos
            # Translate back and apply random translation
            atom['position'] = pos + center + translation
            
        # Update molecule center
        molecule['center'] = center + translation
        
        # Update grid
        self._update_grid_with_molecule(molecule_id)
    
    def get_molecule_data(self, molecule_id: str) -> Dict:
        """Get data for a molecule"""
        if molecule_id not in self.molecules:
            return {}
            
        molecule = self.molecules[molecule_id]
        
        return {
            'id': molecule_id,
            'atoms': [{
                'element': self._element_from_type(atom['type']),
                'position': atom['position'].tolist(),
                'charge': atom['charge'],
                'radius': atom['radius']
            } for atom in molecule['atoms']],
            'center': molecule['center'].tolist(),
            'energy': molecule['energy']
        }
    
    def _element_from_type(self, atom_type: int) -> str:
        """Convert atom type to element symbol"""
        elements = {
            1: 'H',
            6: 'C',
            7: 'N',
            8: 'O',
            15: 'P',
            16: 'S'
        }
        return elements.get(atom_type, 'X')
    
    def integrate_with_cube(self, cube: StringCube):
        """Integrate molecular data with the quantum string cube"""
        # Map grid data to cube tension field
        if cube.dimension == 3 and cube.resolution == self.resolution:
            # Direct mapping
            cube.tension_field += self.grid * 0.2
        else:
            # Resample grid to match cube resolution
            for i in range(cube.resolution):
                for j in range(cube.resolution):
                    for k in range(cube.resolution):
                        # Map cube coordinates [0,resolution-1] to grid coordinates [0,resolution-1]
                        gi = int(i * self.resolution / cube.resolution)
                        gj = int(j * self.resolution / cube.resolution)
                        gk = int(k * self.resolution / cube.resolution)
                        
                        # Apply grid value to cube tension field
                        if 0 <= gi < self.resolution and 0 <= gj < self.resolution and 0 <= gk < self.resolution:
                            cube.tension_field[i, j, k] += self.grid[gi, gj, gk] * 0.2
        
        # Normalize cube tension field
        max_tension = np.max(cube.tension_field)
        if max_tension > 0:
            cube.tension_field /= max_tension

class MirrorEngine:
    def __init__(self, config: Dict):
        self.config = config
        self.memory_threshold = config['memory_threshold']
        self.insight_buffer = []
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.anomaly_detector = DBSCAN(eps=0.3, min_samples=2)
        self.pattern_evolution = nx.DiGraph()
        self.prediction_model = self._initialize_prediction_model()

    def _initialize_prediction_model(self) -> torch.nn.Module:
        return torch.nn.Sequential(
            torch.nn.LSTM(
                input_size=self.config['input_dim'],
                hidden_size=self.config['hidden_dim'],
                num_layers=2,
                dropout=0.1,
                batch_first=True
            ),
            torch.nn.Linear(self.config['hidden_dim'], self.config['input_dim'])
        ).to(self.device)

    async def generate_perspective(self, data: Dict) -> Dict:
        """Generate perspective from input data"""
        node_data = torch.tensor(data['data']).to(self.device)
        resonance_map = data.get('resonance_map', {})

        # Analyze trends and anomalies
        trends = await self._analyze_trends(node_data)
        anomalies = self._detect_anomalies(node_data)
        
        # Generate predictions
        predictions = await self._generate_predictions(node_data, trends)
        
        # Analyze pattern evolution
        evolution = self._analyze_pattern_evolution(node_data, resonance_map)
        
        # Generate speculative insights
        speculations = await self._generate_speculations(
            node_data, trends, anomalies, predictions, evolution
        )

        return {
            "trends": trends,
            "anomalies": anomalies,
            "predictions": predictions,
            "pattern_evolution": evolution,
            "speculations": speculations,
            "timestamp": time.time()
        }

    async def _analyze_trends(self, data: torch.Tensor) -> Dict:
        """Analyze trends in the data"""
        # Calculate rolling statistics
        window_sizes = [5, 10, 20]
        trends = {}

        for window in window_sizes:
            if data.shape[0] > window:
                rolled = torch.nn.functional.avg_pool1d(
                    data.unsqueeze(0),
                    kernel_size=window,
                    stride=1,
                    padding=window//2
                ).squeeze(0)

                trends[f"window_{window}"] = {
                    "direction": torch.sign(rolled[-1] - rolled[0]).cpu().numpy().tolist(),
                    "strength": torch.abs(rolled[-1] - rolled[0]).cpu().numpy().tolist(),
                }
                
                # Calculate acceleration if enough data points
                if data.shape[0] > window + 2:
                    diffs = torch.diff(rolled, n=2)
                    trends[f"window_{window}"]["acceleration"] = diffs.cpu().numpy().tolist()
        
        return trends

    def _detect_anomalies(self, data: torch.Tensor) -> Dict:
        """Detect anomalies in the data"""
        data_np = data.cpu().numpy()
        
        # Skip if not enough data
        if data_np.shape[0] < 3:
            return {
                "indices": [],
                "scores": [],
                "patterns": [],
                "severity": 0.0
            }
            
        # Fit and predict anomalies
        self.anomaly_detector.fit(data_np)
        labels = self.anomaly_detector.labels_
        anomaly_indices = np.where(labels == -1)[0]
        
        # If no anomalies found with DBSCAN, use simple statistical method
        if len(anomaly_indices) == 0:
            mean = np.mean(data_np, axis=0)
            std = np.std(data_np, axis=0)
            z_scores = np.abs((data_np - mean) / (std + 1e-10))
            mean_z_scores = np.mean(z_scores, axis=1)
            anomaly_indices = np.where(mean_z_scores > 2.0)[0]  # Over 2 standard deviations
        
        # Calculate anomaly scores
        if len(anomaly_indices) > 0:
            # Use distance to nearest non-anomaly as score
            non_anomaly_indices = np.setdiff1d(np.arange(data_np.shape[0]), anomaly_indices)
            if len(non_anomaly_indices) > 0:
                scores = []
                for idx in anomaly_indices:
                    distances = np.linalg.norm(data_np[idx] - data_np[non_anomaly_indices], axis=1)
                    scores.append(float(np.min(distances)))
            else:
                scores = [1.0] * len(anomaly_indices)
                
            severity = float(np.mean(scores))
        else:
            scores = []
            severity = 0.0

        # Characterize anomalies
        anomalies = {
            "indices": anomaly_indices.tolist(),
            "scores": scores,
            "patterns": data_np[anomaly_indices].tolist() if len(anomaly_indices) > 0 else [],
            "severity": severity
        }

        return anomalies

    async def _generate_predictions(self, data: torch.Tensor, trends: Dict) -> Dict:
        """Generate predictions based on data and trends"""
        # Prepare sequence for prediction
        if data.shape[0] < 2:
            return {
                "sequence": [],
                "confidence_intervals": [[], []],
                "uncertainty": 1.0
            }
            
        sequence = data.unsqueeze(0)
        
        # Generate future predictions
        with torch.no_grad():
            predictions = []
            hidden = None
            current = sequence[:, -1:].unsqueeze(1)

            for _ in range(min(self.config.get('prediction_steps', 5), 10)):
                output, hidden = self.prediction_model[0](current, hidden)
                projection = self.prediction_model[1](output)
                predictions.append(projection)
                current = projection.unsqueeze(1)

        predictions = torch.cat(predictions, dim=1).squeeze(0)
        
        # Calculate confidence intervals
        mean = predictions.mean(dim=0)
        std = predictions.std(dim=0)
        
        # Calculate uncertainty
        uncertainty = float(std.mean().item())
        
        # Convert to lists for serialization
        pred_list = predictions.cpu().numpy().tolist()
        mean_list = mean.cpu().numpy().tolist()
        std_list = std.cpu().numpy().tolist()
        
        # Create confidence intervals
        lower_bound = [m - 1.96 * s for m, s in zip(mean_list, std_list)]
        upper_bound = [m + 1.96 * s for m, s in zip(mean_list, std_list)]

        return {
            "sequence": pred_list,
            "confidence_intervals": [lower_bound, upper_bound],
            "uncertainty": uncertainty
        }

    def _analyze_pattern_evolution(self, data: torch.Tensor, resonance_map: Dict) -> Dict:
        """Analyze how patterns evolve over time"""
        # Extract pattern transitions
        transitions = []
        resonance_values = list(resonance_map.values()) if resonance_map else []
        
        if len(resonance_values) > 1:
            for i in range(len(resonance_values) - 1):
                transitions.append({
                    "from_resonance": resonance_values[i],
                    "to_resonance": resonance_values[i + 1],
                    "delta": resonance_values[i + 1] - resonance_values[i]
                })

            # Update pattern evolution graph
            for i, t in enumerate(transitions):
                self.pattern_evolution.add_edge(
                    f"state_{len(self.pattern_evolution)}",
                    f"state_{len(self.pattern_evolution) + 1}",
                    weight=t["delta"],
                    resonance_change=t["delta"]
                )

            # Calculate evolution metrics
            deltas = [t["delta"] for t in transitions]
            metrics = {
                "stability": float(np.std(deltas)),
                "trend": float(np.mean(deltas))
            }
            
            # Add acceleration metric if enough data points
            if len(deltas) > 1:
                accel = np.diff(deltas)
                metrics["acceleration"] = float(np.mean(accel))
            else:
                metrics["acceleration"] = 0.0
        else:
            # Default metrics when not enough data
            transitions = []
            metrics = {
                "stability": 1.0,
                "trend": 0.0,
                "acceleration": 0.0
            }

        return {
            "transitions": transitions,
            "metrics": metrics,
            "graph_stats": {k: v for k, v in nx.info(self.pattern_evolution).items()} if hasattr(nx, "info") else {}
        }

    async def _generate_speculations(
        self,
        data: torch.Tensor,
        trends: Dict,
        anomalies: Dict,
        predictions: Dict,
        evolution: Dict
    ) -> List[Dict]:
        """Generate speculative insights based on patterns"""
        speculations = []

        # Analyze trend stability
        trend_stability = 0.3  # Default value
        if trends:
            stabilities = []
            for window_key, window_data in trends.items():
                if "strength" in window_data and isinstance(window_data["strength"], list) and window_data["strength"]:
                    stabilities.append(np.std(window_data["strength"]))
            if stabilities:
                trend_stability = np.mean(stabilities)

        # Generate speculative insights based on patterns
        if trend_stability < 0.3:  # Stable trends
            speculations.append({
                "type": "continuation",
                "confidence": 0.8,
                "description": "Pattern shows strong stability, likely to continue",
                "supporting_evidence": {
                    "trend_stability": float(trend_stability),
                    "prediction_uncertainty": predictions.get("uncertainty", 1.0)
                }
            })

        # Analyze potential disruptions
        anomaly_severity = anomalies.get("severity", 0.0)
        if anomaly_severity > 0.7:
            speculations.append({
                "type": "disruption",
                "confidence": anomaly_severity,
                "description": "Significant anomalies detected, pattern disruption likely",
                "supporting_evidence": {
                    "anomaly_severity": anomaly_severity,
                    "pattern_evolution": evolution.get("metrics", {})
                }
            })

        # Analyze cyclical patterns
        if self._detect_cycles(evolution.get("transitions", [])):
            speculations.append({
                "type": "cyclical",
                "confidence": 0.6,
                "description": "Cyclical pattern detected, expect repetition",
                "supporting_evidence": {
                    "transitions": evolution.get("transitions", [])[-5:] if evolution.get("transitions") else [],
                    "cycle_metrics": self._calculate_cycle_metrics(evolution.get("transitions", []))
                }
            })

        return speculations

    def _detect_cycles(self, transitions: List[Dict]) -> bool:
        """Detect if there are cycles in the transitions"""
        if len(transitions) < 4:
            return False

        # Extract deltas for analysis
        deltas = [t.get("delta", 0) for t in transitions]
        
        # Autocorrelation to detect cycles
        if len(deltas) > 1:
            autocorr = np.correlate(deltas, deltas, mode='full')
            center = len(autocorr) // 2
            autocorr = autocorr[center:]  # Take only the second half
            
            # Find peaks in autocorrelation
            peaks = []
            for i in range(1, len(autocorr)-1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    peaks.append(i)
            
            # If we have multiple peaks, we might have a cycle
            return len(peaks) > 1
        return False

    def _calculate_cycle_metrics(self, transitions: List[Dict]) -> Dict:
        """Calculate metrics for detected cycles"""
        if len(transitions) < 2:
            return {
                "period": 0.0,
                "strength": 0.0,
                "regularity": 0.0
            }
            
        deltas = [t.get("delta", 0) for t in transitions]
        autocorr = np.correlate(deltas, deltas, mode='full')
        center = len(autocorr) // 2
        autocorr = autocorr[center:]  # Take only the second half
        
        # Find peaks
        peaks = []
        for i in range(1, len(autocorr)-1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                peaks.append(i)
        
        if peaks:
            period = np.mean(np.diff(peaks)) if len(peaks) > 1 else 0.0
            strength = np.mean([autocorr[p] for p in peaks]) / autocorr[0] if autocorr[0] != 0 else 0.0
            regularity = np.std(np.diff(peaks)) / period if len(peaks) > 1 and period > 0 else 1.0
        else:
            period = 0.0
            strength = 0.0
            regularity = 1.0
            
        return {
            "period": float(period),
            "strength": float(strength),
            "regularity": float(regularity)
        }