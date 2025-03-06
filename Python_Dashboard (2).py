#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.graph_objects as go
import os


# In[2]:


print(os.path.abspath('BOOKING_REP22.qvd'))


# In[3]:


from pyqvd import QvdTable

# Path to your QVD file
qvd_file_path = 'BOOKING_REP22.qvd'

# Load the QVD file
qvd_table = QvdTable.from_qvd(qvd_file_path)


# In[4]:


# Convert the QvdTable to a Pandas DataFrame
df = qvd_table.to_pandas()

# Display the first few rows of the DataFrame
print(df.head(10))


# In[5]:


df.info()


# In[6]:


import seaborn as sns
import matplotlib.pyplot as plt


# In[7]:


import streamlit as st
import pandas as pd
import plotly.express as px

# File Uploader
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    with st.spinner("Reading Excel file..."):
        # Read Excel file into a Pandas DataFrame
        df = pd.read_excel(uploaded_file)

    st.success("Excel file successfully loaded!")

    # Data Cleaning & Transformation
    df = df.dropna(subset=['AIR_SALE_VALUE', 'LAND_SALE_VALUE'])  # Remove missing values
    df['Total_Sale_Value'] = df['AIR_SALE_VALUE'] + df['LAND_SALE_VALUE']
    df['TOUR_MONTH'] = df['TOUR_START_DATE'].dt.strftime('%Y-%m')  # Format as "YYYY-MM"

    # Unique values for filters
    zone_options = df['ZONE'].unique()
    branch_options = df['BRANCH NAME'].unique()
    month_options = df['TOUR_MONTH'].dropna().unique()

    # Streamlit App
    st.title("Booking Dashboard 2")

    # Filters
    selected_zone = st.selectbox("Select Zone:", options=zone_options)
    selected_branch = st.selectbox("Select Branch:", options=branch_options)
    selected_month = st.selectbox("Select Month:", options=month_options)

    # Filter dataset
    filtered_df = df.copy()
    if selected_zone:
        filtered_df = filtered_df[filtered_df['ZONE'] == selected_zone]
    if selected_branch:
        filtered_df = filtered_df[filtered_df['BRANCH NAME'] == selected_branch]
    if selected_month:
        filtered_df = filtered_df[filtered_df['TOUR_MONTH'] == selected_month]

    # Summary Stats
    total_bookings = filtered_df.shape[0]
    total_revenue = filtered_df['Total_Sale_Value'].sum()
    avg_sale_value = filtered_df['Total_Sale_Value'].mean()

    # Display Summary Stats
    st.subheader("Summary Stats")
    st.write(f"Total Bookings: {total_bookings:,}")
    st.write(f"Total Revenue (INR): {total_revenue:,.2f}")
    st.write(f"Average Sale Value (INR): {avg_sale_value:,.2f}")

    # Monthly Booking Trends
    monthly_booking_trends = px.line(filtered_df.groupby('TOUR_MONTH')['Total_Sale_Value'].sum().reset_index(),
                                     x='TOUR_MONTH', y='Total_Sale_Value',
                                     title="Monthly Booking Trends")
    st.plotly_chart(monthly_booking_trends)

    # Revenue by Month
    revenue_by_month = px.bar(filtered_df.groupby('TOUR_MONTH')['Total_Sale_Value'].sum().reset_index(),
                              x='TOUR_MONTH', y='Total_Sale_Value',
                              title="Revenue by Month")
    st.plotly_chart(revenue_by_month)

    # Booking & Cancellation Trends
    booking_trends = px.line(filtered_df.groupby('TOUR_START_DATE')['Total_Sale_Value'].sum().reset_index(),
                             x='TOUR_START_DATE', y='Total_Sale_Value', title="Booking Trends Over Time")
    st.plotly_chart(booking_trends)


# In[8]:


import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output




# Data Cleaning & Transformation
df = df.dropna(subset=['AIR_SALE_VALUE', 'LAND_SALE_VALUE'])  # Remove missing values
df['Total_Sale_Value'] = df['AIR_SALE_VALUE'] + df['LAND_SALE_VALUE']

# Convert Dates
df['TOUR_START_DATE'] = pd.to_datetime(df['TOUR_START_DATE'])

# Extract Month from TOUR_START_DATE
df['TOUR_MONTH'] = df['TOUR_START_DATE'].dt.strftime('%Y-%m')  # Format as "YYYY-MM"

# Unique values for filters
zone_options = [{'label': zone, 'value': zone} for zone in df['ZONE'].unique()]
branch_options = [{'label': branch, 'value': branch} for branch in df['BRANCH NAME'].unique()]
month_options = [{'label': month, 'value': month} for month in df['TOUR_MONTH'].dropna().unique()]

# Initialize Dash App
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Advanced Booking Dashboard", style={'textAlign': 'center'}),

    # Filters
    html.Div([
        html.Label("Select Zone:"),
        dcc.Dropdown(id='zone-filter', options=zone_options, value=None, clearable=True),
        
        html.Label("Select Branch:"),
        dcc.Dropdown(id='branch-filter', options=branch_options, value=None, clearable=True),

        html.Label("Select Month:"),
        dcc.Dropdown(id='month-filter', options=month_options, value=None, clearable=True),

    ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px 0'}),

    # Summary Cards
    html.Div(id='summary-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px 0'}),

    # Monthly Booking Trends
    dcc.Graph(id='monthly-booking-trends'),

    # Revenue by Month
    dcc.Graph(id='revenue-by-month'),

    # Revenue Heatmap
    dcc.Graph(id='revenue-heatmap'),

    # Booking Status Trends
    dcc.Graph(id='booking-trends'),
])

# Callback to update dashboard based on filters
@app.callback(
    [Output('summary-cards', 'children'),
     Output('monthly-booking-trends', 'figure'),
     Output('revenue-by-month', 'figure'),
     Output('revenue-heatmap', 'figure'),
     Output('booking-trends', 'figure')],
    [Input('zone-filter', 'value'),
     Input('branch-filter', 'value'),
     Input('month-filter', 'value')]
)
def update_dashboard(selected_zone, selected_branch, selected_month):
    # Filter dataset
    filtered_df = df.copy()
    if selected_zone:
        filtered_df = filtered_df[filtered_df['ZONE'] == selected_zone]
    if selected_branch:
        filtered_df = filtered_df[filtered_df['BRANCH NAME'] == selected_branch]
    if selected_month:
        filtered_df = filtered_df[filtered_df['TOUR_MONTH'] == selected_month]

    # Summary Stats
    total_bookings = filtered_df.shape[0]
    total_revenue = filtered_df['Total_Sale_Value'].sum()
    avg_sale_value = filtered_df['Total_Sale_Value'].mean()

    summary_cards = html.Div([
        html.Div([
            html.H3("Total Bookings"),
            html.P(f"{total_bookings:,}")
        ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),

        html.Div([
            html.H3("Total Revenue (INR)"),
            html.P(f"{total_revenue:,.2f}")
        ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),

        html.Div([
            html.H3("Average Sale Value (INR)"),
            html.P(f"{avg_sale_value:,.2f}")
        ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),
    ])

    # Monthly Booking Trends
    monthly_booking_trends = px.line(filtered_df.groupby('TOUR_MONTH')['Total_Sale_Value'].sum().reset_index(),
                                     x='TOUR_MONTH', y='Total_Sale_Value', 
                                     title="Monthly Booking Trends")

    # Revenue by Month
    revenue_by_month = px.bar(filtered_df.groupby('TOUR_MONTH')['Total_Sale_Value'].sum().reset_index(),
                              x='TOUR_MONTH', y='Total_Sale_Value',
                              title="Revenue by Month")

    # Revenue Heatmap
    revenue_heatmap = px.density_heatmap(filtered_df, x='ZONE', y='BRANCH NAME', z='Total_Sale_Value',
                                         title="Revenue Heatmap (Zone vs. Branch)",
                                         labels={'Total_Sale_Value': 'Total Revenue (INR)'})

    # Booking & Cancellation Trends
    booking_trends = px.line(filtered_df.groupby('TOUR_START_DATE')['Total_Sale_Value'].sum().reset_index(),
                             x='TOUR_START_DATE', y='Total_Sale_Value', title="Booking Trends Over Time")

    return summary_cards, monthly_booking_trends, revenue_by_month, revenue_heatmap, booking_trends

# Run the Dashboard
if __name__ == '__main__':
    app.run_server(debug=True)    


# In[ ]:





# In[ ]:




