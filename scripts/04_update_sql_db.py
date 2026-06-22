import os
import pandas as pd
from sqlalchemy import create_engine, text

def sync_processed_data_to_sql():
    print("="*60)
    print("🗄️   STARTING OPTIMIZED SQL SERVER OVERWRITE & EXECUTIVE PROFILING")
    print("="*60)

    # --------------------------------------------------
    # 1. DATABASE CONNECTION & INGESTION
    # --------------------------------------------------
    SERVER = 'localhost\\SQLEXPRESS'
    DATABASE = 'AgentBankingRiskDB'
    connection_string = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    
    # fast_executemany speeds up row inserts by up to 100x
    engine = create_engine(connection_string, fast_executemany=True)

    processed_dir = "data/processed"
    
    # Ingest the clean datasets from your sanitization pipeline
    agents = pd.read_csv(f"{processed_dir}/dim_agents.csv")
    transactions = pd.read_csv(f"{processed_dir}/fact_transactions.csv")
    reviews = pd.read_csv(f"{processed_dir}/fact_reviews.csv")
    incidents = pd.read_csv(f"{processed_dir}/fact_incidents.csv")

    # --------------------------------------------------
    # 2. EXECUTIVE PROFILING INSIGHTS (From Submission 5)
    # --------------------------------------------------
    print("\n📊 Running Exploratory Data Analysis & Executive Profiling...")
    print("-" * 60)
    
    # Track the forced ~500 high risk agent footprint count
    unique_high_risk = reviews[reviews["Risk_Score"] >= 70]["Agent_ID"].nunique()
    print(f"🔴 Total Unique High-Risk Agents Identified: {unique_high_risk:,} ({unique_high_risk / len(agents) * 100:.1f}% of network)")

    # Financial Exposure Tracking
    failed_txns = transactions[transactions["Status"] == "Failed"]
    print(f"💸 Network Financial Health: Total Failed Transaction Volume = ₦{failed_txns['Amount_NGN'].sum():,}")

    # Market Share Tracker
    provider_breakdown = agents.groupby("Provider").size().reset_index(name="Total_Agents")
    provider_breakdown["Market_Share_%"] = (provider_breakdown["Total_Agents"] / len(agents) * 100).round(2)
    print("\n🏢 Provider Network Market Share Summary:")
    print(provider_breakdown.sort_values(by="Total_Agents", ascending=False).to_string(index=False))
    print("-" * 60)

    # --------------------------------------------------
    # 3. SCHEMA MIGRATION & TRANSIT SAFE WRITING (From Submission 4)
    # --------------------------------------------------
    with engine.begin() as conn:
        print("\n🛠️  Verifying SQL Server schema columns for Power BI support...")
        
        # Check dim_agents columns for the dashboard risk category slicer
        if conn.execute(text("SELECT COL_LENGTH('dbo.dim_agents', 'Risk_Category')")).scalar() is None:
            print("➡️   Adding 'Risk_Category' to dbo.dim_agents...")
            conn.execute(text("ALTER TABLE dbo.dim_agents ADD Risk_Category VARCHAR(50) NULL"))
            
        # Check fact_transactions for axis sorting fixes
        if conn.execute(text("SELECT COL_LENGTH('dbo.fact_transactions', 'Month_Year_Trend')")).scalar() is None:
            print("➡️   Adding Trend sorting columns to dbo.fact_transactions...")
            conn.execute(text("ALTER TABLE dbo.fact_transactions ADD Month_Year_Trend VARCHAR(50) NULL"))
            conn.execute(text("ALTER TABLE dbo.fact_transactions ADD Month_Year_Sort INT NULL"))

        print("\n🔗 Temporarily disabling foreign key relationships to prevent blocks...")
        conn.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'"))

        # Payload structure - Ordering prevents relational mapping conflicts
        data_payload = {
            "fact_transactions": transactions, 
            "fact_reviews": reviews,
            "fact_incidents": incidents,
            "dim_agents": agents
        }
        
        print("\n📥 Streaming processed data payloads directly to SQL destination...")
        for table_name, df in data_payload.items():
            
            # Enforce explicit timestamp datatypes before database loading
            for col in df.columns:
                if "Date" in col or "Timeline" in col:
                    df[col] = pd.to_datetime(df[col])

            # Safely sweep old rows out without destroying constraints, indices, or column properties
            print(f" 🧹 Clearing old records from database table [dbo.{table_name}]...")
            conn.execute(text(f"DELETE FROM dbo.{table_name}"))
            
            # Append fresh data stream smoothly into your existing structural database definitions
            print(f" -> Appending fresh rows to table [dbo.{table_name}] ({len(df):,} rows)...")
            df.to_sql(
                name=table_name, 
                con=conn, 
                schema="dbo", 
                if_exists="append",  # SAFE: Protects custom structural primary keys and datatypes
                index=False,
                chunksize=10000 
            )
            print(f" ✔️ Table [dbo.{table_name}] successfully written and synchronized.")

        print("\n🔒 Re-enabling all relational database constraints...")
        conn.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? CHECK CONSTRAINT ALL'"))

    print("="*60)
    print("🎉 SUCCESS: Master unified compliance sync pipeline completed!")
    print("="*60)

if __name__ == "__main__":
    sync_processed_data_to_sql()