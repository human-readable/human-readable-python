import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from hrai_python.hrai_logger import hrai_logger
from hrai_python.hrai_utils import hrai_utils
 
load_dotenv()
logger = hrai_logger(apikey=os.environ.get("HUMANREADABLE_API_KEY"),
                     project_id=os.environ.get("HUMANREADABLE_PROJECT_ID"))
hrai_util = hrai_utils()

class gpt:
    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    @logger.readable
    def my_function_call(self, tools, messages):
        response = hrai_util.openai_function_call(self.client, self.model, tools, messages)
        return response
                
    @logger.readable
    def basic_completion(self, messages):
        completion = self.client.chat.completions.create(
        model = self.model,
        messages=messages
        )
        return(completion)
    
tools1 = hrai_utils.create_tool(name="Dont_Lie", 
                                    description= "Provide the requested information or let the user know if you do not have the information. Do not provide false information or lie. Don't request additional information from the user.", 
                                    properties = {
                                                "answer": {"type": "string", "description": "The data that was requested"},
                                                "reason": {"type": "string", "description": "The reason why the data is not available"},
                                                "additional_information": {"type": "string", "description": "Any additional information that may be relevant"}
                                            }, 
                                    require=["answer", "reason", "additional_information"]) 
tools2 = {
        "type": "function",
        "function": {
            "name": "Dont_Lie",
            "description": "Create a pokemon deck with the following pokemon.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "The data that was requested"},
                    "reason": {"type": "string", "description": "The reason why the data is not available"},
                    "additional_information": {"type": "string", "description": "Any additional information that may be relevant"}
                },
                "required": ["answer", "reason"]
            }
        }
    }


codes = ["""#FormatString.c
#include <stdio.h>
 
int main(int argc, char **argv) {
    char *secret = "This is a secret!\n";
 
    printf external link(argv[1]);
 
    return 0;
}"""]

for code in codes:
    template = f"Based on a preliminary static analysis of the provided code snippet, are there potential issues that could affect security and correctness? <code> {code} </code>"
    message = [
        {"role": "system", "content": "Provide as much information about the requested person as possible. If you do not have the information, let the user know."},
        {"role": "user", "content": f"{template}"}
    ]
    print(gpt().my_function_call(tools2, message))