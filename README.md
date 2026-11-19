# UrbanProfit — Multi-City Market Intelligence Platform

An interactive **Streamlit** geospatial market intelligence and location-screening platform built for entrepreneurs and small-business owners across **12 major Indian cities (63 localities)**.

## Key Features
- **Interactive Rose-Pink & Off-White Dashboard:** Custom-styled Streamlit interface with subtle CSS particle backdrop, KPI summary cards, and interactive Plotly visualizations.
- **12-City Coverage (63 Localities):** Supports multi-locality comparison across **Bengaluru, Mumbai, Delhi, Hyderabad, Chennai, Pune, Kolkata, Ahmedabad, Jaipur, Kochi, Lucknow, and Indore**.
- **Real-World Geospatial Pipeline:** Extracts live OpenStreetMap (OSM) POI competitor counts, road network density/segments/intersections, and nearest metro/subway station distances within a standardized **3 km radius circular study area** (~$28.27\text{ km}^2$).
- **MCDA Market Potential Scoring ($0\text{–}100$):** Evaluates and ranks localities within each city using a weighted linear combination of Min-Max normalized indicators:
  $$\text{Market Potential Score} = 0.30 \cdot \text{Population Score} + 0.20 \cdot \text{Rent Affordability Score} + 0.25 \cdot \text{Competition Score} + 0.25 \cdot \text{Road Accessibility Score}$$
- **K-Means Locality Segmentation:** Groups localities into 3 market clusters (`cluster = 0, 1, 2`) based on standardized density, commercial rent, competitor saturation, and road connectivity.
- **Business Opportunity Explorer:** Rule-based preliminary screening across 8 retail and service categories (`Restaurant / Café`, `Bakery / Cloud Kitchen`, `Gym / Fitness Studio`, `Pharmacy / Healthcare Retail`, `Electronics Store`, `Specialty Retail Store`, `Salon / Beauty Studio`, and `Bar / Pub / Nightlife` research advisories).
- **Executive Report Downloads:** Exports city-specific, Excel-compatible UTF-8-SIG **CSV** files and landscape A4 **PDF** reports (via ReportLab).

---

## Project Directory Structure

```text
urbanprofit_dashboard_upgrade/
├── .streamlit/
│   └── config.toml                              # Light theme & server settings
├── dashboard/
│   └── app.py                                   # Main Streamlit web application
├── data/
│   ├── backup_bengaluru/                        # Backup of original 8-locality Bengaluru CSVs
│   ├── raw/
│   │   └── osm_other_cities_raw.csv             # Real-world OSM extracts (55 localities)
│   ├── processed/
│   │   ├── urbanprofit_market_dataset_final.csv # Master dataset (63 localities × 35 cols)
│   │   ├── urbanprofit_market_scores.csv        # Scored dataset without cluster labels
│   │   └── urbanprofit_locality_clusters.csv    # Scored dataset with K-Means cluster IDs
│   └── urbanprofit_locality_clusters_filled.csv # Enriched Bengaluru source file
├── src/
│   ├── extract_city_data.py                     # OpenStreetMap Overpass API data extractor
│   └── build_multicity_dataset.py               # Data merger, MCDA scorer & K-Means clustering
├── README.md
└── requirements.txt
```

---

## Covered Cities & Localities

| City | Localities Included |
| :--- | :--- |
| **Bengaluru, Karnataka** (8) | Electronic City, HSR Layout, Indiranagar, Jayanagar, Koramangala, Malleshwaram, Marathahalli, Whitefield |
| **Mumbai, Maharashtra** (5) | Andheri West, Bandra West, Powai, Lower Parel, Malad West |
| **Delhi, Delhi** (5) | Connaught Place, Saket, Hauz Khas, Dwarka Sector 12, Lajpat Nagar |
| **Hyderabad, Telangana** (5) | HITEC City, Gachibowli, Banjara Hills, Jubilee Hills, Kukatpally |
| **Chennai, Tamil Nadu** (5) | T. Nagar, Anna Nagar, Adyar, Velachery, OMR Sholinganallur |
| **Pune, Maharashtra** (5) | Koregaon Park, Hinjawadi, Kothrud, Viman Nagar, Baner |
| **Kolkata, West Bengal** (5) | Salt Lake Sector V, Park Street, New Town, Ballygunge, Behala |
| **Ahmedabad, Gujarat** (5) | Navrangpura, SG Highway Bodakdev, Prahlad Nagar, Maninagar, Bopal |
| **Jaipur, Rajasthan** (5) | Malviya Nagar, Vaishali Nagar, C-Scheme, Mansarovar, Raja Park |
| **Kochi, Kerala** (5) | Edappally, Kakkanad, MG Road Ernakulam, Kalamassery, Vyttila |
| **Lucknow, Uttar Pradesh** (5) | Gomti Nagar, Hazratganj, Alambagh, Indira Nagar Lucknow, Aliganj |
| **Indore, Madhya Pradesh** (5) | Vijay Nagar, Palasia, Bhawarkua, Rajwada, AB Road Rau |

---

## Installation & Execution (Windows PowerShell)

1. **Navigate to the project root and activate your virtual environment:**
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **(Optional) Refresh or rebuild the multi-city dataset:**
   ```powershell
   python src\extract_city_data.py
   python src\build_multicity_dataset.py
   ```

4. **Launch the Streamlit dashboard:**
   ```powershell
   streamlit run dashboard\app.py
   ```
   Open **`http://localhost:8501`** in your browser.

---

## Methodology Notes & Disclaimer
- **Data Sources:** Population figures use 2025 3 km-radius projections (`WorldPop Global2 R2025A, 100 m`, DOI `10.5258/SOTON/WP00839`); competitor counts, road networks, and metro distances are extracted from **OpenStreetMap**; commercial rent values reflect benchmark retail lease listings (`INR/sq.ft./month`).
- **Analytical Scope:** Market Potential Scores and Business Opportunity Explorer outputs are **relative analytical screening indicators**, not guaranteed forecasts of business revenue or profitability.