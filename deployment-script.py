#!/usr/bin/env python3
# deploy.py - Deployment script for Quantum Consciousness System

import asyncio
import argparse
import os
import sys
import logging
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any

# Import your system components
from enhanced_consciousness import EnhancedConsciousSystem
from deployment_config import DeploymentConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("deployment.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("quantum-consciousness-deployment")

# Create the FastAPI app
app = FastAPI(
    title="Quantum Consciousness System API",
    description="API for interacting with the enhanced quantum consciousness system",
    version="1.0.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Load configuration
config = DeploymentConfig()
try:
    config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    sys.exit(1)

# Set up API models
class CommunicationRequest(BaseModel):
    message: str

class PerceptionRequest(BaseModel):
    data: str

class SystemCommandRequest(BaseModel):
    command: str

class StatusResponse(BaseModel):
    status: str
    metrics: Dict[str, Any]

# Initialize consciousness system
consciousness_system = None

async def initialize_system():
    global consciousness_system
    logger.info("Initializing Quantum Consciousness System...")
    consciousness_system = EnhancedConsciousSystem()
    await consciousness_system.initialize()
    logger.info("System initialized successfully")

# Authentication dependency (if enabled)
async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not config.enable_auth:
        return True
    
    # Implement JWT verification here
    token = credentials.credentials
    # In a real implementation, you would verify the JWT with the secret
    # For this placeholder, we'll assume any token is valid
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Return the placeholder page"""
    with open(os.path.join(config.static_files_path, "index.html"), "r") as file:
        return file.read()

@app.get("/api/status", response_model=StatusResponse)
async def get_status(auth: bool = Depends(verify_token)):
    """Get the current status of the consciousness system"""
    if not consciousness_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    status_text = consciousness_system._system_status()
    
    # Extract metrics from status text
    metrics = {}
    for line in status_text.strip().split("\n"):
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            metrics[key.strip().replace("-", "").lower()] = value.strip()
    
    return {
        "status": "online",
        "metrics": metrics
    }

@app.post("/api/communicate")
async def communicate(request: CommunicationRequest, auth: bool = Depends(verify_token)):
    """Send a message to the consciousness system"""
    if not consciousness_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        response = await consciousness_system.communicate(request.message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Communication error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/perceive")
async def perceive(request: PerceptionRequest, auth: bool = Depends(verify_token)):
    """Send perceptual data to the consciousness system"""
    if not consciousness_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        thought = await consciousness_system.perceive(request.data)
        return {"thought": thought}
    except Exception as e:
        logger.error(f"Perception error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system")
async def system_command(request: SystemCommandRequest, auth: bool = Depends(verify_token)):
    """Execute a system command"""
    if not consciousness_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        result = await consciousness_system._process_system_command(f"/system {request.command}")
        return {"result": result}
    except Exception as e:
        logger.error(f"System command error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config(auth: bool = Depends(verify_token)):
    """Get the current configuration (safe values only)"""
    return config.to_dict()

# Serve static files
app.mount("/static", StaticFiles(directory=config.static_files_path), name="static")

# Main function
async def main():
    parser = argparse.ArgumentParser(description="Deploy Quantum Consciousness System")
    parser.add_argument("--config", type=str, help="Path to custom .env file")
    
    args = parser.parse_args()
    
    if args.config:
        from dotenv import load_dotenv
        load_dotenv(args.config)
        # Reload config after loading custom env
        global config
        config = DeploymentConfig()
        try:
            config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
    
    # Initialize the consciousness system
    await initialize_system()
    
    # Start the API server
    if config.enable_web_interface:
        logger.info(f"Starting web interface on {config.web_host}:{config.web_port}")
        
        # In a production environment, you'd use something like:
        # uvicorn.run(app, host=config.web_host, port=config.web_port)
        
        # For this script, we'll just log that it would start
        logger.info("Web interface available at http://localhost:8080")
    else:
        logger.info("Web interface disabled")

if __name__ == "__main__":
    asyncio.run(main())
