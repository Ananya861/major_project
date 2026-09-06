\# Smart Farmer Advisory Platform – Backend



\## Project Overview



The Smart Farmer Advisory Platform is an agricultural decision-support system designed to help farmers make data-driven decisions.



The backend is built using FastAPI and follows a modular architecture. It integrates farm information, soil data, weather information, machine learning models, location intelligence, crop recommendations, yield prediction, and market information.



\---



\# Backend Features



The platform currently provides APIs for:



\- Farmer authentication

\- Farm management

\- Soil data management

\- Weather information

\- Crop recommendation

\- Market price information

\- Market price prediction

\- Location intelligence

\- Soil intelligence

\- Location-based crop yield prediction

\- Notifications



\---



\# Member 1 Responsibilities



Member 1 is responsible for the agricultural intelligence and crop-related machine learning components.



Completed work includes:



1\. Crop Recommendation System

2\. Crop Recommendation ML Model

3\. Location Intelligence

4\. Soil Intelligence

5\. Location-Based Crop Yield Prediction

6\. ML Model Integration



\---



\# 1. Farm Management



Farmers can:



\- Create a farm

\- View all their farms

\- View a specific farm

\- Store farm latitude and longitude

\- Store farm area in acres



\## API Endpoints



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/farms` | Create a new farm |

| GET | `/farms` | Get all farms |

| GET | `/farms/{farm\_id}` | Get farm details |



\---



\# 2. Soil Data Management



Farmers can add soil information to their farms.



Supported soil parameters include:



\- pH

\- Nitrogen

\- Phosphorus

\- Potassium

\- Moisture

\- Soil type



\## API Endpoint



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/farms/{farm\_id}/soil` | Add soil data |



\---



\# 3. Weather Service



The weather module provides weather information based on farm location coordinates.



Features include:



\- Current temperature

\- Rainfall information

\- Humidity

\- Weather forecast

\- Location-based weather retrieval



Weather information is fetched using the latitude and longitude of the farm.



\## API Endpoint



| Method | Endpoint | Description |

|--------|----------|-------------|

| GET | `/weather` | Get weather information |



\---



\# 4. Crop Recommendation System



The crop recommendation system suggests suitable crops based on agricultural and environmental parameters.



The ML model uses features such as:



\- Nitrogen

\- Phosphorus

\- Potassium

\- Temperature

\- Humidity

\- Soil pH

\- Rainfall



The trained model generates the top crop recommendations with confidence scores.



\## API Endpoint



| Method | Endpoint | Description |

|--------|----------|-------------|

| GET | `/recommend/crop` | Get crop recommendations for a farm |



Example response:



```json

{

&#x20; "farm\_id": 1,

&#x20; "recommendations": \[

&#x20;   {

&#x20;     "crop": "Rice",

&#x20;     "confidence": 0.52

&#x20;   },

&#x20;   {

&#x20;     "crop": "Jute",

&#x20;     "confidence": 0.475

&#x20;   }

&#x20; ]

}

```



\---



\# 5. Crop Recommendation ML Model



The crop recommendation model is trained using agricultural datasets containing soil and climate parameters.



\## ML Pipeline



```text

Agricultural Dataset

&#x20;       ↓

Data Preprocessing

&#x20;       ↓

Feature Preparation

&#x20;       ↓

Model Training

&#x20;       ↓

Model Evaluation

&#x20;       ↓

Trained Pipeline

&#x20;       ↓

crop\_pipeline.joblib

```



The trained model artifact is stored at:



```text

app/artifacts/crop\_pipeline.joblib

```



Model evaluation metrics are stored at:



```text

app/artifacts/crop\_metrics.json

```



The inference layer loads the trained model and generates the top crop recommendations.



Main ML files:



```text

app/ml/crop\_inference.py

app/ml/feature\_builder.py

app/services/orchestration.py

```



\---



\# 6. Location Intelligence



The Location Intelligence module converts GPS coordinates into meaningful location information.



The system uses reverse geocoding to identify:



\- State

\- District

\- Village/Town

\- Complete location name



\## Workflow



```text

Farm Latitude + Longitude

&#x20;       ↓

Location Intelligence API

&#x20;       ↓

location\_service.py

&#x20;       ↓

Reverse Geocoding

&#x20;       ↓

OpenStreetMap / Nominatim

&#x20;       ↓

State + District + Village

```



\## API Endpoint



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/location/intelligence` | Get location information from coordinates |



Example request:



```json

{

&#x20; "latitude": 15.3173,

&#x20; "longitude": 75.7139

}

```



The frontend can automatically obtain these coordinates using device GPS/location services.



\---



\# 7. Soil Intelligence



The Soil Intelligence module processes soil-related information associated with a farm.



The system uses the farm ID and location information to provide soil intelligence for agricultural decision-making.



\## API Endpoint



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/soil/intelligence/{farm\_id}` | Get soil intelligence for a farm |



\---



\# 8. Location-Based Crop Yield Prediction



A machine learning model is used to predict crop yield using location and historical agricultural production data.



The prediction considers:



\- Farm location

\- District

\- Crop

\- Season

\- Year



The model was trained using Karnataka agricultural production and yield data.



\## API Endpoint



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/location/predict-yield/farm` | Predict crop yield using farm location |



Example request:



```json

{

&#x20; "farm\_id": 1,

&#x20; "crop": "Maize",

&#x20; "season": "Kharif",

&#x20; "year": 2025

}

```



The trained yield prediction model is stored at:



```text

ml/models/karnataka\_yield\_model.pkl

```



\---



\# Project Architecture



```text

Farmer

&#x20;  ↓

Frontend Application

&#x20;  ↓

FastAPI Backend

&#x20;  │

&#x20;  ├── Authentication

&#x20;  │

&#x20;  ├── Farm Management

&#x20;  │       ↓

&#x20;  │   Farm Location

&#x20;  │

&#x20;  ├── Location Intelligence

&#x20;  │       ↓

&#x20;  │   State / District / Village

&#x20;  │

&#x20;  ├── Weather Service

&#x20;  │

&#x20;  ├── Soil Intelligence

&#x20;  │

&#x20;  ├── Crop Recommendation ML Model

&#x20;  │

&#x20;  ├── Yield Prediction ML Model

&#x20;  │

&#x20;  ├── Market Intelligence

&#x20;  │

&#x20;  └── Notifications

&#x20;          ↓

&#x20;       Farmer Advice

```



\---



\# Project Structure



```text

backend/

│

├── app/

│   ├── api/

│   │   ├── router.py

│   │   └── routes/

│   │       ├── auth.py

│   │       ├── farms.py

│   │       ├── weather.py

│   │       ├── market.py

│   │       ├── recommend.py

│   │       ├── location\_intelligence.py

│   │       ├── location\_prediction.py

│   │       ├── soil\_intelligence.py

│   │       └── notifications.py

│   │

│   ├── services/

│   │   ├── orchestration.py

│   │   ├── location\_service.py

│   │   └── soil\_intelligence\_service.py

│   │

│   ├── ml/

│   │   ├── crop\_inference.py

│   │   └── feature\_builder.py

│   │

│   ├── artifacts/

│   │   ├── crop\_pipeline.joblib

│   │   └── crop\_metrics.json

│   │

│   ├── models/

│   ├── schemas/

│   └── db/

│

├── ml/

│   ├── data/

│   └── models/

│       └── karnataka\_yield\_model.pkl

│

├── main.py

└── README.md

```



\---



\# API Documentation



After starting the FastAPI server, interactive API documentation is available at:



```text

http://127.0.0.1:8000/docs

```



The OpenAPI schema is available at:



```text

http://127.0.0.1:8000/openapi.json

```



\---



\# Running the Backend



\## 1. Activate Virtual Environment



Windows:



```cmd

venv\\Scripts\\activate

```



\## 2. Install Dependencies



```cmd

pip install -r requirements.txt

```



\## 3. Configure Environment Variables



Create a `.env` file and configure the required database and API credentials.



\## 4. Start the Server



```cmd

uvicorn app.main:app --reload

```



The backend will start at:



```text

http://127.0.0.1:8000

```



\---



\# Technology Stack



\- Python

\- FastAPI

\- PostgreSQL

\- SQLAlchemy

\- Scikit-learn

\- Pandas

\- Joblib

\- HTTPX

\- OpenStreetMap / Nominatim

\- External Weather APIs

\- Government agricultural datasets



\---



\# Current Status



\## Member 1



| Feature | Status |

|---|---|

| Crop Recommendation ML Model | Completed |

| Crop Model Training | Completed |

| Model Evaluation | Completed |

| ML Model Integration | Completed |

| Top-3 Crop Recommendation | Completed |

| Location Intelligence | Completed |

| Soil Intelligence | Completed |

| Location-Based Yield Prediction | Completed |

| API Integration | Completed |



\---



\# Author



Major Project – Smart Farmer Advisory Platform



Member 1: Crop and Agricultural Intelligence Module

