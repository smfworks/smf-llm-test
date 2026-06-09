"""
OpenAI provider for benchmarking
"""

import os
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from .base import BaseProvider, LLMRequest, LLMResponse

class OpenAIProvider(BaseProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        api_key = config.get("api_key") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")
        self.client = OpenAI(api_key=api_key)
        self.base_url = config.get("base_url")
        if self.base_url:
            self.client.base_url = self.base_url
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        
        # Build user content with context document if provided
        user_content = request.prompt
        if request.context_document:
            user_content = f"Context:\n{request.context_document}\n\n{request.prompt}"
        messages.append({"role": "user", "content": user_content})
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "stream": True,
        }
        
        if request.max_tokens:
            kwargs["max_tokens"] = request.max_tokens
        
        if request.tools:
            kwargs["tools"] = request.tools
            kwargs["tool_choice"] = request.tool_choice or "auto"
        
        if request.response_format:
            kwargs["response_format"] = request.response_format
        
        start_time = time.perf_counter()
        first_token_time = None
        full_text = ""
        tool_calls = []
        
        try:
            stream = self.client.chat.completions.create(**kwargs)
            
            for chunk in stream:
                if first_token_time is None and chunk.choices[0].delta.content:
                    first_token_time = time.perf_counter()
                
                if chunk.choices[0].delta.content:
                    full_text += chunk.choices[0].delta.content
                
                # Handle tool calls
                if chunk.choices[0].delta.tool_calls:
                    for tc in chunk.choices[0].delta.tool_calls:
                        tool_calls.append(tc)
            
            end_time = time.perf_counter()
            total_ms = (end_time - start_time) * 1000
            ttf_ms = (first_token_time - start_time) * 1000 if first_token_time else total_ms * 0.1
            
            # Estimate tokens from response
            # Rough heuristic: ~4 chars per token for English text
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
                raw_metadata={"tool_calls": len(tool_calls)}
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
        # Pricing as of June 2026 (approximate)
        pricing = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "o3": {"input": 10.00, "output": 40.00},
        }
        model_pricing = pricing.get(self.model, {"input": 2.50, "output": 10.00})
        input_cost = (input_tokens / 1000) * model_pricing["input"] / 100  # Convert to dollars
        output_cost = (output_tokens / 1000) * model_pricing["output"] / 100
        return input_cost + output_cost
