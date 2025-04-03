import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#reading the CSV file
try:
    data = pd.read_csv("Population of India.csv")
except FileNotFoundError:
    messagebox.showerror("Error", "Dataset not found! Make sure 'Population of India.csv' is in the correct directory.")
    exit()
except Exception as e:
    messagebox.showerror("Error", f"An error occurred while loading the dataset: {e}")
    exit()

#Creating a mapping of old to new column names
column_cleanup = {
    'Sl No': 'serial_no',
    'State/UT': 'state',
    'Population[50]': 'population',
    'Percent (%)': 'percent_total',
    'Male': 'male',
    'Female': 'female',
    'Difference between male and female': 'gender_gap',
    'Sex ratio': 'sex_ratio',
    'Rural[51]': 'rural_pop',
    'Urban[51]': 'urban_pop',
    'Area[52] (km2)': 'area_km2',
    'Density (per km2)': 'density_km2'
}

# Renaming the columns
data = data.rename(columns=column_cleanup)

print("\nCleaned columns:")
print(data.columns.tolist())

#Checking for missing values
print("\nMissing values in each column:")
print(data.isnull().sum())

# Handling missing values (if any exist)
if data.isnull().sum().sum() > 0:
    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
    data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())

    # For state names (if missing), filling with "Unknown"
    if 'state' in data.columns:
        data['state'] = data['state'].fillna('Unknown')

    print("\nAfter handling missing values:")
    print(data.isnull().sum())

#Converting data types if needed
pop_cols = ['population', 'rural_pop', 'urban_pop', 'male', 'female']
data[pop_cols] = data[pop_cols].astype('int64')

#Verifying the cleaned data
print("\nFirst 5 rows after cleaning:")
print(data.head())

# Identify and separate the total row
total_row = data[data['state'].str.contains('Total|India', case=False, regex=True)]
states_data = data[~data['state'].str.contains('Total|India', case=False, regex=True)]

# Sort data by population (descending)
data = states_data.sort_values('population', ascending=False)
print(data.to_string())

data['color'] = data['sex_ratio'].apply(lambda x: 'red' if x < 1000 else 'blue')
print(data.to_string())

# Tkinter GUI
root = tk.Tk()
root.title("Indian Population Data Explorer")
root.geometry("1200x700")
root.configure(bg="#f0f0f0")

# Styling
style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=10)
style.configure("TLabel", font=("Arial", 14), background="#f0f0f0")
style.configure("TCombobox", font=("Arial", 12))


def plot_data():
    selected_state = state_var.get()
    state_row = states_data[states_data['state'] == selected_state].iloc[0]
    # Clear previous plots
    for widget in plot_frame.winfo_children():
        widget.destroy()

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), constrained_layout=True)
    fig.suptitle(f"Data for {selected_state}", fontsize=18, fontweight='bold')

    # Population Percentage Pie Chart
    axes[0].pie([state_row['percent_total'], 100 - state_row['percent_total']],
                labels=[selected_state, 'Rest of India'], autopct='%1.1f%%', colors=['#4CAF50', '#B0BEC5'])
    axes[0].set_title("% of India's Population", fontsize=14, fontweight='bold')
    # Male vs Female Pie Chart
    axes[1].pie([state_row['male'], state_row['female']], labels=['Male', 'Female'], autopct='%1.1f%%',
                colors=['#42A5F5', '#FF7043'])
    axes[1].set_title("Gender Distribution", fontsize=14, fontweight='bold')
    # Urban vs Rural Bar Chart
    axes[2].bar(['Rural', 'Urban'], [state_row['rural_pop'], state_row['urban_pop']], color=['#388E3C', '#FFA000'])
    axes[2].set_title("Urban vs Rural Population", fontsize=14, fontweight='bold')

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


# Dropdown Menu
header_label = ttk.Label(root, text="Indian Population Data Explorer", font=("Arial", 18, "bold"), background="#f0f0f0")
header_label.pack(pady=10)

description_label = ttk.Label(root, text="Welcome to GovDat. We provide population insights of each state in India.",
                              font=("Arial", 12), background="#f0f0f0")
description_label.pack(pady=5)

state_var = tk.StringVar()
state_dropdown = ttk.Combobox(root, textvariable=state_var, values=list(states_data['state']), font=("Arial", 12))
state_dropdown.pack(pady=10)
state_dropdown.set("Select a State")

tk.Button(root, text="Show Data", command=plot_data, font=("Arial", 12), bg="#2196F3", fg="white", padx=10,
          pady=5).pack(pady=20)

# Frame for Matplotlib Plots
plot_frame = tk.Frame(root, bg="#f0f0f0")
plot_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

root.mainloop()


# Unit Testing
def test_data_loading():
    try:
        test_data = pd.read_csv("Population of India.csv")
        assert not test_data.empty, "Dataset should not be empty"
    except Exception as e:
        assert False, f"Data loading failed: {e}"

def test_column_renaming():
    expected_columns = set(column_cleanup.values())
    actual_columns = set(data.columns)
    assert expected_columns.issubset(actual_columns), "Column renaming failed"

def test_plot_data():
    try:
        state_var.set("Invalid State")
        plot_data()
    except Exception as e:
        assert False, f"plot_data function failed: {e}"



