# test_main.py
from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app is in app/main.py

client = TestClient(app)  # Create a test client for your app

# Test for the root endpoint
def test_read_root():
    response = client.get("/")  # Make a GET request to the root endpoint
    assert response.status_code == 200  # Check if the response status is 200
    assert response.json() == {"message": "Welcome to the Hospital Management System API"}  # Check if the response data is as expected
