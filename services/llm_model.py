import os
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_ORGANIZATION = os.getenv('OPENAI_ORGANIZATION')
clientOpenAI = OpenAI(api_key=OPENAI_API_KEY, organization=OPENAI_ORGANIZATION)


class GPTLLMParametersClass(BaseModel):
    max_tokens: Optional[int] = 4096
    model: Optional[str] = 'gpt-4o'
    temperature: Optional[int | float] = 0.01


class LLMModel:
    def __init__(self):
        self.default_params = GPTLLMParametersClass()

    def generate(self, prompt: str, system_prompt: str | None = None, json_schema: str = None, params: GPTLLMParametersClass = None) -> str:

        params = params if params else self.default_params
        
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        response = clientOpenAI.chat.completions.create(
        model = params.model,
        messages = messages,
        max_tokens = params.max_tokens,
        temperature = params.temperature,
        functions = [{"name": "set_format", "parameters": json.loads(json_schema)}] if json_schema else None,
        function_call = {"name": "set_format"} if json_schema else None,
        )
        
        response_message = response.choices[0].message.function_call.arguments if json_schema else response.choices[0].message.content
        return response_message