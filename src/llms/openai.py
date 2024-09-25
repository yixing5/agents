'''
Author: Sasha
Date: 2024-06-27 11:48:00
LastEditors: Sasha
LastEditTime: 2024-07-03 08:58:36
Description: 
FilePath: /v2/src/llms/openai.py
'''
'''
Author: Sasha
Date: 2024-06-25 11:00:15
LastEditors: Sasha
LastEditTime: 2024-06-26 08:51:32
Description: 
FilePath: /project_agent_raw/src/llm/openai.py
'''
import json
import jsonlines
import os
from typing import List, Optional, Callable
from functools import wraps
from typing import List, Optional
from openai import OpenAI
from core.logger import logger
from src.utils.cache import cache

def log_and_save_result(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        response = func(self, *args, **kwargs)
        total_tokens = response.usage.total_tokens
        query = args[0]  # assuming messages is the first argument
        content = response.choices[0].message.content.strip()
        
        if response.choices[0].message.tool_calls:
            function = response.choices[0].message.tool_calls[0].function
            func_args = function.arguments
            func_name = function.name
        else:
            func_args = None
            func_name = None
        
        result = {
            "total_tokens": total_tokens,
            "tools": True,
            "query": query,
            "content": content,
            "func_name": func_name,
            "func_args": func_args,
        }
        
        logger.info("######" * 20)
        logger.info("tools")
        if isinstance(query, list):
            for q in query:
                logger.info(json.dumps({"query": q}, ensure_ascii=False, indent=4).replace('\\n', '\n'))
        else:
            logger.info(json.dumps({"query": query}, ensure_ascii=False, indent=4).replace('\\n', '\n'))
        
        logger.info(total_tokens)
        logger.info(f"{content}, {func_name}, {func_args}")
        logger.info("******" * 20)
        
        with jsonlines.open('total_tokens.json', "a") as json_file:
            json_file.write(result)
        
        return response
    return wrapper

class BaseAPIModel:
    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None, api_key: Optional[str] = None,):
        self.model = model or os.getenv('MODEL_NAME')
    
    def chat(self, messages: List[dict],tools: Optional[List] = None):
        pass


class OpenAIAPI(BaseAPIModel):
    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None, api_key: Optional[str] = None, temperature: float = 0.1, top_p: float = 0.9):
        self.temperature = temperature
        self.top_p = top_p
        self.model = model or os.getenv('MODEL_NAME')
        base_url = base_url or os.getenv('OPENAI_API_BASE')
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    @log_and_save_result
    def _chat(self, messages: List[dict], tools: Optional[List] = None):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        return response
    
    @cache(tags=('agent', '_chat'), ttl=60*60*24)
    def chat(self, messages: List[dict], tools: Optional[List] = None):
        response = self._chat(messages, tools)
        return response.choices[0].message.model_dump()
    
    
