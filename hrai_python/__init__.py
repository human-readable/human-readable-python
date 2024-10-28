import logging
from datetime import datetime
from functools import wraps
from typing import Dict, List, Callable, Any

logging.basicConfig(
    filename="openai_chat_requests.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
    )

class gpt_utils:
    # Helper to build tools for OpenAI function calls
    # Example usage:
    # name = "my_tool" 
    # description = "This is a tool that does something"    
    # properties = {
    #     "answer": "The answer to the tool",
    #     "request": "The request to the tool"
    # }
    # my_tool = gpt_utils.create_tool(name, description, properties)
    def create_tool(name: str, description: str, properties: Dict[str, str], require: List[str] = None) -> dict:
        properties_dict = {
            prop_name: {
                "type": "string",
                "description": prop_desc
            }
            for prop_name, prop_desc in properties.items()
        }
        
        required_properties = require if require is not None else list(properties.keys())

        tool = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties_dict,
                    "required": required_properties
                }
            }
        }
        return tool

    # Helper to create a prompt string from a template and inputs
    # Example usage:
    # template = "What is the capital of {country}?"
    # inputs = {"country": "France"}
    # prompt = gpt_utils.create_prompt(template, inputs)
    def create_prompt(template, inputs: Dict[str, str]) -> str:
        try:
            prompt = template.format(**inputs)
        except KeyError as e:
            missing_key = str(e).strip("'")
            raise ValueError(f"Missing value for placeholder: '{missing_key}' in inputs.")
        
        return prompt

class hrai_logger:
    def readable(func: Callable) -> Callable:
        """
        A decorator to log the messages, response, and timestamp of a chat completion request.

        Args:
            func (Callable): The function to wrap and log.

        Returns:
            Callable: The wrapped function with logging.
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Extract messages for logging
            messages = kwargs.get("messages", args[0] if args else None)
            
            # Log the messages and current time before making the request
            logging.info({
                "event": "ChatCompletionRequest",
                "messages": messages,
                "timestamp": datetime.now().isoformat()
            })

            try:
                # Call the original function to get the response
                response = func(*args, **kwargs)
                
                logging.info({
                    "event": "ChatCompletionResponse",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                return response
            except Exception as e:
                logging.error({
                    "event": "ChatCompletionError",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                raise

        return wrapper
