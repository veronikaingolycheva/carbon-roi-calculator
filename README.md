# 🏙️ CarbonROI — Smart City Infrastructure ROI Calculator

> An autonomous AI agent that analyzes the financial and environmental impact of switching from traditional urban furniture to carbon fiber alternatives — across 10 major US cities.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Available-10b981?style=flat-square)](https://your-demo-link.vercel.app)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![Anthropic](https://img.shields.io/badge/Anthropic_API-Claude-orange?style=flat-square)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-slate?style=flat-square)](LICENSE)

---

## 🎯 The Problem

US cities spend **billions replacing park benches, trash cans, and urban furniture** every 5–10 years. Traditional steel and wood degrade fast — especially in coastal and harsh climates. Carbon fiber lasts 30+ years with near-zero maintenance.

**No one had built a tool to quantify this opportunity — until now.**

---

## 💡 The Solution

CarbonROI is an autonomous research agent that:

- 🔍 **Researches current prices** via web search (Grainger, ParkWarehouse — verified Feb 2026)
- 📊 **Calculates 30-year Total Cost of Ownership** with climate-adjusted degradation factors
- 🌱 **Quantifies environmental impact** — CO₂ avoided, waste prevented, landfill space saved
- 📄 **Generates executive reports** written by AI for city planners and procurement officers
- 📥 **Exports everything** — CSV, JSON, Markdown — ready for Excel, Jupyter, or Streamlit

---

## 📊 Key Findings

| City | Traditional TCO (30yr) | Carbon Fiber TCO | Net Savings | Break-Even |
|------|------------------------|------------------|-------------|------------|
| New York, NY | ~$180M | ~$95M | **~$85M** | Year 8 |
| Chicago, IL | ~$58M | ~$30M | **~$28M** | Year 9 |
| Miami, FL | ~$12M | ~$6M | **~$6M** | Year 9 |
| Fort Lauderdale, FL | ~$5M | ~$2.5M | **~$2.5M** | Year 9 |
| Los Angeles, CA | ~$85M | ~$50M | **~$35M** | Year 11 |

> *Based on Powder Coated Steel ($1,258 avg) vs Carbon Fiber ($1,200), 30-year horizon, climate-adjusted lifespans.*

---

## 🏗️ Architecture

```
CarbonROI/
├── agent/
│   ├── CarbonROI_FullAgent.jsx     # Autonomous React agent (Anthropic API)
│   └── CarbonROI_Agent.jsx         # Standalone calculator (no API required)
├── python/
│   ├── materials.py                # Material dataclasses & TCO logic
│   ├── calculator.py               # ROI engine
│   ├── environmental.py            # CO₂ & waste calculations
│   ├── visualizations.py           # Matplotlib / Plotly charts
│   └── report.py                   # Report generator
├── app/
│   └── app.py                      # Streamlit web app
├── data/
│   └── Material_Cost_Database.xlsx # Verified price database (4 sheets)
└── README.md
```

---

## 🚀 Quick Start

### React Agent (full autonomous version)

```bash
# Requires Node.js 18+
npx create-react-app carbonroi
cd carbonroi
# Replace src/App.js with agent/CarbonROI_FullAgent.jsx
npm start
```

### Python / Streamlit version

```bash
git clone https://github.com/YOUR_USERNAME/carbon-roi-calculator
cd carbon-roi-calculator

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

streamlit run app/app.py
```

---

## 🤖 AI Agent Features

The React agent uses **Anthropic Claude API with web_search tool** to:

1. Research current bench prices in real time
2. Apply climate degradation factors (NOAA data)
3. Run ROI calculations for all cities
4. Write a professional executive report
5. Export all data in multiple formats

```javascript
// Agent calls Claude with web search tool
const response = await fetch("https://api.anthropic.com/v1/messages", {
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    tools: [{ type: "web_search_20250305", name: "web_search" }],
    messages: [{ role: "user", content: "Search current municipal bench prices..." }]
  })
});
```

---

## 📐 Methodology

### Total Cost of Ownership Formula

```
TCO = (Unit_Cost + Install) × (⌊Years / Lifespan_Adjusted⌋ + 1) × Quantity
    + Maintenance_per_Year × Years × Quantity

Lifespan_Adjusted = Lifespan_Base × Climate_Multiplier
```

### Climate Multipliers (NOAA-based)

| Climate Zone | Multiplier | Example Cities |
|---|---|---|
| Subtropical/Coastal | 0.70x | Fort Lauderdale, Miami |
| Humid Continental | 0.75x | New York, Chicago, Houston |
| Temperate/Wet | 0.80x | Seattle, Washington DC |
| Mild/Coastal | 0.85x | San Francisco |
| Mediterranean | 0.95x | Los Angeles |
| Desert/Hot | 0.90x | Phoenix |

### Environmental Impact

- **Waste prevented**: (Traditional replacements − CF replacements) × qty × 68kg/bench
- **CO₂ avoided**: Waste_kg × 30% steel content × 1.85 tCO₂/t steel
- **Cars equivalent**: CO₂_tons / 4.6 tCO₂/car/year

---

## 💰 Data Sources

All prices verified from commercial sources (February 2026):

| Material | Price Range | Source |
|---|---|---|
| Powder Coated Steel bench | $861 – $2,482 | ✅ Grainger.com |
| Recycled Plastic (HDPE) bench | $368 – $1,583 | ✅ Grainger.com + ParkWarehouse.com |
| Aluminum bench | $353 – $1,490 | ✅ ParkWarehouse.com |
| Wood bench | $326 – $900 | ✅ ParkWarehouse.com |
| Carbon Fiber bench | ~$1,200 (est.) | Alibaba / industry estimates |

**Lifespan sources:** APWA Asset Management Guidelines, Polywood 20-year warranty, USDA Forest Products Laboratory, PMC7182928 (Polymers 2020), PMC9172091 (Carbon Letters 2022)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Agent | Anthropic Claude API (claude-sonnet-4) + web_search tool |
| Frontend | React 18, custom CSS |
| Backend / Analysis | Python 3.10, Pandas, NumPy |
| Visualization | Matplotlib, Plotly, Streamlit |
| Data | Excel (openpyxl), CSV, JSON |
| Deploy | Vercel (React) + Streamlit Cloud (Python) |

---

## 📸 Screenshots

> *Add screenshots here after deployment*

```
[ Dashboard screenshot ]    [ City analysis screenshot ]
[ AI Report screenshot  ]   [ Export panel screenshot  ]
```

---

## 🗺️ Roadmap

- [x] Material cost database (verified 4 sources)
- [x] Climate-adjusted TCO calculator
- [x] Autonomous React agent with Anthropic API
- [x] Environmental impact module
- [x] Multi-city comparison (10 US cities)
- [x] CSV / JSON / Markdown export
- [ ] Python Streamlit web app
- [ ] OpenStreetMap bench count integration
- [ ] PDF report generation
- [ ] Additional cities (EU markets)
- [ ] Real-time price API integration

---

## 👩‍💻 About

Built by **Veronika Ingolycheva** as a portfolio project demonstrating:
- Autonomous AI agent development (Anthropic API, tool use)
- Financial modeling and data analysis
- Full-stack development (React + Python)
- Domain expertise in municipal infrastructure and sustainability

**Connect:** [LinkedIn](https://linkedin.com/in/your-profile) · [Email](mailto:veronika.ingolyche@gmail.com)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Data sources: Grainger.com, ParkWarehouse.com, Polywood.com, NOAA, APWA, PMC/NIH research database*
*Last updated: February 2026*
