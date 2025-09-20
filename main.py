# ================================
# main.py
# Diabetes Data Analysis Project
# ================================

# Import required libraries
import pandas as pd                # For handling CSV files and dataframes
import matplotlib.pyplot as plt     # For plots
import seaborn as sns              # For beautiful charts
import os                          # To manage file paths
import mysql.connector             # For MySQL insertion

# -------------------------------
# Step 1: Load the datasets
# -------------------------------
try:
    # Load main dataset (patients data)
    df = pd.read_csv("diabetic_data.csv")
    
    # Load mapping dataset (IDs mapping, e.g., admission type details)
    mapping = pd.read_csv("IDS_mapping.csv")

    print("✅ Files Loaded Successfully")

except Exception as e:
    print("❌ Error loading files:", e)
    exit()  # Stop program if files not found

# -------------------------------
# Step 1.1: Import CSV into MySQL
# -------------------------------
try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MFabd@021786",  # <-- Put your MySQL password here
        database="diabetes_db"
    )
    cursor = conn.cursor()

    # Escape all column names using backticks to handle special characters
    columns = ', '.join([f"`{col}`" for col in df.columns])
    
    # Create placeholders for each column
    placeholders = ', '.join(['%s'] * len(df.columns))
    
    # Build SQL insert statement dynamically
    sql = f"INSERT INTO patients ({columns}) VALUES ({placeholders})"

    # Insert all rows one by one
    for _, row in df.iterrows():
        cursor.execute(sql, tuple(row))

    # Commit changes to the database
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    print("✅ Data inserted into MySQL successfully!")

except Exception as e:
    print("❌ MySQL Insertion Error:", e)

# -------------------------------
# Step 2: Show basic information
# -------------------------------
print("\n📊 Dataset Information")
print("Main Data Shape:", df.shape)        # (rows, columns)
print("Mapping Shape:", mapping.shape)     # (rows, columns)
print("\n🔹 Total Patients:", len(df))

print("\n🔹 Missing values per column:")
print(df.isnull().sum())                  # Shows count of missing values per column

print("\n🔹 Readmission distribution:")
print(df['readmitted'].value_counts())     # Count of each readmission category (NO / <30 / >30)

print("\n🔹 Average hospital stay length:")
print(df['time_in_hospital'].mean())      # Average hospital stay in days

# -------------------------------
# Step 3: Create folder for charts
# -------------------------------
if not os.path.exists("charts"):
    os.makedirs("charts")  # Create folder to save charts if it does not exist

# -------------------------------
# Step 4: Visualization
# -------------------------------
sns.set(style="whitegrid")  # Clean style for all plots

# (1) Readmission Distribution
plt.figure(figsize=(6,4))
df['readmitted'].value_counts().plot(kind='bar', color=['green','orange','red'])
plt.title("Patient Readmission Distribution")
plt.xlabel("Readmission Status")
plt.ylabel("Number of Patients")
plt.savefig("charts/readmission_distribution.png")  # Save chart
plt.show()

# (2) Gender vs Readmission
plt.figure(figsize=(6,4))
sns.countplot(x="gender", hue="readmitted", data=df, palette="Set2")
plt.title("Gender vs Readmission")
plt.savefig("charts/gender_vs_readmission.png")
plt.show()

# (3) Age Distribution
plt.figure(figsize=(8,4))
df['age'].value_counts().sort_index().plot(kind='bar', color='skyblue')
plt.title("Age Group Distribution")
plt.xlabel("Age Range")
plt.ylabel("Number of Patients")
plt.savefig("charts/age_distribution.png")
plt.show()

# (4) Hospital Stay Distribution
plt.figure(figsize=(6,4))
sns.histplot(df['time_in_hospital'], bins=15, kde=True, color='purple')
plt.title("Distribution of Hospital Stay Length")
plt.xlabel("Days in Hospital")
plt.ylabel("Number of Patients")
plt.savefig("charts/hospital_stay_distribution.png")
plt.show()

# -------------------------------
# Step 5: Save analysis to Excel
# -------------------------------
with pd.ExcelWriter("diabetes_hospital_report.xlsx") as writer:
    # Save main dataset
    df.to_excel(writer, sheet_name="Diabetic Data", index=False)
    
    # Save mapping dataset
    mapping.to_excel(writer, sheet_name="IDS Mapping", index=False)
    
    # Save summary statistics
    df.describe(include="all").to_excel(writer, sheet_name="Summary Stats")

print("\n📂 Report saved as 'diabetes_hospital_report.xlsx'")
print("📂 Charts saved inside 'charts/' folder")
