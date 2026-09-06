\# Crop and Weather Prediction Backend Module



\## Project Overview



This module is part of the Major Project backend system developed for agricultural decision support.



The module provides APIs for:



\- Farmer authentication

\- Farm management

\- Soil data management

\- Weather information

\- Crop recommendation

\- Market price information

\- Location-based crop yield prediction



The backend is built using FastAPI and follows a modular architecture.



\---



\# Member 1 Responsibilities



Member 1 is responsible for the Crop and Weather Prediction functionality.



Completed features include:



\## 1. Farm Management



Farmers can:



\- Create a farm

\- View all their farms

\- View a specific farm

\- Store farm latitude and longitude

\- Store farm area in acres



\### API Endpoints



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/farms` | Create a new farm |

| GET | `/farms` | Get all farms |

| GET | `/farms/{farm\_id}` | Get farm details |



\---



\## 2. Soil Data Management



Farmers can add soil information to their farms.



Supported soil parameters:



\- pH

\- Nitrogen

\- Phosphorus

\- Potassium

\- Moisture

\- Soil type



\### API Endpoint



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/farms/{farm\_id}/soil` | Add soil data |



\---



\## 3. Weather Service



The weather module provides weather information based on farm location coordinates.



Features include:



\- Current temperature

\- Rainfall information

\- Humidity

\- Weather forecast

\- Location-based weather retrieval



Weather data can be retrieved using farm latitude and longitude.



\---



\## 4. Crop Recommendation



The crop recommendation system suggests suitable crops for a selected farm.



Recommendations are generated using farm and agricultural data.



\### API Endpoint



| Method | Endpoint | Description |

|--------|----------|-------------|

| GET | `/recommend/crop?farm\_id={farm\_id}` | Get crop recommendations |



The response includes:



\- Farm ID

\- Recommended crops

\- Confidence score



\---



\## 5. Location-Based Crop Yield Prediction



A machine learning model is used to predict crop yield based on location and historical agricultural data.



The prediction uses:



\- Farmer district

\- Crop

\- Season

\- Year

\- Farm ownership validation



\### API Endpoint



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/location/predict-yield/farm` | Predict crop yield |



Example request:



```json

{

&#x20; "farm\_id": 1,

&#x20; "crop": "Maize",

&#x20; "season": "Kharif",

&#x20; "year": 2025

}

