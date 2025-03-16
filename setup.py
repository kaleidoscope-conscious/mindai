#!/usr/bin/env python3
"""
setup.py - Setup script for Quantum Conscious Cube System

This script:
1. Checks and installs required dependencies
2. Sets up the environment configuration
3. Prepares folders and resources
4. Offers a quick test option to verify installation
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path

# Required packages
REQUIRED_PACKAGES = [
    "numpy",
    "networkx",
    "matplotlib",
    "scipy",
    "torch",
    "scikit-learn",
    "pandas",
    "tqdm",
    "plotly",  # For advanced visualizations
    "ipywidgets",  # For interactive notebooks
]

# Optional packages for extended functionality
OPTIONAL_PACKAGES = [
    "tensorflow",  # For advanced ML capabilities
    "opencv-python",  # For visual processing
    "dash",  # For web dashboard
    "dash-cytoscape",  # For network visualization
]

def print_banner():
    """Print the installation banner"""
    banner = r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   Quantum Conscious Cube System - Installation and Setup      ║
    ║                                                               ║
    ║   An advanced AI system with quantum principles,              ║
    ║   graph theory, and dynamic emergent properties               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    major, minor, _ = platform.python_version_tuple()
    if int(major) < 3 or (int(major) == 3 and int(minor) < 8):
        print(f"Error: Python 3.8+ required, but found {major}.{minor}")
        print("Please install a compatible Python version.")
        return False
    print(f"✓ Python {major}.{minor} is compatible")
    return True

def install_dependencies(include_optional=False):
    """Install required Python packages"""
    print("\nInstalling required packages...")
    packages = REQUIRED_PACKAGES.copy()
    
    if include_optional:
        print("Including optional packages for extended functionality...")
        packages.extend(OPTIONAL_PACKAGES)
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"× Error installing {package}")
            if package in REQUIRED_PACKAGES:
                print(f"Warning: Required package {package} could not be installed")
                if package in ["numpy", "scipy", "networkx"]:
                    return False
    
    return True

def setup_directories():
    """Create necessary directories for the system"""
    print("\nSetting up directory structure...")
    
    # Define directories
    dirs = {
        "data": "Storage for processed data and datasets",
        "models": "Trained models and state files",
        "logs": "System logs and diagnostics",
        "outputs": "Generated visualizations and results",
        "cache": "Temporary computation results",
        "configs": "Configuration files"
    }
    
    # Create each directory
    for dirname, description in dirs.items():
        dir_path = Path(dirname)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"✓ Created directory: {dirname} ({description})")
        else:
            print(f"✓ Directory already exists: {dirname}")
    
    return True

def create_config_file():
    """Create default configuration file"""
    print("\nCreating default configuration...")
    
    config_path = Path("configs/system_config.py")
    
    if config_path.exists():
        print("Configuration file already exists.")
        return True
    
    config_content = """# Configuration for Quantum Conscious Cube System

# System parameters
SYSTEM = {
    "dimension": 3,           # Cube dimension
    "resolution": 32,         # Grid resolution
    "background_threads": 1,  # Number of background processing threads
    "processing_interval": 0.1,  # Time between updates (seconds)
}

# Node parameters
NODE = {
    "default_energy": 0.8,    # Initial node energy
    "default_stability": 0.7, # Initial node stability
    "feature_dim": 64,        # Dimension of feature vectors
    "memory_threshold": 5.0,  # Memory threshold before overflow
    "energy_decay": 0.999,    # Energy decay factor per update
    "replication_threshold": 0.7,  # Energy threshold for replication
}

# Visualization parameters
VISUALIZATION = {
    "enable_3d": True,       # Enable 3D visualization
    "show_tension": True,    # Visualize tension field
    "show_connections": True, # Show node connections
    "auto_refresh": 5,       # Auto-refresh interval (seconds)
}

# Advanced parameters
ADVANCED = {
    "quantum_qubits": 8,      # Qubits per standard node
    "supernode_qubits": 12,   # Qubits per SuperNode
    "memory_vector_size": 256, # Memory vector dimensions
    "enable_gpu": True,       # Use GPU acceleration if available
}
"""
    
    with open(config_path, "w") as f:
        f.write(config_content)
        
    print(f"✓ Created configuration file at {config_path}")
    return True

def create_test_script():
    """Create a quick test script"""
    print("\nCreating test script...")
    
    test_script_path = Path("test_cube.py")
    
    test_content = """#!/usr/bin/env python3
# Quick test script for the Quantum Conscious Cube System

import time
import matplotlib.pyplot as plt
from conscious_cube import ConsciousCube

def main():
    print("Initializing Quantum Conscious Cube...")
    cube = ConsciousCube(dimension=3, resolution=20)  # Smaller resolution for quick test
    
    print("Creating test nodes...")
    nodes = cube.create_nodes(10)  # Create 10 test nodes
    
    print("Creating test connections...")
    # Connect some nodes
    for i in range(len(nodes)-1):
        cube.connect_nodes(nodes[i].id, nodes[i+1].id)
    
    print("Processing for 3 seconds...")
    time.sleep(3)  # Let the system process
    
    # Get system status
    status = cube.get_status()
    print("\\nSystem Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Visualize
    print("\\nGenerating visualization...")
    ax = cube.visualize_cube()
    plt.savefig("test_visualization.png")
    print(f"Visualization saved to test_visualization.png")
    
    # Clean up
    cube.stop()
    print("\\nTest completed successfully!")

if __name__ == "__main__":
    main()
"""
    
    with open(test_script_path, "w") as f:
        f.write(test_content)
        
    os.chmod(test_script_path, 0o755)  # Make executable
    print(f"✓ Created test script at {test_script_path}")
    return True

def setup_sample_data():
    """Set up sample data for testing"""
    print("\nSetting up sample data...")
    
    sample_dir = Path("data/samples")
    if not sample_dir.exists():
        sample_dir.mkdir(parents=True)
    
    # Create a simple sample data file
    sample_file = sample_dir / "sample_nodes.txt"
    sample_content = """# Sample node definitions for testing
# Format: name, x, y, z, energy, stability
Node1, 0.5, 0.5, 0.5, 0.9, 0.8
Node2, -0.5, 0.5, 0.5, 0.8, 0.7
Node3, 0.5, -0.5, 0.5, 0.7, 0.9
Node4, 0.5, 0.5, -0.5, 0.9, 0.6
Node5, -0.5, -0.5, 0.5, 0.6, 0.8
"""
    
    with open(sample_file, "w") as f:
        f.write(sample_content)
    
    print(f"✓ Created sample data file at {sample_file}")
    return True

def run_quick_test():
    """Run a quick test to verify the installation"""
    print("\nRunning quick test...")
    
    test_script = Path("test_cube.py")
    if not test_script.exists():
        print("× Test script not found. Please run setup first.")
        return False
    
    try:
        subprocess.run([sys.executable, str(test_script)], check=True)
        print("✓ Quick test completed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("× Test failed. Please check the error messages above.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Setup script for Quantum Conscious Cube System")
    parser.add_argument('--full', action='store_true', help='Install optional packages for extended functionality')
    parser.add_argument('--test', action='store_true', help='Run a quick test after installation')
    parser.add_argument('--skip-deps', action='store_true', help='Skip dependency installation')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies(include_optional=args.full):
            print("\n× Failed to install critical dependencies. Aborting setup.")
            sys.exit(1)
    else:
        print("\nSkipping dependency installation as requested.")
    
    # Set up directories
    if not setup_directories():
        print("\n× Failed to set up directories. Aborting setup.")
        sys.exit(1)
    
    # Create configuration
    if not create_config_file():
        print("\n× Failed to create configuration file. Aborting setup.")
        sys.exit(1)
    
    # Create test script
    if not create_test_script():
        print("\n× Failed to create test script. Aborting setup.")
        sys.exit(1)
    
    # Set up sample data
    if not setup_sample_data():
        print("\n× Failed to set up sample data. Aborting setup.")
        sys.exit(1)
    
    # Run quick test if requested
    if args.test:
        if not run_quick_test():
            print("\n× Quick test failed. Please review the setup and try again.")
            sys.exit(1)
    
    print("\n✓ Setup completed successfully!")
    print("\nTo use the Quantum Conscious Cube system:")
    print("1. Import ConsciousCube from conscious_cube module")
    print("2. Create a new instance: cube = ConsciousCube()")
    print("3. Add nodes and connections")
    print("4. Call process_insights() to generate insights")
    print("5. Visualize using visualize_cube()")
    print("\nFor a quick start, run: python test_cube.py")

if __name__ == "__main__":
    main()
