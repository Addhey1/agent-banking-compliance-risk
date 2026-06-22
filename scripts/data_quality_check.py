import pandas as pd
import os

# 1. Automatically locate the scripts directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. POINT DIRECTLY TO THE RAW SUBFOLDER
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../data/raw/"))
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../outputs/"))

def run_quality_checks():
    print("Parsing raw datasets for quality assurance...")
    
    # Load datasets safely from the raw directory
    try:
        transactions = pd.read_csv(os.path.join(DATA_DIR, "transactions.csv"))
        incidents = pd.read_csv(os.path.join(DATA_DIR, "incidents.csv"))
        reviews = pd.read_csv(os.path.join(DATA_DIR, "reviews.csv"))
    except FileNotFoundError as e:
        print(f"Error: Missing source file. {e}")
        return

    metrics = []

    # Check 1: Missing Values in Critical Keys
    missing_tx = transactions['Agent_ID'].isnull().sum()
    missing_inc = incidents['Agent_ID'].isnull().sum()
    missing_rev = reviews['Agent_ID'].isnull().sum()
    total_missing = int(missing_tx + missing_inc + missing_rev)
    metrics.append({"Check": "Missing Values in Agent ID", "Result": total_missing})

    # Check 2: Duplicate Records
    total_duplicates = int(transactions.duplicated().sum() + incidents.duplicated().sum() + reviews.duplicated().sum())
    metrics.append({"Check": "Duplicate Records", "Result": total_duplicates})

    # Check 3: Integrity Checks (Outliers - e.g., Negative Transaction Amounts)
    if 'Amount_NGN' in transactions.columns:
        outliers = int((transactions['Amount_NGN'] < 0).sum())
    else:
        outliers = 0
    metrics.append({"Check": "Invalid Negative Amounts (Outliers)", "Result": outliers})

    # Compile and Export Report
    dq_report = pd.DataFrame(metrics)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dq_report.to_csv(os.path.join(OUTPUT_DIR, "data_quality_report.csv"), index=False)
    
    print("✅ Data Quality Report successfully generated in /outputs/")
    print(dq_report)

if __name__ == "__main__":
    run_quality_checks()