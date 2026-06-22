# Agent Banking Compliance & Risk Intelligence Framework

A comprehensive, end-to-end data engineering and analytics framework engineered to detect, monitor, and mitigate compliance and fraud risk within a large-scale agent banking network. This system processes over 500,000 transactions across 5,000 active agents to identify regional risk hotspots, suspicious provider concentrations, and prioritize field investigations.

## 📁 Repository Architecture
* **`scripts/`**: Core data engineering, Relational data simulation, automated processing, and predictive scoring pipelines.
* **`sql/`**: Relational database schemas, staging logic, and deep analytical compliance queries.
* **`AgentBankingDB.pbix`**: Interactive executive Power BI application file mapping operational and geopolitical threat parameters.

---

## 🛠️ Data Engineering & Pipeline Breakdown

The project operates as a structured 7-stage data generation, cleaning, and modeling pipeline:

1. **`01_generate_data.py`**: Generates a synthetic multi-table relational schema containing transaction, customer, agent, incident, and compliance review facts. Uses consistent random states to enforce regional statistical skews (e.g., higher exception concentrations in specific geopolitical zones).
2. **`02_clean_data.py`**: Automated data cleaning pipeline handling missing values, standardizing datetime fields, tracking data integrity rules, and preparing tables for database insertion.
3. **`03_risk_scoring.py` & `07_predictive_risk_model.py`**: Implements deterministic and predictive compliance scoring algorithms. Identifies high-risk agents (Probability score $\ge$ 70) by analyzing weighted patterns of documentation quality, historic fraud flags, and compliance review outcomes.
4. **`04_update_sql_db.py`**: Automated pipeline for structuring connection layouts, staging data frames, and refreshing the relational database tables.
5. **`05_analysis.py` & `06_quick_check.py`**: Diagnostic scripts providing high-level operational reporting, validation checks, and feature performance metrics.

---

## 💻 Relational Database Analytics (SQL)

The database structure relies on relational database management best practices, controlled via three core production scripts:
* **`schema.sql`**: Designs the physical storage layer, enforces primary/foreign key relationships, and standardizes dimensional schemas across tables (`Agents`, `Customers`, `Transactions`, `Reviews`, `Incidents`).
* **`load_data.sql`**: Handles optimized batch insertion and table loading routines.
* **`analysis_queries.sql`**: Deep forensic accounting and investigative analytics queries designed to surface transaction volume metrics, failure rates by individual service provider, and active compliance breaches.

---

## 📊 Business Intelligence & Executive Outcomes

The analytical scripts feed directly into a multi-layered **Power BI Dashboard** that empowers risk management teams to transition from reactive monitoring to evidence-based field intervention:

* **Executive Summary**: Tracks nationwide transactional volume (NGN), operational success rates, and dynamic risk tiers.
* **Geopolitical Risk Profiles**: Visualizes regional compliance hotspots, highlighting critical exception density shifts across regional zones.
* **Predictive Investigation Queue**: Aggregates high-probability fraud flags and customer complaints into a real-time, prioritized investigation action log for field auditors.

---

## 📊 Executive Dashboard Solutions

### Page 1: High-Level Macro Insights & Performance Vectors
![Executive Summary](images/executive_summary.png)

### Page 2: Risk Profiling Overview
![Risk Profiling](images/risk_profile.png)

### Page 3: Geopolitical Risk Profiling & Regional Hotspots
![Regional Risk Profiling](images/regional_risk_profile.png)

### Page 4: Compliance Analysis
![Compliance Analysis](images/compliance_analysis.png)

### Page 5: Predictive Risk Profiles & Active Investigation Queue
![Predictive Risk](images/predictive_analysis.png)

---

## 🚀 How to Run the Pipeline Local Environment

1. Clone this repository to your local directory.
2. Initialize your Python virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
