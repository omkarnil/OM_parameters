import streamlit as st
import pandas as pd
import re

# Load the Excel sheet once
excel_path = 'Consent Paramters.xlsx'
df = pd.read_excel(excel_path)

# Conversion factors
unit_conversion = {'days': 1, 'months': 30, 'years': 365}

def convert_to_days(value):
    value = str(value).strip().lower()
    conversions = {'na': 0, 'coterminous with loan tenure': 10 * unit_conversion['years']}
    if value in conversions:
        return conversions[value]
    match = re.match(r'(\d+)\s*(days|months|years)', value)
    if match:
        number, unit = match.groups()
        return int(number) * unit_conversion[unit]
    return 0

# Custom CSS to enhance appearance
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            font-family: 'Arial', sans-serif;
        }
        .main-title {
            color: #1976d2;
            text-align: center;
            font-size: 50px;
            margin: 20px 0 40px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        .param-container {
            background: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            width: 90%;
            max-width: 800px;
        }
        .param {
            font-size: 18px;
            color: #424242;
            margin: 10px 0;
        }
        .param-title {
            font-weight: 700;
            color: #1976d2;
        }
        .exceed {
            color: #d32f2f;
            font-weight: bold;
            font-size: 18px;
            margin: 10px 0;
        }
        .footer {
            text-align: center;
            color: #616161;
            font-size: 14px;
            margin-top: 50px;
            padding: 10px 0;
            background: #1976d2;
            color: #ffffff;
            border-radius: 0 0 15px 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit app title
st.markdown('<h1 class="main-title">OM Code wise Parameter Viewer - Consumer Protect</h1>', unsafe_allow_html=True)

# Select OM Code
om_codes = df['OM Code'].astype(str).unique()
om_code = st.selectbox('Select OM Code:', om_codes)

# Display details for the selected OM Code
filtered_df = df[df['OM Code'].astype(str) == om_code]
if filtered_df.empty:
    st.error('Invalid OM Code selected. No data found.')
else:
    st.markdown('<div class="param-container">', unsafe_allow_html=True)
    st.write(f'### Parameters for OM Code: {om_code}')
    max_values = {
        "Maximum Frequency": filtered_df['Maximum Frequency'].values[0] if pd.notna(filtered_df['Maximum Frequency'].values[0]) else '0',
        "Maximum FI Data Range": filtered_df['Maximum FI Data Range'].values[0] if pd.notna(filtered_df['Maximum FI Data Range'].values[0]) else '0',
        "Maximum Consent Validity": filtered_df['Maximum Consent Validity'].values[0] if pd.notna(filtered_df['Maximum Consent Validity'].values[0]) else '0',
        "Maximum Data Life": filtered_df['Maximum Data Life'].values[0] if pd.notna(filtered_df['Maximum Data Life'].values[0]) else '0'
    }
    for col, value in filtered_df.iloc[0].items():
        st.markdown(f'<div class="param"><span class="param-title">{col}:</span> {value}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Input form to check parameters
    st.write("### Enter Parameter Values")
    with st.form(key='param_form'):
        max_frequency = st.text_input("Maximum Frequency")
        max_fi_data_range = st.text_input("Maximum FI Data Range")
        max_consent_validity = st.text_input("Maximum Consent Validity")
        max_data_life = st.text_input("Maximum Data Life")
        submit_button = st.form_submit_button(label='Check Limits', use_container_width=True)

    # Check limits after form submission
    if submit_button:
        st.write("### Limit Check Results")
        results = []

        # Convert values for comparison
        input_values = {
            "Maximum Frequency": max_frequency,
            "Maximum FI Data Range": max_fi_data_range,
            "Maximum Consent Validity": max_consent_validity,
            "Maximum Data Life": max_data_life
        }
        
        for key, input_value in input_values.items():
            if input_value:
                input_days = convert_to_days(input_value)
                max_days = convert_to_days(max_values[key])
                if input_days is not None and max_days is not None and (max_days == 0 and input_days > 0 or input_days > max_days):
                    results.append(f"{key} exceeded: {input_value} > {max_values[key]}")
        
        if results:
            for res in results:
                st.markdown(f'<div class="exceed">{res}</div>', unsafe_allow_html=True)
        else:
            st.success("All parameters are within limits.")

# Footer
st.markdown('<div class="footer">Created with ❤️ by bored Omkarni</div>', unsafe_allow_html=True)
