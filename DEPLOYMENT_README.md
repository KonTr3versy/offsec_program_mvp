# Offensive Security Program MVP - Deployment Guide

This guide will help you deploy and run the Offensive Security Program Manager on any server or testing environment.

## 📋 Prerequisites

- **Python 3.9 or higher**
- **pip** (Python package manager)
- **Network access** on port 5000 (or your chosen port)

## 🚀 Quick Start Deployment

### Step 1: Extract the Files

Extract the deployment package to your desired location:

```bash
unzip offsec-program-deployment.zip
cd offsec-program-deployment
```

### Step 2: Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

**Note**: It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Start the Application

Run the application server:

```bash
uvicorn offsec_program_mvp.main:app --host 0.0.0.0 --port 5000
```

The server will start and you'll see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000
```

**Important**: On first startup, check the logs for your API key:
```
INFO:     Seeded user 'malcolm' with API key: YOUR_API_KEY_HERE
```

**Save this API key!** You'll need it to authenticate API requests.

### Step 4: Access the API

Open your browser and navigate to:
- **API Documentation (Swagger UI)**: http://localhost:5000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:5000/redoc

## 🔐 Authentication

All API requests require an API key in the header:

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:5000/engagements/
```

## 🗄️ Database

The application uses SQLite by default. The database file `offsec_program.db` will be created automatically on first run in the application directory.

**For production deployments**, consider migrating to PostgreSQL:
1. Edit `offsec_program_mvp/db.py`
2. Change the `SQLALCHEMY_DATABASE_URL` to your PostgreSQL connection string
3. Restart the application

## 🌐 Production Deployment Options

### Option 1: Run with Gunicorn (Recommended for Production)

Install Gunicorn:
```bash
pip install gunicorn
```

Run with multiple workers:
```bash
gunicorn offsec_program_mvp.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000
```

### Option 2: Run as a System Service (Linux)

Create a systemd service file `/etc/systemd/system/offsec-api.service`:

```ini
[Unit]
Description=Offensive Security Program API
After=network.target

[Service]
Type=notify
User=your-user
WorkingDirectory=/path/to/offsec-program-deployment
Environment="PATH=/path/to/offsec-program-deployment/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn offsec_program_mvp.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable offsec-api
sudo systemctl start offsec-api
```

### Option 3: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY offsec_program_mvp/ ./offsec_program_mvp/

EXPOSE 5000

CMD ["uvicorn", "offsec_program_mvp.main:app", "--host", "0.0.0.0", "--port", "5000"]
```

Build and run:
```bash
docker build -t offsec-api .
docker run -p 5000:5000 -v $(pwd)/offsec_program.db:/app/offsec_program.db offsec-api
```

## 🔧 Configuration Options

### Change the Port

To run on a different port (e.g., 8080):

```bash
uvicorn offsec_program_mvp.main:app --host 0.0.0.0 --port 8080
```

### Enable Auto-Reload (Development Only)

For automatic reloading when code changes:

```bash
uvicorn offsec_program_mvp.main:app --host 0.0.0.0 --port 5000 --reload
```

**Warning**: Do NOT use `--reload` in production!

### Configure CORS (if needed for frontend apps)

Edit `offsec_program_mvp/main.py` and uncomment the CORS middleware section if you need to allow cross-origin requests from a web frontend.

## 📊 Verify Installation

Test that everything is working:

```bash
# Check API health (replace with your API key)
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:5000/users/

# Should return a list of users
```

## 🛠️ Troubleshooting

### "Module not found" Error

Make sure you're in the correct directory and have installed dependencies:
```bash
pip install -r requirements.txt
```

### "Database is locked" Error

This can happen with SQLite under high concurrency. Consider:
1. Reducing concurrent requests
2. Migrating to PostgreSQL for production use

### Cannot Access from Other Machines

Make sure you're binding to `0.0.0.0` (not `127.0.0.1`) and check your firewall:
```bash
# Linux firewall example
sudo ufw allow 5000
```

### API Key Not Working

1. Check the startup logs for the generated API key
2. Regenerate the API key using: `POST /users/{user_id}/regenerate-api-key`
3. Make sure you're using the `X-API-Key` header (not `Authorization`)

## 📁 File Structure

```
offsec-program-deployment/
├── offsec_program_mvp/          # Main application code
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Database models
│   ├── db.py                    # Database configuration
│   ├── routers/                 # API endpoints
│   └── schemas/                 # Request/response schemas
├── requirements.txt             # Python dependencies
├── DEPLOYMENT_README.md         # This file
├── replit.md                    # Architecture documentation
└── offsec_program.db           # Database (created on first run)
```

## 🔗 API Documentation

Once running, visit http://localhost:5000/docs for full interactive API documentation with:
- All available endpoints
- Request/response examples
- Try-it-out functionality
- Schema definitions

## 📝 Next Steps

1. **Create Finding Templates**: Build your vulnerability library at `/finding-templates/`
2. **Import Assets**: Add your target inventory at `/assets/`
3. **Start First Engagement**: Create an engagement at `/engagements/`
4. **Add Findings**: Document vulnerabilities at `/engagements/{id}/findings/`
5. **Export Reports**: Generate CSV or Markdown reports for stakeholders

## 🆘 Support

For issues or questions:
1. Check the logs: Look at the terminal output for error messages
2. Review the API documentation at `/docs`
3. Check `replit.md` for architecture details

## 🔒 Security Notes

- **Change default API keys** in production
- **Use HTTPS** in production (consider a reverse proxy like nginx)
- **Implement rate limiting** for production deployments
- **Backup your database** regularly
- **Restrict network access** to authorized users only

---

**Ready to deploy?** Follow the Quick Start section above and you'll be running in minutes!
