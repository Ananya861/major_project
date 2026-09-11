# Agri Smart AI

**AI-Powered Smart Agriculture Decision Support System**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.1-646CFF.svg)](https://vitejs.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791.svg)](https://www.postgresql.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.5%2B-F7931E.svg)](https://scikit-learn.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![Project Status](https://img.shields.io/badge/Status-Completed_Major_Project-success.svg)](#)

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Problem Statement](#2-problem-statement)
- [3. Key Features](#3-key-features)
- [4. System Architecture](#4-system-architecture)
- [5. Technology Stack](#5-technology-stack)
- [6. Project Structure](#6-project-structure)
- [7. Machine Learning Modules](#7-machine-learning-modules)
  - [Crop Recommendation Module (Member 1)](#crop-recommendation-module-member-1)
  - [Mandi Price Forecasting & MSP Comparison (Member 2)](#mandi-price-forecasting--msp-comparison-member-2)
- [8. API Overview](#8-api-overview)
- [9. How to Setup and Run the Project](#9-how-to-setup-and-run-the-project)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#clone-the-repository)
  - [Backend Setup](#backend-setup)
  - [PostgreSQL Database Setup](#postgresql-database-setup)
  - [Run the FastAPI Backend](#run-the-fastapi-backend)
  - [Frontend Setup](#frontend-setup)
  - [Run the React / Vite Frontend](#run-the-react--vite-frontend)
  - [Running Backend and Frontend Together](#running-backend-and-frontend-together)
  - [Database and API Verification](#database-and-api-verification)
  - [GitHub Codespaces Setup](#github-codespaces-setup)
  - [Troubleshooting](#troubleshooting)
  - [Project Execution Flow](#project-execution-flow)
  - [Security Best Practices](#security-best-practices)
- [10. Environment Configuration](#10-environment-configuration)
- [11. Build Verification](#11-build-verification)
- [12. Team Contributions](#12-team-contributions)
- [13. Future Enhancements](#13-future-enhancements)
- [14. Disclaimer and Data Notes](#14-disclaimer-and-data-notes)

---

## 1. Project Overview

**Agri Smart AI** is an end-to-end, AI-powered smart agriculture decision support platform developed as a final-year major engineering project. The platform integrates soil chemical parameters, live agro-climatic weather data, official Indian agricultural market (mandi) prices, and government Minimum Support Prices (MSP) into a cohesive, user-friendly system.

By combining modern asynchronous web technologies with trained machine learning pipelines, Agri Smart AI provides farmers and agricultural planners with actionable recommendations: identifying optimal crops for specific soil and weather conditions, forecasting future commodity prices across regional mandis, tracking price variances against government-mandated MSP, and dispatching alerts when market prices undergo significant changes.

---

## 2. Problem Statement

Agriculture in India is heavily impacted by systemic informational and operational hurdles:

1. **Information Asymmetry in Mandi Markets:** Smallholder farmers frequently lack timely, transparent access to prevailing mandi rates, making them susceptible to price exploitation by local intermediaries and traders.
2. **Uncertainty in Price Volatility:** Commodity prices fluctuate widely based on seasonal arrivals and regional demand. Without predictive price outlooks, farmers struggle to decide whether to sell immediately or delay harvest marketing.
3. **Suboptimal Crop Planning:** Crop decisions are often made based on tradition or short-term trends rather than scientific matching of soil parameters (Nitrogen, Phosphorus, Potassium, pH, moisture) with local agro-climatic conditions.
4. **Gaps in MSP Awareness:** Although the Government of India regularly establishes Minimum Support Prices (MSP) to protect producers, farmers lack automated, direct comparison tools to evaluate whether market offers are fair relative to official benchmarks.
5. **Fragmented Advisory Tools:** Existing services are segregated—weather applications, soil health cards, and price bulletin boards operate in isolation without an integrated decision-support workflow.

Agri Smart AI resolves these challenges through a unified platform that bridges agronomic intelligence with market economics.

---

## 3. Key Features

All features listed below are fully implemented and verified within the repository:

- **User Authentication & Profile Management:**
  - Secure JWT-based registration and login with phone number and bcrypt password hashing.
  - Farmer profile tracking: personal name, contact details, state, district, village, land holding acreage, farmer classification category, and preferred language.

- **Farm & Soil Management:**
  - Multi-farm registration under individual farmer accounts with GPS coordinates (latitude and longitude) and parcel size (acres).
  - Historical soil reading records: Nitrogen (N), Phosphorus (P), Potassium (K), pH level, soil moisture percentage, and soil type.

- **AI-Powered Crop Recommendation:**
  - Multi-class crop recommendation pipeline supporting 22 distinct crop varieties.
  - Fuses farm soil parameters with real-time temperature, humidity, and rainfall data.
  - Returns top recommended crops ranked by probability-based confidence scores.

- **Agro-Climatic Weather Integration:**
  - Live temperature, relative humidity, precipitation, and multi-day meteorological forecast via OpenWeatherMap API.
  - 3-hour PostgreSQL caching layer (`weather_log`) that prevents redundant network requests and handles network degradation gracefully.

- **Official Mandi Market Prices:**
  - Integration with the Government of India Open Government Data (OGD) Agmarknet API (`data.gov.in`).
  - Fetches daily commodity arrivals, variety, grade, minimum price, maximum price, and modal price.
  - Regional filtering by state, district, and market, backed by an automated database fallback when external APIs are unreachable.

- **Machine Learning Mandi Price Forecasting:**
  - Autoregressive time-series prediction powered by `HistGradientBoostingRegressor`.
  - Configurable multi-day forecasting (1 to 30 days ahead) based on 3-day lag prices, 3-day rolling averages, calendar indices, and market categorical features.

- **Government MSP Comparison:**
  - Automated comparison of current mandi modal prices against official Government of India Minimum Support Prices (MSP) for the 2026-27 crop marketing year.
  - Calculates absolute price difference, percentage deviation, and explicit market status (`ABOVE_MSP`, `BELOW_MSP`, or `AT_MSP`).

- **Price & Market Alerts:**
  - Automated alert engine that monitors price deviations (forecasted price variance $\ge 10\%$ against modal prices; market price deviation $\ge 5\%$ against MSP).
  - Deduplication prevents repetitive unread alerts on the same calendar day.
  - Notification management API allowing farmers to inspect and mark alerts as read.

- **Farmer Dashboard & Agricultural Tools:**
  - Centralized dashboard displaying active farm status, real-time weather summary, top recommended crops, recent market price trends, and active alerts.
  - Interactive price trend visualizations using Recharts.
  - Built-in Agricultural Profit Calculator estimating production costs, projected crop yields, and expected net revenue.

- **Complete Regional Language Support (8 Indian Languages):**
  - Full end-to-end localized experience supporting exactly 8 languages:
    - **English** (`en`)
    - **Kannada (ಕನ್ನಡ)** (`kn`)
    - **Hindi (हिन्दी)** (`hi`)
    - **Telugu (తెలుగు)** (`te`)
    - **Tamil (தமிழ்)** (`ta`)
    - **Malayalam (മലയാളം)** (`ml`)
    - **Marathi (मराठी)** (`mr`)
    - **Bengali (বাংলা)** (`bn`)
  - Global Language Selector with native script typography and real-time instant switching.
  - Persistent language preference saved in browser `localStorage` (`agri_lang`), retaining the user's choice across page reloads and sessions.
  - Entire user-facing UI changes according to the selected language—including Landing Page, Login, Registration, Dashboard, My Farms, Add Farm & Soil Modals, Crop Recommendation, Weather, MSP Comparison, Market Prices, Price Prediction, Profit Calculator, Notifications, Profile, and Help.
  - Integrated Google Noto Sans Indian fonts ensuring crisp native script typography without horizontal overflow or clipped glyphs.

- **Multilingual Farm-Context-Aware AI Assistant:**
  - Persistent floating AI Assistant widget accessible from any page throughout the application.
  - Automatically synchronizes with the user's currently selected regional language.
  - Understands farmer inquiries and responds fluently in any of the 8 supported regional languages.
  - Farm-context-aware intelligence automatically detecting active farm parameters (selected farm name, soil NPK, pH, moisture, live weather, mandi market prices, and MSP benchmarks) to provide tailored agronomic answers.
  - General farming assistance and actionable advice on crop suitability, fertilizer dosages, soil conditioning, irrigation planning, pest & disease precautions, and market selling decisions.
  - Dynamic localized quick-prompt chips for one-tap farmer inquiries in the active language.

---

## 4. System Architecture

The Agri Smart AI platform employs a modern layered architecture that decouples presentation, business orchestration, machine learning inference, and data persistence:

```mermaid
flowchart TD
    subgraph Client["Presentation Layer (Frontend)"]
        UI["React 18 + Vite SPA"]
        Components["Tailwind CSS + Recharts UI"]
        AxiosClient["Axios HTTP Client + JWT Interceptors"]
    end

    subgraph Server["API & Application Layer (FastAPI Backend)"]
        Router["FastAPI Application (app.main:app)"]
        AuthRoute["Auth Routes (/auth)"]
        FarmRoute["Farm & Soil Routes (/farms)"]
        MarketRoute["Market & MSP Routes (/market)"]
        RecoRoute["Recommendation Routes (/recommend)"]
        NotifRoute["Notification Routes (/notifications)"]
        WeatherRoute["Weather Routes (/weather)"]
        AssistantRoute["Assistant Routes (/assistant)"]
        Orchestration["Central Orchestration Engine\n(app.services.orchestration)"]
        AssistantEngine["Multilingual Assistant Engine\n(assistant_service.py)"]
    end

    subgraph Adapters["Model Adapter Layer"]
        CropAdapter["Crop Model Adapter\n(crop_model_adapter.py)"]
        PriceAdapter["Price Model Adapter\n(price_model_adapter.py)"]
    end

    subgraph ML_Engines["Machine Learning Engines"]
        CropModel["RandomForest Pipeline\n(crop_pipeline.joblib)"]
        PriceModel["HistGradientBoosting Regressor\n(price_model.joblib)"]
    end

    subgraph Data_Sources["Data & External Services"]
        PG[("PostgreSQL Database\n(asyncpg + SQLAlchemy 2.0)")]
        OWM["OpenWeatherMap API\n(Agro-weather + 3h Cache)"]
        Agmarknet["data.gov.in Agmarknet API\n(Daily Mandi Arrivals)"]
        MSPData[("MSP Reference Data\n(msp_prices.json)")]
    end

    UI --> Components
    Components --> AxiosClient
    AxiosClient -->|"HTTP / REST (JSON + Bearer Token)"| Router

    Router --> AuthRoute
    Router --> FarmRoute
    Router --> MarketRoute
    Router --> RecoRoute
    Router --> NotifRoute
    Router --> WeatherRoute
    Router --> AssistantRoute

    FarmRoute --> Orchestration
    MarketRoute --> Orchestration
    RecoRoute --> Orchestration
    NotifRoute --> Orchestration
    AssistantRoute --> AssistantEngine

    Orchestration --> CropAdapter
    Orchestration --> PriceAdapter
    Orchestration --> PG

    CropAdapter --> CropModel
    PriceAdapter --> PriceModel

    WeatherRoute --> OWM
    MarketRoute --> Agmarknet
    MarketRoute --> MSPData
    Orchestration --> OWM
```

### Architectural Highlights

1. **Decoupled Model Adapters:** Machine learning models are isolated behind dedicated adapter modules (`crop_model_adapter.py` and `price_model_adapter.py`). Changes to training pipelines or serialization formats do not affect backend business logic.
2. **Asynchronous I/O:** The backend utilizes FastAPI and `asyncpg` with SQLAlchemy 2.0 for non-blocking database queries and external HTTP requests (`httpx`).
3. **Resilient Data Caching:** Real-time weather responses are cached in the PostgreSQL `weather_log` table for 3 hours per coordinate cluster (~100m precision). Market prices queried from Agmarknet are similarly preserved locally, ensuring system reliability during external API downtimes.
4. **Multilingual Context-Aware AI Engine:** An extensible assistant architecture (`assistant_service.py`) that processes agricultural queries across 8 regional languages, extracts intent, and formulates localized agronomic guidance by evaluating active farm, soil, weather, and market parameters.

---

## 5. Technology Stack

| Layer / Category | Technology / Library | Version | Description / Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | React | `^18.3.1` | Declarative user interface component library |
| **Frontend Build Tool** | Vite | `^6.1.0` | Next-generation frontend tooling and bundler |
| **Styling & UI** | Tailwind CSS | `^3.4.17` | Utility-first CSS styling framework |
| **UI Icons** | Lucide React | `^0.475.0` | Modern, clean vector iconography |
| **Data Visualization** | Recharts | `^2.15.1` | Composable charting library for price trends |
| **HTTP Client** | Axios | `^1.7.9` | Promise-based client with auth interceptors |
| **Routing** | React Router DOM | `^6.28.2` | Client-side routing and protected navigation |
| **Backend Framework** | FastAPI | `>=0.115.0` | High-performance asynchronous Python web API |
| **ASGI Web Server** | Uvicorn (Standard) | `>=0.32.0` | Production ASGI server implementation |
| **ORM & Database Client** | SQLAlchemy (asyncio) | `>=2.0.36` | Asynchronous relational data mapping |
| **Database Driver** | asyncpg | `>=0.30.0` | High-performance asynchronous PostgreSQL client |
| **Database Migrations** | Alembic | `>=1.14.0` | Schema versioning and migration tool |
| **Data Validation** | Pydantic / Settings | `>=2.6.0` | Data schema validation and environment management |
| **Authentication & Security** | python-jose & bcrypt | `>=3.3.0` / `>=4.2.0` | JWT token encoding/decoding and password hashing |
| **HTTP Requests** | HTTPX | `>=0.27.0` | Async HTTP client for external government/weather APIs |
| **Machine Learning** | Scikit-Learn | `>=1.5.0` | ML algorithms (RandomForest, HistGradientBoosting) |
| **Data Manipulation** | Pandas | `>=2.2.0` | Data processing, feature extraction, and manipulation |
| **Model Serialization** | Joblib | `>=1.4.0` | Pipeline persistence and model serialization |
| **Database** | PostgreSQL | `14+` | Relational database management system |
| **External APIs** | data.gov.in (Agmarknet) | REST | Official Government of India daily mandi price API |
| **External APIs** | OpenWeatherMap | REST | Real-time agro-climatic and forecast weather API |

---

## 6. Project Structure

```text
major_project/
├── backend/
│   ├── alembic/                         # Database migration environment
│   │   ├── versions/                    # Schema migration revisions
│   │   └── env.py                       # Migration runtime configuration
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/                  # Modular API route controllers
│   │   │   │   ├── assistant.py         # Multilingual AI assistant chat & suggestions
│   │   │   │   ├── auth.py              # Farmer registration, login, and profile
│   │   │   │   ├── catalog.py           # Crop and market reference catalogs
│   │   │   │   ├── farms.py             # Farm profile and soil reading management
│   │   │   │   ├── market.py            # Mandi prices, price prediction, MSP comparison
│   │   │   │   ├── notifications.py     # Farmer notifications and alert checks
│   │   │   │   ├── recommend.py         # AI crop recommendation endpoints
│   │   │   │   └── weather.py           # Coordinate-based weather query endpoint
│   │   │   ├── deps.py                  # Authentication and dependency injection
│   │   │   └── router.py                # Central API router aggregator
│   │   ├── artifacts/                   # Member 1 trained crop model artifacts
│   │   │   ├── crop_metrics.json        # Evaluation metrics for crop recommendation
│   │   │   └── crop_pipeline.joblib     # Serialized Scikit-Learn crop pipeline
│   │   ├── core/                        # Application configuration and security
│   │   │   ├── config.py                # Pydantic environment settings
│   │   │   └── security.py              # JWT token generation and password hashing
│   │   ├── db/                          # Database connection and session management
│   │   │   ├── base.py                  # SQLAlchemy declarative base
│   │   │   └── session.py               # Async engine and session local factory
│   │   ├── ml/                          # Inference code for crop recommendation
│   │   │   ├── crop_inference.py        # Pipeline loading and top-k recommendation
│   │   │   ├── feature_builder.py       # Payload-to-DataFrame feature mapper
│   │   │   └── schema.py                # Numerical feature definitions and bounds
│   │   ├── models/                      # SQLAlchemy database entities
│   │   │   ├── farmer.py                # Farmer, Farm, and SoilData models
│   │   │   ├── market.py                # Crop, Market, MarketPrice, Predictions, Recos
│   │   │   ├── notification.py          # Notification entity and NotificationType enum
│   │   │   └── weather.py               # WeatherLog model for 3-hour caching
│   │   ├── schemas/                     # Pydantic request/response schemas
│   │   │   ├── assistant.py             # Multilingual AI assistant schemas
│   │   │   ├── auth.py                  # Authentication schemas
│   │   │   ├── farm.py                  # Farm and soil data schemas
│   │   │   ├── market.py                # Market price and prediction schemas
│   │   │   ├── notification.py          # Notification and alert output schemas
│   │   │   └── recommend.py             # Recommendation response schemas
│   │   ├── services/                    # Business logic and external service integrations
│   │   │   ├── model_adapters/          # Decoupled adapters for ML pipelines
│   │   │   │   ├── crop_model_adapter.py
│   │   │   │   ├── price_model_adapter.py
│   │   │   │   └── exceptions.py
│   │   │   ├── alerts.py                # Price and MSP alert evaluation logic
│   │   │   ├── assistant_service.py     # Multilingual NLP intent & advisory engine
│   │   │   ├── mandi_service.py         # Agmarknet (data.gov.in) API client
│   │   │   ├── orchestration.py         # Central farm/soil/weather/ML coordinator
│   │   │   └── weather_service.py       # OpenWeatherMap client with DB cache
│   │   └── main.py                      # FastAPI application entrypoint and middleware
│   ├── ml/                              # Member 2 ML scripts, datasets, and models
│   │   ├── data/                        # Market datasets and MSP references
│   │   │   ├── msp_prices.json          # Government of India MSP reference table
│   │   │   └── pan_india_combined.csv   # Cleaned historical mandi price dataset
│   │   ├── models/                      # Serialized price forecasting artifacts
│   │   │   ├── price_model.joblib       # Trained HistGradientBoosting model bundle
│   │   │   └── price_model_metrics.json # Pan-India price model evaluation metrics
│   │   └── scripts/                     # Data preparation and model training scripts
│   │       ├── download_pan_india_data.py
│   │       ├── prepare_pan_india_data.py
│   │       └── train_pan_india_price_model.py
│   ├── .env.example                     # Backend environment configuration template
│   ├── alembic.ini                      # Alembic database migration configuration
│   ├── requirements.txt                 # Backend Python package dependencies
│   └── README_MEMBER2.md                # Member 2 technical documentation
├── frontend/
│   ├── src/
│   │   ├── components/                  # Reusable UI component modules
│   │   │   ├── assistant/               # Multilingual AI Assistant widget
│   │   │   │   └── AiAssistant.jsx      # Context-aware chat drawer & suggestions
│   │   │   ├── common/                  # Navbar, Sidebar, Badges, Modals, StatCards
│   │   │   │   └── LanguageSelector.jsx # 8-language dropdown selector
│   │   │   └── forms/                   # AddFarmModal, AddSoilModal
│   │   ├── context/                     # React state contexts
│   │   │   ├── AuthContext.jsx          # JWT authentication and user session state
│   │   │   └── FarmContext.jsx          # Active farm selection and farm state
│   │   ├── i18n/                        # Internationalization (i18n) modules
│   │   │   ├── LanguageContext.jsx      # Language state provider & useTranslation hook
│   │   │   ├── languages.js             # 8 supported language definitions
│   │   │   └── translations/            # Localization dictionary files
│   │   │       ├── en.js                # English translation dictionary
│   │   │       ├── kn.js                # Kannada (ಕನ್ನಡ) translation dictionary
│   │   │       ├── hi.js                # Hindi (हिन्दी) translation dictionary
│   │   │       ├── te.js                # Telugu (తెలుగు) translation dictionary
│   │   │       ├── ta.js                # Tamil (தமிழ்) translation dictionary
│   │   │       ├── ml.js                # Malayalam (മലയാളം) translation dictionary
│   │   │       ├── mr.js                # Marathi (मराठी) translation dictionary
│   │   │       ├── bn.js                # Bengali (বাংলা) translation dictionary
│   │   │       └── index.js             # Translation dictionary aggregator
│   │   ├── layouts/                     # Master page layouts
│   │   │   ├── AuthLayout.jsx           # Clean layout for login and registration
│   │   │   └── MainLayout.jsx           # Dashboard shell with sidebar and top header
│   │   ├── pages/                       # Application view pages
│   │   │   ├── CropRecommendationPage.jsx # AI crop recommendation interface
│   │   │   ├── DashboardPage.jsx        # Unified farmer dashboard
│   │   │   ├── DiseaseDetectionPage.jsx # Plant disease detection (Roadmap)
│   │   │   ├── FarmsPage.jsx            # Farm registration and soil records
│   │   │   ├── HelpPage.jsx             # User documentation and FAQ
│   │   │   ├── LandingPage.jsx          # Public platform overview and features
│   │   │   ├── LoginPage.jsx            # Farmer login form
│   │   │   ├── MarketPricesPage.jsx     # Live mandi rates and market filters
│   │   │   ├── MspComparisonPage.jsx    # Mandi price vs. MSP comparison table
│   │   │   ├── NotificationsPage.jsx    # Price and market alert inbox
│   │   │   ├── PricePredictionPage.jsx  # Multi-day price forecasting charts
│   │   │   ├── ProfilePage.jsx          # Farmer profile details
│   │   │   ├── ProfitCalculatorPage.jsx # Input cost and yield revenue calculator
│   │   │   ├── RegisterPage.jsx         # Farmer onboarding and registration
│   │   │   ├── SmartIrrigationPage.jsx  # Smart irrigation scheduling (Roadmap)
│   │   │   └── WeatherPage.jsx          # Agro-climatic weather dashboard
│   │   ├── services/                    # Axios API client services
│   │   │   ├── api.js                   # Axios instance, baseURL, interceptors
│   │   │   ├── assistantService.js      # Multilingual AI assistant API bindings
│   │   │   ├── authService.js           # Auth endpoint bindings
│   │   │   ├── catalogService.js        # Crops and markets catalog bindings
│   │   │   ├── farmService.js           # Farm and soil data bindings
│   │   │   ├── marketService.js         # Market prices, predict, MSP bindings
│   │   │   ├── notificationService.js   # Notification bindings
│   │   │   └── weatherService.js        # Weather endpoint bindings
│   │   ├── App.jsx                      # Client router configuration and providers
│   │   ├── index.css                    # Tailwind CSS imports and custom styling
│   │   └── main.jsx                     # Vite React application entrypoint
│   ├── .env.example                     # Frontend environment configuration template
│   ├── package.json                     # Node.js dependencies and build scripts
│   ├── tailwind.config.js               # Tailwind CSS configuration
│   └── vite.config.js                   # Vite bundler configuration
└── README.md                            # Primary project documentation
```

---

## 7. Machine Learning Modules

### Crop Recommendation Module (Member 1)

The Crop Recommendation Engine evaluates farm soil chemistry and meteorological conditions to classify the most suitable crop among 22 agricultural candidates: *apple, banana, blackgram, chickpea, coconut, coffee, cotton, grapes, jute, kidneybeans, lentil, maize, mango, mothbeans, mungbean, muskmelon, orange, papaya, pigeonpeas, pomegranate, rice, and watermelon*.

- **Algorithm:** `RandomForestClassifier` encapsulated in a Scikit-Learn `Pipeline`.
- **Pre-processing:** `SimpleImputer` (median imputation for missing soil metrics) and `StandardScaler` (feature standardization).
- **Input Features (7 continuous variables):**
  - Soil Nitrogen ($N$)
  - Soil Phosphorus ($P$)
  - Soil Potassium ($K$)
  - Soil pH level ($pH$)
  - Ambient Temperature ($^\circ\text{C}$)
  - Relative Humidity ($\%$)
  - Rainfall ($\text{mm}$)
- **Inference Engine:** `backend/app/ml/crop_inference.py` loads `crop_pipeline.joblib`, calculates class probabilities using `predict_proba`, and returns top-3 crop recommendations ranked by confidence score.
- **Evaluation Results (Held-out Test Split):**
  - Total Samples: 2,200 (Training: 1,760, Testing: 440)
  - **Accuracy:** `99.55%` (0.9955)
  - **Macro F1-Score:** `99.55%` (0.9955)
  - **Macro Precision:** `99.57%` (0.9957)
  - **Macro Recall:** `99.55%` (0.9955)
  - **Top-3 Accuracy:** `100.00%` (1.0000)

### Mandi Price Forecasting & MSP Comparison (Member 2)

The Market Price Forecasting Engine models historical commodity prices from Indian mandis to provide multi-day price trajectories, enabling farmers to anticipate market trends and benchmark their offerings against official Minimum Support Prices.

- **Algorithm:** `HistGradientBoostingRegressor` with categorical feature preprocessing.
- **Training Dataset:** Curated Pan-India dataset derived from official Agmarknet arrivals (`data.gov.in`), spanning 311,736 historical records across major commodities (Wheat, Maize, Soyabean, Groundnut, Rice, Potato, Onion, Tomato, Mustard, Bengal Gram, Green Gram).
- **Feature Engineering:**
  - `lag_1`: Previous-day modal price ($t - 1$)
  - `lag_2`: Two-day lag modal price ($t - 2$)
  - `lag_3`: Three-day lag modal price ($t - 3$)
  - `rolling_mean_3`: Three-day moving average of modal price
  - Calendar variables: `month`, `day`, `day_of_week`
  - Categorical market identifiers: `Commodity`, `State`, `District`, `Market`
- **Forecasting Mechanism:** Autoregressive recursive multi-step forecasting generating predictions for 1 to 30 days ahead.
- **Evaluation Results (Chronological Test Split):**
  - Total Records: 311,736 (Training rows: 249,388, Testing rows: 62,348)
  - Evaluation Window: Chronologically held-out test partition
  - **Mean Absolute Error (MAE):** `136.07 ₹/quintal`
  - **Root Mean Squared Error (RMSE):** `342.42 ₹/quintal`
  - **Coefficient of Determination ($R^2$):** `0.9614`
- **MSP Comparison Engine:** Directly compares the latest market price or predicted forecast with official Minimum Support Prices from `msp_prices.json` (for 2026-27 marketing seasons), computing differences and status indicators (`ABOVE_MSP` / `BELOW_MSP`).

---

## 8. API Overview

The backend exposes a fully documented RESTful API built with FastAPI. Interactive OpenAPI documentation is accessible when running the backend:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

### Primary Endpoints Summary

| Tag / Domain | Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/health` | No | System health check and status confirmation |
| **Authentication** | `POST` | `/auth/register` | No | Register a new farmer account (phone, password, location) |
| **Authentication** | `POST` | `/auth/login` | No | Authenticate credentials and receive Bearer JWT token |
| **Authentication** | `GET` | `/auth/me` | Yes | Retrieve the authenticated farmer's profile |
| **Farms & Soil** | `POST` | `/farms` | Yes | Register a new farm (latitude, longitude, acreage) |
| **Farms & Soil** | `GET` | `/farms` | Yes | List all registered farms belonging to the current farmer |
| **Farms & Soil** | `GET` | `/farms/{farm_id}` | Yes | Retrieve farm details with the latest recorded soil reading |
| **Farms & Soil** | `POST` | `/farms/{farm_id}/soil` | Yes | Log a new soil test reading (N, P, K, pH, moisture, type) |
| **Agro-Weather** | `GET` | `/weather` | No | Get current weather and short forecast (cached for 3h) |
| **Market Prices** | `GET` | `/market/prices` | No | Fetch mandi market prices (live from data.gov.in / cached) |
| **Market Prices** | `GET` | `/market/predict` | Yes | Forecast mandi modal price for 1–30 days ahead |
| **Market Prices** | `GET` | `/market/msp` | No | Compare modal mandi price against official 2026-27 MSP |
| **Recommendations**| `GET` | `/recommend/crop` | Yes | Get top AI recommended crops for a specific farm |
| **Recommendations**| `GET` | `/recommend/crops/{farm_id}` | Yes | Path-parameter endpoint for farm crop recommendations |
| **Recommendations**| `GET` | `/recommend/prices` | Yes | Alternative price prediction endpoint for crop/market |
| **Reference Data** | `GET` | `/crops` | No | List supported reference crops in the database |
| **Reference Data** | `GET` | `/markets` | No | List supported reference mandi markets in the database |
| **Notifications** | `GET` | `/notifications` | Yes | List stored price and market notifications for the farmer |
| **Notifications** | `POST` | `/notifications/check-alerts` | Yes | Run price volatility and MSP alert detection logic |
| **Notifications** | `PATCH`| `/notifications/{notif_id}/read`| Yes | Mark a specific notification as read |
| **AI Assistant** | `POST` | `/assistant/chat` | No | Generate context-aware agricultural advice in selected regional language |
| **AI Assistant** | `GET` | `/assistant/languages` | No | Return supported regional languages dictionary |
| **AI Assistant** | `GET` | `/assistant/suggestions` | No | Return localized quick-start suggestions in requested language |

---

## 9. How to Setup and Run the Project

This guide provides step-by-step instructions to configure, run, verify, and troubleshoot the Agri Smart AI platform on your local development machine or GitHub Codespaces.

---

### Prerequisites

Ensure the following tools are installed on your system before proceeding:

- **Git:** Version `2.x` or higher ([Download Git](https://git-scm.com/))
- **Python:** Version `3.10` or higher ([Download Python](https://www.python.org/downloads/))
- **Node.js & npm:** Node.js `18.x` or higher with `npm 9.x` or higher ([Download Node.js](https://nodejs.org/))
- **PostgreSQL:** Version `14` or higher ([Download PostgreSQL](https://www.postgresql.org/download/))
- **Docker & Docker Compose (Optional):** If you prefer running PostgreSQL in a container instead of a local native service, Docker is supported via `backend/docker-compose.yml`.

---

### Clone the Repository

1. Clone the project repository using Git:
   ```bash
   git clone https://github.com/Ananya861/major_project.git
   ```

2. Navigate into the cloned project root directory:
   ```bash
   cd major_project
   ```

---

### Backend Setup

1. **Navigate to the `backend` directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a Python virtual environment:**
   ```bash
   # On Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # On Windows (Command Prompt)
   python -m venv venv
   venv\Scripts\activate.bat

   # On Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install backend dependencies:**
   Install all required packages defined in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure backend environment variables:**
   Create a local `.env` file by copying the template file `.env.example`:
   ```bash
   # On Windows (PowerShell / Command Prompt)
   copy .env.example .env

   # On Linux / macOS
   cp .env.example .env
   ```

   Open `backend/.env` in your text editor and specify your local configuration using placeholders:
   ```ini
   # Database connection string (asyncpg driver)
   DATABASE_URL=postgresql+asyncpg://<db_user>:<db_password>@localhost:5432/smart_farmer

   # JWT Authentication secret (generate a secure random 32+ character string)
   JWT_SECRET=<your-secure-random-secret-key>
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60

   # External API Keys
   OPENWEATHER_API_KEY=<your_openweather_api_key>
   DATA_GOV_API_KEY=<your_data_gov_api_key>

   # Allowed CORS origins (* for development or comma-separated URLs)
   CORS_ORIGINS=*
   ```

   > [!NOTE]
   > Replace `<db_user>`, `<db_password>`, `<your_openweather_api_key>`, and `<your_data_gov_api_key>` with your actual local credentials. Never commit `.env` to version control.

---

### PostgreSQL Database Setup

1. **Ensure the PostgreSQL service is active:**
   - **Local Native PostgreSQL:** Ensure PostgreSQL is running as a local service (e.g., via Windows Services, `pg_ctl start`, or macOS `brew services start postgresql`).
   - **Docker Alternative:** If using Docker, launch the database container from the `backend/` directory:
     ```bash
     docker compose up -d db
     ```

2. **Create the target database:**
   Connect to PostgreSQL using `psql` (or pgAdmin) and create the `smart_farmer` database:
   ```sql
   CREATE DATABASE smart_farmer;
   ```
   Or create it directly from your command line:
   ```bash
   # Windows / Linux / macOS
   psql -U postgres -c "CREATE DATABASE smart_farmer;"
   ```

3. **Verify the database connection string format:**
   Ensure the `DATABASE_URL` in `backend/.env` adheres to the asynchronous `asyncpg` format:
   ```text
   postgresql+asyncpg://<username>:<password>@localhost:5432/smart_farmer
   ```

4. **Run database migrations with Alembic:**
   From within the `backend/` directory (with your virtual environment activated), execute Alembic migrations to create all database schemas and tables:
   ```bash
   alembic upgrade head
   ```
   This command applies all migration revisions, establishing the database tables: `farmer`, `farm`, `soil_data`, `crop`, `crop_recommendation`, `market`, `market_price`, `price_prediction`, `notification`, and `weather_log`.

---

### Run the FastAPI Backend

1. From the `backend/` directory (with `venv` activated), start the Uvicorn ASGI server:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Verify backend server URLs (Local Execution Examples):**
   - **Base API URL:** `http://127.0.0.1:8000`
   - **Interactive Swagger UI:** `http://127.0.0.1:8000/docs`
   - **Alternative ReDoc API Docs:** `http://127.0.0.1:8000/redoc`
   - **Health Check Endpoint:** `http://127.0.0.1:8000/health`

---

### Frontend Setup

1. **Open a new terminal and navigate to the `frontend/` directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   Install all dependencies specified in `package.json`:
   ```bash
   npm install
   ```

3. **Configure frontend environment variables:**
   Copy the frontend `.env.example` template to `.env`:
   ```bash
   # On Windows (PowerShell / Command Prompt)
   copy .env.example .env

   # On Linux / macOS
   cp .env.example .env
   ```

   Open `frontend/.env` and ensure the API base URL points to your running local FastAPI backend:
   ```ini
   VITE_API_BASE_URL=http://localhost:8000
   ```

   > [!IMPORTANT]
   > For standard local development, keep `VITE_API_BASE_URL` set to your local backend URL (`http://localhost:8000`). Do not hardcode remote or Codespaces URLs in your default local configuration.

---

### Run the React / Vite Frontend

1. From the `frontend/` directory, start the Vite development server:
   ```bash
   npm run dev
   ```

2. **Access the application in your browser:**
   Open [http://localhost:5173](http://localhost:5173) to view the Agri Smart AI web interface.

---

### Running Backend and Frontend Together

To run the full stack locally, open three separate terminal windows:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Terminal 1: PostgreSQL Database                                             │
│ $ psql / pg_ctl / Docker: cd backend && docker compose up -d db             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Terminal 2: FastAPI Backend                                                 │
│ $ cd backend                                                                │
│ $ .\venv\Scripts\Activate.ps1   # (or source venv/bin/activate on Unix)     │
│ $ python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Terminal 3: React / Vite Frontend                                           │
│ $ cd frontend                                                               │
│ $ npm run dev                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Database and API Verification

After starting the services, verify that everything is running properly:

1. **Verify Database Migrations:**
   In the `backend/` directory, check that Alembic is up to date:
   ```bash
   alembic current
   ```
   To list all tables in the `smart_farmer` database:
   ```bash
   psql -U postgres -d smart_farmer -c "\dt"
   ```
   You should see: `alembic_version`, `crop`, `crop_recommendation`, `farm`, `farmer`, `market`, `market_price`, `notification`, `price_prediction`, `soil_data`, and `weather_log`.

2. **Verify the Backend Health Check:**
   Run a curl request against the `/health` endpoint:
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   **Expected Response:**
   ```json
   {"status": "ok"}
   ```

3. **Verify Interactive API Documentation:**
   Open `http://127.0.0.1:8000/docs` in your browser. Confirm that the routes under `auth`, `farms`, `market`, `recommend`, `weather`, `notifications`, and `catalog` are loaded and functional.

---

### GitHub Codespaces Setup

The project natively supports running inside GitHub Codespaces. If you are developing inside a Codespace, follow these specific configurations:

1. **Port Visibility Configuration:**
   - In GitHub Codespaces, open the **Ports** panel in the bottom toolbar.
   - Forward port `8000` (FastAPI backend) and port `5173` (Vite frontend).
   - Right-click on port `8000` and set **Port Visibility** to **Public** so browser requests from the frontend can reach the API.
   - **SECURITY RULE:** Keep port `5432` (PostgreSQL) strictly **Private** (internal). Never expose database ports publicly.

2. **CORS Support:**
   The backend entrypoint (`app/main.py`) includes built-in CORS middleware configured with a regular expression matching GitHub Codespaces domain patterns (`https://.*\.app\.github\.dev`).

3. **Codespaces Frontend Configuration:**
   In Codespaces, `.env` files are ignored by git and must be created fresh:
   - Create `backend/.env` from `backend/.env.example`.
   - In `frontend/.env`, set `VITE_API_BASE_URL` to your forwarded backend Codespaces URL:
     ```ini
     VITE_API_BASE_URL=https://<your-codespace-name>-8000.app.github.dev
     ```

---

### Troubleshooting

| Issue / Symptom | Probable Cause | Recommended Resolution |
| :--- | :--- | :--- |
| **`connection to server at "localhost", port 5432 failed: Connection refused`** | PostgreSQL service is not running or credentials are wrong. | 1. Ensure PostgreSQL is active (`net start postgresql` on Windows or `sudo systemctl status postgresql` on Linux).<br>2. Verify host, port (`5432`), user, and password in `backend/.env`. |
| **`ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`** | Port `8000` is already occupied by another running server instance. | 1. Stop the existing process running on port 8000.<br>2. Alternatively, specify another port: `python -m uvicorn app.main:app --port 8001` (and update `VITE_API_BASE_URL` in `frontend/.env`). |
| **Frontend shows "Network Error" or cannot connect to backend** | Frontend cannot resolve `VITE_API_BASE_URL` or backend is down. | 1. Confirm FastAPI backend is active and responds at `http://127.0.0.1:8000/health`.<br>2. Verify `VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env`.<br>3. Restart the Vite server (`npm run dev`) after modifying `.env`. |
| **CORS Policy Error: `No 'Access-Control-Allow-Origin' header is present`** | Request origin host is not permitted by backend CORS settings. | 1. Check `CORS_ORIGINS` in `backend/.env`. For local development, set `CORS_ORIGINS=*`.<br>2. For Codespaces, ensure `main.py` contains `allow_origin_regex=r"https://.*\.app\.github\.dev"`. |
| **`Missing / NoneType Error` during startup or API calls** | Missing environment variable in `.env`. | 1. Verify `backend/.env` exists and matches the keys defined in `backend/.env.example`.<br>2. Ensure `OPENWEATHER_API_KEY` and `DATA_GOV_API_KEY` are defined. |
| **`alembic.util.exc.CommandError: Can't locate revision identified by...`** | Database schema is out of sync with migration history or database does not exist. | 1. Ensure the `smart_farmer` database was created before running migrations.<br>2. Run `alembic upgrade head` from the `backend/` directory. |
| **Codespaces: 401 / 403 or API fetch failure in browser** | Port 8000 visibility is set to Private. | In the Codespaces Ports tab, right-click Port `8000` and change **Port Visibility** to **Public**. |

---

### Project Execution Flow

The end-to-end operational architecture connects the presentation tier, REST services, persistence, external public APIs, and machine learning inference engines:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          User / Web Browser Client                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    React 18 + Vite Single-Page Application                  │
│                     (Port 5173 — Tailwind CSS + Recharts)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │  Axios HTTP / REST (JSON + Bearer JWT)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FastAPI Application Server                            │
│                        (Port 8000 — app.main:app)                           │
└─────────────────────────────────────────────────────────────────────────────┘
          │                           │                           │
          ▼                           ▼                           ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ PostgreSQL (5432)│        │  External APIs   │        │   ML Adapters    │
│ (asyncpg driver) │        │ (httpx client)   │        │ (Scikit-Learn)   │
│                  │        │                  │        │                  │
│ • farmer         │        │ • OpenWeatherMap │        │ • Crop Reco      │
│ • farm           │        │   (Temp, Humid,  │        │   (RandomForest) │
│ • soil_data      │        │    3h Cache)     │        │                  │
│ • crop_reco      │        │ • data.gov.in    │        │ • Price Forecast │
│ • market_price   │        │   (Agmarknet     │        │   (HistGradient  │
│ • price_pred     │        │    Mandi Rates)  │        │    Boosting)     │
│ • notification   │        │ • MSP Benchmarks │        │                  │
└──────────────────┘        └──────────────────┘        └──────────────────┘
```

---

### Security Best Practices

To protect sensitive credentials and ensure system integrity:

- **Never Commit `.env` Files:** Ensure `.env` is listed in your `.gitignore` before committing. Always use `.env.example` as a template containing only placeholders.
- **Never Hardcode Credentials:** Secrets, database passwords, JWT signing keys, and external API tokens must always be supplied via environment variables.
- **Isolate Database Ports:** In cloud/Codespaces environments, never expose PostgreSQL port `5432` to the public internet. Keep database access internal.
- **Key Rotation:** If an API key or password is ever accidentally exposed in code or terminal logs, immediately revoke and regenerate it from the provider's dashboard (OpenWeatherMap, data.gov.in, or database administrator).

---

## 10. Environment Configuration

### Backend Environment Variables (`backend/.env`)

| Variable Name | Required | Default / Example | Purpose |
| :--- | :---: | :--- | :--- |
| `DATABASE_URL` | **Yes** | `postgresql+asyncpg://postgres:password@localhost:5432/smart_farmer` | Asynchronous PostgreSQL connection string using `asyncpg` |
| `JWT_SECRET` | **Yes** | `change-me-to-a-long-random-string` | Cryptographic secret key used to sign authentication tokens |
| `JWT_ALGORITHM` | No | `HS256` | Token hashing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Token expiration duration in minutes |
| `OPENWEATHER_API_KEY` | **Yes** | `your_openweather_api_key_here` | API key for OpenWeatherMap current and forecast data |
| `DATA_GOV_API_KEY` | **Yes** | `your_data_gov_api_key_here` | API key for Government of India data.gov.in Agmarknet API |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed CORS origin hosts |

> **Security Note:** Never commit actual `.env` files containing production passwords or API tokens to source control. Always use `.env.example` as a template.

### Frontend Environment Variables (`frontend/.env`)

| Variable Name | Required | Default / Example | Purpose |
| :--- | :---: | :--- | :--- |
| `VITE_API_BASE_URL` | **Yes** | `http://localhost:8000` | Base URL of the running FastAPI backend |

---

## 11. Build Verification

Both the frontend and backend include automated verification commands to ensure code integrity, module resolution, and compilation before deployment:

### Backend Code & Syntax Compilation Check

Verify that all Python modules, models, routes, and scripts compile without syntax or import errors:

```bash
cd backend
python -m compileall app ml
```

### Frontend Production Build Verification

Verify that all React components, Tailwind CSS styles, assets, and route dependencies compile and bundle cleanly for production:

```bash
cd frontend
npm run build
```

The compiled assets will be created in the `frontend/dist/` directory.

---

## 12. Team Contributions

This project was developed collaboratively with clear division of technical responsibilities:

- **Member 1: Crop Recommendation and Agro-Climatic Intelligence**
  - Curated and pre-processed the agricultural crop recommendation dataset.
  - Designed and trained the multi-class `RandomForestClassifier` Scikit-Learn pipeline.
  - Implemented the top-k probabilistic recommendation inference engine (`app/ml/crop_inference.py`).
  - Integrated the crop model adapter linking farm soil attributes and weather parameters.

- **Member 2: Mandi Market Forecasting, Pan-India Price Analysis, and MSP Comparison**
  - Sourced and cleaned historical pan-India mandi market transaction data from official Agmarknet sources.
  - Conducted time-series feature engineering (lag values, rolling means, temporal markers).
  - Trained and evaluated the `HistGradientBoostingRegressor` multi-day price forecasting model.
  - Implemented the MSP comparison logic and rule-based price volatility alert detection.

- **Member 3: Backend Integration, APIs, Orchestration, and Frontend Dashboard**
  - Designed the system architecture, RESTful API endpoints, and central orchestration service.
  - Configured PostgreSQL database models, relationships, and Alembic migrations.
  - Implemented JWT authentication, password hashing, and user profile management.
  - Built the responsive React/Vite single-page application, interactive charts, and API client integration.

---

## 13. Future Enhancements

The Agri Smart AI platform architecture is designed to accommodate planned future modules:

- **Automated Plant Leaf Disease Detection:** Integrating computer vision models (e.g., Convolutional Neural Networks trained on the PlantVillage dataset) to diagnose crop foliage pathologies via smartphone camera uploads.
- **Smart Irrigation Scheduling & Evapotranspiration Telemetry:** Computing precise millimeter irrigation requirements using the FAO-56 Penman-Monteith equation combined with local weather forecasts to automate drip irrigation zones.
- **Multilingual Voice & SMS Notifications:** Extending accessibility for rural farmers through automated regional language voice calls (IVR) and SMS alerts for critical price and weather warnings.
- **Distributed Background Task Processing:** Deploying Celery / Redis / APScheduler worker queues for scheduled daily price ingestion, automated alert checks, and background data synchronization.
- **Satellite Remote Sensing (NDVI):** Integrating Sentinel-2 / Landsat multispectral imagery to provide crop health vegetation index monitoring at parcel resolution.

---

## 14. Disclaimer and Data Notes

- **Market Price Data Source:** Agricultural market commodity prices and arrival records are retrieved from the official Open Government Data (OGD) platform of India ([data.gov.in](https://data.gov.in/)) via the Agmarknet resource.
- **Agro-Weather Data Source:** Weather observations and short-term forecasts are provided via the OpenWeatherMap API service.
- **Decision Support Advisory:** All machine learning predictions, crop recommendations, and market forecasts generated by Agri Smart AI are intended solely as an informational decision-support aid. Agricultural yields and market realization are inherently subject to dynamic weather phenomena, localized microclimates, pest pressures, and broader macroeconomic conditions. Users are advised to cross-reference recommendations with regional agricultural extension officers and Krishi Vigyan Kendras (KVKs).
