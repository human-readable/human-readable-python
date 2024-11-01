## Installation


    pip install hrai_python

## Configuration



    from hrai_python import Logger

    #Initialize the Logger

    logger_instance = Logger(
        client_attr_name='client',        # Attribute name of the OpenAI client in your class
        enable_remote=True,               # Enable remote logging
        enable_async=True,                # Use asynchronous remote logging
        return_type=Logger.Return_Type.content_only
    )


## Configuration
hrai_python offers several configuration options when initializing the Logger class:

- client_instance (Optional[openai.ChatCompletion]): OpenAI client instance if standalone.
- client_attr_name (Optional[str]): Attribute name of the OpenAI client in your class (default: "client").
- base_url (Optional[str]): Remote server URL for logging (default: "https://api.humanreadable.ai/").
- apikey (Optional[str]): API key for authenticating with the remote logging server.
- log_file (str): Log file name (default: "hrai.log").
- log_level (str): Logging level, e.g., "INFO", "DEBUG", "WARNING".
- log_format (Optional[str]): Log message format (default: '%(asctime)s - %(levelname)s - %(message)s').
- enable_remote (bool): Enable/disable remote logging (default: True).
- enable_async (bool): Use asynchronous remote logging (default: False).
- return_type (Return_Type): Defines the format of the returned response from API calls.
### Return Types
The Return_Type enum in hrai_python defines the format of the response from OpenAI API calls:
- content_only (1): Returns only the message content. (default)
- json (2): Returns the response as a JSON object.
- openai_object (3): Returns the full OpenAI response object.