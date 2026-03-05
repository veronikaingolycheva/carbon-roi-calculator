"""
CarbonROI — app.py
==================
Streamlit web application for Smart City Infrastructure ROI Calculator.

Run:
    streamlit run app.py
"""

import io
import math
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CarbonROI — Smart City Calculator",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
}

/* Dark background */
.stApp {
    background-color: #050c1a;
    color: #cbd5e1;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0a0f1e;
    border-right: 1px solid #0f172a;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #0a0f1e;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: #475569 !important; font-size: 11px; letter-spacing: 2px; }
[data-testid="stMetricValue"] { color: #10b981 !important; font-family: 'Syne', sans-serif; font-size: 28px; }
[data-testid="stMetricDelta"] { color: #06b6d4 !important; }

/* Headings */
h1 { font-family: 'Syne', sans-serif !important; font-weight: 900 !important; color: #f1f5f9 !important; }
h2 { font-family: 'Syne', sans-serif !important; font-weight: 700 !important; color: #e2e8f0 !important; font-size: 18px !important; }
h3 { color: #94a3b8 !important; font-size: 13px !important; letter-spacing: 2px !important; text-transform: uppercase !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #1e293b; border-radius: 8px; }

/* Buttons */
.stDownloadButton button {
    background-color: #10b981 !important;
    color: #000012 !important;
    border: none !important;
    font-family: 'DM Mono', monospace !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}
.stDownloadButton button:hover {
    background-color: #0d9488 !important;
}

/* Select / slider labels */
label { color: #64748b !important; font-size: 11px !important; letter-spacing: 1px !important; }

/* Divider */
hr { border-color: #0f172a !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] { background-color: #0a0f1e; border-bottom: 1px solid #1e293b; }
.stTabs [data-baseweb="tab"] { color: #475569; font-family: 'DM Mono', monospace; font-size: 12px; }
.stTabs [aria-selected="true"] { color: #10b981 !important; border-bottom: 2px solid #10b981 !important; }
</style>
""", unsafe_allow_html=True)


# ── DATA ─────────────────────────────────────────────────────────────────────

MATERIALS_DATA = {
    "steel":    {"name": "Powder Coated Steel",    "cost": 1258, "install": 150, "lifespan": 10, "maint": 80,  "co2": 125},
    "hdpe":     {"name": "Recycled Plastic (HDPE)","cost": 992,  "install": 100, "lifespan": 20, "maint": 20,  "co2": 45},
    "aluminum": {"name": "Aluminum",               "cost": 730,  "install": 100, "lifespan": 20, "maint": 25,  "co2": 85},
}

CF_DATA = {"name": "Carbon Fiber (CFRP)", "install": 100, "lifespan": 30, "maint": 10, "co2": 30}

CITIES_DATA = [
    {"name": "New York",        "state": "NY", "pop": 8_336_817, "climate": "Humid Continental",    "mult": 0.75, "per1k": 4},
    {"name": "Los Angeles",     "state": "CA", "pop": 3_979_576, "climate": "Mediterranean",        "mult": 0.95, "per1k": 4},
    {"name": "Chicago",         "state": "IL", "pop": 2_696_555, "climate": "Continental/Harsh",    "mult": 0.70, "per1k": 4},
    {"name": "Houston",         "state": "TX", "pop": 2_304_580, "climate": "Humid Subtropical",    "mult": 0.75, "per1k": 4},
    {"name": "Phoenix",         "state": "AZ", "pop": 1_608_139, "climate": "Desert/Hot",           "mult": 0.90, "per1k": 3},
    {"name": "San Francisco",   "state": "CA", "pop": 873_965,   "climate": "Mild/Coastal",         "mult": 0.85, "per1k": 5},
    {"name": "Seattle",         "state": "WA", "pop": 749_256,   "climate": "Temperate/Wet",        "mult": 0.80, "per1k": 5},
    {"name": "Washington",      "state": "DC", "pop": 689_545,   "climate": "Humid Subtropical",    "mult": 0.80, "per1k": 5},
    {"name": "Miami",           "state": "FL", "pop": 442_241,   "climate": "Subtropical/Humid",    "mult": 0.72, "per1k": 6},
    {"name": "Fort Lauderdale", "state": "FL", "pop": 182_437,   "climate": "Subtropical/Coastal",  "mult": 0.70, "per1k": 6},
]

COLORS = {
    "savings":  "#10b981",
    "trad":     "#64748b",
    "cf":       "#10b981",
    "co2":      "#06b6d4",
    "waste":    "#8b5cf6",
    "accent":   "#f59e0b",
    "bg":       "#050c1a",
    "surface":  "#0a0f1e",
    "border":   "#1e293b",
}


# ── CALCULATIONS ─────────────────────────────────────────────────────────────

def tco(cost, install, lifespan, maint, qty, years, mult):
    life_adj     = max(1, math.floor(lifespan * mult))
    replacements = math.floor(years / life_adj)
    capex        = (cost + install) * (replacements + 1) * qty
    opex         = maint * years * qty
    return {"total": capex + opex, "capex": capex, "opex": opex,
            "replacements": replacements, "life_adj": life_adj}


def find_break_even(trad_mat, cf_cost, qty, mult, max_yr=50):
    for y in range(1, max_yr + 1):
        t = tco(trad_mat["cost"], trad_mat["install"], trad_mat["lifespan"],
                trad_mat["maint"], qty, y, mult)
        c = tco(cf_cost, CF_DATA["install"], CF_DATA["lifespan"],
                CF_DATA["maint"], qty, y, mult)
        if c["total"] < t["total"]:
            return y
    return None


def calc_city(city, trad_mat, cf_cost, years):
    qty  = round(city["pop"] * city["per1k"] / 1000)
    mult = city["mult"]
    t    = tco(trad_mat["cost"], trad_mat["install"], trad_mat["lifespan"],
               trad_mat["maint"], qty, years, mult)
    c    = tco(cf_cost, CF_DATA["install"], CF_DATA["lifespan"],
               CF_DATA["maint"], qty, years, mult)

    savings         = t["total"] - c["total"]
    replacements_saved = max(0, t["replacements"] - c["replacements"])
    waste_kg        = replacements_saved * qty * 68
    co2_tons        = waste_kg * 0.30 * 1.85 / 1000

    return {
        "City":               city["name"],
        "State":              city["state"],
        "Population":         city["pop"],
        "Benches":            qty,
        "Climate":            city["climate"],
        "Mult":               mult,
        "Traditional TCO":    round(t["total"]),
        "CF TCO":             round(c["total"]),
        "Net Savings":        round(savings),
        "Savings %":          round(savings / t["total"] * 100, 1) if t["total"] else 0,
        "Break-Even Year":    find_break_even(trad_mat, cf_cost, qty, mult),
        "CO₂ Avoided (t)":   round(co2_tons, 1),
        "Waste Prevented (t)": round(waste_kg / 1000, 1),
        "Cars Off Road":      round(co2_tons / 4.6),
    }


def yearly_cashflow(city, trad_mat, cf_cost, years):
    qty  = round(city["pop"] * city["per1k"] / 1000)
    mult = city["mult"]
    rows = []
    for y in range(1, years + 1):
        t = tco(trad_mat["cost"], trad_mat["install"], trad_mat["lifespan"],
                trad_mat["maint"], qty, y, mult)
        c = tco(cf_cost, CF_DATA["install"], CF_DATA["lifespan"],
                CF_DATA["maint"], qty, y, mult)
        rows.append({"Year": y,
                     "Traditional": t["total"],
                     "Carbon Fiber": c["total"],
                     "Savings": t["total"] - c["total"]})
    return pd.DataFrame(rows)


# ── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🏙️ CARBONROI")
    st.markdown("*Smart City Infrastructure Calculator*")
    st.divider()

    st.markdown("### PARAMETERS")

    trad_key = st.selectbox(
        "TRADITIONAL MATERIAL",
        options=list(MATERIALS_DATA.keys()),
        format_func=lambda k: MATERIALS_DATA[k]["name"],
    )
    trad_mat = MATERIALS_DATA[trad_key]

    cf_price = st.slider(
        "CARBON FIBER UNIT PRICE ($)",
        min_value=800, max_value=3000, value=1200, step=50,
    )

    years = st.slider(
        "ANALYSIS HORIZON (YEARS)",
        min_value=10, max_value=50, value=30, step=5,
    )

    st.divider()
    st.markdown("### CITIES")
    all_city_names = [c["name"] for c in CITIES_DATA]
    selected_names = st.multiselect(
        "SELECT CITIES",
        options=all_city_names,
        default=all_city_names,
    )

    st.divider()
    st.caption(f"Data verified: Feb 2026")
    st.caption(f"Sources: Grainger, ParkWarehouse, NOAA")


# ── COMPUTE ───────────────────────────────────────────────────────────────────

selected_cities = [c for c in CITIES_DATA if c["name"] in selected_names]

if not selected_cities:
    st.warning("Please select at least one city from the sidebar.")
    st.stop()

rows = [calc_city(c, trad_mat, cf_price, years) for c in selected_cities]
df   = pd.DataFrame(rows).sort_values("Net Savings", ascending=False).reset_index(drop=True)

total_savings   = df["Net Savings"].sum()
total_co2       = df["CO₂ Avoided (t)"].sum()
total_waste     = df["Waste Prevented (t)"].sum()
total_cars      = df["Cars Off Road"].sum()
avg_break_even  = df["Break-Even Year"].median()


# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown("""
<h1 style='font-size:32px; letter-spacing:-1px; margin-bottom:4px;'>
    🏙️ CarbonROI
</h1>
<p style='color:#475569; font-family:DM Mono,monospace; font-size:13px; margin-top:0;'>
    Smart City Infrastructure ROI Calculator &nbsp;·&nbsp;
    Carbon Fiber vs Traditional Materials &nbsp;·&nbsp;
    30-Year Analysis
</p>
""", unsafe_allow_html=True)

st.divider()

# ── TOP METRICS ───────────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("TOTAL NET SAVINGS",
              f"${total_savings/1e6:.1f}M",
              f"{len(selected_cities)} cities · {years}yr")
with c2:
    st.metric("CO₂ AVOIDED",
              f"{total_co2:,.0f}t",
              "metric tons")
with c3:
    st.metric("WASTE PREVENTED",
              f"{total_waste:,.0f}t",
              "tons of material")
with c4:
    st.metric("CARS OFF ROAD",
              f"{total_cars:,}",
              "1-year equivalent")

st.divider()

# ── TABS ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["📊  Dashboard", "🏙️  City Detail", "📥  Export"])


# ─── TAB 1: DASHBOARD ────────────────────────────────────────────────────────
with tab1:

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### SAVINGS BY CITY")

        fig_bar = px.bar(
            df.sort_values("Net Savings"),
            x="Net Savings",
            y="City",
            orientation="h",
            color="Net Savings",
            color_continuous_scale=[[0, "#0f4c35"], [1, "#10b981"]],
            text=df.sort_values("Net Savings")["Net Savings"].apply(
                lambda v: f"${v/1e6:.1f}M"),
            hover_data={"Savings %": True, "Break-Even Year": True},
        )
        fig_bar.update_layout(
            paper_bgcolor="#0a0f1e", plot_bgcolor="#0a0f1e",
            font_color="#94a3b8", font_family="DM Mono",
            coloraxis_showscale=False,
            xaxis=dict(showgrid=False, zeroline=False, tickfont_color="#334155",
                       title=None, tickprefix="$", ticksuffix=""),
            yaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8", size=12), title=None),
            margin=dict(l=0, r=20, t=10, b=10),
            height=360,
        )
        fig_bar.update_traces(textposition="outside", textfont_color="#10b981",
                              marker_line_width=0)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown("### CLIMATE IMPACT RANKING")

        fig_env = go.Figure()
        df_env  = df.sort_values("CO₂ Avoided (t)", ascending=False).head(8)

        fig_env.add_trace(go.Bar(
            x=df_env["CO₂ Avoided (t)"],
            y=df_env["City"],
            orientation="h",
            marker_color=COLORS["co2"],
            name="CO₂ Avoided",
            opacity=0.85,
        ))
        fig_env.update_layout(
            paper_bgcolor="#0a0f1e", plot_bgcolor="#0a0f1e",
            font_color="#94a3b8", font_family="DM Mono",
            xaxis=dict(showgrid=False, zeroline=False, tickfont_color="#334155",
                       title="metric tons CO₂"),
            yaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8", size=12), title=None),
            margin=dict(l=0, r=20, t=10, b=10),
            height=360,
            showlegend=False,
        )
        st.plotly_chart(fig_env, use_container_width=True)

    # Summary table
    st.markdown("### FULL COMPARISON TABLE")
    display_df = df[[
        "City", "State", "Benches", "Traditional TCO", "CF TCO",
        "Net Savings", "Savings %", "Break-Even Year", "CO₂ Avoided (t)"
    ]].copy()

    # Format dollar columns
    for col in ["Traditional TCO", "CF TCO", "Net Savings"]:
        display_df[col] = display_df[col].apply(lambda v: f"${v:,.0f}")
    display_df["Savings %"] = display_df["Savings %"].apply(lambda v: f"{v:.1f}%")
    display_df["Break-Even Year"] = display_df["Break-Even Year"].apply(
        lambda v: f"Year {int(v)}" if v else "N/A")

    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ─── TAB 2: CITY DETAIL ──────────────────────────────────────────────────────
with tab2:

    selected_city_name = st.selectbox(
        "SELECT CITY",
        options=[c["name"] for c in selected_cities],
    )

    city_data   = next(c for c in selected_cities if c["name"] == selected_city_name)
    city_row    = df[df["City"] == selected_city_name].iloc[0]
    cashflow_df = yearly_cashflow(city_data, trad_mat, cf_price, years)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("NET SAVINGS",
                  f"${city_row['Net Savings']/1e6:.1f}M",
                  f"{city_row['Savings %']}% reduction")
    with col2:
        be = city_row["Break-Even Year"]
        st.metric("BREAK-EVEN", f"Year {int(be)}" if be else "N/A",
                  f"{years-int(be) if be else 0} yrs of pure savings")
    with col3:
        st.metric("CO₂ AVOIDED",
                  f"{city_row['CO₂ Avoided (t)']:.0f}t",
                  f"{city_row['Cars Off Road']:,} cars off road")

    st.markdown("### CUMULATIVE COST OVER TIME")

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=cashflow_df["Year"], y=cashflow_df["Traditional"],
        mode="lines", name=trad_mat["name"],
        line=dict(color=COLORS["trad"], width=2, dash="dash"),
        fill="none",
    ))
    fig_line.add_trace(go.Scatter(
        x=cashflow_df["Year"], y=cashflow_df["Carbon Fiber"],
        mode="lines", name="Carbon Fiber",
        line=dict(color=COLORS["cf"], width=3),
        fill="tonexty",
        fillcolor="rgba(16,185,129,0.08)",
    ))

    # Break-even marker
    be_yr = city_row["Break-Even Year"]
    if be_yr:
        be_val = cashflow_df[cashflow_df["Year"] == int(be_yr)]["Carbon Fiber"].values
        if len(be_val):
            fig_line.add_trace(go.Scatter(
                x=[int(be_yr)], y=[be_val[0]],
                mode="markers+text",
                marker=dict(color=COLORS["accent"], size=10, symbol="star"),
                text=["Break-even"], textposition="top right",
                textfont=dict(color=COLORS["accent"], size=11),
                name="Break-even",
                showlegend=False,
            ))

    fig_line.update_layout(
        paper_bgcolor="#0a0f1e", plot_bgcolor="#0a0f1e",
        font_color="#94a3b8", font_family="DM Mono",
        xaxis=dict(title="Year", showgrid=False, tickfont_color="#334155"),
        yaxis=dict(title="Cumulative Cost ($)", showgrid=True,
                   gridcolor="#0f172a", tickprefix="$", tickfont_color="#334155"),
        legend=dict(bgcolor="#0a0f1e", bordercolor="#1e293b", borderwidth=1),
        margin=dict(l=20, r=20, t=20, b=20),
        height=380,
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # City profile
    st.markdown("### CITY PROFILE")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
| Parameter | Value |
|---|---|
| Population | {city_data['pop']:,} |
| Benches analyzed | {city_row['Benches']:,} |
| Climate zone | {city_data['climate']} |
| Climate multiplier | {city_data['mult']}x |
| CF lifespan (adjusted) | {math.floor(30 * city_data['mult'])} years |
| Trad. lifespan (adjusted) | {math.floor(trad_mat['lifespan'] * city_data['mult'])} years |
        """)
    with col_b:
        st.markdown(f"""
| Metric | Value |
|---|---|
| Traditional TCO ({years}yr) | ${city_row['Traditional TCO']:,.0f} |
| Carbon Fiber TCO ({years}yr) | ${city_row['CF TCO']:,.0f} |
| Net savings | ${city_row['Net Savings']:,.0f} |
| Waste prevented | {city_row['Waste Prevented (t)']:.0f} tons |
| Trees equivalent | {round(city_row['CO₂ Avoided (t)'] * 45):,} |
        """)


# ─── TAB 3: EXPORT ───────────────────────────────────────────────────────────
with tab3:
    st.markdown("### DOWNLOAD RESULTS")

    col_e1, col_e2, col_e3 = st.columns(3)

    # Summary CSV
    csv_bytes = df.to_csv(index=False).encode()
    with col_e1:
        st.markdown("**📊 Summary CSV**")
        st.caption(f"{len(df)} cities · all KPIs · open in Excel")
        st.download_button(
            "↓ Download Summary CSV",
            data=csv_bytes,
            file_name=f"CarbonROI_Summary_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Yearly CSV
    all_yearly = pd.concat([
        yearly_cashflow(c, trad_mat, cf_price, years).assign(City=c["name"])
        for c in selected_cities
    ], ignore_index=True)
    yearly_csv = all_yearly.to_csv(index=False).encode()
    with col_e2:
        st.markdown("**📈 Yearly Cashflow CSV**")
        st.caption(f"{len(all_yearly)} rows · year-by-year · all cities")
        st.download_button(
            "↓ Download Yearly CSV",
            data=yearly_csv,
            file_name=f"CarbonROI_Yearly_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Excel multi-sheet
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Summary", index=False)
        all_yearly.to_excel(writer, sheet_name="Yearly Cashflow", index=False)
        pd.DataFrame([{
            "Generated":         date.today().isoformat(),
            "Traditional Material": trad_mat["name"],
            "CF Price ($)":      cf_price,
            "Analysis Years":    years,
            "Cities":            len(selected_cities),
            "Total Savings ($)": total_savings,
            "CO2 Avoided (t)":   total_co2,
            "Waste Prevented (t)": total_waste,
        }]).to_excel(writer, sheet_name="Parameters", index=False)
    excel_bytes = excel_buf.getvalue()

    with col_e3:
        st.markdown("**📋 Excel Report (.xlsx)**")
        st.caption("3 sheets: Summary · Yearly · Parameters")
        st.download_button(
            "↓ Download Excel",
            data=excel_bytes,
            file_name=f"CarbonROI_Report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.divider()
    st.markdown("### CURRENT PARAMETERS")
    st.json({
        "traditional_material": trad_mat["name"],
        "cf_unit_price_usd":    cf_price,
        "analysis_years":       years,
        "cities_count":         len(selected_cities),
        "cities":               [c["name"] for c in selected_cities],
        "generated":            date.today().isoformat(),
    })


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<p style='color:#1e3a5f; font-size:10px; font-family:DM Mono,monospace; text-align:center;'>
CarbonROI · Data: Grainger.com, ParkWarehouse.com, NOAA, APWA · Verified Feb 2026
</p>
""", unsafe_allow_html=True)
