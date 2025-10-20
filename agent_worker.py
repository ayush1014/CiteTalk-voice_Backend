"""
LiveKit Agent Worker for Simli Avatar.
Run this separately as: python agent_worker.py start
"""
import logging
import os
from dotenv import load_dotenv
from livekit.agents import (
    cli,
    WorkerOptions,
    WorkerType,
)
from services.simli_service import simli_agent_entrypoint

# Load environment variables
load_dotenv()

logger = logging.getLogger("simli-avatar-worker")
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Starting Simli Avatar LiveKit Agent Worker...")
    logger.info(f"🔗 LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    logger.info(f"🔑 API Key: {os.getenv('LIVEKIT_API_KEY', 'NOT SET')[:10]}...")
    
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=simli_agent_entrypoint,
            worker_type=WorkerType.ROOM,
            # Enable automatic dispatch for all rooms
            agent_name="simli-avatar-agent",
        )
    )
