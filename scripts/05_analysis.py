import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# =================================================================
# 1. Load Data (Fixed File Paths from Staging)
# =================================================================
print("📥 Ingesting staged analytics models...")
agents = pd.read_csv("data/processed/dim_agents.csv")
transactions = pd.read_csv("data/processed/fact_transactions.csv")
incidents = pd.read_csv("data/processed/fact_incidents.csv")
reviews = pd.read_csv("data/processed/fact_reviews.csv")

# =================================================================
# 2. Risk Scoring Calculations & Validation
# =================================================================
print("⚡ Processing final compliance calculations...")

reviews["Risk_Score"] = reviews["Risk_Score"].astype(float).round(2)

def assign_agent_risk_tier(row):
    if row["KYC_Score"] < 40 or row["AML_Score"] < 45:
        return "High Risk"
    elif row["KYC_Score"] < 65 or row["AML_Score"] < 65:
        return "Medium Risk"
    else:
        return "Low Risk"

agents["Risk_Category"] = agents.apply(assign_agent_risk_tier, axis=1)

agents["Date_Onboarded"] = pd.to_datetime(agents["Date_Onboarded"])
transactions["Transaction_Date"] = pd.to_datetime(transactions["Transaction_Date"])
incidents["Incident_Date"] = pd.to_datetime(incidents["Incident_Date"])
reviews["Review_Date"] = pd.to_datetime(reviews["Review_Date"])

# =================================================================
# 3. ADVANCED COMPLIANCE ANALYSIS PHASE (New Feature)
# =================================================================
print("\n📊 Running Exploratory Data Analysis & Executive Profiling...")
print("-" * 60)

# Insight 1: High-Risk Footprint Count
high_risk_reviews = reviews[reviews["Risk_Score"] >= 70]
unique_high_risk_agents = high_risk_reviews["Agent_ID"].nunique()
print(f"🔴 Total Unique High-Risk Agents Identified: {unique_high_risk_agents:,} ({unique_high_risk_agents / len(agents) * 100:.1f}% of network)")

# Insight 2: Geographic Risk Concentration (Merge reviews with agent dimension)
merged_reviews = reviews.merge(agents, on="Agent_ID", how="inner")
regional_risk = merged_reviews[merged_reviews["Risk_Score"] >= 70].groupby("Zone").size().reset_index(name="High_Risk_Incident_Count")
regional_risk = regional_risk.sort_values(by="High_Risk_Incident_Count", ascending=False)

print("\n🌍 High-Risk Incident Distribution by Zone:")
for _, row in regional_risk.iterrows():
    print(f" - {row['Zone']}: {row['High_Risk_Incident_Count']:,} critical flags")

# Insight 3: Financial Exposure Analysis
failed_txns = transactions[transactions["Status"] == "Failed"]
total_failed_volume = failed_txns["Amount_NGN"].sum()
print(f"\n💸 Network Financial Health: Total Failed Transaction Volume = ₦{total_failed_volume:,}")

# Insight 4: Top Strategic Provider Breakdown
provider_breakdown = agents.groupby("Provider").size().reset_index(name="Total_Agents")
provider_breakdown["Market_Share_%"] = (provider_breakdown["Total_Agents"] / len(agents) * 100).round(2)
print("\n🏢 Provider Network Market Share Summary:")
print(provider_breakdown.sort_values(by="Total_Agents", ascending=False).to_string(index=False))
print("-" * 60)

# =================================================================
# 4. Load Phase: Push Clean Data to SQL Server (Explicit Connection)
# =================================================================
print("\n🚀 Staging data into local SQLEXPRESS instance...")

engine = create_engine(
    "mssql+pyodbc://localhost\\SQLEXPRESS/AgentBankingRiskDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes",
    fast_executemany=True
)

data_payload = {
    "fact_transactions": transactions, 
    "dim_agents": agents,
    "fact_incidents": incidents,
    "fact_reviews": reviews
}

for table_name, dataframe in data_payload.items():
    print(f" -> Writing [dbo.{table_name}] ({len(dataframe):,} rows)...")
    dataframe.to_sql(
        name=table_name, 
        con=engine, 
        schema="dbo", 
        if_exists="replace", 
        index=False,
        chunksize=10000 
    )
    print(f" ✔️ Table [dbo.{table_name}] successfully updated in SQL Server.")

print("\n🎉 Success! ETL pipeline completed! All analyzed tables are fully staged.")