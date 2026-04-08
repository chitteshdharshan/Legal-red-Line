import uvicorn
import os
import sys
from fastapi import FastAPI

# Add parent directory to path so legal_env can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import HTTPEnvServer
from legal_env import LegalRedLineEnv, LegalAction, LegalObservation

# Initialize the OpenEnv HTTP server wrapper
# Note: HTTPEnvServer expects the class (factory), not an instance.
server = HTTPEnvServer(
    env=LegalRedLineEnv,
    action_cls=LegalAction,
    observation_cls=LegalObservation,
)

# Create FastAPI app
app = FastAPI(title="Legal Red Line OpenEnv")

# Register OpenEnv routes
server.register_routes(app)

def main():
    """Main entry point for the OpenEnv server."""
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
