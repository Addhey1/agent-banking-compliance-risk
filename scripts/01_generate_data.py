import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# Set consistent random seeds for reproducibility
np.random.seed(42)
random.seed(42)

# -----------------------------
# CONFIG
# -----------------------------
N_AGENTS = 5000
N_CUSTOMERS = 50000
N_TRANSACTIONS = 500000
N_REVIEWS = 15000
N_INCIDENTS = 5000

# -----------------------------
# HELPERS
# -----------------------------
def normalise(values):
    values = np.array(values, dtype=float)
    return values / values.sum()

def sample(items, probs):
    return np.random.choice(items, p=normalise(probs))

# -----------------------------
# GEOGRAPHY
# -----------------------------
zones = {
    "North East": 0.06,
    "North Central": 0.16,
    "North West": 0.12,
    "South South": 0.16,
    "South East": 0.13,
    "South West": 0.37
}

states = {
    "North East": ["Adamawa","Bauchi","Borno","Gombe","Taraba","Yobe"],
    "North Central": ["Benue","Kogi","Kwara","Nasarawa","Niger","Plateau","FCT"],
    "North West": ["Jigawa","Kaduna","Kano","Katsina","Kebbi","Sokoto","Zamfara"],
    "South South": ["Akwa Ibom","Bayelsa","Cross River","Delta","Edo","Rivers"],
    "South East": ["Abia","Anambra","Ebonyi","Enugu","Imo"],
    "South West": ["Lagos","Ogun","Oyo","Ondo","Osun","Ekiti"]
}

# -----------------------------
# THE ACTUAL TOP 5 SUPERAGENTS
# -----------------------------
top_5_super_agents = ["IPay", "Monie", "Palmx", "Kudi", "Puge"]

# -----------------------------
# TRANSACTION TYPES
# -----------------------------
txn_types = ["Cash In","Cash Out","Transfer","Bills","Airtime","Account Opening","BVN"]
txn_volume_weights = normalise([0.1998,0.5795,0.1017,0.0508,0.0650,0.0025,0.0008])

# -----------------------------
# AGENTS GENERATION
# -----------------------------
start_timeline = datetime(2019, 1, 1)
end_timeline = datetime(2025, 12, 31)
total_timeline_days = (end_timeline - start_timeline).days

agent_ids = np.arange(100000, 100000 + N_AGENTS)
zone_names = list(zones.keys())
zone_probs = normalise(list(zones.values()))

agent_list = []

raw_providers = [
    "Banks", "Capri", "EFEX", "Others", "UTES", 
    "Xpress", "V-Settle", "TeamA", "NewNew", "Purk", 
    "G-Tranz", "Unif", "Crowd", "Innovate", 
    "Accel", "9Lone", "Kilo", "Low Tier Providers"
]
raw_weights = [0.6185, 0.0710, 0.0327, 0.0328, 0.0284, 0.0252, 0.0202, 0.0187, 
               0.0174, 0.0169, 0.0153, 0.0134, 0.0135, 0.0133, 0.0120, 0.0119, 
               0.0114, 0.0250]

raw_providers.extend(top_5_super_agents)
raw_weights.extend([0.12, 0.08, 0.05, 0.04, 0.01])

# Dictionaries to permanently bind an agent's base attributes across tables
agent_kyc_base = {}
agent_aml_base = {}
agent_zone_lookup = {}

for agent_id in agent_ids:
    zone = np.random.choice(zone_names, p=zone_probs)
    state = random.choice(states[zone])
    
    selected_p = sample(raw_providers, raw_weights)
    
    if selected_p in ["Banks", "FirstMonie", "Access CLOSA", "UBA Moni", "GTExpress", "Zenith Agent", "EcobankXpress"]:
        final_provider = "Banks"
    elif selected_p in top_5_super_agents:
        final_provider = selected_p
    else:
        final_provider = "Others"

    agent_type = random.choice(["Shop","Pharmacy","FMCG","Petrol Station","Kiosk"])
    
    # Regional Variance Rules for Dimensions
    if zone == "North East":
        kyc_score = np.random.randint(5, 35)
        aml_score = np.random.randint(5, 35)
    elif zone == "North Central":
        kyc_score = np.random.randint(15, 55)
        aml_score = np.random.randint(15, 55)
    elif zone == "North West":
        kyc_score = np.random.randint(25, 65)
        aml_score = np.random.randint(25, 65)
    elif zone == "South East":
        kyc_score = np.random.randint(40, 85)
        aml_score = np.random.randint(40, 85)
    else: 
        kyc_score = np.random.randint(50, 100)
        aml_score = np.random.randint(50, 100)

    # Fraud tracking flags
    fraud_flag = "Yes" if (kyc_score < 40 and aml_score < 45 and random.random() < 0.45) else "No"

    random_days_offset = random.randint(0, total_timeline_days)
    date_onboarded = start_timeline + timedelta(days=random_days_offset)

    agent_list.append([
        agent_id, zone, state, final_provider, agent_type,
        kyc_score, aml_score, fraud_flag, date_onboarded
    ])
    
    # Cache attributes for proper relational integrity across fact generation
    agent_kyc_base[agent_id] = kyc_score
    agent_aml_base[agent_id] = aml_score
    agent_zone_lookup[agent_id] = zone

agents = pd.DataFrame(agent_list, columns=[
    "Agent_ID","Zone","State","Provider","Agent_Type",
    "KYC_Score","AML_Score","Fraud_Flag","Date_Onboarded"
])
agents["Date_Onboarded"] = pd.to_datetime(agents["Date_Onboarded"])

# -----------------------------
# CUSTOMERS GENERATION
# -----------------------------
customers = pd.DataFrame({
    "Customer_ID": np.arange(200000, 200000 + N_CUSTOMERS),
    "Gender": np.random.choice(["M","F"], N_CUSTOMERS),
    "Age_Group": np.random.choice(["18-25","26-35","36-45","46-60"], N_CUSTOMERS),
    "Customer_Type": np.random.choice(["Banked","Underbanked","Unbanked"], N_CUSTOMERS, p=[0.55,0.30,0.15])
})

# -----------------------------
# TRANSACTIONS GENERATION
# -----------------------------
transactions = pd.DataFrame({
    "Transaction_ID": np.arange(N_TRANSACTIONS),
    "Agent_ID": np.random.choice(agent_ids, N_TRANSACTIONS),
    "Customer_ID": np.random.choice(customers["Customer_ID"], N_TRANSACTIONS),
    "Transaction_Type": np.random.choice(txn_types, N_TRANSACTIONS, p=txn_volume_weights),
    "Status": np.where(np.random.rand(N_TRANSACTIONS) < 0.03, "Failed", "Successful"),
    "Days_Offset": np.random.randint(0, total_timeline_days + 1, N_TRANSACTIONS)
})

def assign_amount(row):
    if row["Transaction_Type"] == "Airtime":
        return np.random.randint(100, 5000)
    elif row["Transaction_Type"] in ["Cash In","Cash Out","Transfer"]:
        return np.random.randint(500, 200000)
    else:
        return np.random.randint(1000, 50000)

transactions["Amount_NGN"] = transactions.apply(assign_amount, axis=1)

transactions["Transaction_Date"] = transactions["Days_Offset"].apply(
    lambda x: start_timeline + timedelta(days=int(x))
)
transactions["Transaction_Date"] = pd.to_datetime(transactions["Transaction_Date"])
transactions.drop(columns=["Days_Offset"], inplace=True)

# -----------------------------
# COMPLIANCE REVIEWS (FIXED REGIONAL VARIANCE)
# -----------------------------
reviews = []

# Ensure every single agent gets evaluated at least once
forced_pool = list(agent_ids)
extra_pool = list(np.random.choice(agent_ids, size=N_REVIEWS - len(forced_pool)))
distributed_agents = forced_pool + extra_pool
random.shuffle(distributed_agents)

# Define target high-risk zones to create realistic variance on your charts
high_risk_zones = ["North East", "North Central"]

for i in range(N_REVIEWS):
    agent = distributed_agents[i]
    
    kyc = agent_kyc_base.get(agent, 50)
    aml = agent_aml_base.get(agent, 50)
    zone = agent_zone_lookup.get(agent, "South West") 
    
    # Minor variance for operational metadata tracking
    doc = np.clip(kyc + np.random.randint(-10, 10), 5, 100)
    
    # Standard formula baseline calculation
    risk = float(100 - (kyc + aml + doc) / 3)
    
    # FIX: Tie high-risk spike probabilities to actual geographic zones
    if zone in high_risk_zones and random.random() < 0.65:
        np.random.seed(42 + i)
        risk = float(np.random.randint(75, 97))
    elif zone in ["North West", "South East"] and random.random() < 0.20:
        np.random.seed(42 + i)
        risk = float(np.random.randint(65, 85))
        
    if risk >= 70:
        result, action = "Fail", "Suspension"
    elif risk >= 50:
        result, action = "Conditional Pass", "Warning"
    else:
        result, action = "Pass", "None"
        
    reviews.append([i, agent, kyc, aml, doc, risk, result, action])

reviews = pd.DataFrame(reviews, columns=["Review_ID","Agent_ID","KYC_Score","AML_Score","Documentation_Score","Risk_Score","Result","Action"])
reviews["Review_Date"] = pd.to_datetime([start_timeline + timedelta(days=int(d)) for d in np.random.randint(0, total_timeline_days + 1, N_REVIEWS)])

# -----------------------------
# INCIDENTS GENERATION
# -----------------------------
incident_types = ["Fraud","KYC Breach","Suspicious Transfer","Excess Limit","Identity Theft"]
incidents = []
for i in range(N_INCIDENTS):
    agent = random.choice(agent_ids)
    incident = np.random.choice(incident_types, p=normalise([0.15,0.25,0.35,0.15,0.10]))
    severity = sample(["Low","Medium","High"], [0.5,0.3,0.2])
    impact = np.random.randint(5000, 500000)
    incidents.append([i, agent, incident, severity, impact])

incidents = pd.DataFrame(incidents, columns=["Incident_ID","Agent_ID","Incident_Type","Severity","Financial_Impact"])
incidents["Incident_Date"] = pd.to_datetime([start_timeline + timedelta(days=int(d)) for d in np.random.randint(0, total_timeline_days + 1, N_INCIDENTS)])

# -----------------------------
# EXPORT
# -----------------------------
agents.to_csv("data/raw/agents.csv", index=False)
customers.to_csv("data/raw/customers.csv", index=False)
transactions.to_csv("data/raw/transactions.csv", index=False)
reviews.to_csv("data/raw/reviews.csv", index=False)
incidents.to_csv("data/raw/incidents.csv", index=False)

print("\nDataset generated successfully with corrected regional variance patterns.")
print("Date range:", transactions["Transaction_Date"].min().strftime('%Y-%m-%d'), "to", transactions["Transaction_Date"].max().strftime('%Y-%m-%d'))