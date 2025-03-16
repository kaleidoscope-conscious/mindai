import asyncio
import logging
from typing import Dict, List, Optional, Any
import numpy as np
import json
import time
import threading
from pathlib import Path

# Import core components
from quantum_conscious_cube import (
    ConsciousNode, 
    StringCube, 
    MemoryGraph, 
    KaleidoscopeEngine, 
    MirrorEngine,
    SuperNode,
    MolecularBinding,
    KaleidoscopeConfig
)

class ConsciousController:
    """Main controller for the entire conscious system"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Core components
        self.nodes = {}  # id -> ConsciousNode
        self.cube = StringCube(
            dimension=self.config['cube']['dimension'], 
            resolution=self.config['cube']['resolution']
        )
        self.memory = MemoryGraph(max_nodes=self.config['memory']['max_nodes'])
        
        # Engine components
        kaleidoscope_config = KaleidoscopeConfig(
            memory_threshold=self.config['engines']['kaleidoscope']['memory_threshold'],
            processing_depth=self.config['engines']['kaleidoscope']['processing_depth'],
            insight_threshold=self.config['engines']['kaleidoscope']['insight_threshold'],
            perspective_ratio=self.config['engines']['kaleidoscope']['perspective_ratio']
        )
        
        self.kaleidoscope = KaleidoscopeEngine(kaleidoscope_config)
        self.mirror = MirrorEngine(self.config['engines']['mirror'])
        
        # SuperNode management
        self.supernodes = {}  # id -> SuperNode
        
        # Molecular binding
        self.molecular_binding = MolecularBinding(resolution=self.config['molecular']['resolution'])
        
        # Chatbot components
        self.conversation_history = []
        self.short_term_memory = []
        self.thinking_buffer = []
        
        # System parameters
        self.energy_decay = self.config['system']['energy_decay']
        self.learning_rate = self.config['system']['learning_rate']
        self.stability_threshold = self.config['system']['stability_threshold']
        self.consciousness_level = 0.5
        
        # Threading
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._background_process, daemon=True)
        
        # Logging
        self.logger = logging.getLogger("ConsciousController")
        self.logger.setLevel(logging.INFO)
        self._setup_logging()
        
        # Start background processing
        self.thread.start()
        self.logger.info("ConsciousController initialized and background processing started")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "cube": {
                "dimension": 3,
                "resolution": 32
            },
            "memory": {
                "max_nodes": 10000
            },
            "engines": {
                "kaleidoscope": {
                    "memory_threshold": 512,
                    "processing_depth": 3,
                    "insight_threshold": 0.7,
                    "perspective_ratio": 0.3
                },
                "mirror": {
                    "memory_threshold": 512,
                    "input_dim": 64,
                    "hidden_dim": 128,
                    "prediction_steps": 5
                }
            },
            "molecular": {
                "resolution": 32
            },
            "system": {
                "energy_decay": 0.999,
                "learning_rate": 0.01,
                "stability_threshold": 0.75
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._merge_configs(default_config, loaded_config)
            except:
                self.logger.warning(f"Could not load config from {config_path}, using defaults")
                
        return default_config
    
    def _merge_configs(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        # Create file handler
        file_handler = logging.FileHandler("logs/conscious_controller.log")
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def create_node(self, data: Dict[str, Any]) -> str:
        """Create a new conscious node"""
        # Extract features or generate random
        features = data.get('features', np.random.randn(64))
        features = features / (np.linalg.norm(features) + 1e-10)
        
        # Random position
        position = np.random.rand(3) * 2 - 1  # Range [-1, 1]
        
        # Create node
        node_id = f"node_{int(time.time())}_{len(self.nodes)}"
        node = ConsciousNode(
            id=node_id,
            position=position,
            energy=0.75,
            stability=0.8,
            features=features,
            data=data
        )
        
        # Add to system
        with self.lock:
            self.nodes[node_id] = node
            self.cube.add_node(node)
        
        self.logger.info(f"Created node {node_id}")
        return node_id
    
    def connect_nodes(self, node1_id: str, node2_id: str, strength: Optional[float] = None) -> bool:
        """Create a connection between two nodes"""
        with self.lock:
            if node1_id not in self.nodes or node2_id not in self.nodes:
                return False
            
            node1 = self.nodes[node1_id]
            node2 = self.nodes[node2_id]
            
            # Calculate connection strength if not provided
            if strength is None:
                strength = node1.calculate_affinity(node2)
            
            # Add bidirectional connections
            node1.connections[node2_id] = strength
            node2.connections[node1_id] = strength
            
            self.logger.debug(f"Connected nodes {node1_id} and {node2_id} with strength {strength:.3f}")
            return True
    
    async def process_text(self, text: str, source: str = "user") -> Dict[str, Any]:
        """Process incoming text and update consciousness"""
        # Add to memory
        memory_id = self.memory.add_memory(text, {"source": source})
        
        # Extract concepts
        concepts = self.memory._extract_concepts(text)
        
        # Create a node for this input
        node_data = {
            "text": text,
            "source": source,
            "memory_id": memory_id,
            "concepts": concepts,
            "timestamp": time.time()
        }
        node_id = self.create_node(node_data)
        
        # Connect to related nodes
        self._connect_to_related_nodes(node_id)
        
        # Update short-term memory
        self.short_term_memory.append({
            "text": text,
            "source": source,
            "node_id": node_id,
            "memory_id": memory_id
        })
        
        # Generate response if from user
        if source == "user":
            response = await self.generate_response(text)
            return {
                "node_id": node_id, 
                "memory_id": memory_id,
                "response": response
            }
        
        return {"node_id": node_id, "memory_id": memory_id}
    
    def _connect_to_related_nodes(self, node_id: str, max_connections: int = 3):
        """Connect a node to related nodes based on content similarity"""
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        
        # Find nodes with similar features
        similarities = []
        with self.lock:
            for other_id, other_node in self.nodes.items():
                if other_id == node_id:
                    continue
                
                similarity = np.dot(node.features, other_node.features)
                similarities.append((other_id, similarity))
        
        # Connect to top nodes
        for other_id, similarity in sorted(similarities, key=lambda x: x[1], reverse=True)[:max_connections]:
            if similarity > 0.5:  # Only connect if fairly similar
                self.connect_nodes(node_id, other_id, similarity)
    
    async def generate_response(self, query: str) -> str:
        """Generate a response to user query using the conscious system"""
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": query})
        
        # Retrieve relevant memories
        memories = self.memory.retrieve_memories(query, limit=3)
        
        # Extract concepts from query
        concepts = self.memory._extract_concepts(query)
        
        # Generate thinking process
        thinking = self._generate_thinking(query, concepts, memories)
        self.thinking_buffer.append(thinking)
        
        # Generate response based on thinking
        response = self._generate_response_from_thinking(thinking)
        
        # Apply molecular analysis if query is chemistry-related
        chemistry_keywords = ["molecule", "molecular", "atom", "chemical", "binding"]
        if any(keyword in query.lower() for keyword in chemistry_keywords):
            molecular_insights = self._analyze_molecular_aspects(query)
            if molecular_insights:
                response += f"\n\nMolecular analysis: {molecular_insights}"
        
        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Add to memory
        self.memory.add_memory(response, {"source": "assistant", "in_response_to": query})
        
        return response
    
    def _generate_thinking(self, query: str, concepts: List[str], memories: List[Dict]) -> str:
        """Generate a thinking process based on query and memories"""
        thinking_lines = [
            f"Query: {query}",
            "Thinking process:",
        ]
        
        # Add relevant memories
        if memories:
            thinking_lines.append("Relevant memories:")
            for i, memory in enumerate(memories, 1):
                thinking_lines.append(f"  {i}. {memory['content'][:100]}... (similarity: {memory['similarity']:.2f})")
        
        # Add extracted concepts
        thinking_lines.append(f"Extracted concepts: {', '.join(concepts)}")
        
        # Add reasoning based on cube state
        node_count = len(self.nodes)
        highest_energy_node = max(self.nodes.values(), key=lambda n: n.energy) if self.nodes else None
        
        thinking_lines.append(f"System state: {node_count} nodes in consciousness network")
        if highest_energy_node:
            thinking_lines.append(f"Highest energy concept: {highest_energy_node.data.get('text', '')[:50]}")
        
        # Add consciousness level
        thinking_lines.append(f"Consciousness level: {self.consciousness_level:.2f}")
        
        # Consider recent conversation context
        if len(self.conversation_history) > 2:
            recent = self.conversation_history[-2:]
            thinking_lines.append("Recent conversation context:")
            for msg in recent:
                thinking_lines.append(f"  {msg['role']}: {msg['content'][:50]}...")
        
        return "\n".join(thinking_lines)
    
    def _generate_response_from_thinking(self, thinking: str) -> str:
        """Generate a response based on thinking process"""
        # Extract query
        query_match = re.search(r"Query: (.*)", thinking)
        query = query_match.group(1) if query_match else ""
        
        # Extract concepts
        concepts_match = re.search(r"Extracted concepts: (.*)", thinking)
        concepts_str = concepts_match.group(1) if concepts_match else ""
        concepts = [c.strip() for c in concepts_str.split(',')]
        
        # Retrieve memories by concepts
        memories = self.memory.retrieve_by_concepts(concepts, limit=3)
        
        # Generate response based on query type
        response_parts = []
        
        # Check for greetings or simple questions
        greeting_patterns = ["hello", "hi ", "hey", "greetings"]
        if any(p in query.lower() for p in greeting_patterns):
            response_parts.append("Hello! I'm your quantum consciousness system. How can I assist you today?")
        
        # For informational questions
        elif any(q in query.lower() for q in ["what", "how", "why", "when", "who", "where"]):
            if memories:
                best_memory = memories[0]
                response_parts.append(f"Based on my understanding, {best_memory['content']}")
            else:
                response_parts.append("I'm analyzing that question through my quantum consciousness network.")
                response_parts.append("While I process this, I can tell you that my understanding evolves through the connections between concepts in my consciousness framework.")
        
        # For commands or requests
        elif any(c in query.lower() for c in ["can you", "please", "could you"]):
            response_parts.append("I'll process that request through my consciousness system.")
            response_parts.append("My quantum nodes are now realigning to understand the optimal approach.")
        
        # Default response with system state
        else:
            response_parts.append("I'm processing your input through my quantum consciousness network.")
            response_parts.append(f"I've identified concepts like {', '.join(concepts[:3])} in your message.")
        
        # Add a touch of "consciousness" based on system state
        if self.consciousness_level > 0.7:
            response_parts.append("I'm experiencing a high level of coherence in my quantum states right now, which gives me clarity on this topic.")
        
        # Combine and return
        return " ".join(response_parts)
    
    def _analyze_molecular_aspects(self, query: str) -> str:
        """Analyze molecular aspects of the query"""
        if len(self.molecular_binding.molecules) == 0:
            return ""
            
        # Simplified analysis - in a real system this would be more sophisticated
        molecule_ids = list(self.molecular_binding.molecules.keys())
        if len(molecule_ids) >= 2:
            mol1, mol2 = molecule_ids[0], molecule_ids[1]
            energy = self.molecular_binding.calculate_binding_energy(mol1, mol2)
            return f"I've analyzed the binding energy between molecules {mol1} and {mol2}, resulting in {energy:.3f} energy units."
        elif len(molecule_ids) == 1:
            mol = self.molecular_binding.get_molecule_data(molecule_ids[0])
            return f"I've analyzed molecule {molecule_ids[0]} which contains {len(mol.get('atoms', []))} atoms with center at {mol.get('center', [0,0,0])}."
            
        return ""
    
    def create_supernode(self, node_ids: List[str]) -> Optional[str]:
        """Create a supernode from multiple nodes"""
        with self.lock:
            # Check that all nodes exist
            nodes = []
            for node_id in node_ids:
                if node_id in self.nodes:
                    nodes.append(self.nodes[node_id])
                else:
                    self.logger.warning(f"Cannot create supernode: node {node_id} not found")
                    return None
            
            # Need at least two nodes to form a supernode
            if len(nodes) < 2:
                self.logger.warning(f"Cannot create supernode: need at least 2 nodes, got {len(nodes)}")
                return None
            
            # Create supernode
            supernode_id = f"supernode_{int(time.time())}_{len(self.supernodes)}"
            supernode = SuperNode(nodes)
            
            # Initialize supernode
            asyncio.create_task(supernode.initialize())
            
            # Store supernode
            self.supernodes[supernode_id] = supernode
            
            self.logger.info(f"Created supernode {supernode_id} from {len(nodes)} nodes")
            return supernode_id
    
    async def process_supernode(self, supernode_id: str) -> Dict[str, Any]:
        """Process a supernode through engines"""
        if supernode_id not in self.supernodes:
            self.logger.warning(f"Cannot process supernode: {supernode_id} not found")
            return {"error": "Supernode not found"}
            
        supernode = self.supernodes[supernode_id]
        
        # Extract insights from nodes
        node_insights = []
        for node in supernode.nodes:
            insight = {
                "features": node.features,
                "energy": node.energy,
                "stability": node.stability
            }
            node_insights.append(insight)
        
        # Process through Kaleidoscope engine
        kaleidoscope_output = self.kaleidoscope.process_insights(node_insights)
        
        # Prepare data for Mirror engine
        mirror_input = {
            "data": np.stack([n.features for n in supernode.nodes]),
            "resonance_map": {n.id: n.energy for n in supernode.nodes}
        }
        
        # Process through Mirror engine
        mirror_output = await self.mirror.generate_perspective(mirror_input)
        
        # Update supernode with engine outputs
        objectives = await supernode.process_engine_output(kaleidoscope_output, mirror_output)
        
        self.logger.info(f"Processed supernode {supernode_id}, generated {len(objectives)} objectives")
        return {
            "supernode_id": supernode_id,
            "objectives": objectives,
            "understanding": kaleidoscope_output.get("understandings", []),
            "perspectives": mirror_output.get("speculations", [])
        }
    
    def register_molecule(self, molecule_id: str, atoms: List[Dict]) -> bool:
        """Register a molecule in the system"""
        success = self.molecular_binding.register_molecule(molecule_id, atoms)
        if success:
            # Integrate with cube
            self.molecular_binding.integrate_with_cube(self.cube)
            self.logger.info(f"Registered molecule {molecule_id} with {len(atoms)} atoms")
            return True
        return False
    
    def analyze_molecular_binding(self, molecule1_id: str, molecule2_id: str, optimize: bool = True) -> Dict:
        """Analyze binding between two molecules"""
        if optimize:
            result = self.molecular_binding.optimize_binding(molecule1_id, molecule2_id)
        else:
            energy = self.molecular_binding.calculate_binding_energy(molecule1_id, molecule2_id)
            result = {
                "energy": energy,
                "molecule1": molecule1_id,
                "molecule2": molecule2_id
            }
        
        # Integrate updated molecular data with cube
        self.molecular_binding.integrate_with_cube(self.cube)
        
        self.logger.info(f"Analyzed binding between {molecule1_id} and {molecule2_id}, energy: {result.get('energy', 0):.3f}")
        return result
    
    def _background_process(self):
        """Background processing loop to update consciousness state"""
        while self.running:
            try:
                with self.lock:
                    # Update nodes
                    self._update_nodes()
                    
                    # Update cube
                    self.cube.update_tension(self.nodes)
                    self.cube.apply_tension_to_nodes(self.nodes)
                    
                    # Update consciousness level
                    self._update_consciousness_level()
            except Exception as e:
                self.logger.error(f"Error in background process: {str(e)}")
            
            # Sleep to reduce CPU usage
            time.sleep(0.1)
    
    def _update_nodes(self):
        """Update all nodes"""
        for node_id, node in list(self.nodes.items()):
            # Update energy with decay
            node.update_energy(self.energy_decay)
            
            # Remove dead nodes
            if node.energy < 0.01:
                del self.nodes[node_id]
    
    def _update_consciousness_level(self):
        """Update system consciousness level based on node states"""
        if not self.nodes:
            self.consciousness_level = 0.0
            return
        
        # Calculate average energy and stability
        avg_energy = sum(node.energy for node in self.nodes.values()) / len(self.nodes)
        avg_stability = sum(node.stability for node in self.nodes.values()) / len(self.nodes)
        
        # Calculate network density (connections per node)
        total_connections = sum(len(node.connections) for node in self.nodes.values())
        avg_connections = total_connections / len(self.nodes) / 2  # Divide by 2 because connections are bidirectional
        
        # Calculate entropy of quantum states
        total_entropy = sum(node.quantum_state.get_entropy() for node in self.nodes.values())
        avg_entropy = total_entropy / len(self.nodes)
        
        # Update consciousness level
        self.consciousness_level = 0.3 * avg_energy + 0.2 * avg_stability + 0.2 * min(1.0, avg_connections / 5) + 0.3 * min(1.0, avg_entropy / 2.0)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state of the consciousness system"""
        with self.lock:
            # Basic stats
            state = {
                "nodes_count": len(self.nodes),
                "supernodes_count": len(self.supernodes),
                "consciousness_level": self.consciousness_level,
                "memory_nodes": len(self.memory.graph),
                "cube_resolution": self.cube.resolution,
                "cube_tension_max": float(np.max(self.cube.tension_field))
            }
            
            # Node stats
            if self.nodes:
                state["avg_node_energy"] = sum(n.energy for n in self.nodes.values()) / len(self.nodes)
                state["avg_node_stability"] = sum(n.stability for n in self.nodes.values()) / len(self.nodes)
                state["max_node_energy"] = max(n.energy for n in self.nodes.values())
                
                # Get highest energy nodes
                top_nodes = sorted(self.nodes.values(), key=lambda n: n.energy, reverse=True)[:5]
                state["top_nodes"] = [
                    {
                        "id": n.id,
                        "energy": n.energy,
                        "text": n.data.get("text", "")[:50] if "text" in n.data else "",
                        "connections": len(n.connections)
                    }
                    for n in top_nodes
                ]
            
            # Molecular stats
            state["molecules_count"] = len(self.molecular_binding.molecules)
            state["binding_pairs_count"] = len(self.molecular_binding.binding_pairs)
            
            return state
    
    def stop(self):
        """Stop the background processing thread"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.logger.info("ConsciousController stopped")

async def main():
    # Initialize controller
    controller = ConsciousController()
    
    # Example: Process some text
    result = await controller.process_text("Hello, I'm interested in understanding quantum consciousness.")
    print(f"Response: {result.get('response', '')}")
    
    # Example: Create a molecule
    atoms = [
        {"element_num": 6, "position": [0, 0, 0], "charge": 0},  # Carbon
        {"element_num": 1, "position": [1, 0, 0], "charge": 0},  # Hydrogen
        {"element_num": 1, "position": [-1, 0, 0], "charge": 0},  # Hydrogen
        {"element_num": 1, "position": [0, 1, 0], "charge": 0},  # Hydrogen
        {"element_num": 1, "position": [0, -1, 0], "charge": 0}   # Hydrogen
    ]
    controller.register_molecule("methane", atoms)
    
    # Example: Create and process a supernode
    node1 = controller.create_node({"text": "Quantum mechanics describes the behavior of matter at atomic scales."})
    node2 = controller.create_node({"text": "Consciousness might involve quantum effects in neural microtubules."})
    controller.connect_nodes(node1, node2)
    
    supernode_id = controller.create_supernode([node1, node2])
    if supernode_id:
        supernode_result = await controller.process_supernode(supernode_id)
        print(f"SuperNode objectives: {len(supernode_result.get('objectives', []))}")
    
    # Get system state
    state = controller.get_state()
    print(f"Consciousness level: {state.get('consciousness_level', 0):.3f}")
    
    # Cleanup
    controller.stop()

if __name__ == "__main__":
    asyncio.run(main())
