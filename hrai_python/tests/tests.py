import pytest
import openai
import os
from datetime import datetime
from hrai_python import hrai_logger, gpt_utils

# Configure OpenAI with your API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Tests for gpt_utils functions

def test_create_tool_all_required():
    name = "test_tool"
    description = "A tool for testing"
    properties = {
        "answer": "The answer to the tool",
        "request": "The request to the tool"
    }
    
    tool = gpt_utils.create_tool(name, description, properties)
    
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
    tool = gpt_utils.create_tool(name, description, properties, require=required_fields)
    
    # Assertions
    assert tool["function"]["parameters"]["required"] == required_fields

def test_create_prompt_success():
    template = "What is the capital of {country}?"
    inputs = {"country": "France"}
    
    prompt = gpt_utils.create_prompt(template, inputs)
    
    # Assertion
    assert prompt == "What is the capital of France?"

def test_create_prompt_missing_input():
    template = "What is the capital of {country}?"
    inputs = {"city": "Paris"}
    
    with pytest.raises(ValueError, match="Missing value for placeholder"):
        gpt_utils.create_prompt(template, inputs)


# Integration Tests with Real OpenAI Requests

@hrai_logger.readable
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
