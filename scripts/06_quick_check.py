import pandas as pd
import os

print("\n" + "="*50)
print("🔍 COMPLIANCE PROFILE VERIFICATION")
print("="*50)

raw_path = "data/raw/agents.csv"
proc_path = "data/processed/dim_agents.csv"

if os.path.exists(raw_path):
    raw_agents = pd.read_csv(raw_path)
    print(f"Raw Agents CSV Floor:       {raw_agents['KYC_Score'].min()}")
else:
    print("❌ Cannot find data/raw/agents.csv")

if os.path.exists(proc_path):
    proc_agents = pd.read_csv(proc_path)
    print(f"Processed Dim Agents Floor: {proc_agents['KYC_Score'].min()}")
else:
    print("❌ Cannot find data/processed/dim_agents.csv")
print("="*50 + "\n")