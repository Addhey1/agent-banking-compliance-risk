import pandas as pd
import os

# Automatically locate the scripts directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Point to your processed subfolder
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../data/processed/"))
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../outputs/"))

def generate_risk_model():
    print("Initializing Compliance Risk Scoring Engine...")
    
    # Read Processed Datasets (Matching your clean files perfectly)
    try:
        tx = pd.read_csv(os.path.join(DATA_DIR, "fact_transactions.csv"))
        incidents = pd.read_csv(os.path.join(DATA_DIR, "fact_incidents.csv"))
        reviews = pd.read_csv(os.path.join(DATA_DIR, "fact_reviews.csv"))
        agents = pd.read_csv(os.path.join(DATA_DIR, "agents_clean.csv"))
    except FileNotFoundError as e:
        print(f"Error: Missing processed file. {e}")
        return

    # Process Metrics
    failed_reviews = reviews[reviews['Result'] == 'Fail'].groupby('Agent_ID').size().reset_index(name='Exceptions')
    complaints = incidents.groupby('Agent_ID').size().reset_index(name='Complaints')

    if 'Suspicious Flags' in tx.columns:
        flags = tx.groupby('Agent_ID')['Suspicious Flags'].sum().reset_index(name='Flags')
    elif 'Suspicious Transactions' in tx.columns:
        flags = tx.groupby('Agent_ID')['Suspicious Transactions'].sum().reset_index(name='Flags')
    else:
        flags = tx.groupby('Agent_ID').size().reset_index(name='Flags')

    # Merge Data
    master_df = agents.merge(failed_reviews, on='Agent_ID', how='left')
    master_df = master_df.merge(complaints, on='Agent_ID', how='left')
    master_df = master_df.merge(flags, on='Agent_ID', how='left')
    master_df.fillna(0, inplace=True)

    # HMRC Risk Weighted Score Calculation
    master_df['Risk_Score'] = (master_df['Exceptions'] * 5) + (master_df['Complaints'] * 3) + (master_df['Flags'] * 10)

    # Aggregate by Zone (Region)
    regional_risk = master_df.groupby('Zone')['Risk_Score'].mean().reset_index()
    regional_risk.columns = ['Region', 'Risk_Score']

    # Assign Risk Categories
    def assign_tier(score):
        if score >= 70: return "High Risk"
        elif score >= 50: return "Medium Risk"
        else: return "Low Risk"

    regional_risk['Category'] = regional_risk['Risk_Score'].apply(assign_tier)
    regional_risk = regional_risk.sort_values(by='Risk_Score', ascending=False)

    # Export
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    regional_risk.to_csv(os.path.join(OUTPUT_DIR, "risk_scores.csv"), index=False)
    print("✅ Regional Risk Matrix calculated and saved to /outputs/")
    print(regional_risk)

if __name__ == "__main__":
    generate_risk_model()