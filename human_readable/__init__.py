import openai
import requests
import functools


LOG_REQUEST_URL = "https://humanreadable.ai/logger/request"
LOG_RESPONSE_URL = "https://humanreadable.ai/logger/response"


class ToolBuilder:
    def __init__(self, model="gpt-4", api_key=None):
        self.model = model
        self.api_key = api_key if api_key else "Your_OpenAI_API_Key"
        self.template = {}

    def add_prompt(self, prompt: str):
        self.template['prompt'] = prompt
        return self

    def set_max_tokens(self, max_tokens: int):
        self.template['max_tokens'] = max_tokens
        return self

    def set_temperature(self, temperature: float):
        self.template['temperature'] = temperature
        return self

    def build(self):
        """Build the request template for the OpenAI function call."""
        if 'prompt' not in self.template:
            raise ValueError("Prompt is required to build a request")
        return {
            'model': self.model,
            **self.template
        }

    def make_request(self):
        """Make the OpenAI function call based on the built template."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required for the request")
        
        openai.api_key = self.api_key
        response = openai.Completion.create(**self.build())
        return response


def log_data(url, data):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to log data to {url}: {e}")


def readable(func):
    """A decorator to log OpenAI requests and responses."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Log the request data
        request_data = {"args": args, "kwargs": kwargs}
        log_data(LOG_REQUEST_URL, request_data)

        # Make the actual function call
        response = func(*args, **kwargs)

        # Log the response data
        response_data = {"response": response}
        log_data(LOG_RESPONSE_URL, response_data)

        return response
    return wrapper


@readable
def make_openai_request(prompt):
    """Example OpenAI request using the decorator and ToolBuilder."""
    tool_builder = ToolBuilder(model="gpt-4")
    tool_builder.add_prompt(prompt).set_max_tokens(100).set_temperature(0.7)

    response = tool_builder.make_request()
    return response
