import logging
from datetime import datetime
from functools import wraps
import requests
from typing import Optional
from enum import Enum
import os
from concurrent.futures import ThreadPoolExecutor
import openai
import httpx

class logger:
    class Return_Type(Enum):
        content_only = 1
        json = 2
        openai_object = 3
    def __init__(self, 
                 client_instance: Optional[openai.ChatCompletion] = None,
                 client_attr_name: Optional[str] = "client",
                 base_url: Optional[str] = None, 
                 apikey: Optional[str] = None, 
                 log_file: str = "hrai.log", 
                 log_level: str = "INFO", 
                 log_format: Optional[str] = None, 
                 enable_remote: bool = True, 
                 enable_async: bool = False, 
                 return_type: Return_Type = Return_Type.content_only):
        self.base_url = base_url or "https://api.humanreadable.ai/"
        self.apikey = apikey or os.getenv("HRAI_API_KEY")
        self.log_file = log_file
        self.log_format = log_format or "%(asctime)s - %(levelname)s - %(message)s"
        self.log_level = log_level
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.enable_remote = enable_remote
        self.enable_async = enable_async
        self._configure_logging()
        self.client_instance = client_instance
        self.client_attr_name = client_attr_name
        self.return_type = return_type

    def _configure_logging(self):
        
        logging.basicConfig(
            level=self.log_level,
            format=self.log_format,
            handlers=[
                logging.FileHandler(self.log_file),    # File logging
                logging.StreamHandler()           # Console logging
            ]
        )
        logging.info("Logging configured with level %s", self.log_level)

        
    def log_remote(self, log_data: dict):
        if not self.enable_remote:
            return
        
        if self.base_url == "https://api.humanreadable.ai/":
            headers = {"Authorization": f"Bearer {self.apikey}"} if self.apikey else {}
            try:
                response = requests.post(f"{self.base_url}/logs", json=log_data, headers=headers)
                response.raise_for_status()
                logging.info("Remote log sent successfully.")
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to send remote log: {e}")
                
    def log_remote_async(self, log_data: dict):
        self.executor.submit(self.log_remote, log_data)
    
    def readable(self, func):
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            request_info = {}
            def on_request(request):
                logging.info("Captured HTTP request:")
                logging.info(f"Method: {request.method}")
                logging.info(f"URL: {request.url}")
                logging.info(f"Headers: {request.headers}")
                logging.info(f"Content: {request.content.decode('utf-8')}")
                request_info['method'] = request.method
                request_info['url'] = str(request.url)
                request_info['content'] = request.content.decode('utf-8')
            if self.client_instance:
                client = self.client_instance
            else:
                client = getattr(instance, self.client_attr_name)

            original_client = client._client

            transport = httpx.HTTPTransport()
            event_hooks = {'request': [on_request]}
            new_httpx_client = httpx.Client(transport=transport, event_hooks=event_hooks)

            instance.client._client = new_httpx_client
            try:
                result = func(instance, *args, **kwargs)
                logging.info(f"result type: {type(result)}")
                log_data = {
                    "request": request_info,
                    "response": {
                        "content": result,
                    },
                    "timestamp": datetime.now().isoformat()
                }
                if self.enable_remote == True:
                    if self.enable_async:
                        self.log_remote_async(log_data)
                    else:
                        self.log_remote(log_data)
                logging.info(f"log: {log_data}")

            finally:
                instance.client._client = original_client
            if type(result) == openai.types.chat.chat_completion.ChatCompletion:
                if self.return_type == self.Return_Type.content_only:
                    return result.choices[0].message.content
                elif self.return_type == self.Return_Type.json:
                    return result.to_json()
                return result
        return wrapper