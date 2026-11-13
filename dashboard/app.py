
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    ROOT / "data" / "processed"
    / "urbanprofit_locality_clusters.csv"
)

st.set_page_config(
    page_title="UrbanProfit | Market Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CUSTOM CSS
# ==========================================

st.markdown("""
<style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #183153;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 19px;
        color: #52647a;
        margin-top: 5px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        color: #183153;
        margin-top: 25px;
    }

    .info-text {
        color: #64748b;
        font-size: 13px;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 16px;
        border-radius: 12px;
    }

    .footer {
        text-align: center;
        color: #64748b;
        padding: 20px;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LOAD DATA
# ==========================================

@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    data = pd.read_csv(DATA_FILE)

    required_columns = [
        "locality",
        "population_density",
        "commercial_rent_per_sqft",
        "rent_listing_count",
        "road_density_km_per_sq_km",
        "total_mapped_businesses",
        "market_potential_score",
        "market_rank",
        "potential_category",
        "cluster"
    ]

    missing = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing dataset columns: {missing}"
        )

    return data

try:
    df = load_data()
except Exception as error:
    st.error(f"Unable to load project dataset: {error}")
    st.stop()

# ==========================================
# 4. SIDEBAR FILTERS
# ==========================================

st.sidebar.title("📊 UrbanProfit")
st.sidebar.caption("Market Analysis Dashboard")
st.sidebar.divider()

st.sidebar.subheader("Dashboard Filters")

all_localities = sorted(df["locality"].dropna().unique())

selected_localities = st.sidebar.multiselect(
    "Select Localities",
    options=all_localities,
    default=all_localities,
    help="Select one or more localities to compare."
)

st.sidebar.divider()

st.sidebar.subheader("Project Information")
st.sidebar.write("**Study Area:** Bengaluru, Karnataka")
st.sidebar.write("**Localities:** 8")
st.sidebar.write("**ML Algorithm:** K-Means")
st.sidebar.write("**Scoring:** Weighted Index")

st.sidebar.divider()

st.sidebar.caption(
    "UrbanProfit | MCA Data Analytics Project"
)

# ==========================================
# 5. FILTER DATA
# ==========================================

filtered = df[
    df["locality"].isin(selected_localities)
].copy()

if filtered.empty:
    st.warning(
        "Please select at least one locality "
        "from the sidebar."
    )
    st.stop()

# ==========================================
# 6. HEADER
# ==========================================

st.markdown(
    '<p class="main-title">UrbanProfit</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">'
    'Market Potential Prediction & Visualization'
    '</p>',
    unsafe_allow_html=True
)

st.caption(
    "An analytical platform for comparing "
    "commercial market potential across Bengaluru localities."
)

st.divider()

# ==========================================
# 7. KPI METRICS
# ==========================================

best_locality = filtered.loc[
    filtered["market_potential_score"].idxmax()
]

average_score = filtered[
    "market_potential_score"
].mean()

average_population = filtered[
    "population_density"
].mean()

total_businesses = filtered[
    "total_mapped_businesses"
].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Localities Analyzed",
    len(filtered)
)

c2.metric(
    "Highest Potential",
    best_locality["locality"]
)

c3.metric(
    "Average Market Score",
    f"{average_score:.2f}/100"
)

c4.metric(
    "Total Mapped Businesses",
    f"{total_businesses:,.0f}"
)

st.divider()

# ==========================================
# 8. MARKET POTENTIAL RANKING
# ==========================================

st.markdown(
    '<p class="section-title">'
    'Market Potential Ranking'
    '</p>',
    unsafe_allow_html=True
)

ranking = filtered.sort_values(
    "market_potential_score",
    ascending=True
)

fig1 = px.bar(
    ranking,
    x="market_potential_score",
    y="locality",
    orientation="h",
    color="potential_category",
    text="market_potential_score",
    color_discrete_map={
        "High Potential": "#16a34a",
        "Moderate Potential": "#f59e0b",
        "Low Potential": "#dc2626"
    },
    labels={
        "market_potential_score": "Market Potential Score",
        "locality": "Locality",
        "potential_category": "Potential Category"
    },
    title="Locality-wise Market Potential Score"
)

fig1.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig1.update_layout(
    xaxis=dict(range=[0, 110]),
    height=480,
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(
    fig1,
    width="stretch"
)

# ==========================================
# 9. RENT AND POPULATION COMPARISON
# ==========================================

st.markdown(
    '<p class="section-title">'
    'Market Indicator Comparison'
    '</p>',
    unsafe_allow_html=True
)

left, right = st.columns(2)

with left:
    st.subheader("Commercial Rent Comparison")

    fig2 = px.bar(
        filtered.sort_values(
            "commercial_rent_per_sqft",
            ascending=False
        ),
        x="locality",
        y="commercial_rent_per_sqft",
        text="commercial_rent_per_sqft",
        color="commercial_rent_per_sqft",
        color_continuous_scale="Blues",
        labels={
            "locality": "Locality",
            "commercial_rent_per_sqft":
                "Median Asking Rent (₹/sq.ft./month)"
        }
    )

    fig2.update_traces(
        texttemplate="₹%{text:.2f}",
        textposition="outside"
    )

    fig2.update_layout(
        height=420,
        showlegend=False
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

    st.caption(
        "Rent figures are preliminary online asking-rent "
        "observations. Sample counts vary by locality."
    )

with right:
    st.subheader("Population vs Competition")

    fig3 = px.scatter(
        filtered,
        x="population_density",
        y="total_mapped_businesses",
        color="potential_category",
        size="market_potential_score",
        hover_name="locality",
        color_discrete_map={
            "High Potential": "#16a34a",
            "Moderate Potential": "#f59e0b",
            "Low Potential": "#dc2626"
        },
        labels={
            "population_density":
                "Population Density (people/km²)",
            "total_mapped_businesses":
                "Mapped Businesses",
            "potential_category":
                "Potential Category"
        }
    )

    fig3.update_layout(height=420)

    st.plotly_chart(
        fig3,
        width="stretch"
    )

# ==========================================
# 10. ROAD ACCESSIBILITY ANALYSIS
# ==========================================

st.markdown(
    '<p class="section-title">'
    'Road Network Accessibility'
    '</p>',
    unsafe_allow_html=True
)

fig_road = px.bar(
    filtered.sort_values(
        "road_density_km_per_sq_km",
        ascending=False
    ),
    x="locality",
    y="road_density_km_per_sq_km",
    text="road_density_km_per_sq_km",
    color="road_density_km_per_sq_km",
    color_continuous_scale="Teal",
    labels={
        "locality": "Locality",
        "road_density_km_per_sq_km":
            "Road Density (km/km²)"
    }
)

fig_road.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig_road.update_layout(
    height=400,
    showlegend=False
)

st.plotly_chart(
    fig_road,
    width="stretch"
)

st.caption(
    "Road density represents mapped driving-road length "
    "per unit study-area. It is a network-supply proxy, "
    "not actual travel time or traffic conditions."
)

# ==========================================
# 11. K-MEANS CLUSTERING
# ==========================================

st.markdown(
    '<p class="section-title">'
    'K-Means Locality Clustering'
    '</p>',
    unsafe_allow_html=True
)

fig4 = px.scatter(
    filtered,
    x="population_density",
    y="commercial_rent_per_sqft",
    color=filtered["cluster"].astype(str),
    text="locality",
    hover_name="locality",
    size="total_mapped_businesses",
    color_discrete_sequence=px.colors.qualitative.Set1,
    labels={
        "cluster": "Cluster",
        "population_density":
            "Population Density (people/km²)",
        "commercial_rent_per_sqft":
            "Rent (₹/sq.ft./month)"
    },
    title="Locality Groups Based on Market Characteristics"
)

fig4.update_traces(
    textposition="top center"
)

fig4.update_layout(
    height=520,
    legend_title_text="Cluster"
)

st.plotly_chart(
    fig4,
    width="stretch"
)

st.caption(
    "K-Means cluster labels (0, 1 and 2) are group identifiers, "
    "not potential rankings."
)

# ==========================================
# 12. LOCALITY ANALYSIS TABLE
# ==========================================

st.markdown(
    '<p class="section-title">'
    'Locality Analysis Table'
    '</p>',
    unsafe_allow_html=True
)

display_columns = {
    "locality": "Locality",
    "population_density": "Population Density",
    "commercial_rent_per_sqft":
        "Median Rent (₹/sq.ft.)",
    "rent_listing_count": "Rent Samples",
    "road_density_km_per_sq_km": "Road Density",
    "total_mapped_businesses": "Mapped Businesses",
    "market_potential_score": "Market Score",
    "market_rank": "Rank",
    "potential_category": "Potential Category",
    "cluster": "Cluster"
}

table = filtered[
    list(display_columns.keys())
].copy()

table = table.rename(
    columns=display_columns
)

table = table.sort_values("Rank")

st.dataframe(
    table,
    width="stretch",
    hide_index=True
)

# ==========================================
# 13. TOP LOCALITY RECOMMENDATION
# ==========================================

st.markdown(
    '<p class="section-title">'
    'Top Locality Recommendation'
    '</p>',
    unsafe_allow_html=True
)

top = filtered.sort_values(
    "market_potential_score",
    ascending=False
).iloc[0]

st.success(
    f"Among the selected localities, {top['locality']} "
    f"has the highest analytical market-potential score: "
    f"{top['market_potential_score']:.2f}/100."
)

st.write(
    "This ranking reflects the selected weighted indicators. "
    "It should be considered alongside business category, "
    "actual customer demand, rental costs and local market research."
)

# ==========================================
# 14. CSV DOWNLOAD
# ==========================================

st.markdown(
    '<p class="section-title">'
    'Download Analysis'
    '</p>',
    unsafe_allow_html=True
)

csv_data = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Locality Analysis CSV",
    data=csv_data,
    file_name="urbanprofit_locality_analysis.csv",
    mime="text/csv",
    width="stretch"
)

# ==========================================
# 15. PROJECT METHODOLOGY
# ==========================================

with st.expander("View Project Methodology"):

    st.markdown("""
    ### UrbanProfit Methodology

    **1. Data Collection**
    - OpenStreetMap business information.
    - WorldPop population estimates.
    - Commercial property asking-rent observations.
    - OpenStreetMap driving-road network.

    **2. Data Preprocessing**
    - Missing-value inspection.
    - Duplicate checks.
    - Numeric conversion.
    - Feature engineering.
    - Dataset integration.

    **3. Exploratory Data Analysis**
    - Business category distribution.
    - Locality distribution.
    - Competition comparison.
    - Geographical analysis.

    **4. Weighted Market Potential Index**

    | Indicator | Weight |
    |---|---:|
    | Population Density | 30% |
    | Road Density | 25% |
    | Rent Affordability | 20% |
    | Competition | 25% |

    **5. Machine Learning**
    - K-Means clustering.
    - StandardScaler normalization.
    - Three exploratory clusters.

    **6. Visualization**
    - Streamlit.
    - Plotly.
    - Pandas.
    """)

# ==========================================
# 16. LIMITATIONS
# ==========================================

with st.expander("Data Sources, Assumptions and Limitations"):

    st.markdown("""
    - The analysis covers eight selected Bengaluru study areas.
    - Population values are WorldPop modelled 2025 estimates
      for approximate 3 km-radius circles, not official
      locality census counts.
    - OSM business records represent mapped businesses,
      not complete ground-truth competitor inventories.
    - Rent observations are preliminary online asking-rent
      samples, with different sample sizes across localities.
    - Road density measures mapped network supply, not
      congestion, actual journey time or public transport access.
    - Metro distance is not included because it has not
      yet been collected.
    - The market score is a weighted analytical index,
      not a probability of business success.
    - K-Means results are exploratory and based on only
      eight locality observations.
    """)

# ==========================================
# 17. FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div class="footer">
        <b>UrbanProfit</b><br>
        Market Potential Prediction & Visualization<br>
        MCA | Data Analytics Project<br>
        Bengaluru, Karnataka, India
    </div>
    """,
    unsafe_allow_html=True
)
