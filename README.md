# 🌾 MandiFlow · Agricultural Supply Chain Analytics

End-to-end agricultural supply chain analytics platform integrating mandi arrivals, crop prices, MSP, weather, and transport data — with an AI-powered natural-language chart generator built on Groq LLaMA 3.3-70B.

---

## Stack

| Layer | Technology |
|---|---|
| Dashboard | Streamlit ≥ 1.36 |
| Visualizations | Plotly Express / Graph Objects |
| AI Agent | Groq API · LLaMA 3.3-70B-Versatile |
| Data | Pandas ≥ 2.0 · NumPy · OpenPyXL |
| Credentials | python-dotenv · Streamlit Secrets |

---

## Project Structure

```
├── streamlit_app/
│   ├── streamlit_app.py        # Main entry point — nav, layout, data loading
│   ├── requirements.txt        # Python dependencies
│   ├── run_dashboard.bat       # One-click Windows launcher
│   └── .streamlit/
│       └── secrets.example.toml
│
├── src/
│   ├── data_loader.py          # CSV/JSON/Excel loaders with cleaning & type coercion
│   ├── charts.py               # All Plotly chart factory functions
│   ├── metrics.py              # KPI calculations and insight generators
│   ├── filters.py              # Sidebar filter helpers
│   ├── styles.py               # Custom CSS, color tokens, chart theme
│   └── pages/
│       ├── overview.py         # Page 1 · Market Overview
│       ├── mandi_analysis.py   # Page 2 · Mandi Analysis
│       ├── crop_price.py       # Page 3 · Crop & Price
│       ├── transport.py        # Page 4 · Transport Logistics
│       ├── weather.py          # Page 5 · Weather Impact
│       ├── data_quality.py     # Page 6 · Data Quality
│       └── ai_analytics.py     # Page 7 · AI Analytics ✨
│
├── Datasets/
│   ├── Raw/                    # 5 source files (CSV, JSON, Excel)
│   └── Cleaned/
│       └── final_integrated_dataset.csv   # 25,750 rows × 21+ columns
│
├── .env                        # GROQ_API_KEY (not committed)
├── requirements.txt            # Root-level requirements
└── Agricultural_Supply_Chain_Price_Discovery.ipynb
```

---

## Quickstart

### 1. Clone

```bash
git clone https://github.com/nexus9601/Mandiflow-agricultural-supply-chain-analytics.git
cd Mandiflow-agricultural-supply-chain-analytics
```

### 2. Install dependencies

```bash
pip install -r streamlit_app/requirements.txt
```

### 3. Configure your Groq API key

**Option A — `.env` file** (recommended for local dev):

Create a `.env` file in the project root:

```ini
GROQ_API_KEY=gsk_your_key_here
# Optional: pin a specific model
# GROQ_MODEL=llama-3.3-70b-versatile
```

**Option B — Streamlit Secrets** (recommended for Streamlit Cloud):

Copy the example file and add your key:

```bash
cp streamlit_app/.streamlit/secrets.example.toml streamlit_app/.streamlit/secrets.toml
```

```toml
GROQ_API_KEY = "gsk_your_key_here"
GROQ_MODEL = ""   # Optional: leave blank for auto-selection
```

Get a free Groq key at [console.groq.com](https://console.groq.com).

### 4. Run

**Windows — double-click `streamlit_app/run_dashboard.bat`**, or from a terminal:

```bash
cd streamlit_app
streamlit run streamlit_app.py
```

Open **http://localhost:8501**

---

## Pages

### 🏠 Overview
High-level KPI cards (total arrivals, avg modal price, MSP breach rate, transit delay rate) plus arrival trend by crop and crop distribution charts.

### 📊 Mandi Analysis
Top-N mandi volume ranking, district distribution, mandi-level arrival time series, and an operational performance summary table.

### 💰 Crop & Price
Price vs MSP floor parity, MSP gap analysis, price volatility / downside risk matrix, historical price-trend series, and a crop price risk summary table.

### 🚛 Transport Logistics
Warehouse fleet performance (transit time, distance), transit duration distribution, corridor volume, mandi-to-warehouse route benchmarks, and automated logistics risk insights.

### 🌦️ Weather Impact
Precipitation × daily inflow dual-axis overlay, rainfall scatter, temperature trend, humidity trajectory, and a weather impact summary.

### 🔍 Data Quality
Dataset schema explorer, column-level null / outlier / type audit, anomaly flags, and downloadable quality report.

### ✨ AI Analytics
Type a natural-language question — the agent generates Pandas + Plotly code via Groq LLM, executes it against the live dataframe, and renders the chart. The generated code is always inspectable in the collapsible panel below.

**Example queries:**
- `Bar chart of top 10 mandis by total arrival quantity`
- `Line chart of modal price trend for Wheat over time`
- `Scatter plot of avg temperature vs modal price, colored by crop`
- `Heatmap of average modal price by crop and district`
- `Top 5 crops by inflow volume`
- `Rainfall vs arrival dynamics over time`

---

## Dataset

The integrated dataset (`Datasets/Cleaned/final_integrated_dataset.csv`) merges 5 raw sources:

| Source | Description |
|---|---|
| `track3_mandi_arrivals.csv` | Crop arrivals with mixed units and dates |
| `track3_price_and_msp.json` | Wholesale modal prices and MSP floor prices |
| `track3_weather_sensors.xlsx` | Temperature, rainfall, humidity readings |
| `track3_transport_logistics.csv` | Trip distances and transit times |
| `track3_mandi_master.csv` | Mandi and district reference data |

**Key columns:** `crop_name`, `mandi_name`, `district`, `mandi_type`, `arrival_quantity_qtl`, `modal_price`, `msp`, `price_vs_msp`, `price_crash`, `avg_temperature_c`, `total_rainfall_mm`, `distance_km`, `transit_hours_clean`, `long_transit_flag`

---

## Requirements

```
streamlit>=1.36.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.22.0
openpyxl>=3.1.0
openai>=1.0.0
python-dotenv>=1.0.0
```
