# 🚀 Dripple Video Processing Backend - Setup Guide

This guide will help you set up and run the Dripple Video Processing Backend locally.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.9+**
- **PostgreSQL 12+**
- **Redis 6+**
- **FFmpeg 4.4+**
- **Docker & Docker Compose** (optional, for containerized setup)

### Installing Prerequisites

#### Windows
```bash
# Install Python from python.org
# Install PostgreSQL from postgresql.org
# Install Redis from redis.io
# Install FFmpeg using Chocolatey:
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

#### macOS
```bash
# Install using Homebrew
brew install python postgresql redis ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip postgresql redis-server ffmpeg
```

## 🛠️ Setup Options

### Option 1: Docker Setup (Recommended)

1. **Clone and navigate to backend directory**
```bash
cd backend
```

2. **Start all services with Docker Compose**
```bash
docker-compose up --build
```

3. **Access the application**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Option 2: Local Development Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Run the development setup script**
```bash
python run_dev.py
```

3. **Start required services**
```bash
# Start PostgreSQL (adjust for your system)
sudo systemctl start postgresql

# Start Redis (adjust for your system)
sudo systemctl start redis
```

4. **Initialize the database**
```bash
python init_db.py
```

5. **Start the application**
```bash
python start.py
```

## 🔧 Manual Setup

If you prefer to set up manually:

1. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your configuration
```

4. **Create database**
```sql
-- Connect to PostgreSQL and run:
CREATE DATABASE dripple_db;
CREATE USER dripple_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE dripple_db TO dripple_user;
```

5. **Initialize database tables**
```bash
python init_db.py
```

6. **Start the application**
```bash
python start.py
```

## 🧪 Running Tests

```bash
python run_tests.py
```

Or manually:
```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term
```

## 📊 API Endpoints

Once running, you can access:

- **Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health
- **API Health**: http://localhost:8000/api/v1/health
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/videos/upload` - Upload a video
- `GET /api/v1/videos/` - List videos
- `POST /trim` - Trim a video (Level 2)
- `GET /status/{job_id}` - Get job status (Level 4)
- `GET /result/{job_id}` - Download processed video (Level 4)

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in .env file
   - Verify database exists

2. **Redis Connection Error**
   - Ensure Redis is running
   - Check Redis URL in .env file

3. **FFmpeg Not Found**
   - Install FFmpeg and ensure it's in PATH
   - Update FFMPEG_PATH in .env if needed

4. **Port Already in Use**
   - Change port in start.py or docker-compose.yml
   - Kill existing processes using the port

### Logs

- **Docker**: `docker-compose logs -f`
- **Local**: Check console output

## 🚀 Production Deployment

For production deployment, see the deployment scripts in `scripts/` directory:

```bash
# AWS
./scripts/deploy.sh production aws

# GCP
./scripts/deploy.sh production gcp

# Azure
./scripts/deploy.sh production azure
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)

## 🆘 Support

If you encounter issues:

1. Check the logs for error messages
2. Verify all prerequisites are installed
3. Ensure all services are running
4. Check the configuration in .env file

For additional help, create an issue in the repository.
