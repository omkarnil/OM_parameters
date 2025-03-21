import streamlit as st
import pandas as pd
import re
import uuid

# Load the Excel sheet once
excel_path = 'Consent Paramters.xlsx'
df = pd.read_excel(excel_path)

# Conversion factors
unit_conversion = {
    'days': 1,
    'months': 30,
    'years': 365
}

consent_list = []

def convert_to_days(value):
    value = str(value).strip().lower()
    conversions = {
        'na': 0,
        'coterminous with loan tenure': 10 * unit_conversion['years']
    }
    if value in conversions:
        return conversions[value]
    match = re.match(r'^(\d+)\s*(days|months|years)$', value)
    if match:
        number, unit = match.groups()
        return int(number) * unit_conversion[unit]
    return 0

# Custom CSS to enhance appearance
st.markdown("""
    <style>
        .stApp {
            background-color: #e3f2fd;
            color: #333;
            font-family: 'Arial', sans-serif;
        }
        .main-title {
            color: #1976d2;
            text-align: center;
            font-size: 42px;
            margin: 20px 0 40px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .param-container {
            background: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            width: 80%;
        }
        .param {
            font-size: 18px;
            color: #424242;
            margin: 8px 0;
        }
        .param-title {
            font-weight: 600;
            color: #1976d2;
        }
        .exceed {
            color: #d32f2f;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            color: #616161;
            font-size: 14px;
            margin-top: 40px;
            padding: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit app title
st.markdown('<h1 class="main-title">OM Code Parameter Viewer</h1>', unsafe_allow_html=True)

# Button Selection
option = st.radio("Choose an action:", ('Check Limit', 'Create Consent'))

if option == 'Check Limit':
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
        for col, value in filtered_df.iloc[0].items():
            st.markdown(f'<div class="param"><span class="param-title">{col}:</span> {value}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif option == 'Create Consent':
    st.write("### Create Consent")
    with st.form(key='create_consent_form'):
        om_code = st.selectbox('Select OM Code:', df['OM Code'].astype(str).unique())
        purpose_code = st.text_input("Purpose Code")
        purpose_text = st.text_area("Purpose Text")
        max_frequency = st.text_input("Maximum Frequency")
        max_fi_data_range = st.text_input("Maximum FI Data Range")
        max_consent_validity = st.text_input("Maximum Consent Validity")
        max_data_life = st.text_input("Maximum Data Life")
        submit_consent = st.form_submit_button(label='Create Consent')

    # Check limits and create consent
    if submit_consent:
        filtered_df = df[df['OM Code'].astype(str) == om_code]
        max_values = {
            "Maximum Frequency": convert_to_days(filtered_df['Maximum Frequency'].values[0]) if pd.notna(filtered_df['Maximum Frequency'].values[0]) else 0,
            "Maximum FI Data Range": convert_to_days(filtered_df['Maximum FI Data Range'].values[0]) if pd.notna(filtered_df['Maximum FI Data Range'].values[0]) else 0,
            "Maximum Consent Validity": convert_to_days(filtered_df['Maximum Consent Validity'].values[0]) if pd.notna(filtered_df['Maximum Consent Validity'].values[0]) else 0,
            "Maximum Data Life": convert_to_days(filtered_df['Maximum Data Life'].values[0]) if pd.notna(filtered_df['Maximum Data Life'].values[0]) else 0
        }
        
        input_values = {
            "Maximum Frequency": max_frequency,
            "Maximum FI Data Range": max_fi_data_range,
            "Maximum Consent Validity": max_consent_validity,
            "Maximum Data Life": max_data_life
        }

        results = []
        for key, input_value in input_values.items():
            if input_value:
                input_days = convert_to_days(input_value)
                max_days = max_values[key]
                if input_days > max_days:
                    results.append(f"{key} exceeded: {input_days} days > {max_days} days")
        
        if results:
            for res in results:
                st.markdown(f'<div class="exceed">{res}</div>', unsafe_allow_html=True)
        else:
            consent_id = str(uuid.uuid4())
            consent_list.append({
                'Consent ID': consent_id,
                'OM Code': om_code,
                'Purpose Code': purpose_code,
                'Purpose Text': purpose_text,
                'Maximum Frequency': max_frequency,
                'Maximum FI Data Range': max_fi_data_range,
                'Maximum Consent Validity': max_consent_validity,
                'Maximum Data Life': max_data_life
            })
            st.success(f"Consent Created Successfully! Consent ID: {consent_id}")

# Display consent list
if consent_list:
    st.write("### Consent List")
    st.write(pd.DataFrame(consent_list))

# Footer
st.markdown('<div class="footer">Created with ❤️ by Omkarni</div>', unsafe_allow_html=True)
