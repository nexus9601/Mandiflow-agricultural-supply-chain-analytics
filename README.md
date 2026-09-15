# MandiFlow · Agricultural Supply Chain Analytics

End-to-end agricultural supply chain analytics platform integrating mandi arrivals, crop prices, MSP, weather, and transport data — with an AI-powered natural-language chart generator built on Groq LLaMA 3.3-70B.

---

## Stack

| Layer | Technology |
|---|---|
| Dashboard | Plotly Dash |
| Visualizations | Plotly Express / Graph Objects |
| AI Agent | Groq API · LLaMA 3.3-70B-Versatile |
| Data | Pandas |
| Credentials | python-dotenv |

---

## Project Structure

```
├── app.py                     # Dash app — router, navbar, all callbacks
├── run.bat                    # One-click launcher
├── requirements.txt
├── .env                       # GROQ_API_KEY (not committed)
│
├── dash_pages/
│   ├── dataset_view.py        # Page 1: Dataset explorer with filters + table
│   ├── manual_dashboard_view.py  # Page 2: Controls, toggles, integration slot
│   └── ai_dashboard_view.py   # Page 3: AI agent chart generator
│
├── utils/
│   └── data_store.py          # Cached CSV loader (get_data())
│
├── assets/
│   └── style.css              # Agriculture dark theme (soil + crop green)
│
└── Datasets/
    ├── Raw/                   # 5 source files (CSV, JSON, Excel)
    └── Cleaned/
        └── final_integrated_dataset.csv   # 25,750 rows × 21 columns
```

---

## Quickstart

### 1. Clone

```bash
git clone https://github.com/nexus9601/Mandiflow-agricultural-supply-chain-analytics.git
cd Mandiflow-agricultural-supply-chain-analytics
```

### 2. Configure API key

Get a free key at [console.groq.com](https://console.groq.com), then add it to `.env`:

```
GROQ_API_KEY=gsk_your_key_here
```

### 3. Run

**Windows — double-click `run.bat`**, or from a terminal:

```bash
pip install -r requirements.txt
python app.py
```

Open **http://localhost:8050**

---

## Pages

### 📋 Dataset Explorer (`/dataset`)
Filter records by crop, district, and mandi type. Paginated table with the 10 core columns.

### 📊 Manual Dashboard (`/manual-dashboard`)
Multi-select crop and mandi type filters, primary metric selector, and analysis toggles (log scale, moving average, outlier filter, MSP overlay). The chart workspace section is left open for custom Plotly components.

### ✨ AI Analytics (`/ai-dashboard`)
Type a natural language question — the agent generates Pandas + Plotly code via Groq, executes it against the live dataframe, and renders the chart. The generated code is always inspectable via the collapsible panel below the chart.

**Example queries:**
- `Bar chart of top 10 mandis by total arrival quantity`
- `Line chart of modal price trend for Wheat over time`
- `Scatter plot of avg temperature vs modal price, colored by crop`
- `Heatmap of average modal price by crop and district`

---

## Dataset

The integrated dataset (`final_integrated_dataset.csv`) merges 5 raw sources:

| Source | Description |
|---|---|
| `track3_mandi_arrivals.csv` | Crop arrivals with mixed units and dates |
| `track3_price_and_msp.json` | Wholesale modal prices and MSP |
| `track3_weather_sensors.xlsx` | Temperature, rainfall, humidity |
| `track3_transport_logistics.csv` | Trip distances and transit times |
| `track3_mandi_master.csv` | Mandi and district reference data |

**Key columns:** `crop_name`, `mandi_name`, `district`, `mandi_type`, `arrival_quantity_qtl`, `modal_price`, `msp`, `avg_temperature_c`, `total_rainfall_mm`, `avg_distance_km`, `avg_transit_hours`, `transit_delay_rate`
