# 🌍 Germany Renewable Energy Forecasting & Analytics Dashboard

**A Data Science Project for Gridcog – Driving the Transition to a Decentralised and Decarbonised Energy Future**

---

## 📘 Project Overview

This project analyses Germany’s electricity generation between **2014–2020** using **15-minute resolution data** from the ENTSO-E Transparency Platform.
The goal is to understand renewable generation dynamics (solar and wind), their ramp rates, and forecast their contribution to the national load using advanced time-series modeling.

---

## ⚡ Objectives

1. **Perform Exploratory Data Analysis (EDA)** to understand trends in solar and wind generation, installed capacity, and ramp rate behavior.
2. **Develop and train a deep learning LSTM model** to forecast renewable generation share, focusing on interpretability and temporal structure.
3. **Deploy insights in an interactive Streamlit dashboard** for visualising KPIs, generation dynamics, and model forecasts.

---

## 🧩 Data Description

| Variable                                     | Description                             |
| -------------------------------------------- | --------------------------------------- |
| `utc_timestamp`                              | Timestamp in UTC (15-minute intervals)  |
| `DE_load_actual_entsoe_transparency`         | Actual electricity load in Germany (MW) |
| `DE_load_forecast_entsoe_transparency`       | Day-ahead load forecast (MW)            |
| `DE_solar_capacity`                          | Installed solar capacity (MW)           |
| `DE_solar_generation_actual`                 | Actual solar generation (MW)            |
| `DE_wind_capacity`                           | Installed wind capacity (MW)            |
| `DE_wind_generation_actual`                  | Actual wind generation (MW)             |
| `DE_wind_offshore_generation_actual`         | Offshore wind generation (MW)           |
| `DE_wind_onshore_generation_actual`          | Onshore wind generation (MW)            |
| `DE_50hertz_load_actual_entsoe_transparency` | Load in 50Hertz region (MW)             |

---

## 🔍 1. Exploratory Data Analysis (EDA)

EDA provided a detailed picture of Germany’s renewable energy generation profile:

* **Solar and Wind Capacity Growth**: Clear upward trend in installed capacity, with strong seasonal patterns.
* **Generation Variability**: Wind shows higher temporal volatility than solar; complementarity between them observed.
* **Renewable Diurnal Patterns**: Solar peaks during midday; wind generation more evenly distributed.
* **Ramp Rate Analysis**:

  * Computed **solar and wind ramp rates** (`Δ generation`) to identify grid flexibility requirements.
  
Insights from EDA informed model design and helped identify key temporal dependencies for forecasting.

---

## 🤖 2. LSTM Model Architecture

To forecast renewable generation (combined solar and wind), a **Long Short-Term Memory (LSTM)** neural network was trained.

### **Model Summary**

| Layer | Type                                        | Description                                                  |
| ----- | ------------------------------------------- | ------------------------------------------------------------ |
| 1️⃣   | **LSTM (50 units)**                         | Captures sequential dependencies in the time series          |
| 2️⃣   | **Dropout (0.2)**                           | Regularization layer ignoring 20% of neurons during training |
| 3️⃣   | **LSTM (50 units, return_sequences=False)** | Summarizes the sequence information into a single vector     |
| 4️⃣   | **Dropout (0.2)**                           | Additional regularization layer                              |
| 5️⃣   | **Dense (1 unit)**                          | Final output layer predicting renewable generation           |

**Total Trainable Parameters:** 34,251

### **Training Details**

* **Loss function:** Mean Squared Error (MSE)
* **Optimizer:** Adam (learning rate = 0.001)
* **Epochs:** 50 with early stopping based on validation loss
* **Batch size:** 32

The model successfully captured temporal dependencies and seasonal dynamics, producing realistic short-term renewable generation forecasts.

---

## 📊 3. Streamlit Dashboard

The Germany Energy Intelligence Dashboard is an interactive web application that provides comprehensive analysis and visualization of Germany's energy sector from 2014 to 2020. Built with Streamlit and Plotly, this dashboard offers insights into renewable energy generation, capacity growth, and grid performance metrics.

**Key Performance Indicators (KPIs)**
* Renewable Energy Share: Percentage of solar and wind in total energy mix
* Capacity Utilization: Solar and wind generation efficiency
* Offshore Wind Contribution: Share of offshore wind in total wind capacity
* Load Forecast Accuracy: Grid management performance metrics

**Interactive Visualizations**
* Energy Generation Mix: Time-series analysis of solar, wind, and total load
* Capacity vs Generation: Real-time utilization profiles
* Wind Generation Breakdown: Onshore vs offshore wind analysis
* Renewable Capacity Growth: Year-over-year capacity expansion trends
* Seasonal Patterns: Monthly generation and load patterns
* Capacity Factor Analysis: Technology efficiency comparisons

**Data Insights**
* Renewable Growth Trends: Tracking Germany's energy transition
* Seasonal Performance: Understanding generation patterns
* Grid Stability: Assessing forecast accuracy and reliability


Streamlit Dashboard can be found in this URL Link: [Link](https://kwdeq2kxhg9b282r53sq3w.streamlit.app/)

---
## 📁 4. Project Structure
The project is organized as follows:
```
.
└── py-german-electricity
    ├── CHANGELOG        
    │   └── v0.1.0.md     
    ├── CODE_OF_CONDUCT.md
    ├── CONTRIBUTING.md   
    ├── data
    │   └── time_series_15min_singleindex.csv
    ├── docs
    │   ├── api.md
    │   ├── index.md
    │   ├── installation.md
    │   └── usage.md
    ├── justfile
    ├── LICENSE
    ├── notebooks
    │   ├── german_electricity_eda_notebook.ipynb
    │   └── german_electricity_forecasting.ipynb
    ├── pyproject.toml
    ├── README.md
    ├── requirements.txt
    ├── SECURITY.md
    ├── src
    │   ├── py_german_electricity
    │   │   ├── cli.py
    │   │   ├── py.typed
    │   │   ├── utils.py
    │   │   ├── __init__.py
    │   │   └── __main__.py
    │   └── streamlit_app.py
    ├── tests
    │   └── test_py_german_electricity.py
    └── zensical.toml