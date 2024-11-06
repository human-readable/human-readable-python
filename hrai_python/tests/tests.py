import pytest
import openai
import os
from datetime import datetime
from hrai_python.hrai_logger import hrai_logger
from hrai_python.hrai_utils import hrai_utils

# Configure OpenAI with your API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
logger = hrai_logger(base_url="https://api.humanreadable.ai/", apikey="test_api_key", enable_async=False, enable_remote=True,)

# Tests for gpt_utils functions

def test_create_tool_all_required():
    name = "test_tool"
    description = "A tool for testing"
    properties = {
        "answer": "The answer to the tool",
        "request": "The request to the tool"
    }
    
    tool = hrai_utils.create_tool(name, description, properties)
    
    # Assertions
    assert tool["function"]["name"] == name
    assert tool["function"]["description"] == description
    assert "answer" in tool["function"]["parameters"]["properties"]
    assert "request" in tool["function"]["parameters"]["properties"]
    assert tool["function"]["parameters"]["required"] == list(properties.keys())

def test_create_tool_custom_required():
    name = "test_tool"
    description = "A tool for testing"
    properties = {
        "answer": "The answer to the tool",
        "request": "The request to the tool"
    }
    
    required_fields = ["answer"]
    tool = hrai_utils.create_tool(name, description, properties, require=required_fields)
    
    # Assertions
    assert tool["function"]["parameters"]["required"] == required_fields

def test_create_prompt_success():
    template = "What is the capital of {country}?"
    inputs = {"country": "France"}
    
    prompt = hrai_utils.create_prompt(template, inputs)
    
    # Assertion
    assert prompt == "What is the capital of France?"

def test_create_prompt_missing_input():
    template = "What is the capital of {country}?"
    inputs = {"city": "Paris"}
    
    with pytest.raises(ValueError, match="Missing value for placeholder"):
        hrai_utils.create_prompt(template, inputs)


# Integration Tests with Real OpenAI Requests
@logger.readable
def real_chat_completion(messages, model="gpt-4o"):
    """
    A test function to send real requests to OpenAI's Chat API.
    Decorated with @hrai_logger.readable to log messages, response, and timestamp.
    """
    response = openai.chat.completions.create(
        model=model,
        messages=messages
    )
    return str(response.choices[0].message)  # Access the content in the updated format

def test_real_chat_completion_success():
    # Send a real request to OpenAI
    messages = [{"role": "user", "content": "What is the capital of France?"}]
    response = real_chat_completion(messages=messages)
    
    # Assertions
    assert isinstance(response, str)
    assert "Paris" in response  # Check if response contains the correct answer

def test_real_chat_completion_error():
    # Test a real request with an invalid model to trigger an error
    messages = [{"role": "user", "content": "This should fail"}]

    with pytest.raises(openai.OpenAIError):  # Use OpenAI's general error
        real_chat_completion(messages=messages, model="invalid-model")
        
import pytest
from hrai_python.hrai_logger import logger
import logging
from datetime import datetime

# Updated mock function to return a response structure expected by the decorator
def mock_function_call(*args, **kwargs):
    return {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "get_current_weather",
                                "arguments": "{\"location\": \"Boston, MA\"}"
                            }
                        }
                    ]
                }
            },
            {
                "message": {
                    "content": "The capital of France is Paris."
                }
            }
        ]
    }

def test_readable_decorator_with_function_call(monkeypatch):
    # Instantiate logger with enable_async=False to ensure log_remote is used
    test_logger = logger(base_url="https://api.humanreadable.ai/", apikey="test_api_key", enable_async=False)

    # Wrap the mock function with the readable decorator
    decorated_function = test_logger.readable(mock_function_call)

    # Prepare to capture requests.post calls
    post_calls = []

    def mock_post(url, json, headers):
        post_calls.append({"url": url, "json": json, "headers": headers})
        # Mock response with raise_for_status method
        class MockResponse:
            status_code = 200
            def raise_for_status(self):
                pass  # No-op method to simulate successful status check

        return MockResponse()

    # Ensure monkeypatch points to the correct path in the logger module
    monkeypatch.setattr("hrai_python.hrai_logger.requests.post", mock_post)

    # Define input for the decorated function
    messages = [{"role": "user", "content": "What is the capital of France?"}]

    # Call the decorated function
    response = decorated_function(messages=messages)

    # Assertions for the function response
    assert response["choices"][0]["message"]["tool_calls"][0]["function"]["name"] == "get_current_weather"
    assert response["choices"][1]["message"]["content"] == "The capital of France is Paris."

    # Validate the combined log entry structure
    log_entry = post_calls[0]["json"]
    assert log_entry["request"]["event"] == "ChatCompletionRequest"
    assert log_entry["request"]["request"] == messages

    # Validate the response structure within the single log entry
    assert len(log_entry["responses"]) == 2
    assert log_entry["responses"][0]["event"] == "ChatCompletionToolCall"
    assert log_entry["responses"][0]["function_name"] == "get_current_weather"
    assert log_entry["responses"][1]["event"] == "ChatCompletionResponse"
    assert log_entry["responses"][1]["content"] == "The capital of France is Paris."