# Quiz Master - CSV Export with Celery

This project includes an async CSV export functionality using Celery for user quiz data.

## Setup Instructions

### 1. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies (if you delete node_modules, just run this again)
cd ../frontend
npm install
```

### 2. Install Redis

Download and install Redis for Windows from: https://github.com/microsoftarchive/redis/releases

Or use WSL2 with Redis:
```bash
sudo apt-get install redis-server
```

### 3. Start Services

#### Option 1: Using Batch Files (Windows)
1. Start Redis: `start_redis.bat`
2. Start Celery Worker: `start_celery_worker.bat`
3. Start Flask Backend: `python backend/main.py`
4. Start Frontend: `cd frontend && npm run dev`

#### Option 2: Manual Commands
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
cd backend
celery -A celery_worker.celery worker --loglevel=info --pool=solo

# Terminal 3: Start Flask Backend
cd backend
python main.py

# Terminal 4: Start Frontend
cd frontend
npm run dev
```

## CSV Export Feature

### How it works:
1. User clicks "Export as CSV" button in the Statistics section
2. Frontend sends POST request to `/api/user/export-csv`
3. Backend creates a Celery task to generate CSV file
4. Frontend polls `/api/user/export-csv-status/<task_id>` for completion
5. When complete, user can download the CSV file

### CSV Format:
- Quiz ID
- Quiz Name
- Chapter ID
- Chapter Name
- Subject Name
- Date of Quiz
- Score
- Status
- Remarks

### API Endpoints:
- `POST /api/user/export-csv` - Trigger export job
- `GET /api/user/export-csv-status/<task_id>` - Check job status
- `GET /api/user/export-csv-file/<filename>` - Download CSV file

## Troubleshooting

1. **Redis Connection Error**: Make sure Redis server is running
2. **Celery Worker Not Starting**: Check if Redis is accessible on localhost:6379
3. **Import Errors**: Ensure all dependencies are installed
4. **File Not Found**: Check if exports directory exists in backend folder

## Project Structure

```
Quiz Master/
├── backend/
│   ├── __init__.py
│   ├── main.py                # Flask app entry
│   ├── models.py              # SQLAlchemy models
│   ├── tasks.py               # Celery tasks (CSV, reminders, reports)
│   ├── celery_worker.py       # Celery worker setup
│   ├── celery_beat_schedule.py# Celery beat schedule
│   ├── exports/               # Generated CSV files
│   ├── uploads/               # Uploaded images
│   ├── requirements.txt       # Python dependencies
│   ├── monthly_report_template.html
│   └── routes/
│       ├── admin_routes.py
│       └── user_routes.py
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── components/
│   │   ├── assets/
│   │   └── router/
│   ├── package.json
│   └── ...
├── Quiz Master DBs.xlsx       # Excel DB
├── README.md
└── setup_backend_env.py       # Script to setup backend venv & install requirements
```

## Backend Requirements

See `backend/requirements.txt` for all dependencies. Example:

```
Flask
Flask-Cors
Flask-Login
SQLAlchemy
marshmallow
requests
celery
redis
billiard
kombu
python-dotenv
```

## Automated Setup & Run (Windows, PowerShell)

1. **Create venv & install requirements**

```powershell
python setup_backend_env.py
```

2. **Open 5 terminals and run the following:**

**Terminal 1: Start Redis**
```powershell
redis-server
```

**Terminal 2: Start Flask Backend**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
$env:FLASK_APP="main.py"; $env:FLASK_ENV="development"; flask run
```

**Terminal 3: Start Frontend**
```powershell
cd frontend
npm run dev
```

**Terminal 4: Start Celery Worker**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

**Terminal 5: Start Celery Beat**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
celery -A celery_worker.celery beat --loglevel=info
```