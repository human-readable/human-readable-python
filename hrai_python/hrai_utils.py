from typing import Dict, List
from openai import OpenAI
import logging
import json

class hrai_utils:
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
    
    
    def openai_function_call(self, client: OpenAI, model: str, tools: dict, messages: List[dict], retry_count: int = 3) -> Dict:
        choice = {"type": "function", "function": {"name": tools["function"]["name"]}}
        chat_response = client.chat.completions.create(model=model, messages=messages, tools=[tools], tool_choice=choice)
        json_response = chat_response.choices[0].message.model_dump_json()
        data = json.loads(json_response)
        tools_calls = data.get("tool_calls", [])
        if tools_calls and 'function' in tools_calls[0]:
                function_data = tools_calls[0].get("function", {})
                arguments = function_data.get("arguments", "{}")
                try:
                    arguments_dict = json.loads(arguments)
                except json.JSONDecodeError:
                    if retry_count > 0:
                        return self.openai_function_call(tools, messages, retry_count - 1)
                    else:
                        logging.error("JSON Decode Error: Exceeded maximum retries")
                        return None
                required_fields = tools[0]["function"]["parameters"].get("required", [])
                missing_fields = [field for field in required_fields if arguments_dict.get(field) is None]
                if missing_fields:
                    logging.error(f"Missing required fields in arguments: {missing_fields}")
                    if retry_count > 0:
                        logging.warning("JSON Decode Error: Retrying function call")
                        return self.openai_function_call(tools, messages, retry_count - 1)
                    else:
                        logging.error("Missing required fields: Exceeded maximum retries")
                        return None
                return arguments_dict


    def openai_chat_completion(self, client: OpenAI, model: str, messages: List[dict], retry_count: int = 3) -> str:
        chat_response = client.chat.completions.create(model=model, messages=messages)
        return str(chat_response.choices[0].message)