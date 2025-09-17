# 🎬 How to Use Dripple Video Processing API

This guide will walk you through using the Dripple Video Processing API from the very first time you set it up.

## 🚀 Quick Start (First Time Setup)

### Step 1: Start the Application

Choose one of these methods:

#### Option A: Docker (Easiest)
```bash
cd backend
docker-compose up --build
```

#### Option B: Local Setup
```bash
cd backend
python run_dev.py
python init_db.py
python start.py
```

### Step 2: Verify It's Working
Open your browser and go to:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

You should see the interactive API documentation and a healthy status.

## 📚 API Usage Guide

### 🔗 Base URL
All API calls should be made to: `http://localhost:8000`

### 📖 Interactive Documentation
The easiest way to explore the API is through the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Level-by-Level Usage Guide

### Level 1: Upload & Metadata

#### 1.1 Upload a Video
```bash
# Option 1: Upload a local video file
curl -X POST "http://localhost:8000/api/v1/videos/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@input.mp4"


**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "video_id": "112c7962-b958-4947-8da4-db02b011a48e",
  "job_type": "upload",
  "status": "pending",
  "progress": 0,
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### 1.2 List All Videos
```bash
curl -X GET "http://localhost:8000/api/v1/videos/"
```

**Response:**
```json
{
  "videos": [
    {
      "id": "112c7962-b958-4947-8da4-db02b011a48e",
      "filename": "video_123.mp4",
      "original_filename": "my_video.mp4",
      "file_size": 10485760,
      "duration": 120.5,
      "format": "mov,mp4,m4a,3gp,3g2,mj2",
      "resolution": "1920x1080",
      "fps": 30.0,
      "bitrate": 5000000,
      "upload_time": "2024-01-01T12:00:00Z",
      "status": "uploaded"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 100
}
```

#### 1.3 Get Video Details
```bash
curl -X GET "http://localhost:8000/api/v1/videos/{video_id}"
```

### Level 2: Trimming API

#### 2.1 Trim a Video
```bash
# Option 1: Using video_id in URL path (Recommended)
curl -X POST "http://localhost:8000/api/v1/videos/{video_id}/trim" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": 10.0,
    "end_time": 30.0
  }'

# Option 2: Using video_id in request body
curl -X POST "http://localhost:8000/api/v1/videos/trim" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "112c7962-b958-4947-8da4-db02b011a48e",
    "start_time": 10.0,
    "end_time": 30.0
  }'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "video_id": "112c7962-b958-4947-8da4-db02b011a48e",
  "job_type": "trim",
  "status": "pending",
  "progress": 0,
  "parameters": {
    "start_time": 10.0,
    "end_time": 30.0
  },
  "created_at": "2024-01-01T12:05:00Z"
}
```

### Level 3: Overlays & Watermarking

#### 3.1 Add Text Overlay (English)
```bash
curl -X POST "http://localhost:8000/api/v1/overlays/text" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "112c7962-b958-4947-8da4-db02b011a48e",
    "overlay_type": "text",
    "content": "Gyanesh!",
    "position_x": 100,
    "position_y": 100,
    "font_size": 24,
    "font_color": "#FFFFFF",
    "language": "en"
  }'
```

#### 3.2 Add Text Overlay (Hindi - Bonus Feature)
```bash
curl -X POST "http://localhost:8000/api/v1/overlays/text" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "112c7962-b958-4947-8da4-db02b011a48e",
    "overlay_type": "text",
    "content": "नमस्ते दुनिया",
    "position_x": 100,
    "position_y": 100,
    "font_size": 24,
    "font_color": "#FFFFFF",
    "language": "hindi"
  }'
```

#### 3.3 Add Image Overlay
```bash
curl -X POST "http://localhost:8000/api/v1/overlays/image" \
  -H "Content-Type: multipart/form-data" \
  -F 'overlay_file=@logo.png' \
  -F 'video_id=112c7962-b958-4947-8da4-db02b011a48e' \
  -F 'overlay_type=image' \
  -F 'position_x=10' \
  -F 'position_y=10' \
  -F 'width=200' \
  -F 'height=100'
```

#### 3.4 Add Watermark
```bash
curl -X POST "http://localhost:8000/api/v1/overlays/watermark" \
  -H "Content-Type: multipart/form-data" \
  -F 'watermark_file=@logo.png' \
  -F 'video_id=112c7962-b958-4947-8da4-db02b011a48e' \
  -F 'watermark_type=image' \
  -F 'position=bottom-right' \
  -F 'opacity=0.5'
```

### Level 4: Async Job Queue

#### 4.1 Check Job Status
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/{job_id}"
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "status": "processing",
  "progress": 75,
  "error_message": null,
  "result_path": null
}
```

#### 4.2 Download Processed Video
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/{job_id}/download" \
  -o processed_video.mp4
```

### Level 5: Multiple Output Qualities

#### 5.1 Generate Multiple Qualities
```bash
curl -X POST "http://localhost:8000/api/v1/videos/qualities" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "112c7962-b958-4947-8da4-db02b011a48e",
    "qualities": ["1080p", "720p", "480p"]
  }'
```

#### 5.2 Download Specific Quality
```bash
curl -X GET "http://localhost:8000/api/v1/videos/{video_id}/download/720p" \
  -o video_720p.mp4
``
## 🌐 Using the Interactive API Documentation

### Step 1: Open Swagger UI
Go to http://localhost:8000/docs in your browser.

### Step 2: Try the API
1. **Expand any endpoint** by clicking on it
2. **Click "Try it out"**
3. **Fill in the parameters**
4. **Click "Execute"**
5. **See the response**

### Step 3: Upload a File
For file uploads:
1. Click "Choose File" in the Swagger UI
2. Select your video file
3. Click "Execute"
4. Copy the response IDs for further operations

## 🐍 Python Client Example

Here's a Python script to interact with the API:

```python
import requests
import time
import uuid

# Base URL
BASE_URL = "http://localhost:8000"

def upload_video(file_path):
    """Upload a video file"""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/v1/videos/upload", files=files)
    return response.json()

def trim_video(video_id, start_time, end_time):
    """Trim a video"""
    data = {
        "start_time": start_time,
        "end_time": end_time
    }
    response = requests.post(f"{BASE_URL}/api/v1/videos/{video_id}/trim", json=data)
    return response.json()

def check_job_status(job_id):
    """Check job status"""
    response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
    return response.json()

def wait_for_completion(job_id):
    """Wait for job to complete"""
    while True:
        status = check_job_status(job_id)
        print(f"Job {job_id}: {status['status']} ({status['progress']}%)")
        
        if status['status'] == 'completed':
            return status
        elif status['status'] == 'failed':
            raise Exception(f"Job failed: {status.get('error_message', 'Unknown error')}")
        
        time.sleep(2)

def download_result(job_id, output_path):
    """Download processed video"""
    response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/download")
    with open(output_path, 'wb') as f:
        f.write(response.content)

# Example usage
if __name__ == "__main__":
    # Upload video
    print("Uploading video...")
    upload_result = upload_video("sample_video.mp4")
    video_id = upload_result['video_id']
    print(f"Video uploaded: {video_id}")
    
    # Trim video
    print("Trimming video...")
    trim_result = trim_video(video_id, 10.0, 30.0)
    job_id = trim_result['id']
    print(f"Trim job started: {job_id}")
    
    # Wait for completion
    print("Waiting for completion...")
    final_status = wait_for_completion(job_id)
    
    # Download result
    print("Downloading result...")
    download_result(job_id, "trimmed_video.mp4")
    print("Done!")
```

## 🔧 JavaScript/Node.js Client Example

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const BASE_URL = 'http://localhost:8000';

async function uploadVideo(filePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    
    const response = await axios.post(`${BASE_URL}/api/v1/videos/upload`, form, {
        headers: form.getHeaders()
    });
    
    return response.data;
}

async function trimVideo(videoId, startTime, endTime) {
    const response = await axios.post(`${BASE_URL}/api/v1/videos/${videoId}/trim`, {
        start_time: startTime,
        end_time: endTime
    });
    
    return response.data;
}

async function checkJobStatus(jobId) {
    const response = await axios.get(`${BASE_URL}/api/v1/jobs/${jobId}`);
    return response.data;
}

async function waitForCompletion(jobId) {
    while (true) {
        const status = await checkJobStatus(jobId);
        console.log(`Job ${jobId}: ${status.status} (${status.progress}%)`);
        
        if (status.status === 'completed') {
            return status;
        } else if (status.status === 'failed') {
            throw new Error(`Job failed: ${status.error_message || 'Unknown error'}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}

async function downloadResult(jobId, outputPath) {
    const response = await axios.get(`${BASE_URL}/api/v1/jobs/${jobId}/download`, {
        responseType: 'stream'
    });
    
    const writer = fs.createWriteStream(outputPath);
    response.data.pipe(writer);
    
    return new Promise((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
    });
}

// Example usage
async function main() {
    try {
        console.log('Uploading video...');
        const uploadResult = await uploadVideo('sample_video.mp4');
        const videoId = uploadResult.video_id;
        console.log(`Video uploaded: ${videoId}`);
        
        console.log('Trimming video...');
        const trimResult = await trimVideo(videoId, 10.0, 30.0);
        const jobId = trimResult.id;
        console.log(`Trim job started: ${jobId}`);
        
        console.log('Waiting for completion...');
        await waitForCompletion(jobId);
        
        console.log('Downloading result...');
        await downloadResult(jobId, 'trimmed_video.mp4');
        console.log('Done!');
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

## 🚨 Common Issues & Solutions

### Issue: "Connection refused"
**Solution**: Make sure the application is running on http://localhost:8000

### Issue: "File too large"
**Solution**: Check the file size limit in your configuration (default: 500MB)

### Issue: "Job failed"
**Solution**: Check the job status for error details, ensure FFmpeg is installed

### Issue: "Video not found"
**Solution**: Make sure you're using the correct video_id from the upload response

## 📊 Monitoring Your Jobs

### Check All Jobs
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/"
```

### Check Jobs by Status
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/?status=processing"
```

### Check Jobs by Type
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/?job_type=trim"
```

## 🎯 Next Steps

1. **Explore the API**: Use the interactive documentation at http://localhost:8000/docs
2. **Try different features**: Test overlays, watermarks, and quality generation
3. **Build your application**: Use the examples above to integrate with your app
4. **Scale up**: Deploy to production using the deployment scripts

## 📞 Need Help?

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **System Status**: http://localhost:8000/api/v1/status

Happy video processing! 🎬✨
