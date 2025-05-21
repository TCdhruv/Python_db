#!/usr/bin/env python
# coding: utf-8


# In[1]:


import pandas as pd
import plotly.express as px
import base64
from dash import dcc, html, Input, Output, State, dash_table
from jupyter_dash import JupyterDash
from pyqvd import QvdTable

# Load data from QVD
qvd_file_path = 'BOOKING_REP22.qvd'
qvd_table = QvdTable.from_qvd(qvd_file_path)
df = qvd_table.to_pandas()

# Data prep
df['TOUR_START_DATE'] = pd.to_datetime(df['TOUR_START_DATE'], errors='coerce')
df['TOUR_MONTH'] = df['TOUR_START_DATE'].dt.to_period('M').astype(str)
df['Total_Sale_Value'] = df['LAND_SALE_VALUE'].fillna(0) + df['AIR_SALE_VALUE'].fillna(0)

zone_options = [{'label': z, 'value': z} for z in df['ZONE'].dropna().unique()]
branch_options = [{'label': b, 'value': b} for b in df['BRANCH'].dropna().unique()]
month_options = [{'label': m, 'value': m} for m in df['TOUR_MONTH'].dropna().unique()]

USERS = {"dhruv": "travel123", "john": "john2024", "alice": "passalice"}

app = JupyterDash(__name__, suppress_callback_exceptions=True)

def login_layout():
    return html.Div([
        html.Div([
            html.H2("Login", style={"textAlign": "center"}),
            dcc.Input(id='username-input', placeholder='Username', style={'width': '100%', 'padding': '10px'}),
            dcc.Input(id='password-input', type='password', placeholder='Password', style={'width': '100%', 'padding': '10px'}),
            html.Button('Login', id='login-button', style={'width': '100%', 'marginTop': '10px'}),
            html.Div(id='login-message', style={'color': 'red', 'textAlign': 'center'})
        ], style={'width': '350px', 'margin': 'auto', 'padding': '40px'})
    ], style={"height": "100vh", "display": "flex", "justifyContent": "center", "alignItems": "center"})

def dashboard_layout():
    return html.Div([
        html.H1("Booking Dashboard", style={'textAlign': 'center'}),
        html.Div([
            html.Div([html.Label("Zone"), dcc.Dropdown(id='zone-filter', options=zone_options, style={'width': '300px'})]),
            html.Div([html.Label("Branch"), dcc.Dropdown(id='branch-filter', options=branch_options, style={'width': '300px'})]),
            html.Div([html.Label("Month"), dcc.Dropdown(id='month-filter', options=month_options, style={'width': '300px'})])
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '20px'}),
        html.Div(id='kpi-cards'),
        dcc.Graph(id='monthly-trends'),
        dcc.Graph(id='revenue-bar'),
        dcc.Graph(id='pie-chart'),
        dcc.Graph(id='scatter-chart'),
        html.H3("Full Dataset Viewer"),
        html.Div(id='data-table-container'),
        html.Button('Logout', id='logout-button', style={'marginTop': '30px'})
    ])

app.layout = html.Div([
    dcc.Store(id='auth-store', data={'logged_in': False}),
    html.Div(id='layout-container')
])

@app.callback(Output('layout-container', 'children'), Input('auth-store', 'data'))
def switch_layout(auth):
    return dashboard_layout() if auth.get('logged_in') else login_layout()

@app.callback(
    Output('auth-store', 'data'),
    Output('login-message', 'children'),
    Input('login-button', 'n_clicks'),
    State('username-input', 'value'),
    State('password-input', 'value'),
    prevent_initial_call=True
)
def do_login(n, user, pw):
    if user in USERS and USERS[user] == pw:
        return {'logged_in': True}, ""
    return {'logged_in': False}, "Invalid login."

@app.callback(
    Output('auth-store', 'data', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def do_logout(n): return {'logged_in': False}

@app.callback(
    Output('kpi-cards', 'children'),
    Output('monthly-trends', 'figure'),
    Output('revenue-bar', 'figure'),
    Output('pie-chart', 'figure'),
    Output('scatter-chart', 'figure'),
    Output('data-table-container', 'children'),
    Input('zone-filter', 'value'),
    Input('branch-filter', 'value'),
    Input('month-filter', 'value')
)
def update_dashboard(zone, branch, month):
    dff = df.copy()
    if zone:
        dff = dff[dff['ZONE'] == zone]
    if branch:
        dff = dff[dff['BRANCH'] == branch]
    if month:
        dff = dff[dff['TOUR_MONTH'] == month]

    total = dff['Total_Sale_Value'].sum()
    count = dff.shape[0]
    avg = dff['Total_Sale_Value'].mean()

    kpis = html.Div([
        html.Div([html.H4("Total Bookings"), html.P(f"{count:,}")]),
        html.Div([html.H4("Total Revenue"), html.P(f"{total:,.2f}")]),
        html.Div([html.H4("Average Value"), html.P(f"{avg:,.2f}")])
    ], style={'display': 'flex', 'justifyContent': 'space-around'})

    monthly = px.line(dff.groupby('TOUR_MONTH')['Total_Sale_Value'].sum().reset_index(),
                      x='TOUR_MONTH', y='Total_Sale_Value', title='Monthly Booking Trends')

    bar = px.bar(dff.groupby('TOUR_MONTH')['Total_Sale_Value'].sum().reset_index(),
                 x='TOUR_MONTH', y='Total_Sale_Value', title='Revenue by Month')

    pie = px.pie(dff, names='ASTRA BOOKING', title='ASTRA Booking Distribution')

    scatter = px.scatter(dff, x='LAND_SALE_VALUE', y='AIR_SALE_VALUE', color='ZONE', title='Land vs Air Sales')

    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in dff.columns],
        data=dff.to_dict('records'),
        page_size=10,
        style_table={'width': '100%', 'overflowX': 'scroll', 'overflowY': 'scroll', 'height': '300px'},
        style_cell={
            'textAlign': 'left', 'minWidth': '160px', 'width': '160px', 'maxWidth': '220px',
            'overflow': 'hidden', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap'
        }
    )

    csv_string = dff.to_csv(index=False)
    b64 = base64.b64encode(csv_string.encode()).decode()
    download_link = html.A(
        "Download Filtered Dataset (CSV)",
        href=f'data:text/csv;base64,{b64}',
        download="filtered_data.csv",
        target="_blank",
        style={'marginTop': '10px', 'display': 'block', 'fontWeight': 'bold'}
    )

    return kpis, monthly, bar, pie, scatter, html.Div([table, html.Br(), download_link], style={'width': '100%'})

app.run_server(mode='inline', debug=True)

