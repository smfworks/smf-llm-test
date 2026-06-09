"""
Anthropic provider for benchmarking
"""

import os
import time
from typing import Dict, Any
from anthropic import Anthropic
from .base import BaseProvider, LLMRequest, LLMResponse

class AnthropicProvider(BaseProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        api_key = config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key required")
        self.client = Anthropic(api_key=api_key)
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        system = request.system_prompt
        
        # Build user content with context document
        user_content = request.prompt
        if request.context_document:
            user_content = f"Context:\n{request.context_document}\n\n{request.prompt}"
        
        kwargs = {
            "model": self.model,
            "max_tokens": request.max_tokens or 4096,
            "temperature": request.temperature,
            "messages": [{"role": "user", "content": user_content}],
            "stream": True,
        }
        
        if system:
            kwargs["system"] = system
        
        if request.tools:
            kwargs["tools"] = request.tools
            kwargs["tool_choice"] = {"type": request.tool_choice or "auto"}
        
        start_time = time.perf_counter()
        first_token_time = None
        full_text = ""
        
        try:
            with self.client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                    full_text += text
            
            end_time = time.perf_counter()
            total_ms = (end_time - start_time) * 1000
            ttf_ms = (first_token_time - start_time) * 1000 if first_token_time else total_ms * 0.1
            
            # Estimate tokens
            output_tokens = len(full_text) // 4 if full_text else 0
            input_tokens = len(user_content) // 4 if user_content else 0
            
            tokens_per_sec = None
            if output_tokens > 0 and first_token_time:
                gen_time = end_time - first_token_time
                if gen_time > 0:
                    tokens_per_sec = output_tokens / gen_time
            
            return LLMResponse(
                text=full_text.strip(),
                time_to_first_token_ms=ttf_ms,
                total_time_ms=total_ms,
                tokens_generated=output_tokens,
                tokens_per_second=tokens_per_sec,
            )
            
        except Exception as e:
            return LLMResponse(
                text="",
                time_to_first_token_ms=0,
                total_time_ms=0,
                error=str(e)
            )
    
    def supports_tools(self) -> bool:
        return True
    
    def supports_json_mode(self) -> bool:
        return True
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = {
            "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
            "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
            "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        }
        model_pricing = pricing.get(self.model, {"input": 3.00, "output": 15.00})
        input_cost = (input_tokens / 1000) * model_pricing["input"] / 100
        output_cost = (output_tokens / 1000) * model_pricing["output"] / 100
        return input_cost + output_cost
