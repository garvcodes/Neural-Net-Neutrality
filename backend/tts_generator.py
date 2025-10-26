"""
Text-to-Speech audio generation for podcasts.

This module provides simple TTS functionality for converting podcast scripts to audio.
Currently uses pyttsx3 (offline) but can be extended to use ElevenLabs or other services.
"""

import os
import asyncio
from typing import Optional
from datetime import datetime
import base64


async def generate_audio_from_script(
    script: str,
    voice: str = "news_anchor",
    output_dir: str = "podcast_audio"
) -> Optional[str]:
    """
    Generate audio from a podcast script.
    
    Args:
        script: The podcast script text to convert to audio
        voice: Voice profile to use (e.g., "news_anchor")
        output_dir: Directory to save audio files
    
    Returns:
        Base64 encoded audio data that can be used as data URL
    
    Note: For production, integrate with ElevenLabs, Google TTS, or AWS Polly
    """
    try:
        import pyttsx3
        
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize text-to-speech engine
        engine = pyttsx3.init()
        
        # Configure voice settings
        engine.setProperty('rate', 150)  # Slower rate for news-like delivery
        engine.setProperty('volume', 0.9)
        
        # Set voice (male for news anchor feel)
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)  # Usually male voice is second
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_file = os.path.join(output_dir, f"podcast_{timestamp}.mp3")
        
        # Save to file
        engine.save_to_file(script, audio_file)
        engine.runAndWait()
        
        print(f"Generated audio: {audio_file}")
        
        # For now, return the file path
        # In production, upload to cloud storage and return URL
        return f"/api/audio/{os.path.basename(audio_file)}"
        
    except ImportError:
        print("pyttsx3 not installed. Install with: pip install pyttsx3")
        return None
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None


async def generate_audio_base64(script: str, voice: str = "news_anchor") -> Optional[str]:
    """
    Generate audio and return as base64-encoded data URL.
    
    This allows embedding audio directly in responses without file storage.
    
    Returns:
        Data URL with base64-encoded audio (e.g., "data:audio/mp3;base64,...")
    """
    try:
        import pyttsx3
        from io import BytesIO
        
        # Create in-memory audio
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # Configure for news-like voice
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        
        # Use a temporary file (pyttsx3 requires file output)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            temp_path = tmp.name
        
        try:
            engine.save_to_file(script, temp_path)
            engine.runAndWait()
            
            # Read and encode
            with open(temp_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Convert to base64 data URL
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            return f"data:audio/mp3;base64,{audio_b64}"
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except ImportError:
        print("pyttsx3 not installed. Install with: pip install pyttsx3")
        return None
    except Exception as e:
        print(f"Error generating audio data URL: {e}")
        return None


# Future integration examples

async def generate_with_elevenlabs(
    script: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel - professional female
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    Generate audio using ElevenLabs API (requires API key).
    
    Args:
        script: Script text
        voice_id: ElevenLabs voice ID
        api_key: ElevenLabs API key (or use ELEVENLABS_API_KEY env var)
    
    Returns:
        URL to generated audio file
    
    Install with: pip install elevenlabs
    """
    try:
        from elevenlabs import generate, play, save
        from elevenlabs.client import ElevenLabs
        
        api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            print("ElevenLabs API key not found")
            return None
        
        client = ElevenLabs(api_key=api_key)
        
        # Generate audio
        audio = generate(
            text=script,
            voice=voice_id,
            model="eleven_monolingual_v1",
            api_key=api_key
        )
        
        # Save to file
        os.makedirs("podcast_audio", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = f"podcast_audio/podcast_{timestamp}.mp3"
        
        save(audio, audio_path)
        
        print(f"Generated audio with ElevenLabs: {audio_path}")
        return f"/api/audio/{os.path.basename(audio_path)}"
        
    except ImportError:
        print("elevenlabs not installed. Install with: pip install elevenlabs")
        return None
    except Exception as e:
        print(f"Error with ElevenLabs: {e}")
        return None


async def generate_with_google_tts(
    script: str,
    language: str = "en-US",
    output_file: Optional[str] = None
) -> Optional[str]:
    """
    Generate audio using Google Text-to-Speech API.
    
    Args:
        script: Script text
        language: Language code (e.g., "en-US")
        output_file: Path to save audio
    
    Returns:
        Path to generated audio file
    
    Install with: pip install google-cloud-texttospeech
    """
    try:
        from google.cloud import texttospeech
        
        client = texttospeech.TextToSpeechClient()
        
        # Set synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=script)
        
        # Build voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            name=f"{language}-Neural2-C"  # Neural voice
        )
        
        # Select audio encoding
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95
        )
        
        # Make request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Write audio to file
        output_file = output_file or f"podcast_audio/podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        
        print(f"Generated audio with Google TTS: {output_file}")
        return f"/api/audio/{os.path.basename(output_file)}"
        
    except ImportError:
        print("google-cloud-texttospeech not installed")
        print("Install with: pip install google-cloud-texttospeech")
        return None
    except Exception as e:
        print(f"Error with Google TTS: {e}")
        return None


# Integration ready for FastAPI

def get_tts_generator(provider: str = "pyttsx3"):
    """
    Get TTS generator function based on provider.
    
    Usage in FastAPI:
        tts_gen = get_tts_generator("elevenlabs")
        audio_url = await tts_gen(script)
    """
    providers = {
        "pyttsx3": generate_audio_from_script,
        "elevenlabs": generate_with_elevenlabs,
        "google": generate_with_google_tts,
    }
    
    generator = providers.get(provider)
    if not generator:
        print(f"Unknown TTS provider: {provider}")
        return None
    
    return generator
