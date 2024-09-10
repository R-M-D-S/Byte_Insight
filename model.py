import pandas as pd
# Redefine the financial data excluding rent and fuel, and adding relevant categories
data_revised = {
    'Description': ['Monthly Payroll', 'Office Supplies', 'Travel', 'Insurance', 
                    'Maintenance', 'Utilities', 'Educational Materials', 'Technology', 'Sundry Costs', 'Property Purchase'],
    'Monthly Cost (R)': [300000, 50000, 40000, 30000, 54000, 40000, 50000, 50000, 125000, 0],
    'Annual Cost (R)': [0]*10,  # To be calculated
    '2-Year Cost (R)': [0]*10   # To be calculated
}

# Convert to DataFrame
df_revised = pd.DataFrame(data_revised)

# Calculate Annual and 2-Year Costs
df_revised['Annual Cost (R)'] = df_revised['Monthly Cost (R)'] * 12
df_revised['2-Year Cost (R)'] = df_revised['Annual Cost (R)'] * 2

# Property Purchase is a one-time cost
df_revised.loc[df_revised['Description'] == 'Property Purchase', ['Annual Cost (R)', '2-Year Cost (R)']] = [4000000, 4000000]

# Show the DataFrame
df_revised
