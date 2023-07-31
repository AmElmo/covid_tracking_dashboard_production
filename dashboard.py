import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
from google.cloud import bigquery
import os
import json
import google.auth
import google.auth.transport.requests
import google.oauth2.service_account

service_account_key = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_KEY'])
credentials = google.oauth2.service_account.Credentials.from_service_account_info(service_account_key)

client = bigquery.Client(location="US", project="covid-dashboard-378011", credentials=credentials)

bigquery_ref = 'covid-dashboard-378011.covid_data_script'

# Query for the data

query = f"""
SELECT *
FROM {bigquery_ref}.`cum_caseslatest`
"""
df_1 = client.query(query).to_dataframe()

query = f"""
SELECT *
FROM {bigquery_ref}.`evol_casesalltime`
WHERE Country = 'United States of America'
ORDER BY Date_reported ASC;
"""
df_2 = client.query(query).to_dataframe()


# Build the layout for the Dash app

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    dcc.Graph(
        id='example-graph-1',
        figure={
            'data': [
                {'x': df_1['Country'], 'y': df_1['Cum_caseslatest'], 'type': 'bar', 'name': 'Data'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    ),
    dcc.Graph(
        id='example-graph-2',
        figure={
            'data': [
                {'x': df_2['Date_reported'], 'y': df_2['New_cases'], 'type': 'line', 'name': 'Value'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)