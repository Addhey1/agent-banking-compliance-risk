import os
import pandas as pd
import numpy as np

def clean_and_transform_pipeline():
    print("="*60)
    print("🚀 INITIALIZING RISKS & COMPLIANCE DATA CLEANSING PIPELINE")
    print("="*60)

    # -----------------------------
    # 1. DIRECTORY & SAFETY CHECKS
    # -----------------------------
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    required_files = {
        "agents": f"{raw_dir}/agents.csv",
        "transactions": f"{raw_dir}/transactions.csv",
        "reviews": f"{raw_dir}/reviews.csv",
        "incidents": f"{raw_dir}/incidents.csv"
    }

    # Verify all generated files exist before beginning transformations
    for name, path in required_files.items():
        if not os.path.exists(path):
            print(f"❌ Critical Error: Missing '{path}'. Please execute your generation script first.")
            return

    # -----------------------------
    # 2. INGESTION
    # -----------------------------
    print("\n📥 Ingesting raw source files...")
    agents = pd.read_csv(required_files["agents"])
    transactions = pd.read_csv(required_files["transactions"])
    reviews = pd.read_csv(required_files["reviews"])
    incidents = pd.read_csv(required_files["incidents"])
    print("✨ Ingestion complete.")

    # -----------------------------
    # 3. ENFORCE TIME SERIES DATATYPES (Slicer Fix)
    # -----------------------------
    print("\n📅 Formatting chronological timelines...")
    
    # Force pure datetime engine matching your generator parameters
    transactions["Transaction_Date"] = pd.to_datetime(transactions["Transaction_Date"])
    reviews["Review_Date"] = pd.to_datetime(reviews["Review_Date"])
    incidents["Incident_Date"] = pd.to_datetime(incidents["Incident_Date"])
    agents["Date_Onboarded"] = pd.to_datetime(agents["Date_Onboarded"]) 

    # Generate custom reporting keys to resolve Power BI alphabetical axis bugs
    transactions["Month_Year_Trend"] = transactions["Transaction_Date"].dt.strftime('%b %Y')
    transactions["Month_Year_Sort"] = transactions["Transaction_Date"].dt.year * 100 + transactions["Transaction_Date"].dt.month
    
    print(f"✔️ Min Date Found: {transactions['Transaction_Date'].min().strftime('%Y-%m-%d')}")
    print(f"✔️ Max Date Found: {transactions['Transaction_Date'].max().strftime('%Y-%m-%d')}")

    # -----------------------------
    # 4. TRANSFORMATION & QUALITY ASSURANCE
    # -----------------------------
    print("\n🛠️ Running data sanitization & profiling checks...")
    
    # Financial Value Type Constraints
    transactions["Amount_NGN"] = transactions["Amount_NGN"].fillna(0).astype(np.int64)
    transactions["Status"] = transactions["Status"].str.strip().fillna("Unknown")
    
    # Score Boundaries Compliance
    # Verified: Floor set to 5 to protect the newly engineered low-compliance regional profiles
    agents["KYC_Score"] = agents["KYC_Score"].clip(5, 100).fillna(50).astype(int)
    agents["AML_Score"] = agents["AML_Score"].clip(5, 100).fillna(50).astype(int)
    
    # Feature Engineering: Calculate Baseline Agent Risk Category for the Power BI Slicer
    def assign_agent_risk_tier(row):
        if row["KYC_Score"] < 40 or row["AML_Score"] < 45:
            return "High Risk"
        elif row["KYC_Score"] < 65 or row["AML_Score"] < 65:
            return "Medium Risk"
        else:
            return "Low Risk"

    agents["Risk_Category"] = agents.apply(assign_agent_risk_tier, axis=1)
    
    # Calculate a composite risk index for the reporting tier directly in Python
    reviews["Risk_Score"] = reviews["Risk_Score"].round(2)
    
    # PIPELINE RE-ALIGNMENT CHECK: Ensure categorization strings perfectly match the new scores
    def align_review_status(row):
        if row["Risk_Score"] >= 70:
            return pd.Series(["Fail", "Suspension"])
        elif row["Risk_Score"] >= 50:
            return pd.Series(["Conditional Pass", "Warning"])
        else:
            return pd.Series(["Pass", "None"])

    reviews[["Result", "Action"]] = reviews.apply(align_review_status, axis=1)
    
    # Visual health check to your console
    high_risk_count = len(reviews[reviews["Risk_Score"] >= 70])
    print(f"🛡️ Quality Gate Check: Found {high_risk_count:,} review records matching the high-risk threshold (>= 70).")
    
    print("\n📋 Current Unique Providers Staged for SQL:")
    print(", ".join(agents["Provider"].unique()))

    # -----------------------------
    # 5. STAGING EXPORT FOR POWER BI
    # -----------------------------
    print("\n💾 Exporting analytical models to staging area...")
    
    agents.to_csv(f"{processed_dir}/dim_agents.csv", index=False)
    transactions.to_csv(f"{processed_dir}/fact_transactions.csv", index=False)
    reviews.to_csv(f"{processed_dir}/fact_reviews.csv", index=False)
    incidents.to_csv(f"{processed_dir}/fact_incidents.csv", index=False)

    print("="*60)
    print("🎉 SUCCESS: MODEL PIPELINE RUN COMPLETE")
    print(f"📍 Processed Models Staged In: '{processed_dir}/'")
    print(f"📊 Volume Counter: {len(transactions):,} Active Logged Rows")
    print("="*60)

if __name__ == "__main__":
    clean_and_transform_pipeline()