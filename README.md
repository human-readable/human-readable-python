## hrai_python

A Python package designed to log and monitor interactions with OpenAI’s API, supporting both local and remote logging. It enables structured logging for OpenAI API calls and facilitates asynchronous remote logging for scalability.

### Installation

Install the package using pip:

```bash
pip install hrai_python
```

### Configuration

Initialize the logger with options for configuring the OpenAI client, logging preferences, and remote logging.

```python
from hrai_python.hrai_logger import hrai_logger

# Initialize the Logger
logger_instance = hrai_logger(
    client_attr_name='client',       # Attribute name of the OpenAI client in your class
    enable_remote=True,              # Enable remote logging
    enable_async=True,               # Use asynchronous remote logging
    return_type=hrai_logger.Return_Type.content_only
)
```

### Basic Usage Example

```python
import os
from openai import OpenAI
from dotenv import load_dotenv
from hrai_python.hrai_logger import hrai_logger

# Initialize the logger
logger = hrai_logger()

class GPTClient:
    def __init__(self):
        load_dotenv()
        self.model = os.environ.get("OPENAI_MODEL")
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    @logger.readable
    def basic_completion(self, messages):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return completion
```

### Configuration Options

`hrai_logger` offers flexible configuration options:

- **client_instance** (*Optional[openai.ChatCompletion]*): OpenAI client instance if standalone.
- **client_attr_name** (*Optional[str]*): Attribute name of the OpenAI client in your class (`default: "client"`).
- **base_url** (*Optional[str]*): Remote server URL for logging (`default: "https://api.humanreadable.ai/"`).
- **apikey** (*Optional[str]*): API key for authenticating with the remote logging server.
- **log_file** (*str*): Log file name (`default: "hrai.log"`).
- **log_level** (*str*): Logging level, e.g., "INFO", "DEBUG", "WARNING".
- **log_format** (*Optional[str]*): Log message format (`default: "%(asctime)s - %(levelname)s - %(message)s"`).
- **enable_remote** (*bool*): Enable/disable remote logging (`default: True`).
- **enable_async** (*bool*): Use asynchronous remote logging (`default: False`).
- **return_type** (*Return_Type*): Format of the response from API calls (`default: content_only`).

### Return Types

`Return_Type` defines the format of responses from OpenAI API calls:
- **content_only** (1): Returns only the message content.
- **json** (2): Returns the response as a JSON object.
- **openai_object** (3): Returns the full OpenAI response object.

---

## Utilities with hrai_utils

### Tool Creation

`hrai_utils.create_tool` helps build tool structures for OpenAI function calls.

```python
from hrai_python.hrai_utils import hrai_utils

# Define tool properties
name = "my_tool"
description = "This is a tool that does something"
properties = {
    "answer": "The answer to the tool",
    "request": "The request to the tool"
}

# Create a tool dictionary
my_tool = hrai_utils.create_tool(name, description, properties)
```