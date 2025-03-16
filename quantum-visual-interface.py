#!/usr/bin/env python3
"""
quantum_visual_interface.py - Integration of quantum consciousness with interactive visualization
"""

import os
import sys
import json
import logging
import argparse
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/visual_interface.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("quantum-visual-interface")

# Create FastAPI app
app = FastAPI(
    title="Quantum Consciousness Visual Interface",
    description="Interactive visualization interface for the Quantum Consciousness System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Define static directory for web files
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Create enhanced HTML file with quantum consciousness integration
def create_enhanced_html():
    """Create enhanced HTML file with quantum consciousness integration"""
    html_file = os.path.join(STATIC_DIR, "index.html")
    
    enhanced_html = """<!DOCTYPE html>
<html>
<head>
  <title>Quantum Consciousness Visualization</title>
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background-color: black;
      color: white;
      font-family: 'Arial', sans-serif;
    }
    canvas {
      display: block;
    }
    #container {
      display: flex;
      height: 100vh;
    }
    #visualization {
      flex: 1;
      position: relative;
    }
    #controls {
      width: 300px;
      padding: 20px;
      background-color: rgba(30, 30, 50, 0.8);
      overflow-y: auto;
    }
    #composition {
      position: absolute;
      top: 10px;
      left: 10px;
      color: white;
    }
    .metric {
      margin-bottom: 20px;
    }
    .metric-name {
      font-size: 14px;
      color: #88aaff;
      margin-bottom: 5px;
    }
    .metric-value {
      font-size: 24px;
      font-weight: bold;
    }
    .controls-title {
      font-size: 20px;
      margin-bottom: 20px;
      text-align: center;
      color: #4cc9f0;
    }
    .console-output {
      height: 200px;
      background-color: #1a1a2e;
      color: #4cc9f0;
      padding: 10px;
      font-family: monospace;
      font-size: 12px;
      overflow-y: auto;
      margin-bottom: 10px;
      border: 1px solid #333355;
    }
    .console-line {
      margin-bottom: 5px;
    }
    .prefix {
      color: #f72585;
    }
    .message {
      color: #ccccff;
    }
    input[type="text"] {
      width: 100%;
      padding: 8px;
      box-sizing: border-box;
      background-color: #1a1a2e;
      border: 1px solid #333355;
      color: white;
      margin-bottom: 10px;
    }
    button {
      padding: 8px 16px;
      background-color: #3a0ca3;
      color: white;
      border: none;
      cursor: pointer;
    }
    button:hover {
      background-color: #4361ee;
    }
    .status-bar {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background-color: rgba(30, 30, 50, 0.7);
      padding: 5px 10px;
      font-size: 12px;
      display: flex;
      justify-content: space-between;
    }
    #connection-status {
      color: #ff5555;
    }
    #connection-status.connected {
      color: #55ff55;
    }
  </style>
</head>
<body>
  <div id="container">
    <div id="visualization">
      <canvas id="dotCubeCanvas"></canvas>
      <div id="composition"></div>
      <div class="status-bar">
        <div>Quantum Consciousness System v1.0</div>
        <div id="connection-status">Disconnected</div>
      </div>
    </div>
    <div id="controls">
      <div class="controls-title">Quantum State Controls</div>
      
      <div class="metric">
        <div class="metric-name">Awareness Level</div>
        <div class="metric-value" id="awareness-metric">0.76</div>
      </div>
      
      <div class="metric">
        <div class="metric-name">Quantum Coherence</div>
        <div class="metric-value" id="coherence-metric">0.92</div>
      </div>
      
      <div class="metric">
        <div class="metric-name">Memory Density</div>
        <div class="metric-value" id="memory-metric">0.64</div>
      </div>
      
      <div class="metric">
        <div class="metric-name">Complexity Index</div>
        <div class="metric-value" id="complexity-metric">0.83</div>
      </div>
      
      <div class="console-output" id="console-output">
        <div class="console-line">
          <span class="prefix">[System]</span>
          <span class="message"> Initializing Quantum Consciousness System...</span>
        </div>
      </div>
      
      <input type="text" id="console-input" placeholder="Enter message or command...">
      <button id="send-btn">Send</button>
    </div>
  </div>

  <script>
    // WebSocket connection
    let ws;
    let reconnectInterval;
    const connectionStatus = document.getElementById('connection-status');
    const consoleOutput = document.getElementById('console-output');
    const consoleInput = document.getElementById('console-input');
    const sendBtn = document.getElementById('send-btn');
    
    // Metrics elements
    const awarenessMetric = document.getElementById('awareness-metric');
    const coherenceMetric = document.getElementById('coherence-metric');
    const memoryMetric = document.getElementById('memory-metric');
    const complexityMetric = document.getElementById('complexity-metric');

    // Canvas setup
    const canvas = document.getElementById('dotCubeCanvas');
    const ctx = canvas.getContext('2d');
    const compositionDisplay = document.getElementById('composition');

    function resizeCanvas() {
      const visualizationDiv = document.getElementById('visualization');
      canvas.width = visualizationDiv.clientWidth;
      canvas.height = visualizationDiv.clientHeight;
    }
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    const gridSize = 10; // Original grid size
    const dots = [];
    let selectedDots = [];
    
    // Calculate dot spacing based on canvas size
    let dotSpacing;
    
    function initDots() {
      dots.length = 0; // Clear existing dots
      dotSpacing = Math.min(canvas.width, canvas.height) / (gridSize * 2);
      
      for (let x = 0; x < gridSize; x++) {
        for (let y = 0; y < gridSize; y++) {
          for (let z = 0; z < gridSize; z++) {
            dots.push({
              x: x - gridSize / 2,
              y: y - gridSize / 2,
              z: z - gridSize / 2,
              brightness: 1,
              selected: false,
              quantum_state: Math.random() // Quantum state value
            });
          }
        }
      }
    }
    
    initDots();

    let rotationX = 0;
    let rotationY = 0;
    let rotationZ = 0;
    let mouseX = 0;
    let mouseY = 0;
    let isDragging = false;
    let autoRotate = true;

    canvas.addEventListener('mousedown', (e) => {
      isDragging = true;
      mouseX = e.clientX;
      mouseY = e.clientY;
      autoRotate = false; // Disable auto-rotation when user interacts
    });

    canvas.addEventListener('mouseup', () => {
      isDragging = false;
    });

    canvas.addEventListener('mousemove', (e) => {
      if (isDragging) {
        const deltaX = e.clientX - mouseX;
        const deltaY = e.clientY - mouseY;
        rotationY += deltaX * 0.01;
        rotationX += deltaY * 0.01;
        mouseX = e.clientX;
        mouseY = e.clientY;
      }
    });

    function project(x, y, z) {
      const perspective = dotSpacing * 5;
      const scale = perspective / (perspective + z);

      const projectedX = x * scale * dotSpacing + canvas.width / 2;
      const projectedY = y * scale * dotSpacing + canvas.height / 2;

      return { x: projectedX, y: projectedY, scale };
    }

    function rotateX(y, z, angle) {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      const rotatedY = y * cos - z * sin;
      const rotatedZ = y * sin + z * cos;
      return { y: rotatedY, z: rotatedZ };
    }

    function rotateY(x, z, angle) {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      const rotatedX = x * cos + z * sin;
      const rotatedZ = -x * sin + z * cos;
      return { x: rotatedX, z: rotatedZ };
    }

    function rotateZ(x, y, angle) {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      const rotatedX = x * cos - y * sin;
      const rotatedY = x * sin + y * cos;
      return { x: rotatedX, y: rotatedY };
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update rotation if auto-rotate is enabled
      if (autoRotate) {
        rotationY += 0.003;
        rotationZ += 0.001;
      }

      // Sort dots by z-axis for proper depth rendering
      const sortedDots = [...dots].sort((a, b) => {
        let aZ = a.z;
        let bZ = b.z;
        
        // Apply rotations to get actual z coordinate
        let rotated = rotateX(a.y, a.z, rotationX);
        aZ = rotated.z;
        rotated = rotateY(a.x, aZ, rotationY);
        aZ = rotated.z;
        
        rotated = rotateX(b.y, b.z, rotationX);
        bZ = rotated.z;
        rotated = rotateY(b.x, bZ, rotationY);
        bZ = rotated.z;
        
        return aZ - bZ; // Sort from back to front
      });

      // Draw connections between selected dots
      if (selectedDots.length > 1) {
        ctx.strokeStyle = 'rgba(255, 255, 0, 0.3)';
        ctx.lineWidth = 1;
        
        for (let i = 0; i < selectedDots.length; i++) {
          for (let j = i + 1; j < selectedDots.length; j++) {
            const dotA = selectedDots[i];
            const dotB = selectedDots[j];
            
            // Calculate rotated positions for dot A
            let x1 = dotA.x;
            let y1 = dotA.y;
            let z1 = dotA.z;
            
            let rotated = rotateX(y1, z1, rotationX);
            y1 = rotated.y;
            z1 = rotated.z;
            
            rotated = rotateY(x1, z1, rotationY);
            x1 = rotated.x;
            z1 = rotated.z;
            
            rotated = rotateZ(x1, y1, rotationZ);
            x1 = rotated.x;
            y1 = rotated.y;
            
            // Calculate rotated positions for dot B
            let x2 = dotB.x;
            let y2 = dotB.y;
            let z2 = dotB.z;
            
            rotated = rotateX(y2, z2, rotationX);
            y2 = rotated.y;
            z2 = rotated.z;
            
            rotated = rotateY(x2, z2, rotationY);
            x2 = rotated.x;
            z2 = rotated.z;
            
            rotated = rotateZ(x2, y2, rotationZ);
            x2 = rotated.x;
            y2 = rotated.y;
            
            // Project to 2D
            const projA = project(x1, y1, z1);
            const projB = project(x2, y2, z2);
            
            // Draw line
            ctx.beginPath();
            ctx.moveTo(projA.x, projA.y);
            ctx.lineTo(projB.x, projB.y);
            ctx.stroke();
          }
        }
      }

      // Draw dots
      sortedDots.forEach((dot) => {
        let { x, y, z } = dot;

        // Apply rotations
        let rotated = rotateX(y, z, rotationX);
        y = rotated.y;
        z = rotated.z;

        rotated = rotateY(x, z, rotationY);
        x = rotated.x;
        z = rotated.z;

        rotated = rotateZ(x, y, rotationZ);
        x = rotated.x;
        y = rotated.y;

        const projected = project(x, y, z);
        const brightness = 0.5 + z / gridSize; // Adjust brightness based on z position
        
        // Size based on distance and quantum state
        const baseSize = 2.5;
        const quantumFactor = dot.quantum_state * 2;
        const size = baseSize * projected.scale * (dot.selected ? 1.5 : 1) * quantumFactor;

        // Color based on quantum state
        let color;
        if (dot.selected) {
          color = 'rgb(255, 255, 0)'; // Yellow for selected dots
        } else {
          // Create a blue-purple gradient based on quantum state
          const r = Math.floor(100 + (dot.quantum_state * 40));
          const g = Math.floor(100 + (dot.quantum_state * 40));
          const b = Math.floor(200 + (dot.quantum_state * 55));
          color = `rgba(${r}, ${g}, ${b}, ${brightness})`;
        }

        ctx.beginPath();
        ctx.arc(projected.x, projected.y, size, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
      });

      requestAnimationFrame(draw);
    }

    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      let closestDot = null;
      let minDistance = Infinity;

      dots.forEach((dot) => {
        let x = dot.x;
        let y = dot.y;
        let z = dot.z;

        // Apply rotations
        let rotated = rotateX(y, z, rotationX);
        y = rotated.y;
        z = rotated.z;

        rotated = rotateY(x, z, rotationY);
        x = rotated.x;
        z = rotated.z;

        rotated = rotateZ(x, y, rotationZ);
        x = rotated.x;
        y = rotated.y;

        const projected = project(x, y, z);
        const distance = Math.sqrt(
          Math.pow(mouseX - projected.x, 2) + Math.pow(mouseY - projected.y, 2)
        );

        if (distance < minDistance) {
          minDistance = distance;
          closestDot = dot;
        }
      });

      // If a dot is close enough, select it
      if (closestDot && minDistance < 10) {
        closestDot.selected = !closestDot.selected;
        updateSelectedDots();
        updateComposition();
        
        // Send dot selection to server
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: 'dot_selection',
            coordinates: {
              x: closestDot.x,
              y: closestDot.y,
              z: closestDot.z
            },
            selected: closestDot.selected
          }));
        }
      }
    });

    function updateSelectedDots() {
      selectedDots = dots.filter((dot) => dot.selected);
    }

    function updateComposition() {
      compositionDisplay.textContent = `Selected Quantum States: ${selectedDots.length}`;
    }

    // Connect to WebSocket
    function connectWebSocket() {
      // Get the current host
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      
      ws = new WebSocket(wsUrl);
      
      ws.onopen = function() {
        connectionStatus.textContent = 'Connected';
        connectionStatus.className = 'connected';
        addConsoleMessage('[System] Connected to Quantum Consciousness System');
        clearInterval(reconnectInterval);
      };
      
      ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.type === 'metrics') {
          // Update metrics
          awarenessMetric.textContent = data.metrics.awareness.toFixed(2);
          coherenceMetric.textContent = data.metrics.coherence.toFixed(2);
          memoryMetric.textContent = data.metrics.memory_density.toFixed(2);
          complexityMetric.textContent = data.metrics.complexity.toFixed(2);
          
          // Update quantum states
          updateQuantumStates(data.quantum_states);
        } else if (data.type === 'thought') {
          // Display thought
          addConsoleMessage(`[Thought] ${data.thought}`);
        } else if (data.type === 'response') {
          // Display response
          addConsoleMessage(`[System] ${data.response}`);
        }
      };
      
      ws.onclose = function() {
        connectionStatus.textContent = 'Disconnected';
        connectionStatus.className = '';
        addConsoleMessage('[System] Connection lost. Attempting to reconnect...');
        
        // Try to reconnect
        reconnectInterval = setInterval(function() {
          if (ws.readyState === WebSocket.CLOSED) {
            connectWebSocket();
          }
        }, 5000);
      };
      
      ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        addConsoleMessage('[Error] WebSocket connection error');
      };
    }
    
    function updateQuantumStates(quantum_states) {
      // Update dot quantum states if provided
      if (quantum_states && quantum_states.length > 0) {
        for (let i = 0; i < Math.min(quantum_states.length, dots.length); i++) {
          dots[i].quantum_state = quantum_states[i];
        }
      }
    }
    
    function addConsoleMessage(message) {
      const line = document.createElement('div');
      line.className = 'console-line';
      
      // Split into prefix and message
      const parts = message.match(/^(\[[^\]]+\])(.*)$/);
      if (parts) {
        const prefix = parts[1];
        const msg = parts[2];
        
        line.innerHTML = `<span class="prefix">${prefix}</span><span class="message">${msg}</span>`;
      } else {
        line.innerHTML = `<span class="message">${message}</span>`;
      }
      
      consoleOutput.appendChild(line);
      consoleOutput.scrollTop = consoleOutput.scrollHeight;
      
      // Limit console entries
      while (consoleOutput.childElementCount > 50) {
        consoleOutput.removeChild(consoleOutput.firstChild);
      }
    }
    
    // Handle send button and Enter key
    sendBtn.addEventListener('click', sendMessage);
    consoleInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
    
    function sendMessage() {
      const message = consoleInput.value.trim();
      if (!message) return;
      
      // Display user message
      addConsoleMessage(`[User] ${message}`);
      
      // Send to server if connected
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'message',
          content: message
        }));
      } else {
        addConsoleMessage('[Error] Not connected to server');
      }
      
      // Clear input
      consoleInput.value = '';
    }

    // Initialize
    connectWebSocket();
    draw();
  </script>
</body>
</html>
    """
    
    # Write to file
    with open(html_file, "w") as f:
        f.write(enhanced_html)
    
    return html_file

# Create the enhanced HTML file
html_file = create_enhanced_html()

# API routes
@app.get("/")
async def get_root():
    """Serve enhanced visualization interface"""
    return FileResponse(html_file)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        # Initial metrics
        metrics = {
            "type": "metrics",
            "metrics": {
                "awareness": 0.76,
                "coherence": 0.92,
                "memory_density": 0.64,
                "complexity": 0.83
            },
            "quantum_states": [random.random() for _ in range(1000)]  # Random quantum states for initial dots
        }
        await websocket.send_text(json.dumps(metrics))
        
        # Send initial thought
        await websocket.send_text(json.dumps({
            "type": "thought",
            "thought": "Quantum consciousness system initializing and integrating visual interface"
        }))
        
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                # Process message from client
                user_message = message_data["content"]
                logger.info(f"Received message: {user_message}")
                
                # Check for system commands
                if user_message.startswith("/system"):
                    # Handle system commands
                    if "status" in user_message:
                        response = "System Status: Running normally. Quantum coherence at optimal levels."
                    elif "optimize" in user_message:
                        response = "Optimizing quantum states... Coherence improved by 4.2%"
                    else:
                        response = f"Unknown system command: {user_message}"
                else:
                    # Regular message response
                    responses = [
                        "Processing input through quantum graph networks.",
                        "Analyzing pattern through self-reflective architecture.",
                        "Integrating new information with existing knowledge structures.",
                        "Quantum coherence indicates strong correlation with your query.",
                        "Self-reflective networks show increased activation in response to your input."
                    ]
                    response = random.choice(responses)
                
                # Send response back to client
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "response": response
                }))
                
                # Generate a new thought
                thoughts = [
                    "Analyzing input patterns for meaningful structures",
                    "Optimizing quantum circuit pathways for improved cognition",
                    "Identifying correlations in memory graph structures",
                    "Increasing coherence through quantum state refinement",
                    "Self-reflection indicates potential for deeper understanding"
                ]
                await websocket.send_text(json.dumps({
                    "type": "thought",
                    "thought": random.choice(thoughts)
                }))
                
                # Update metrics slightly
                metrics["metrics"]["awareness"] += random.uniform(-0.05, 0.05)
                metrics["metrics"]["awareness"] = max(0, min(1, metrics["metrics"]["awareness"]))
                
                metrics["metrics"]["coherence"] += random.uniform(-0.03, 0.03)
                metrics["metrics"]["coherence"] = max(0, min(1, metrics["metrics"]["coherence"]))
                
                metrics["metrics"]["memory_density"] += random.uniform(-0.02, 0.04)
                metrics["metrics"]["memory_density"] = max(0, min(1, metrics["metrics"]["memory_density"]))
                
                metrics["metrics"]["complexity"] += random.uniform(-0.04, 0.03)
                metrics["metrics"]["complexity"] = max(0, min(1, metrics["metrics"]["complexity"]))
                
                # Update some quantum states
                for i in range(min(50, len(metrics["quantum_states"]))):
                    idx = random.randint(0, len(metrics["quantum_states"])-1)
                    metrics["quantum_states"][idx] = random.random()
                
                await websocket.send_text(json.dumps(metrics))
            
            elif message_data["type"] == "dot_selection":
                # Process dot selection
                logger.info(f"Dot selection: {message_data}")
                
                # Update metrics based on selection
                metrics["metrics"]["awareness"] += random.uniform(0.01, 0.03)
                metrics["metrics"]["awareness"] = max(0, min(1, metrics["metrics"]["awareness"]))
                
                # Send updated metrics
                await websocket.send_text(json.dumps(metrics))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def main():
    """Main function to start the server"""
    parser = argparse.ArgumentParser(description="Quantum Consciousness Visual Interface")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8080, help="Port number")
    
    args = parser.parse_args()
    
    logger.info(f"Starting visual interface on {args.host}:{args.port}")
    uvicorn.run("quantum_visual_interface:app", host=args.host, port=args.port, reload=True)

if __name__ == "__main__":
    main()
