import pytest
import requests
from meal_max.utils.random_utils import get_random


RANDOM_NUMBER = 0.42  # Example of a mock random number

@pytest.fixture
def mock_random_org(mocker):
    """Fixture to mock the response from random.org."""
    # Create a mock response object
    mock_response = mocker.Mock()
    # Set the text attribute to the value we want to simulate for random.org's response
    mock_response.text = f"{RANDOM_NUMBER}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_get_random_success(mock_random_org):
    """Test retrieving a random number from random.org."""
    result = get_random()

    # Assert that the result matches the mocked random number
    assert result == RANDOM_NUMBER, f"Expected random number {RANDOM_NUMBER}, but got {result}"

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with("https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new", timeout=5)


def test_get_random_request_failure(mocker):
    """Simulate a request failure (e.g., network issues)."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        get_random()


def test_get_random_timeout(mocker):
    """Simulate a timeout error from the request."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()


def test_get_random_invalid_response(mock_random_org):
    """Simulate receiving an invalid response (non-numeric value)."""
    mock_random_org.text = "invalid_response"

    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_response"):
        get_random()
