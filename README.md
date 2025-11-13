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



