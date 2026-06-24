import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from flask import Flask, render_template, jsonify, abort

# ==========================================
# 1. ADVANCED ENGINE CONFIGURATION & LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CodespaceEngine")

app = Flask(__name__)

# System paths
BASE_DIR = Path(__file__).resolve().parent
CPP_SOURCE = BASE_DIR / "surprise.cpp"
CPP_BINARY = BASE_DIR / "surprise"

# ==========================================
# 2. AUTOMATED COMPILATION SUBSYSTEM
# ==========================================
def compile_cpp_backend():
    """
    Validates, optimizes, and compiles the massive C++ core engine.
    Uses -O3 optimization for maximum execution speed.
    """
    if not CPP_SOURCE.exists():
        logger.error(f"Critical Error: {CPP_SOURCE.name} not found in workspace!")
        return False

    # Clean old binaries if they exist to force a fresh build
    if CPP_BINARY.exists():
        try:
            CPP_BINARY.unlink()
            logger.info("Cleared previous binary cache.")
        except Exception as e:
            logger.warning(f"Could not clear old binary: {e}")

    logger.info("Initializing high-performance C++ compilation...")
    start_time = time.time()

    try:
        # Compiling with standard C++17 and O3 optimization flags
        compile_command = [
            "g++", 
            "-std=c++17", 
            "-O3", 
            str(CPP_SOURCE), 
            "-o", 
            str(CPP_BINARY)
        ]
        
        result = subprocess.run(
            compile_command, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"C++ Engine successfully compiled in {elapsed_time:.2f} seconds.")
        return True

    except subprocess.CalledProcessError as e:
        logger.error("!!! C++ COMPILATION FAILED !!!")
        logger.error(f"Compiler StdErr:\n{e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected compilation system error: {e}")
        return False

# Trigger compilation immediately upon Python server launch
ENGINE_READY = compile_cpp_backend()

# ==========================================
# 3. ROUTING & CONTROLLER LAYERS
# ==========================================
@app.route('/')
def index():
    """Renders the cinematic frontend UI."""
    return render_template('index.html')


@app.route('/get-surprise', methods=['GET'])
def get_surprise():
    """
    Securely executes the high-performance C++ backend binary
    and pipes the real-time engine stream directly to the web interface.
    """
    if not ENGINE_READY and not CPP_BINARY.exists():
        logger.warning("Web request hit endpoint, but C++ engine is offline.")
        return "The universe is loading something beautiful... Try refreshing! ✨"

    try:
        logger.info("Executing native C++ binary subprocess call...")
        
        # Run the binary with a strict 5-second execution safety timeout
        runtime_result = subprocess.run(
            [str(CPP_BINARY)],
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )
        
        logger.info("C++ execution cycle completed successfully.")
        return runtime_result.stdout

    except subprocess.TimeoutExpired:
        logger.error("Execution Timeout: C++ engine taking too long to compute.")
        return "Processing high-level configurations... Click again in a moment! ❤️"
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Runtime Crash inside C++ execution: {e.stderr}")
        return "Engine processing raw perfection. (Everything is under control!)"
        
    except Exception as e:
        logger.error(f"Core execution failure: {e}")
        return "You look absolutely stunning today! ✨"


@app.route('/health', methods=['GET'])
def health_check():
    """Internal diagnostic endpoint for tracking Codespace environment status."""
    return jsonify({
        "status": "ONLINE",
        "engine_compiled": CPP_BINARY.exists(),
        "python_version": sys.version,
        "environment": "GitHub Codespaces"
    })

# ==========================================
# 4. SERVER RUNTIME ENTRYPOINT
# ==========================================
if __name__ == '__main__':
    # Configured specifically for GitHub Codespaces network architecture
    logger.info("Launching Flask server on port 5000...")
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=True, 
        use_reloader=False  # Disabled reloader to prevent double-compiling the C++ engine
    )
