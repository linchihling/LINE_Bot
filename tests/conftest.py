import pytest

from dotenv import load_dotenv
load_dotenv() 

from fastapi.testclient import TestClient
from main import app  

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
