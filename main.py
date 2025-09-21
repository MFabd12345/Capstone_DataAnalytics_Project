# ================================
# main.py
# Diabetes Data Analysis Project (Power BI-ready)
# ================================

# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import mysql.connector

# -------------------------------
# Step 1: Load the datasets
# -------------------------------
try:
    df = pd.read_csv("diabetic_data.csv")
    mapping = pd.read_csv("IDS_mapping.csv")
    print("✅ Files Loaded Successfully")
except Exception as e:
    print("❌ Error loading files:", e)
    exit()

# -------------------------------
# Step 1.1: Import CSV into MySQL
# -------------------------------
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MFabd@021786",
        database="diabetes_db"
    )
    cursor = conn.cursor()
    columns = ', '.join([f"`{col}`" for col in df.columns])
    placeholders = ', '.join(['%s'] * len(df.columns))
    sql = f"INSERT INTO patients ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE encounter_id=encounter_id"

    for _, row in df.iterrows():
        cursor.execute(sql, tuple(row))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All data inserted into MySQL successfully (duplicates safely handled)!")
except Exception as e:
    print("❌ MySQL Insertion Error:", e)

# -------------------------------
# Step 2: Show basic information
# -------------------------------
print("\n📊 Dataset Information")
print("Main Data Shape:", df.shape)
print("Mapping Shape:", mapping.shape)
print("\n🔹 Total Patients:", len(df))
print("\n🔹 Missing values per column:")
print(df.isnull().sum())
print("\n🔹 Readmission distribution:")
print(df['readmitted'].value_counts())
print("\n🔹 Average hospital stay length:")
print(df['time_in_hospital'].mean())

# -------------------------------
# Step 3: Create folder for charts
# -------------------------------
if not os.path.exists("charts"):
    os.makedirs("charts")

# -------------------------------
# Step 4: Visualization
# -------------------------------
sns.set(style="whitegrid")

# Readmission Distribution
plt.figure(figsize=(6,4))
df['readmitted'].value_counts().plot(kind='bar', color=['green','orange','red'])
plt.title("Patient Readmission Distribution")
plt.xlabel("Readmission Status")
plt.ylabel("Number of Patients")
plt.savefig("charts/readmission_distribution.png")
plt.show()

# Gender vs Readmission
plt.figure(figsize=(6,4))
sns.countplot(x="gender", hue="readmitted", data=df, palette="Set2")
plt.title("Gender vs Readmission")
plt.savefig("charts/gender_vs_readmission.png")
plt.show()

# Age Distribution
plt.figure(figsize=(8,4))
df['age'].value_counts().sort_index().plot(kind='bar', color='skyblue')
plt.title("Age Group Distribution")
plt.xlabel("Age Range")
plt.ylabel("Number of Patients")
plt.savefig("charts/age_distribution.png")
plt.show()

# Hospital Stay Distribution
plt.figure(figsize=(6,4))
sns.histplot(df['time_in_hospital'], bins=15, kde=True, color='purple')
plt.title("Distribution of Hospital Stay Length")
plt.xlabel("Days in Hospital")
plt.ylabel("Number of Patients")
plt.savefig("charts/hospital_stay_distribution.png")
plt.show()

# -------------------------------
# Step 5: Save analysis to Excel (Power BI-ready)
# -------------------------------
with pd.ExcelWriter("diabetes_hospital_report.xlsx") as writer:
    # Original data
    df.to_excel(writer, sheet_name="Diabetic Data", index=False)
    mapping.to_excel(writer, sheet_name="IDS Mapping", index=False)
    df.describe(include="all").to_excel(writer, sheet_name="Summary Stats")
    
    # ---------------------------
    # KPIs Sheet for Power BI
    # ---------------------------
    kpis = pd.DataFrame({
        "Metric": [
            "Total Patients",
            "Average Hospital Stay",
            "Readmission NO",
            "Readmission <30",
            "Readmission >30"
        ],
        "Value": [
            len(df),
            df['time_in_hospital'].mean(),
            df['readmitted'].value_counts().get("NO", 0),
            df['readmitted'].value_counts().get("<30", 0),
            df['readmitted'].value_counts().get(">30", 0)
        ]
    })
    kpis.to_excel(writer, sheet_name="KPIs", index=False)
    
    # ---------------------------
    # Pivot Data Sheet for Power BI
    # ---------------------------
    pivot_gender = df.groupby(['gender','readmitted']).size().reset_index(name='Count')
    pivot_age = df.groupby(['age','readmitted']).size().reset_index(name='Count')
    pivot_medications = df.groupby(['readmitted'])['num_medications'].mean().reset_index(name='Avg_Medications')
    
    pivot_gender.to_excel(writer, sheet_name="Pivot_Gender", index=False)
    pivot_age.to_excel(writer, sheet_name="Pivot_Age", index=False)
    pivot_medications.to_excel(writer, sheet_name="Pivot_Medications", index=False)

print("\n📂 Report saved as 'diabetes_hospital_report.xlsx'")
print("📂 Charts saved inside 'charts/' folder")
print("✅ Excel is now Power BI-ready with KPIs and Pivot data")
