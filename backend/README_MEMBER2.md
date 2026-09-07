# Member 2 – MSP & Market Price Forecasting

## Overview

Member 2 is responsible for the market-price forecasting and Minimum Support Price (MSP) comparison module of the Smart Farming Advisory System.

The module combines official mandi market-price data, historical price data, machine-learning-based forecasting, MSP comparison, and price-alert notifications.

## Features

### 1. Mandi Market Price Integration

Market prices are retrieved from the official Government of India data.gov.in Mandi API.

The system supports:
- Commodity
- State
- District
- Market
- Variety
- Grade
- Arrival date
- Minimum price
- Maximum price
- Modal price

The mandi source provides daily market-price data.

### 2. Pan-India Market Data

Historical mandi data was collected and prepared for multiple commodities and markets across India.

The dataset includes:
- Wheat
- Maize
- Soyabean
- Groundnut
- Rice
- Paddy (Common)
- Potato
- Onion
- Tomato
- Mustard
- Bengal Gram (Gram) (Whole)
- Green Gram (Moong) (Whole)

The collected data covers multiple Indian states and includes Uttarakhand markets.

### 3. Machine Learning Price Forecasting

A machine-learning model is trained using historical mandi prices.

Features include:
- Previous-day price (lag 1)
- Two-day lag (lag 2)
- Three-day lag (lag 3)
- Three-day rolling mean
- Month
- Day
- Day of week
- Commodity
- State
- District
- Market

The forecasting model uses HistGradientBoostingRegressor with categorical preprocessing.

### 4. MSP Comparison

The system compares the predicted/current market price with the Minimum Support Price (MSP).

The response provides:
- Market price
- MSP
- Difference
- Difference percentage
- Whether the price is above or below MSP
- Season
- Marketing year

### 5. Price Alerts

The alert service checks price conditions and creates notifications for farmers.

Alerts include:
- Significant forecast/current price changes
- Prices significantly above or below MSP
- Market-price movement alerts

Duplicate unread alerts for the same day are avoided.

### 6. Notification API

Price alerts are stored in the PostgreSQL database and can be retrieved through the notification API.

Important endpoints:

`GET /notifications`

Returns notifications for the authenticated farmer.

`POST /notifications/check-alerts`

Runs the price-alert checks and creates applicable notifications.

## Main API Endpoints

### Price Forecast

`GET /market/predict`

Parameters:
- `crop_id`
- `market_id`
- `days_ahead`

Returns predicted prices for the requested number of days.

### Market Prices

`GET /market/prices`

Returns available mandi market-price information.

### MSP Comparison

`GET /market/msp`

Parameters:
- `crop_id`
- `market_id`

Returns the market price compared with the applicable MSP.

### Notifications

`GET /notifications`

Returns saved farmer notifications.

### Alert Check

`POST /notifications/check-alerts`

Runs the price-alert detection logic.

## Model Performance

The Pan-India price model was evaluated using a chronological train/test split.

Evaluation results:

- MAE: 136.07
- RMSE: 342.42
- R²: 0.9614

These metrics describe model performance on the held-out test data.

## Project Files

Important Member 2 files include:

`ml/scripts/download_pan_india_data.py`

Downloads historical mandi data.

`ml/scripts/prepare_pan_india_data.py`

Cleans and prepares the collected market-price data.

`ml/scripts/train_pan_india_price_model.py`

Trains the Pan-India price forecasting model.

`ml/data/pan_india_combined.csv`

Prepared Pan-India market-price dataset.

`ml/data/msp_prices.json`

MSP reference data.

`ml/models/price_model.joblib`

Trained price forecasting model.

`ml/models/price_model_metrics.json`

Saved model evaluation metrics.

`app/services/mandi_service.py`

Connects the backend to the official mandi API.

`app/services/model_adapters/price_model_adapter.py`

Connects the trained forecasting model to the backend.

`app/services/alerts.py`

Contains price-alert logic.

`app/api/routes/market.py`

Provides market-price, prediction, and MSP APIs.

`app/api/routes/notifications.py`

Provides notification and alert-check APIs.

## Data Source

Government of India – data.gov.in Mandi market-price dataset.

The Mandi API provides daily market-price data and is dynamically queried by the backend.

MSP reference values are maintained for the applicable marketing year.

## Important Configuration

The backend requires the following environment configuration:

`DATABASE_URL`

PostgreSQL database connection.

`DATA_GOV_API_KEY`

API key required to access the data.gov.in Mandi API.

The API key must be kept private and should not be committed to GitHub.

## Integration

The price forecasting module is connected to the existing backend through:

`app/services/model_adapters/price_model_adapter.py`

The orchestration layer is not modified by Member 2.

The trained model and price adapter provide predictions to the existing market-service flow.

## Verification

The complete Member 2 flow was tested through Swagger:

1. Market prices retrieved successfully.
2. Price predictions generated successfully.
3. MSP comparison returned successfully.
4. Price-alert check returned successfully.
5. Price alerts were created and stored.
6. Notifications were retrieved successfully through `GET /notifications`.

Example alert-check result:

`price_alerts_created: 5`

This confirms that the alert-generation and notification flow is functioning end-to-end.
