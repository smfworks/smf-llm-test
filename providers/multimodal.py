"""
OpenRouter Multimodal Provider Extension
Handles image, video, and audio uploads for NVIDIA Nemotron 3 Nano Omni and other multimodal models.
"""

import os
import base64
import mimetypes
from typing import Optional, List, Dict, Any
from pathlib import Path

class MultimodalRequest:
    """Extended request with asset attachment support"""
    def __init__(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        video_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        text_context_path: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        self.prompt = prompt
        self.image_path = image_path
        self.video_path = video_path
        self.audio_path = audio_path
        self.text_context_path = text_context_path
        self.max_tokens = max_tokens
        self.temperature = temperature

    def has_multimodal_assets(self) -> bool:
        return any([self.image_path, self.video_path, self.audio_path])

    def asset_count(self) -> int:
        return sum([
            1 if self.image_path else 0,
            1 if self.video_path else 0,
            1 if self.audio_path else 0
        ])


def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 for API upload."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def encode_audio_to_base64(audio_path: str) -> str:
    """Encode an audio file to base64 for API upload."""
    with open(audio_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')


def get_mime_type(file_path: str) -> str:
    """Determine MIME type from file extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


def build_openai_multimodal_messages(request: MultimodalRequest) -> List[Dict[str, Any]]:
    """
    Build OpenAI-compatible message list with multimodal content.
    Supports: image_url (base64), audio (base64), text context.
    Note: Video is not natively supported by OpenAI API — requires frame extraction.
    """
    content = []
    
    # Add image if present
    if request.image_path and os.path.exists(request.image_path):
        mime_type = get_mime_type(request.image_path)
        base64_data = encode_image_to_base64(request.image_path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{base64_data}",
                "detail": "high"
            }
        })
    
    # Add audio if present (OpenAI now supports audio in some models)
    if request.audio_path and os.path.exists(request.audio_path):
        mime_type = get_mime_type(request.audio_path)
        base64_data = encode_audio_to_base64(request.audio_path)
        content.append({
            "type": "input_audio",
            "input_audio": {
                "data": base64_data,
                "format": mime_type.split('/')[-1] if '/' in mime_type else "mp3"
            }
        })
    
    # Add text context if present (for cross-modal pair tests)
    if request.text_context_path and os.path.exists(request.text_context_path):
        with open(request.text_context_path, 'r') as f:
            text_context = f.read()
        content.append({
            "type": "text",
            "text": f"[Context from accompanying text:]\n{text_context}\n\n[Question:]\n{request.prompt}"
        })
    else:
        content.append({
            "type": "text",
            "text": request.prompt
        })
    
    return [{"role": "user", "content": content}]


def build_gemini_multimodal_payload(request: MultimodalRequest) -> Dict[str, Any]:
    """
    Build Gemini-compatible payload.
    Gemini supports: images (base64), video (file upload or base64 chunks), audio (base64).
    """
    parts = []
    
    # Add text prompt
    parts.append({"text": request.prompt})
    
    # Add image
    if request.image_path and os.path.exists(request.image_path):
        mime_type = get_mime_type(request.image_path)
        base64_data = encode_image_to_base64(request.image_path)
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": base64_data
            }
        })
    
    # Add video (Gemini supports video file uploads up to 1 hour)
    if request.video_path and os.path.exists(request.video_path):
        mime_type = get_mime_type(request.video_path)
        # For Gemini, video is typically uploaded as a file resource
        # This is a simplified base64 approach — in production, use file upload API
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": "VIDEO_UPLOAD_REQUIRED"  # Placeholder — use file upload API
            }
        })
    
    # Add audio
    if request.audio_path and os.path.exists(request.audio_path):
        mime_type = get_mime_type(request.audio_path)
        base64_data = encode_audio_to_base64(request.audio_path)
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": base64_data
            }
        })
    
    return {"contents": [{"role": "user", "parts": parts}]}


def build_ollama_multimodal_payload(request: MultimodalRequest) -> Dict[str, Any]:
    """
    Build Ollama-compatible payload.
    Ollama (Qwen2-VL) supports: images (base64 only), no video/audio natively.
    """
    messages = []
    
    content = request.prompt
    
    # Add image as base64
    if request.image_path and os.path.exists(request.image_path):
        base64_data = encode_image_to_base64(request.image_path)
        content = f"{request.prompt}\n\n![image](data:image/jpeg;base64,{base64_data})"
    
    messages.append({"role": "user", "content": content})
    
    return {
        "model": "qwen2-vl:7b",
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": request.temperature,
            "num_predict": request.max_tokens
        }
    }


# Video frame extraction helper
def extract_video_frames(video_path: str, frame_count: int = 3) -> List[str]:
    """
    Extract evenly-spaced frames from a video for models without native video support.
    Returns list of base64-encoded frame strings.
    """
    import cv2
    
    frames_base64 = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        raise ValueError(f"Video has no frames: {video_path}")
    
    # Calculate frame positions
    step = total_frames // (frame_count + 1)
    positions = [step * (i + 1) for i in range(frame_count)]
    
    for pos in positions:
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ret, frame = cap.read()
        if ret:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            base64_frame = base64.b64encode(buffer).decode('utf-8')
            frames_base64.append(base64_frame)
    
    cap.release()
    return frames_base64


# Provider dispatch map
MULTIMODAL_BUILDERS = {
    "openai": build_openai_multimodal_messages,
    "openrouter": build_openai_multimodal_messages,  # OpenRouter is OpenAI-compatible
    "gemini": build_gemini_multimodal_payload,
    "ollama": build_ollama_multimodal_payload,
}

def build_multimodal_payload(provider: str, request: MultimodalRequest) -> Any:
    """Dispatch to the appropriate builder based on provider type."""
    builder = MULTIMODAL_BUILDERS.get(provider)
    if not builder:
        raise ValueError(f"No multimodal builder for provider: {provider}")
    return builder(request)
