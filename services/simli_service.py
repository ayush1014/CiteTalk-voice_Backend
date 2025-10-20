"""
Simli + LiveKit Avatar Service for real-time interactive AI agent.
"""
import logging
import os
from typing import Dict, Any
from config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SimliAvatarService:
    """Service for managing Simli avatar sessions with LiveKit."""
    
    def __init__(self):
        self.simli_api_key = settings.simli_api_key
        self.simli_face_id = settings.simli_face_id
        self.active_sessions: Dict[str, Any] = {}
        
    async def create_avatar_session(self, room_name: str, instructions: str = "You are a helpful AI assistant. Talk to me!") -> Dict[str, Any]:
        """
        Create a new Simli avatar session with LiveKit.
        
        Args:
            room_name: Name of the LiveKit room
            instructions: Instructions for the AI agent
            
        Returns:
            Dict containing session info with room_url and access_token
        """
        try:
            print(f"\n🚀 CREATE_AVATAR_SESSION CALLED with room_name: {room_name}")
            print(f"🔍 Type of room_name: {type(room_name)}")
            print(f"🔍 Room name value: '{room_name}'\n")
            
            logger.info(f"🚀 Creating Simli avatar session for room: {room_name}")
            
            # Generate LiveKit access token
            try:
                from livekit import api
                
                livekit_api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
                livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", "secret")
                
                print(f"🔑 Using LiveKit API Key: {livekit_api_key[:10]}...")
                print(f"🏠 Room name: {room_name}")
                
                logger.info(f"🚀 Creating Simli avatar session for room: {room_name}")
                logger.info(f"🔑 Using LiveKit API Key: {livekit_api_key[:10]}...")
                logger.info(f"🏠 Room name: {room_name}")
                
                # Create VideoGrants
                grants = api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True
                )
                logger.info(f"📋 Created VideoGrants: room_join=True, room={room_name}")
                
                # Create token using fluent API with method chaining
                token = (api.AccessToken(livekit_api_key, livekit_api_secret)
                        .with_identity("user")
                        .with_name("User")
                        .with_grants(grants))
                
                logger.info(f"🎫 Token object created with method chaining")
                
                access_token = token.to_jwt()
                logger.info(f"✅ LiveKit JWT token generated successfully: {access_token[:50]}...")
                
            except Exception as e:
                logger.error(f"❌ Error generating LiveKit token: {str(e)}")
                raise Exception(f"LiveKit token generation failed: {str(e)}")
            
            # LiveKit URL
            livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
            
            session_info = {
                "success": True,
                "room_name": room_name,
                "room_url": livekit_url,
                "access_token": access_token,
                "session_id": room_name,
                "instructions": instructions,
            }
            
            self.active_sessions[room_name] = session_info
            
            logger.info(f"✅ Simli avatar session created: {room_name}")
            return session_info
            
        except Exception as e:
            logger.error(f"❌ Error creating Simli avatar session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_message_to_avatar(self, session_id: str, text: str) -> Dict[str, Any]:
        """
        Send a message for the avatar to speak (handled by LiveKit agent).
        
        Args:
            session_id: The session ID (room name)
            text: Text for the avatar to speak
            
        Returns:
            Dict with success status
        """
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            logger.info(f"📤 Sending message to avatar in session {session_id}: {text[:50]}...")
            
            # The actual text-to-speech will be handled by the LiveKit agent
            # This is just for tracking
            return {
                "success": True,
                "message": "Message queued for avatar"
            }
            
        except Exception as e:
            logger.error(f"❌ Error sending message to avatar: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_session(self, session_id: str) -> Dict[str, Any]:
        """
        Stop a Simli avatar session.
        
        Args:
            session_id: The session ID to stop
            
        Returns:
            Dict with success status
        """
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"✅ Stopped Simli avatar session: {session_id}")
                
            return {
                "success": True,
                "message": "Session stopped"
            }
            
        except Exception as e:
            logger.error(f"❌ Error stopping session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def trigger_agent_for_room(self, room_name: str, instructions: str) -> None:
        """
        Trigger an agent to join a specific room.
        This spawns a background task that connects the Simli agent.
        """
        import asyncio
        
        logger.info(f"🤖 Spawning agent for room: {room_name}")
        
        # Spawn agent in background
        asyncio.create_task(self._run_agent_for_room(room_name, instructions))
    
    async def _run_agent_for_room(self, room_name: str, instructions: str) -> None:
        """Background task that runs the agent for a specific room."""
        try:
            from livekit import rtc
            from livekit.plugins import openai, simli
            from livekit.agents.utils import http_context
            import os
            import asyncio
            
            logger.info(f"🎬 Agent connecting to room: {room_name}")
            
            # Get configuration
            livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
            livekit_api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
            livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", "secret")
            simli_api_key = os.getenv("SIMLI_API_KEY")
            simli_face_id = os.getenv("SIMLI_FACE_ID")
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            if not all([simli_api_key, simli_face_id, openai_api_key]):
                logger.error("❌ Missing required API keys")
                return
            
            # Initialize a plugin-compatible HTTP session context (outside worker)
            # This avoids "Attempted to use an http session outside of a job context" errors.
            http_context._new_session_ctx()

            # Generate agent token
            from livekit import api
            from livekit.agents import AgentSession
            from livekit.plugins.openai import realtime as openai_realtime
            
            token = (
                api.AccessToken(livekit_api_key, livekit_api_secret)
                # Mark this participant as an agent for clarity (optional but recommended)
                .with_kind("agent")
                .with_identity("simli-agent")
                .with_name("Simli Avatar Agent")
                .with_grants(
                    api.VideoGrants(
                        room_join=True,
                        room=room_name,
                        can_publish=True,
                        can_subscribe=True,
                        can_publish_data=True,
                    )
                )
            )
            agent_token = token.to_jwt()

            room = rtc.Room()
            await room.connect(livekit_url, agent_token)
            logger.info(f"✅ Agent connected to room: {room_name}")

            # Create Simli configuration
            simli_config = simli.SimliConfig(
                api_key=simli_api_key,
                face_id=simli_face_id,
            )

            # Create OpenAI Realtime Model with http session
            realtime_model = openai_realtime.RealtimeModel(
                model="gpt-4o-realtime-preview",
                voice="alloy",
                api_key=openai_api_key,
                temperature=0.8,
                http_session=http_context.http_session(),
            )
            
            # Create AgentSession with the Realtime LLM
            # AgentSession has .output property that AvatarSession.start() will use
            agent_session = AgentSession(
                llm=realtime_model,
            )
            
            # Create a simple Agent with instructions
            from livekit.agents import Agent
            agent = Agent(
                instructions=instructions,
                llm=realtime_model,
            )
            
            logger.info("✅ AgentSession created with OpenAI Realtime")
            
            # Create Simli avatar session
            logger.info("🎭 Starting Simli avatar with OpenAI Realtime...")
            avatar_session = simli.AvatarSession(
                simli_config=simli_config,
                avatar_participant_identity="simli-avatar",
                avatar_participant_name="AI Avatar",
            )

            # Start the avatar session - this handles everything internally:
            # - Spawns the Simli avatar agent via API
            # - Sets agent_session.output.audio to DataStreamAudioOutput
            # - The avatar renders video with lip-sync from audio stream
            await avatar_session.start(
                agent_session=agent_session,
                room=room,
                livekit_url=livekit_url,
                livekit_api_key=livekit_api_key,
                livekit_api_secret=livekit_api_secret,
            )
            logger.info("✅ Simli avatar started successfully!")
            
            # Start the agent session to process audio input
            # This connects the room audio to the OpenAI Realtime model
            # Disable audio output since AvatarSession already set up the output routing
            logger.info("🎧 Starting agent session to process audio...")
            from livekit.agents import RoomOutputOptions
            await agent_session.start(
                agent, 
                room=room,
                room_output_options=RoomOutputOptions(
                    audio_enabled=False,  # Disable default audio output - use Simli avatar instead
                    transcription_enabled=False,  # Disable transcription output
                )
            )
            logger.info("✅ Agent session running - listening for user input!")

            # Keep running while connected
            while room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
                await asyncio.sleep(1)

            # Cleanup
            await room.disconnect()
            logger.info(f"👋 Agent disconnected from room: {room_name}")
                
        except Exception as e:
            logger.error(f"❌ Error in agent task: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Ensure we close the plugin-managed HTTP session context
            try:
                await http_context._close_http_ctx()
            except Exception:
                pass


# Global service instance
simli_service = SimliAvatarService()
