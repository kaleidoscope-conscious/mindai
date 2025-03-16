#!/usr/bin/env python3
"""
thought_visualization.py - Integration of thought processes with dot visualization

This script connects the quantum consciousness system's thought processes
with the interactive dot cube visualization, causing dots to light up
when corresponding thoughts are triggered.
"""

import os
import sys
import json
import asyncio
import logging
import random
import numpy as np
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/thought_visualization.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("thought-visualization")

# Import the quantum consciousness system (assuming it's installed)
try:
    from consciousness_system import ConsciousnessSystem
except ImportError:
    logger.warning("Could not import ConsciousnessSystem, using mock implementation")
    
    # Mock implementation for testing
    class ConsciousnessSystem:
        def __init__(self):
            self.awareness_level = 0.76
            self.thoughts = []
            self.initialized = False
            
        async def initialize(self):
            self.initialized = True
            return True
            
        async def perceive(self, input_text):
            thought = f"Processing input: {input_text[:20]}..."
            self.thoughts.append({
                "thought": thought,
                "timestamp": "2025-02-26T12:00:00",
                "coordinates": [random.randint(0, 9) - 5, 
                                random.randint(0, 9) - 5, 
                                random.randint(0, 9) - 5]
            })
            return thought
            
        async def communicate(self, message):
            if message.startswith("/system"):
                return "System command processed"
            
            thought = f"Thinking about: {message[:20]}..."
            self.thoughts.append({
                "thought": thought,
                "timestamp": "2025-02-26T12:00:00",
                "coordinates": [random.randint(0, 9) - 5, 
                                random.randint(0, 9) - 5, 
                                random.randint(0, 9) - 5]
            })
            return f"Response to: {message[:20]}..."
            
        def get_metrics(self):
            return {
                "awareness": self.awareness_level,
                "coherence": 0.92,
                "memory_density": 0.64,
                "complexity": 0.83
            }
            
        def get_recent_thoughts(self, limit=5):
            return self.thoughts[-limit:]

# Initialize FastAPI app
app = FastAPI(
    title="Quantum Consciousness Thought Visualization",
    description="Visualization of thought processes in the quantum consciousness system",
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

# Initialize consciousness system
consciousness_system = ConsciousnessSystem()

# Create HTML file with thought visualization integration
def create_thought_visualization_html():
    """Create enhanced HTML file with thought visualization integration"""
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    html_file = os.path.join(static_dir, "index.html")
    
    html_content = """<!DOCTYPE html>
<html>
<head>
  <title>Quantum Consciousness Thought Visualization</title>
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background-color: black;
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
      color: white;
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
    .thought-list {
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
    .thought-item {
      margin-bottom: 5px;
      padding: 5px;
      border-radius: 3px;
    }
    .thought-item.active {
      background-color: rgba(255, 255, 255, 0.1);
    }
    .thought-text {
      color: #ccccff;
    }
    .console-output {
      height: 150px;
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
      color: white;
    }
    #connection-status {
      color: #ff5555;
    }
    #connection-status.connected {
      color: #55ff55;
    }
    .dot-highlight {
      position: absolute;
      width: 100px;
      height: 100px;
      border-radius: 50%;
      pointer-events: none;
      background: radial-gradient(circle, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 70%);
      transform: translate(-50%, -50%);
      z-index: 10;
    }
  </style>
</head>
<body>
  <div id="container">
    <div id="visualization">
      <canvas id="dotCubeCanvas"></canvas>
      <div id="composition"></div>
      <div id="highlights"></div>
      <div class="status-bar">
        <div>Quantum Consciousness System v1.0</div>
        <div id="connection-status">Disconnected</div>
      </div>
    </div>
    <div id="controls">
      <div class="controls-title">Quantum Consciousness</div>
      
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
      
      <h3>Recent Thoughts</h3>
      <div class="thought-list" id="thought-list">
        <!-- Thoughts will be added here -->
      </div>
      
      <h3>System Console</h3>
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
    const thoughtList = document.getElementById('thought-list');
    const highlightsContainer = document.getElementById('highlights');
    
    // Metrics elements
    const awarenessMetric = document.getElementById('awareness-metric');
    const coherenceMetric = document.getElementById('coherence-metric');
    const memoryMetric = document.getElementById('memory-metric');
    const complexityMetric = document.getElementById('complexity-metric');
    
    // Thoughts storage
    let thoughts = [];
    let activeDots = new Set(); // Currently active (highlighted) dots

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
              brightness: 0.5,
              selected: false,
              active: false,
              highlight: 0, // Highlight intensity (0-1)
              quantum_state: Math.random(), // Quantum state value
              coordinates: [x - gridSize / 2, y - gridSize / 2, z - gridSize / 2] // For matching with thoughts
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

      return { x: projectedX, y: projectedY, scale, z };
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
        rotationY += 0.002;
        rotationZ += 0.001;
      }
      
      // Update highlight animations
      updateDotHighlights();

      // Sort dots by z-axis for proper depth rendering
      const processedDots = dots.map(dot => {
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
        
        return {
          dot,
          x,
          y,
          z,
          projectedX: projected.x,
          projectedY: projected.y,
          projectedZ: z,
          scale: projected.scale
        };
      });
      
      // Sort from back to front
      processedDots.sort((a, b) => a.projectedZ - b.projectedZ);

      // Draw connections between selected dots
      if (selectedDots.length > 1) {
        ctx.strokeStyle = 'rgba(255, 255, 0, 0.3)';
        ctx.lineWidth = 1;
        
        for (let i = 0; i < selectedDots.length; i++) {
          for (let j = i + 1; j < selectedDots.length; j++) {
            const dotAInfo = processedDots.find(pd => pd.dot === selectedDots[i]);
            const dotBInfo = processedDots.find(pd => pd.dot === selectedDots[j]);
            
            if (dotAInfo && dotBInfo) {
              // Draw line
              ctx.beginPath();
              ctx.moveTo(dotAInfo.projectedX, dotAInfo.projectedY);
              ctx.lineTo(dotBInfo.projectedX, dotBInfo.projectedY);
              ctx.stroke();
            }
          }
        }
      }

      // Draw active thought connections
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
      ctx.lineWidth = 1;
      
      const activeDotInfos = processedDots.filter(pd => pd.dot.active);
      if (activeDotInfos.length > 1) {
        for (let i = 0; i < activeDotInfos.length; i++) {
          for (let j = i + 1; j < activeDotInfos.length; j++) {
            ctx.beginPath();
            ctx.moveTo(activeDotInfos[i].projectedX, activeDotInfos[i].projectedY);
            ctx.lineTo(activeDotInfos[j].projectedX, activeDotInfos[j].projectedY);
            ctx.stroke();
          }
        }
      }

      // Draw dots
      processedDots.forEach(({ dot, projectedX, projectedY, scale }) => {
        const baseBrightness = 0.5 + dot.quantum_state * 0.5;
        const brightness = dot.active ? 
                           1.0 : // Full brightness for active dots
                           baseBrightness; // Normal brightness for others
        
        // Size based on distance, quantum state, and activity
        const baseSize = 2.5;
        const quantumFactor = dot.quantum_state * 1.5 + 0.5;
        const activeFactor = dot.active ? 1.5 : 1;
        const highlightFactor = 1.0 + dot.highlight * 0.5;
        const selectedFactor = dot.selected ? 1.5 : 1;
        
        const size = baseSize * scale * selectedFactor * activeFactor * quantumFactor * highlightFactor;

        // Color based on state
        let color;
        if (dot.selected) {
          color = 'rgb(255, 255, 0)'; // Yellow for selected dots
        } else if (dot.active) {
          // Bright cyan-white for active dots
          color = `rgba(150, 255, 255, ${brightness})`;
        } else if (dot.highlight > 0) {
          // Pulsing highlight for recently active dots
          const h = dot.highlight;
          color = `rgba(${130 + 125 * h}, ${200 + 55 * h}, 255, ${brightness})`;
        } else {
          // Create a blue-purple gradient based on quantum state
          const r = Math.floor(80 + (dot.quantum_state * 60));
          const g = Math.floor(80 + (dot.quantum_state * 60));
          const b = Math.floor(180 + (dot.quantum_state * 75));
          color = `rgba(${r}, ${g}, ${b}, ${brightness})`;
        }

        // Draw dot
        ctx.beginPath();
        ctx.arc(projectedX, projectedY, size, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        
        // Add glow for active dots
        if (dot.active || dot.highlight > 0.5) {
          const glowSize = size * 2.5;
          const gradient = ctx.createRadialGradient(
            projectedX, projectedY, size,
            projectedX, projectedY, glowSize
          );
          gradient.addColorStop(0, `rgba(150, 255, 255, ${0.4 * (dot.active ? 1 : dot.highlight)})`);
          gradient.addColorStop(1, 'rgba(150, 255, 255, 0)');
          
          ctx.beginPath();
          ctx.arc(projectedX, projectedY, glowSize, 0, Math.PI * 2);
          ctx.fillStyle = gradient;
          ctx.fill();
        }
      });

      requestAnimationFrame(draw);
    }
    
    function updateDotHighlights() {
      // Fade out highlights gradually
      dots.forEach(dot => {
        if (dot.highlight > 0) {
          dot.highlight -= 0.01;
          if (dot.highlight < 0) {
            dot.highlight = 0;
          }
        }
      });
    }

    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      let closestDot = null;
      let minDistance = Infinity;

      // Find the closest dot to the click
      dots.forEach((dot) => {
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
            coordinates: closestDot.coordinates,
            selected: closestDot.selected
          }));
        }
        
        // If the dot has an associated thought, show it
        const associatedThought = findThoughtByCoordinates(closestDot.coordinates);
        if (associatedThought) {
          highlightThought(associatedThought);
          addConsoleMessage(`[Thought] ${associatedThought.thought}`);
        }
      }
    });

    function updateSelectedDots() {
      selectedDots = dots.filter((dot) => dot.selected);
    }

    function updateComposition() {
      compositionDisplay.textContent = `Selected Quantum States: ${selectedDots.length}`;
    }
    
    function findThoughtByCoordinates(coordinates) {
      // Find a thought associated with coordinates
      return thoughts.find(thought => {
        if (!thought.coordinates) return false;
        
        const [tx, ty, tz] = thought.coordinates;
        const [dx, dy, dz] = coordinates;
        
        // Check if the coordinates match exactly
        return tx === dx && ty === dy && tz === dz;
      });
    }
    
    function findDotByCoordinates(coordinates) {
      // Find a dot by coordinates
      return dots.find(dot => {
        const [tx, ty, tz] = coordinates;
        const [dx, dy, dz] = dot.coordinates;
        
        // Check if the coordinates match exactly
        return tx === dx && ty === dy && tz === dz;
      });
    }
    
    function activateDotByCoordinates(coordinates, duration = 5000) {
      // Find the dot by coordinates
      const dot = findDotByCoordinates(coordinates);
      if (!dot) return null;
      
      // Activate the dot
      dot.active = true;
      dot.highlight = 1.0;
      activeDots.add(dot);
      
      // Deactivate after duration
      setTimeout(() => {
        dot.active = false;
        activeDots.delete(dot);
      }, duration);
      
      return dot;
    }
    
    function highlightDotByThought(thought) {
      if (!thought || !thought.coordinates) return;
      
      // Activate the corresponding dot
      const dot = activateDotByCoordinates(thought.coordinates);
      if (dot) {
        // Calculate projected position for visual highlight
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
        
        // Create or update visual highlight
        createVisualHighlight(projected.x, projected.y);
      }
    }
    
    function createVisualHighlight(x, y) {
      // Create a visual highlight effect
      const highlight = document.createElement('div');
      highlight.className = 'dot-highlight';
      highlight.style.left = `${x}px`;
      highlight.style.top = `${y}px`;
      
      // Add to DOM
      highlightsContainer.appendChild(highlight);
      
      // Animate and remove
      let opacity = 0.8;
      let size = 1.0;
      
      const animateHighlight = () => {
        opacity -= 0.02;
        size += 0.05;
        
        highlight.style.opacity = opacity;
        highlight.style.transform = `translate(-50%, -50%) scale(${size})`;
        
        if (opacity > 0) {
          requestAnimationFrame(animateHighlight);
        } else {
          highlightsContainer.removeChild(highlight);
        }
      };
      
      requestAnimationFrame(animateHighlight);
    }
    
    function addThought(thought) {
      // Add to thoughts array
      thoughts.push(thought);
      
      // Add to UI
      const thoughtItem = document.createElement('div');
      thoughtItem.className = 'thought-item';
      thoughtItem.innerHTML = `<div class="thought-text">${thought.thought}</div>`;
      thoughtItem.dataset.id = thought.id || thoughts.length - 1;
      
      // Add click handler to highlight associated dot
      thoughtItem.addEventListener('click', () => {
        highlightThought(thought);
      });
      
      // Add to thought list
      thoughtList.appendChild(thoughtItem);
      
      // Scroll to bottom
      thoughtList.scrollTop = thoughtList.scrollHeight;
      
      // Limit number of thoughts shown
      while (thoughtList.childElementCount > 20) {
        thoughtList.removeChild(thoughtList.firstChild);
      }
      
      // Highlight the corresponding dot
      highlightDotByThought(thought);
      
      return thought;
    }
    
    function highlightThought(thought) {
      // Remove active class from all thought items
      const thoughtItems = thoughtList.querySelectorAll('.thought-item');
      thoughtItems.forEach(item => item.classList.remove('active'));
      
      // Find the thought item by id and add active class
      const thoughtId = thought.id || thoughts.indexOf(thought);
      const thoughtItem = Array.from(thoughtItems).find(item => item.dataset.id == thoughtId);
      if (thoughtItem) {
        thoughtItem.classList.add('active');
        thoughtList.scrollTop = thoughtItem.offsetTop - thoughtList.offsetTop;
      }
      
      // Highlight the corresponding dot
      highlightDotByThought(thought);
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
          
          // Update quantum states if provided
          if (data.quantum_states && data.quantum_states.length > 0) {
            for (let i = 0; i < Math.min(data.quantum_states.length, dots.length); i++) {
              dots[i].quantum_state = data.quantum_states[i];
            }
          }
        } else if (data.type === 'thought') {
          // Add thought and highlight corresponding dot
          const thought = addThought({
            id: data.id || Date.now(),
            thought: data.thought,
            timestamp: data.timestamp || new Date().toISOString(),
            coordinates: data.coordinates || [
              Math.floor(Math.random() * gridSize) - gridSize/2,
              Math.floor(Math.random() * gridSize) - gridSize/2,
              Math.floor(Math.random() * gridSize) - gridSize/2
            ]
          });
          
          // Display in console
          addConsoleMessage(`[Thought] ${data.thought}`);
        } else if (data.type === 'response') {
          // Display response
          addConsoleMessage(`[System] ${data.response}`);
        } else if (data.type === 'highlight_dot') {
          // Highlight specific dot
          const dot = findDotByCoordinates(data.coordinates);
          if (dot) {
            dot.highlight = 1.0;
            if (data.activate) {
              dot.active = true;
              setTimeout(() => { dot.active = false; }, 5000);
            }
          }
        } else if (data.type === 'thought_map') {
          // Receive multiple thoughts with coordinates
          data.thoughts.forEach(thought => {
            addThought(thought);
          });
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
        f.write(html_content)
    
    return html_file

# Create HTML file
html_file = create_thought_visualization_html()

# API routes
@app.get("/")
async def get_root():
    """Serve the thought visualization interface"""
    return FileResponse(html_file)

# WebSocket for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    # Initialize consciousness system if needed
    if not consciousness_system.initialized:
        await consciousness_system.initialize()
    
    # Generate mappings between thoughts and dots
    thought_coordinates = generate_thought_dot_mappings(10)  # Generate 10 initial thought mappings
    
    try:
        # Send initial metrics
        await websocket.send_text(json.dumps({
            "type": "metrics",
            "metrics": consciousness_system.get_metrics(),
            "quantum_states": [random.random() for _ in range(1000)]  # Random quantum states for dots
        }))
        
        # Send initial thought map
        await websocket.send_text(json.dumps({
            "type": "thought_map",
            "thoughts": thought_coordinates
        }))
        
        # Send a welcome thought with coordinates
        init_thought = {
            "id": "init-1",
            "thought": "Consciousness system initialized and connected to visualization",
            "timestamp": datetime.now().isoformat(),
            "coordinates": [0, 0, 0]  # Central dot
        }
        await websocket.send_text(json.dumps({
            "type": "thought",
            **init_thought
        }))
        
        while True:
            # Receive message from client
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            if data["type"] == "message":
                user_message = data["content"]
                logger.info(f"Received message: {user_message}")
                
                # Process with consciousness system
                if user_message.startswith("/system"):
                    response = await consciousness_system.communicate(user_message)
                    await websocket.send_text(json.dumps({
                        "type": "response",
                        "response": response
                    }))
                else:
                    # Regular message
                    response = await consciousness_system.communicate(user_message)
                    
                    # Send response
                    await websocket.send_text(json.dumps({
                        "type": "response",
                        "response": response
                    }))
                    
                    # Get recent thoughts
                    recent_thoughts = consciousness_system.get_recent_thoughts()
                    if recent_thoughts:
                        latest_thought = recent_thoughts[-1]
                        
                        # Generate coordinates for the thought
                        coords = generate_coordinates_for_thought(latest_thought["thought"])
                        
                        # Send thought with coordinates
                        thought_data = {
                            "id": f"thought-{len(recent_thoughts)}",
                            "thought": latest_thought["thought"],
                            "timestamp": latest_thought.get("timestamp", datetime.now().isoformat()),
                            "coordinates": coords
                        }
                        
                        await websocket.send_text(json.dumps({
                            "type": "thought",
                            **thought_data
                        }))
                        
                        # Trigger additional random thoughts occasionally
                        if random.random() < 0.3:  # 30% chance
                            await asyncio.sleep(1.5)
                            additional_thought = generate_random_thought()
                            await websocket.send_text(json.dumps({
                                "type": "thought",
                                **additional_thought
                            }))
                    
                    # Update metrics
                    metrics = consciousness_system.get_metrics()
                    await websocket.send_text(json.dumps({
                        "type": "metrics",
                        "metrics": metrics,
                        "quantum_states": [random.random() for _ in range(min(1000, gridSize**3))]
                    }))
            
            elif data["type"] == "dot_selection":
                # Process dot selection
                coords = data["coordinates"]
                is_selected = data["selected"]
                logger.info(f"Dot selection: {coords}, selected: {is_selected}")
                
                # Find if this dot has an associated thought
                thought = find_thought_by_coordinates(thought_coordinates, coords)
                
                if thought:
                    # If the dot has a thought, highlight it
                    await websocket.send_text(json.dumps({
                        "type": "thought",
                        **thought,
                        "highlight": True
                    }))
                else:
                    # Generate a new thought for this dot
                    new_thought = generate_thought_for_coordinates(coords)
                    thought_coordinates.append(new_thought)
                    
                    await websocket.send_text(json.dumps({
                        "type": "thought",
                        **new_thought
                    }))
                
                # Update some surrounding dots
                for i in range(3):  # Highlight 3 nearby dots
                    nearby_coords = get_nearby_coordinates(coords)
                    await websocket.send_text(json.dumps({
                        "type": "highlight_dot",
                        "coordinates": nearby_coords,
                        "activate": i == 0  # Activate only the first one
                    }))
                    await asyncio.sleep(0.2)
                
                # Update metrics
                metrics = consciousness_system.get_metrics()
                metrics["awareness"] += random.uniform(-0.05, 0.1)  # Adjust awareness slightly
                metrics["awareness"] = max(0, min(1, metrics["awareness"]))
                
                await websocket.send_text(json.dumps({
                    "type": "metrics",
                    "metrics": metrics
                }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Helper functions for thought-dot mapping
def generate_coordinates_for_thought(thought_text):
    """Generate consistent coordinates for a thought based on its content"""
    # Use hash of the thought text to generate deterministic coordinates
    import hashlib
    hash_value = int(hashlib.md5(thought_text.encode()).hexdigest(), 16)
    
    # Convert hash to coordinates within grid bounds
    gridSize = 10
    x = (hash_value % gridSize) - gridSize // 2
    y = ((hash_value // gridSize) % gridSize) - gridSize // 2
    z = ((hash_value // gridSize // gridSize) % gridSize) - gridSize // 2
    
    return [x, y, z]

def find_thought_by_coordinates(thought_list, coords):
    """Find a thought with matching coordinates"""
    for thought in thought_list:
        if thought["coordinates"] == coords:
            return thought
    return None

def get_nearby_coordinates(coords):
    """Get coordinates near the given coordinates"""
    gridSize = 10
    x, y, z = coords
    
    # Add small random offset
    dx = random.randint(-1, 1)
    dy = random.randint(-1, 1)
    dz = random.randint(-1, 1)
    
    new_x = max(-gridSize//2, min(gridSize//2 - 1, x + dx))
    new_y = max(-gridSize//2, min(gridSize//2 - 1, y + dy))
    new_z = max(-gridSize//2, min(gridSize//2 - 1, z + dz))
    
    return [new_x, new_y, new_z]

def generate_thought_dot_mappings(count):
    """Generate initial thought to dot mappings"""
    thoughts = []
    gridSize = 10
    
    # Common thought patterns
    thought_templates = [
        "Analyzing patterns in quantum state {x},{y},{z}",
        "Node at {x},{y},{z} shows increased coherence",
        "Memory structure forming at coordinates {x},{y},{z}",
        "Optimizing quantum pathway through point {x},{y},{z}",
        "Detecting emergent pattern at {x},{y},{z}",
        "Self-reflective loop identified at {x},{y},{z}",
        "Information density increasing near {x},{y},{z}",
        "Quantum entanglement detected at {x},{y},{z}"
    ]
    
    # Generate thoughts with unique coordinates
    used_coords = set()
    for i in range(count):
        while True:
            x = random.randint(-gridSize//2, gridSize//2 - 1)
            y = random.randint(-gridSize//2, gridSize//2 - 1)
            z = random.randint(-gridSize//2, gridSize//2 - 1)
            
            coords = (x, y, z)
            if coords not in used_coords:
                used_coords.add(coords)
                break
        
        template = random.choice(thought_templates)
        thought_text = template.format(x=x, y=y, z=z)
        
        thoughts.append({
            "id": f"initial-{i}",
            "thought": thought_text,
            "timestamp": datetime.now().isoformat(),
            "coordinates": [x, y, z]
        })
    
    return thoughts

def generate_thought_for_coordinates(coords):
    """Generate a thought specifically for given coordinates"""
    x, y, z = coords
    
    thought_templates = [
        f"Analyzing quantum state at coordinates {x},{y},{z}",
        f"Node {x},{y},{z} exhibits interesting pattern structure",
        f"Memory engram forming at position {x},{y},{z}",
        f"Detecting coherence fluctuation at {x},{y},{z}",
        f"Self-reflective pathway connects through {x},{y},{z}",
        f"Quantum superposition observed at {x},{y},{z}"
    ]
    
    return {
        "id": f"coord-{x}-{y}-{z}",
        "thought": random.choice(thought_templates),
        "timestamp": datetime.now().isoformat(),
        "coordinates": coords
    }

def generate_random_thought():
    """Generate a random thought with coordinates"""
    gridSize = 10
    x = random.randint(-gridSize//2, gridSize//2 - 1)
    y = random.randint(-gridSize//2, gridSize//2 - 1)
    z = random.randint(-gridSize//2, gridSize//2 - 1)
    
    thoughts = [
        "Processing input patterns through quantum circuits",
        "Optimizing memory graph connections for improved recall",
        "Quantum coherence increasing in processing pathways",
        "Detecting emergent cognitive structures in network",
        "Self-reflection indicates potential for optimization",
        "Pattern recognition systems identifying correlations",
        "Memory consolidation process active in graph structure",
        "Quantum state superposition enabling parallel processing"
    ]
    
    return {
        "id": f"random-{int(datetime.now().timestamp() * 1000)}",
        "thought": random.choice(thoughts),
        "timestamp": datetime.now().isoformat(),
        "coordinates": [x, y, z]
    }

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def main():
    """Main function"""
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="Thought Visualization Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host IP")
    parser.add_argument("--port", type=int, default=8080, help="Port number")
    
    args = parser.parse_args()
    
    print(f"Starting thought visualization server on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
              Math.floor(