import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Dripple Video Processing API" in response.json()["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_health_check():
    """Test API health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_system_status():
    """Test system status endpoint"""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert response.json()["system"] == "operational"


def test_metrics_endpoint():
    """Test metrics endpoint"""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.json()


def test_list_videos_empty():
    """Test listing videos when none exist"""
    response = client.get("/api/v1/videos/")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["videos"] == []


def test_upload_video_invalid_file():
    """Test uploading invalid file"""
    response = client.post(
        "/api/v1/videos/upload",
        files={"file": ("test.txt", b"not a video", "text/plain")}
    )
    assert response.status_code == 400


def test_get_nonexistent_video():
    """Test getting non-existent video"""
    response = client.get("/api/v1/videos/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_trim_video_invalid_request():
    """Test trim video with invalid request"""
    response = client.post(
        "/trim",
        json={
            "video_id": "00000000-0000-0000-0000-000000000000",
            "start_time": 10.0,
            "end_time": 5.0  # Invalid: end time before start time
        }
    )
    assert response.status_code == 400


def test_job_status_nonexistent():
    """Test getting status of non-existent job"""
    response = client.get("/status/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_job_result_nonexistent():
    """Test getting result of non-existent job"""
    response = client.get("/result/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
