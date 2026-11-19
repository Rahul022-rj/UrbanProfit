import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime
import html
import io

# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="UrbanProfit | Market Intelligence",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# 2. PROJECT PATHS
# ==========================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "data" / "processed" / "urbanprofit_market_dataset_final.csv"
SCORE_FILE = ROOT / "data" / "processed" / "urbanprofit_market_scores.csv"
CLUSTER_FILE = ROOT / "data" / "processed" / "urbanprofit_locality_clusters.csv"

# ==========================================================
# 3. CUSTOM UI DESIGN
# ==========================================================

st.markdown("""
<style>

/* PROFESSIONAL URBANPROFIT THEME */

.stApp {
    background: #FAF8F7;
    color: #000000;
    font-family: 'Segoe UI', sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Main headings */

h1, h2, h3 {
    color: #000000 !important;
    font-weight: 750 !important;
}

/* Section headings */

.section-heading {
    color: #000000;
    font-size: 24px;
    font-weight: 800;
    margin-top: 30px;
    margin-bottom: 7px;
}

.section-subtitle {
    color: #897B82;
    font-size: 14px;
    margin-bottom: 22px;
}

/* Metric cards */

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #EADFE3;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 5px 18px rgba(23,43,58,0.045);
}

[data-testid="stMetricLabel"] {
    color: #82747B;
}

[data-testid="stMetricValue"] {
    color: #D96C91;
    font-weight: 800;
}

/* Buttons */

.stButton > button,
.stDownloadButton > button {
    background: #D96C91;
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 11px 22px;
    font-weight: 700;
    transition: 0.2s;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #BF527C;
    transform: translateY(-2px);
}

/* Inputs */

[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    border-radius: 10px !important;
    border-color: #EADDE3 !important;
    background: white;
}

/* Expanders */

[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid #EADFE3;
    border-radius: 14px;
}

/* Dataframes */

[data-testid="stDataFrame"] {
    border: 1px solid #EADFE3;
    border-radius: 12px;
}

/* Info messages */

[data-testid="stAlert"] {
    border-radius: 12px;
}

/* UrbanProfit: refined off-white and pink component styling */
.stApp {
    background: #FAF8F7 !important;
    color: #000000 !important;
}
html, body, [class*="css"] {
    color: #000000;
}
[data-testid="stHeader"] {
    background: rgba(250, 248, 247, 0.92);
}
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stTextInput"] label {
    color: #000000 !important;
    font-weight: 600;
}
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
    background: #FFFFFF !important;
    border-color: #EADFE3 !important;
}
/* Selected locality chips in the multiselect */
[data-testid="stMultiSelect"] [data-baseweb="tag"],
[data-testid="stMultiSelect"] [data-baseweb="tag"] > span,
[data-testid="stMultiSelect"] [data-baseweb="tag"] > div {
    background: #FCEAF0 !important;
    color: #000000 !important;
    border: 1px solid #EFC8D6 !important;
    box-shadow: none !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] *,
[data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
    color: #000000 !important;
    fill: #000000 !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] button:hover {
    background: #F7D6E1 !important;
}
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #EADFE3 !important;
    border-radius: 16px !important;
}
[data-testid="stMetricLabel"] p {
    color: #82747B !important;
}
[data-testid="stMetricValue"] {
    color: #C95D83 !important;
}
.stButton > button,
.stDownloadButton > button {
    background: #D96C91 !important;
    color: #FFFFFF !important;
    border: 1px solid #D96C91 !important;
    border-radius: 11px !important;
    font-weight: 700 !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #BF527C !important;
    border-color: #BF527C !important;
    color: #FFFFFF !important;
}
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #EADFE3 !important;
    border-radius: 14px !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid #EADFE3 !important;
    border-radius: 12px !important;
}
[data-testid="stAlert"] {
    border-radius: 12px !important;
}
hr {
    border-color: #EADFE3 !important;
}

/* UrbanProfit multiselect chips: override Streamlit/BaseWeb default orange */
div[data-baseweb="tag"],
span[data-baseweb="tag"],
[data-baseweb="tag"] {
    background: #FCEAF0 !important;
    background-color: #FCEAF0 !important;
    color: #000000 !important;
    border: 1px solid #EFC8D6 !important;
    box-shadow: none !important;
}
div[data-baseweb="tag"] *,
span[data-baseweb="tag"] *,
[data-baseweb="tag"] * {
    background: transparent !important;
    background-color: transparent !important;
    color: #000000 !important;
    fill: #000000 !important;
}
div[data-baseweb="tag"] svg,
span[data-baseweb="tag"] svg,
[data-baseweb="tag"] svg {
    color: #000000 !important;
    fill: #000000 !important;
}
div[data-baseweb="tag"]:hover,
span[data-baseweb="tag"]:hover,
[data-baseweb="tag"]:hover {
    background: #F7D6E1 !important;
    background-color: #F7D6E1 !important;
}
[data-testid="stMultiSelect"] [role="listbox"] [aria-selected="true"] {
    background: #FCEAF0 !important;
    color: #000000 !important;
}

/* ==========================================
   URBANPROFIT - FLOATING BACKGROUND PARTICLES
========================================== */

#particles-bg {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100vh;
    overflow: hidden;
    pointer-events: none;
    z-index: 0;
}

#particles-bg .particle {
    position: absolute;
    top: -10px;
    display: block;
    border-radius: 50%;
    background: rgba(217, 108, 145, 0.35);
    box-shadow: 0 0 10px rgba(217, 108, 145, 0.25);
    animation-name: urbanprofit-float;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}

@keyframes urbanprofit-float {
    0% {
        transform: translateY(-10vh) translateX(0);
        opacity: 0;
    }
    15% {
        opacity: 0.65;
    }
    85% {
        opacity: 0.45;
    }
    100% {
        transform: translateY(110vh) translateX(45px);
        opacity: 0;
    }
}

/* Keep dashboard content above particles */
.block-container {
    position: relative;
    z-index: 1;
}

</style>
""", unsafe_allow_html=True)

# Generate particles
particles = "".join([
    f'''
    <span class="particle"
    style="
    left:{(i * 37) % 100}%;
    width:{3 + (i % 5)}px;
    height:{3 + (i % 5)}px;
    animation-duration:{9 + (i % 10)}s;
    animation-delay:-{(i * 3) % 15}s;">
    </span>
    '''
    for i in range(60)
])

st.html(
    f'<div id="particles-bg">{particles}</div>'
)

# ==========================================================
# 4. LOAD DATASETS
# ==========================================================

@st.cache_data
def load_data():

    if not DATA_FILE.exists():
        return None, "Main market dataset not found."

    market = pd.read_csv(DATA_FILE)
    market.columns = market.columns.str.strip()

    if "locality" not in market.columns:
        return None, "The main dataset must contain locality column."

    if "city" not in market.columns:
        market["city"] = "Bengaluru, Karnataka"

    merge_keys = ["city", "locality"]

    # ----------------------------------------------
    # Load market scores
    # ----------------------------------------------

    if SCORE_FILE.exists():

        scores = pd.read_csv(SCORE_FILE)
        scores.columns = scores.columns.str.strip()

        if "locality" in scores.columns:
            if "city" not in scores.columns:
                scores["city"] = "Bengaluru, Karnataka"

            score_columns = [
                col for col in [
                    "population_score",
                    "rent_affordability_score",
                    "competition_score",
                    "market_potential_score",
                    "market_rank",
                    "potential_category"
                ]
                if col in scores.columns
                and col not in market.columns
            ]

            if score_columns:
                scores_small = scores[
                    merge_keys + score_columns
                ].drop_duplicates(subset=merge_keys)

                market = market.merge(
                    scores_small,
                    on=merge_keys,
                    how="left",
                    validate="one_to_one"
                )

    # ----------------------------------------------
    # Load locality clusters
    # ----------------------------------------------

    if CLUSTER_FILE.exists():

        clusters = pd.read_csv(CLUSTER_FILE)
        clusters.columns = clusters.columns.str.strip()

        if "locality" in clusters.columns and "cluster" in clusters.columns:
            if "city" not in clusters.columns:
                clusters["city"] = "Bengaluru, Karnataka"

            if "cluster" not in market.columns:
                clusters_small = clusters[
                    merge_keys + ["cluster"]
                ].drop_duplicates(subset=merge_keys)

                market = market.merge(
                    clusters_small,
                    on=merge_keys,
                    how="left",
                    validate="one_to_one"
                )

    # ----------------------------------------------
    # Convert numeric columns
    # ----------------------------------------------

    numeric_columns = [
        "population",
        "area_sq_km",
        "population_density",
        "commercial_rent_per_sqft",
        "rent_listing_count",
        "road_density_km_per_sq_km",
        "road_accessibility_score",
        "metro_distance_km",
        "nearest_metro_distance_km",
        "total_mapped_businesses",
        "market_potential_score",
        "market_rank",
        "population_score",
        "rent_affordability_score",
        "competition_score",
        "cluster",
        "competitors_cafe_restaurant",
        "competitors_electronics_store",
        "competitors_gym_fitness_center",
        "competitors_pharmacy",
        "competitors_retail_shop",
        "competitors_salon_beauty_center"
    ]

    for col in numeric_columns:
        if col in market.columns:
            market[col] = pd.to_numeric(
                market[col],
                errors="coerce"
            )

    if "nearest_metro_distance_km" in market.columns:
        if "metro_distance_km" in market.columns:
            market["metro_distance_km"] = market[
                "metro_distance_km"
            ].combine_first(market["nearest_metro_distance_km"])
        else:
            market["metro_distance_km"] = market[
                "nearest_metro_distance_km"
            ]

    market = market.drop_duplicates(
        subset=merge_keys
    ).copy()

    return market, None


try:
    df, data_error = load_data()

except Exception as error:
    st.error(f"Dataset loading error: {error}")
    st.stop()

if df is None:
    st.error(data_error)
    st.info(f"Expected location: {DATA_FILE}")
    st.stop()

if df.empty:
    st.error("Your dataset contains no records.")
    st.stop()

# ==========================================================
# 5. HELPER FUNCTIONS
# ==========================================================

def valid(value):
    try:
        return pd.notna(value) and float(value) >= 0
    except (TypeError, ValueError):
        return False


def number(value, decimals=0):
    if not valid(value):
        return "Not available"
    return f"{float(value):,.{decimals}f}"


def get_category(score):
    if not valid(score):
        return "Score unavailable"
    if score >= 70:
        return "High Potential"
    elif score >= 45:
        return "Moderate Potential"
    return "Low Potential"


def business_recommendations(row):

    ideas = []

    population = row.get("population")
    density = row.get("population_density")
    rent = row.get("commercial_rent_per_sqft")

    cafe_comp = row.get("competitors_cafe_restaurant")
    gym_comp = row.get("competitors_gym_fitness_center")
    pharmacy_comp = row.get("competitors_pharmacy")
    electronics_comp = row.get("competitors_electronics_store")
    retail_comp = row.get("competitors_retail_shop")
    salon_comp = row.get("competitors_salon_beauty_center")

    large_market = valid(population) and population >= 200000
    dense_market = valid(density) and density >= 8000

    # Food and beverage
    if large_market and valid(cafe_comp) and cafe_comp <= 200:
        ideas.append({
            "business": "Restaurant / Café",
            "reason": "Large estimated population with a relatively lower mapped food-business count.",
            "priority": "Worth investigating",
            "icon": "🍽️"
        })

    # Bakery / cloud kitchen
    if large_market and valid(cafe_comp) and cafe_comp <= 300:
        ideas.append({
            "business": "Bakery / Cloud Kitchen",
            "reason": "Explore convenient food delivery, takeaway and bakery demand.",
            "priority": "Worth investigating",
            "icon": "🥐"
        })

    # Fitness
    if dense_market and valid(gym_comp) and gym_comp <= 12:
        ideas.append({
            "business": "Gym / Fitness Studio",
            "reason": "High population density and relatively limited mapped fitness competitors.",
            "priority": "Worth investigating",
            "icon": "💪"
        })

    # Pharmacy
    if large_market and valid(pharmacy_comp) and pharmacy_comp <= 15:
        ideas.append({
            "business": "Pharmacy / Healthcare Retail",
            "reason": "Investigate neighbourhood healthcare retail demand and competition.",
            "priority": "Worth investigating",
            "icon": "💊"
        })

    # Electronics
    if large_market and valid(electronics_comp) and electronics_comp <= 12:
        ideas.append({
            "business": "Electronics Store",
            "reason": "Explore demand for electronics, accessories and repair services.",
            "priority": "Worth investigating",
            "icon": "💻"
        })

    # Retail
    if dense_market and valid(retail_comp) and retail_comp <= 100:
        ideas.append({
            "business": "Specialty Retail Store",
            "reason": "Investigate a focused retail concept for local customers.",
            "priority": "Worth investigating",
            "icon": "🛍️"
        })

    # Salon
    if large_market and valid(salon_comp) and salon_comp <= 20:
        ideas.append({
            "business": "Salon / Beauty Studio",
            "reason": "Explore personal care and grooming services in the locality.",
            "priority": "Worth investigating",
            "icon": "💇"
        })

    # Rent consideration
    if valid(rent):
        if rent >= 150:
            rent_note = (
                "Commercial rent is relatively high. "
                "Evaluate a compact format and break-even costs."
            )
        elif rent <= 70:
            rent_note = (
                "Observed rent is relatively lower. "
                "Evaluate whether demand supports the proposed business."
            )
        else:
            rent_note = (
                "Compare rent with expected monthly revenue "
                "before choosing a business."
            )
    else:
        rent_note = (
            "Rent data is unavailable. Collect current rental "
            "quotes before estimating investment."
        )

    # Nightlife / bar recommendation
    ideas.append({
        "business": "Bar / Pub / Nightlife",
        "reason": (
            "Insufficient nightlife and evening-footfall data. "
            "Validate local demand, licensing and operating costs."
        ),
        "priority": "Further research required",
        "icon": "🌃"
    })

    return ideas, rent_note


# ==========================================================
# 6. CHART DESIGN
# ==========================================================

def style_chart(fig, height=400):

    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Segoe UI",
            color="#574650"
        ),
        margin=dict(
            l=30,
            r=35,
            t=35,
            b=40
        ),
        xaxis=dict(
            gridcolor="#F1E4E8",
            zerolinecolor="#F1E4E8"
        ),
        yaxis=dict(
            gridcolor="#F1E4E8",
            zerolinecolor="#F1E4E8"
        )
    )

    return fig


# ==========================================================
# 7. WELCOME HERO
# ==========================================================

st.html("""
<div style="
    background: linear-gradient(120deg,#FCEAF0,#ffffff,#F7D6E1);
    border: 1px solid #EED3DD;
    border-radius: 25px;
    padding: 55px 50px;
    margin-bottom: 35px;
    box-shadow: 0 12px 40px rgba(180,90,40,0.08);
">

    <div style="
        color:#D96C91;
        font-size:15px;
        font-weight:800;
        letter-spacing:2px;
    ">
        📍 URBANPROFIT
    </div>

    <h1 style="
        font-size:42px;
        color:#000000;
        margin-top:25px;
    ">
        Welcome, entrepreneur! 👋
    </h1>

    <p style="
        color:#7D6C76;
        font-size:17px;
        line-height:1.8;
    ">
        Find promising places for your next business.
        Compare local markets, understand competition,
        discover business opportunities and make
        smarter location decisions across major Indian cities.
    </p>

</div>
""")


# ==========================================================
# 8. CITY AND LOCALITY SELECTION
# ==========================================================

st.markdown(
    '<div class="section-heading">Explore a market</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Choose a city and compare one or more local areas.'
    '</div>',
    unsafe_allow_html=True
)


def reset_localities_for_city_change():
    """Clear locality choices and old analysis whenever the city changes."""
    st.session_state["locality_selector_v2"] = []
    st.session_state.pop("analyzed_localities", None)
    st.session_state.pop("analyzed_city", None)


DEFAULT_CITIES = [
    "Bengaluru, Karnataka",
    "Mumbai, Maharashtra",
    "Delhi, Delhi",
    "Hyderabad, Telangana",
    "Chennai, Tamil Nadu",
    "Pune, Maharashtra",
    "Kolkata, West Bengal",
    "Ahmedabad, Gujarat",
    "Jaipur, Rajasthan",
    "Kochi, Kerala",
    "Lucknow, Uttar Pradesh",
    "Indore, Madhya Pradesh"
]

available_cities_in_data = set(df["city"].dropna().astype(str).unique())
CITY_OPTIONS = DEFAULT_CITIES + sorted(
    c for c in available_cities_in_data if c not in DEFAULT_CITIES
)

col1, col2 = st.columns([1, 2])

with col1:

    selected_city = st.selectbox(
        "Search / select city",
        CITY_OPTIONS,
        index=None,
        placeholder="Select a city",
        key="city_selector_v2",
        on_change=reset_localities_for_city_change
    )

with col2:

    if selected_city in available_cities_in_data:

        city_df = df[df["city"] == selected_city]
        locality_options = sorted(
            city_df["locality"].dropna().astype(str).unique().tolist()
        )

        selected_localities = st.multiselect(
            "Select areas to compare",
            locality_options,
            default=[],
            placeholder="Select some location",
            key="locality_selector_v2"
        )

    elif selected_city is None:

        selected_localities = []

        st.multiselect(
            "Select areas to compare",
            options=[],
            placeholder="Select a city first",
            disabled=True,
            key="locality_selector_waiting"
        )

    else:

        selected_localities = []

        st.info(
            f"Verified locality-level data for {selected_city} "
            "is not available yet. Add a verified dataset "
            "for this city to enable analysis."
        )


# ==========================================================
# 9. ANALYZE AND CLEAR BUTTONS
# ==========================================================

def clear_selection():
    """Reset both selectors and remove any previously displayed analysis."""
    st.session_state["city_selector_v2"] = None
    st.session_state["locality_selector_v2"] = []
    st.session_state.pop("analyzed_localities", None)
    st.session_state.pop("analyzed_city", None)


c1, c2 = st.columns([1, 5])

with c1:

    analyze = st.button(
        "Analyze locations →",
        width="stretch",
        disabled=(
            selected_city not in available_cities_in_data
            or not selected_localities
        )
    )

with c2:

    st.button(
        "Clear selection",
        width="content",
        on_click=clear_selection
    )


if analyze:

    if selected_city not in available_cities_in_data:
        st.warning("This city does not have verified market data yet.")
        st.session_state.pop("analyzed_localities", None)

    elif not selected_localities:
        st.warning("Please select at least one locality.")

    else:
        st.session_state["analyzed_localities"] = selected_localities
        st.session_state["analyzed_city"] = selected_city


# ==========================================================
# 10. DISPLAY ANALYSIS
# ==========================================================

analyzed_city = st.session_state.get("analyzed_city")
analyzed_localities = st.session_state.get("analyzed_localities", [])

selected = (
    analyzed_localities
    if analyzed_city == selected_city
    and selected_city is not None
    and selected_localities
    and set(analyzed_localities) == set(selected_localities)
    else []
)

city = analyzed_city or selected_city or "Bengaluru, Karnataka"


if selected:

    result = df[
        (df["city"] == city) & (df["locality"].isin(selected))
    ].copy()

    if "market_potential_score" in result.columns:
        result = result.sort_values(
            "market_potential_score",
            ascending=False,
            na_position="last"
        )

    st.divider()

    st.markdown(
        '<div class="section-heading">Your market snapshot</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="section-subtitle">'
        f'Analysis for {html.escape(city)}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ======================================================
    # 11. KPI CARDS
    # ======================================================

    avg_population = (
        result["population"].mean()
        if "population" in result.columns
        else float("nan")
    )

    avg_rent = (
        result["commercial_rent_per_sqft"].mean()
        if "commercial_rent_per_sqft" in result.columns
        else float("nan")
    )

    avg_score = (
        result["market_potential_score"].mean()
        if "market_potential_score" in result.columns
        else float("nan")
    )

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Selected locations",
        len(result)
    )

    k2.metric(
        "Average population",
        number(avg_population)
    )

    k3.metric(
        "Average rent / sq.ft.",
        f"₹{number(avg_rent, 2)}"
        if valid(avg_rent)
        else "Not available"
    )

    k4.metric(
        "Average market score",
        f"{number(avg_score, 2)} / 100"
        if valid(avg_score)
        else "Not available"
    )

    # ======================================================
    # 12. MARKET POTENTIAL SCORE CHART
    # ======================================================

    st.markdown(
        '<div class="section-heading">Market potential ranking</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Compare the market potential score of selected areas.'
        '</div>',
        unsafe_allow_html=True
    )

    if (
        "market_potential_score" in result.columns
        and result["market_potential_score"].notna().any()
    ):

        chart_df = result.dropna(
            subset=["market_potential_score"]
        ).sort_values("market_potential_score")

        fig = px.bar(
            chart_df,
            x="market_potential_score",
            y="locality",
            orientation="h",
            text="market_potential_score",
            color="market_potential_score",
            color_continuous_scale=[
                "#FCE1EA",
                "#EFA5BC",
                "#D96C91",
                "#B94D76"
            ],
            range_color=[0, 100],
            hover_data=[
                c for c in [
                    "population",
                    "commercial_rent_per_sqft",
                    "population_density",
                    "market_rank"
                ]
                if c in chart_df.columns
            ]
        )

        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            xaxis_title="Market Potential Score (0–100)",
            yaxis_title="",
            xaxis_range=[0, 110],
            coloraxis_showscale=False
        )

        st.plotly_chart(
            style_chart(
                fig,
                max(350, len(chart_df) * 65)
            ),
            width="stretch"
        )

    else:
        st.warning(
            "Market scores are missing. Check "
            "urbanprofit_market_scores.csv."
        )

    # ======================================================
    # 13. POPULATION VS COMPETITION
    # ======================================================

    st.markdown(
        '<div class="section-heading">Population vs. competition</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Understand estimated population compared with mapped businesses.'
        '</div>',
        unsafe_allow_html=True
    )

    if {
        "population",
        "total_mapped_businesses"
    }.issubset(result.columns):

        scatter_df = result.dropna(
            subset=[
                "population",
                "total_mapped_businesses"
            ]
        )

        if not scatter_df.empty:

            scatter_args = {}

            if "market_potential_score" in scatter_df.columns:
                scatter_args["color"] = "market_potential_score"
                scatter_args["color_continuous_scale"] = [
                    "#FCE1EA",
                    "#EFA5BC",
                    "#D96C91"
                ]

            fig2 = px.scatter(
                scatter_df,
                x="population",
                y="total_mapped_businesses",
                text="locality",
                size="population",
                hover_data=[
                    c for c in [
                        "commercial_rent_per_sqft",
                        "population_density"
                    ]
                    if c in scatter_df.columns
                ],
                **scatter_args
            )

            fig2.update_traces(
                textposition="top center",
                marker=dict(
                    opacity=0.85,
                    line=dict(color="white", width=1)
                )
            )

            fig2.update_layout(
                xaxis_title="Estimated population",
                yaxis_title="Mapped businesses"
            )

            st.plotly_chart(
                style_chart(fig2, 430),
                width="stretch"
            )

    # ======================================================
    # 14. RENT COMPARISON
    # ======================================================

    st.markdown(
        '<div class="section-heading">Commercial rent comparison</div>',
        unsafe_allow_html=True
    )

    if "commercial_rent_per_sqft" in result.columns:

        rent_df = result.dropna(
            subset=["commercial_rent_per_sqft"]
        ).sort_values("commercial_rent_per_sqft")

        if not rent_df.empty:

            fig3 = px.bar(
                rent_df,
                x="locality",
                y="commercial_rent_per_sqft",
                text="commercial_rent_per_sqft",
                color="commercial_rent_per_sqft",
                color_continuous_scale=[
                    "#FCE1EA",
                    "#D96C91",
                    "#B94D76"
                ]
            )

            fig3.update_traces(
                texttemplate="₹%{text:.2f}",
                textposition="outside",
                cliponaxis=False
            )

            fig3.update_layout(
                xaxis_title="Locality",
                yaxis_title="Rent per sq.ft. (INR)",
                coloraxis_showscale=False
            )

            st.plotly_chart(
                style_chart(fig3, 400),
                width="stretch"
            )

        else:
            st.info("Rent data is not available.")

    # ======================================================
    # 15. ROAD DENSITY
    # ======================================================

    st.markdown(
        '<div class="section-heading">Road network density</div>',
        unsafe_allow_html=True
    )

    if "road_density_km_per_sq_km" in result.columns:

        road_df = result.dropna(
            subset=["road_density_km_per_sq_km"]
        )

        if not road_df.empty:

            fig4 = px.bar(
                road_df,
                x="locality",
                y="road_density_km_per_sq_km",
                text="road_density_km_per_sq_km",
                color="road_density_km_per_sq_km",
                color_continuous_scale=[
                    "#FCE1EA",
                    "#EFA5BC",
                    "#C95D83"
                ]
            )

            fig4.update_traces(
                texttemplate="%{text:.2f}",
                textposition="outside",
                cliponaxis=False
            )

            fig4.update_layout(
                xaxis_title="Locality",
                yaxis_title="Road density (km / sq.km.)",
                coloraxis_showscale=False
            )

            st.plotly_chart(
                style_chart(fig4, 400),
                width="stretch"
            )

    # ======================================================
    # 16. SCORE COMPONENTS
    # ======================================================

    component_columns = [
        c for c in [
            "population_score",
            "rent_affordability_score",
            "competition_score"
        ]
        if c in result.columns
    ]

    if component_columns:

        st.markdown(
            '<div class="section-heading">What contributes to the score?</div>',
            unsafe_allow_html=True
        )

        component_df = result[
            ["locality"] + component_columns
        ].melt(
            id_vars="locality",
            var_name="Score component",
            value_name="Score"
        )

        component_df["Score component"] = (
            component_df["Score component"]
            .str.replace("_", " ")
            .str.title()
        )

        fig5 = px.bar(
            component_df,
            x="locality",
            y="Score",
            color="Score component",
            barmode="group",
            text_auto=".1f",
            color_discrete_sequence=[
                "#D96C91",
                "#E9A4B9",
                "#B9A0AD"
            ]
        )

        fig5.update_layout(
            xaxis_title="Locality",
            yaxis_title="Component score (0–100)"
        )

        st.plotly_chart(
            style_chart(fig5, 420),
            width="stretch"
        )

    # ======================================================
    # 17. LOCALITY-WISE DETAILS
    # ======================================================

    st.markdown(
        '<div class="section-heading">Locality insights & competition</div>',
        unsafe_allow_html=True
    )

    for _, row in result.iterrows():

        score = row.get("market_potential_score")

        score_text = (
            f"{float(score):.2f}/100"
            if valid(score)
            else "Score unavailable"
        )

        with st.expander(
            f"📍 {row['locality']}  |  {score_text}  |  "
            f"{get_category(score)}"
        ):

            a, b, c = st.columns(3)

            a.metric(
                "Population",
                number(row.get("population"))
            )

            b.metric(
                "Population density",
                number(row.get("population_density"), 2)
            )

            c.metric(
                "Mapped businesses",
                number(row.get("total_mapped_businesses"))
            )

            d, e, f = st.columns(3)

            rent = row.get("commercial_rent_per_sqft")
            road = row.get("road_density_km_per_sq_km")
            metro = row.get("metro_distance_km")

            d.metric(
                "Rent / sq.ft.",
                f"₹{number(rent, 2)}"
                if valid(rent)
                else "Not available"
            )

            e.metric(
                "Road density",
                number(road, 2)
            )

            f.metric(
                "Metro distance",
                f"{number(metro, 2)} km"
                if valid(metro)
                else "Not within 8 km"
            )

            st.write(
                "**Market category:**",
                get_category(score)
            )

            if valid(row.get("market_rank")):
                st.write(
                    f"**City market rank:** {int(row['market_rank'])}"
                )

            if valid(row.get("cluster")):
                st.write(
                    f"**Cluster:** {int(row['cluster'])}"
                )

            if pd.notna(row.get("nearest_metro_station")):
                st.write(
                    f"**Nearest metro station:** {row['nearest_metro_station']}"
                )

            # Competitor information
            competitor_columns = [
                "competitors_cafe_restaurant",
                "competitors_electronics_store",
                "competitors_gym_fitness_center",
                "competitors_pharmacy",
                "competitors_retail_shop",
                "competitors_salon_beauty_center"
            ]

            competitor_data = []

            for col in competitor_columns:
                if col in row.index and valid(row[col]):
                    competitor_data.append({
                        "Business category": (
                            col.replace("competitors_", "")
                            .replace("_", " ")
                            .title()
                        ),
                        "Mapped competitors": int(row[col])
                    })

            if competitor_data:
                st.write("**Business competition**")
                st.dataframe(
                    pd.DataFrame(competitor_data),
                    hide_index=True,
                    width="stretch"
                )

    # ======================================================
    # BUSINESS OPPORTUNITY RECOMMENDATIONS
    # ======================================================

    st.divider()

    st.subheader("💡 Business Opportunity Explorer")

    st.caption(
        "Explore business categories based on available "
        "population, competition and rental indicators."
    )

    for _, row in result.iterrows():

        ideas, rent_note = business_recommendations(row)

        with st.expander(
            f"📍 Business opportunities in {row['locality']}",
            expanded=True
        ):

            st.markdown(f"### {row['locality']}")

            st.info(rent_note)

            for idea in ideas:

                st.markdown(f"### {idea['icon']} {idea['business']}")

                st.write(idea["reason"])

                if idea["priority"] == "Worth investigating":
                    st.success("Opportunity to investigate")
                else:
                    st.warning("More research required")

            st.caption(
                "These are preliminary screening suggestions, "
                "not guaranteed business-success predictions."
            )

    # ======================================================
    # 18. PROFESSIONAL MARKET COMPARISON TABLE
    # ======================================================

    st.divider()

    st.subheader("📊 Complete Locality Comparison")

    st.caption(
        "Compare all selected locations using available "
        "market, infrastructure and competition indicators."
    )

    display_columns = [
        "city",
        "locality",
        "market_rank",
        "market_potential_score",
        "potential_category",
        "population",
        "population_density",
        "commercial_rent_per_sqft",
        "rent_listing_count",
        "metro_distance_km",
        "nearest_metro_station",
        "total_mapped_businesses",
        "competitors_cafe_restaurant",
        "competitors_electronics_store",
        "competitors_gym_fitness_center",
        "competitors_pharmacy",
        "competitors_retail_shop",
        "competitors_salon_beauty_center",
        "road_segment_count",
        "total_road_length_km",
        "intersection_count",
        "road_density_km_per_sq_km",
        "cluster"
    ]

    display_columns = [
        col for col in display_columns
        if col in result.columns
    ]

    comparison = result[display_columns].copy()

    comparison = comparison.rename(columns={
        "city": "City",
        "locality": "Locality",
        "market_rank": "City Rank",
        "market_potential_score": "Market Score",
        "potential_category": "Market Category",
        "population": "Estimated Population",
        "population_density": "Population Density",
        "commercial_rent_per_sqft": "Rent / Sq.ft. (INR)",
        "rent_listing_count": "Rent Listings",
        "metro_distance_km": "Nearest Metro Distance (km)",
        "nearest_metro_station": "Nearest Metro Station",
        "total_mapped_businesses": "Total Businesses",
        "competitors_cafe_restaurant": "Food Businesses",
        "competitors_electronics_store": "Electronics",
        "competitors_gym_fitness_center": "Fitness Centres",
        "competitors_pharmacy": "Pharmacies",
        "competitors_retail_shop": "Retail Shops",
        "competitors_salon_beauty_center": "Salons",
        "road_segment_count": "Road Segments",
        "total_road_length_km": "Road Length (km)",
        "intersection_count": "Intersections",
        "road_density_km_per_sq_km": "Road Density",
        "cluster": "Market Cluster"
    })

    st.dataframe(
        comparison.round(2),
        hide_index=True,
        width="stretch"
    )

    if (
        "metro_distance_km" in result.columns
        and result["metro_distance_km"].isna().all()
    ):
        st.warning(
            "No operational metro/subway stations were mapped within 8 km "
            "for the selected areas in OpenStreetMap."
        )

    # ======================================================
    # 19. DOWNLOAD CSV REPORT
    # ======================================================

    st.markdown(
        '<div class="section-heading">Download your market report</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Download your selected locality analysis.'
        '</div>',
        unsafe_allow_html=True
    )

    safe_city_slug = city.split(",")[0].strip().replace(" ", "_")

    csv_report = result.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Download CSV report",
        data=csv_report,
        file_name=f"UrbanProfit_{safe_city_slug}_Market_Report.csv",
        mime="text/csv",
        width="stretch"
    )

    # ======================================================
    # 20. DOWNLOAD PDF REPORT
    # ======================================================

    try:

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle
        )
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm

        buffer = io.BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm
        )

        styles = getSampleStyleSheet()

        story = [
            Paragraph(
                "URBANPROFIT - Market Intelligence Report",
                styles["Title"]
            ),
            Paragraph(
                f"City: {html.escape(city)}",
                styles["Normal"]
            ),
            Paragraph(
                f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
                styles["Normal"]
            ),
            Spacer(1, 8 * mm)
        ]

        pdf_columns = [
            ("locality", "Locality"),
            ("market_potential_score", "Score"),
            ("potential_category", "Category"),
            ("population", "Population"),
            ("commercial_rent_per_sqft", "Rent / sq.ft."),
            ("total_mapped_businesses", "Businesses"),
            ("road_density_km_per_sq_km", "Road density")
        ]

        pdf_columns = [
            (col, label)
            for col, label in pdf_columns
            if col in result.columns
        ]

        table_data = [
            [label for col, label in pdf_columns]
        ]

        for _, record in result.iterrows():

            row_values = []

            for col, label in pdf_columns:

                value = record[col]

                if pd.isna(value):
                    row_values.append("Not available")

                elif isinstance(value, (int, float)):
                    row_values.append(f"{value:,.2f}")

                else:
                    row_values.append(str(value))

            table_data.append(row_values)

        report_table = Table(
            table_data,
            repeatRows=1
        )

        report_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D96C91")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E8D5DC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF6F8")]),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
            ])
        )

        story.append(report_table)
        story.append(Spacer(1, 6 * mm))
        story.append(
            Paragraph(
                "Note: Scores are analytical estimates based on "
                "available market indicators. They do not guarantee "
                "business revenue or profitability.",
                styles["Italic"]
            )
        )

        document.build(story)

        pdf_report = buffer.getvalue()

        st.download_button(
            label="📄 Download PDF report",
            data=pdf_report,
            file_name=f"UrbanProfit_{safe_city_slug}_Market_Report.pdf",
            mime="application/pdf",
            width="stretch"
        )

    except ImportError:
        st.info(
            "To enable PDF downloads, install ReportLab using: "
            "python -m pip install reportlab"
        )

    except Exception as error:
        st.warning(f"PDF report could not be generated: {error}")


# ==========================================================
# 21. EMPTY DASHBOARD MESSAGE
# ==========================================================

else:

    st.html("""
<div style="
    background:white;
    border:1px solid #EEDDE4;
    border-radius:18px;
    padding:25px;
    margin-top:20px;
">
    <h3 style="color:#000000;">
        Your market analysis starts here ✨
    </h3>

    <p style="color:#897782;">
        Select any city and one or more localities.
        Click Analyze locations to explore market scores,
        graphs and business opportunities.
    </p>
</div>
""")


# ==========================================================
# 22. FOOTER
# ==========================================================

st.html("""
<div style="
    background:linear-gradient(120deg,#FCEAF0,#ffffff);
    border:1px solid #EEDDE4;
    border-radius:18px;
    padding:30px;
    margin-top:45px;
    text-align:center;
">
    <div style="
        color:#D96C91;
        font-size:19px;
        font-weight:800;
        letter-spacing:2px;
    ">
        📍 URBANPROFIT
    </div>

    <p style="color:#776873;font-size:14px;">
        Market Intelligence Platform
    </p>

    <p style="color:#897782;">
        Helping entrepreneurs make smarter location decisions.
    </p>

    <p style="color:#A99AA2;font-size:12px;">
        MCA Final Year Project · 2026–27
    </p>
</div>
""")