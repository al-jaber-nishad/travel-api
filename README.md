# 🌍 Travel Recommendation API

This Django REST API recommends the best districts in Bangladesh for travel based on 2PM temperature and air quality (PM2.5). It also advises whether to travel based on your current location, destination, and travel date.

## 🚀 Features

- Fetches 7-day weather and air quality forecast using [Open-Meteo API](https://open-meteo.com/)
- Ranks districts by lowest average 2PM temperature and PM2.5
- Travel recommendation API based on live user input
- Cached with Redis, updated periodically via Celery Beat
- Interactive API documentation using Swagger UI
- Fully automated setup with `setup.py`

---


## Setup Instructions (via setup.py)

### 📦 Step 1: Clone the repository

```bash
git clone https://github.com/al-jaber-nishad/travel-api.git
cd travel-api
```

### 🛠 Step 2: Run setup script
```bash
python3 setup.py
```

This script will:
* Create a virtual environment (venv/)
* Install all required Python packages
* Run database migrations
* Start Redis (Linux only)
* Delete existing cache key if needed
* Prefill top districts (only if not cached)
* Start Celery worker & beat
* Launch Django server at http://localhost:8000

🔑 On Windows, please make sure Redis is installed and started manually before running setup.py.

### Step 3: Run the tests
To run the tests, use the following command:
```bash
pytest
```


### 📚 API Documentation
Once the server is running, open your browser and visit:
```bash
http://localhost:8000/api/schema/swagger-ui/
```

You’ll find:

* /api/travel-recommendation/ – Compare two locations and get a recommendation
* /api/top-districts/ – See the coolest and cleanest top 10 districts


### 🤝 License
You are free to reuse and extend the logic under MIT license or for learning purposes.
