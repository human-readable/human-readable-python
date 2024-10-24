import pytest
from human_readable import readable

@readable
def mock_function(x, y):
    return x + y

def test_mock_function():
    assert mock_function(2, 3) == 5
