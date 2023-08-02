import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
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
SELECT
    DATE_SUB(DATE_TRUNC(Date_reported, WEEK), INTERVAL 1 DAY) AS week,
    SUM(New_cases) as total_cases
FROM
    `{bigquery_ref}.evol_casesalltime`
WHERE
    Country = 'United States of America'
GROUP BY
    week
ORDER BY
    week ASC;
"""
df_1 = client.query(query).to_dataframe()

query = f"""
SELECT
    DATE_SUB(DATE_TRUNC(Date_reported, WEEK), INTERVAL 1 DAY) AS week,
    SUM(Cumulative_deaths) as total_deaths
FROM
    `{bigquery_ref}.evol_cumdeaths`
WHERE
    Country = 'France'
GROUP BY
    week
ORDER BY
    week ASC
LIMIT 1000 OFFSET 1;
"""
df_2 = client.query(query).to_dataframe()

query = f"""
SELECT Country, Cum_deathslatest
FROM
    `{bigquery_ref}.cum_deathslatest`
ORDER BY
    Cum_deathslatest DESC
LIMIT 15;
"""
df_3 = client.query(query).to_dataframe()

query = f"""
SELECT *
FROM
    `{bigquery_ref}.top_15_new_cases_lastweek`
ORDER BY
    Incidence DESC
"""
df_4 = client.query(query).to_dataframe()

query = f"""
SELECT *
FROM
    `{bigquery_ref}.total_vaccinatedpeople_country`
ORDER BY
    Total_vaccinations DESC
LIMIT 20;
"""
df_5 = client.query(query).to_dataframe()

# Build the layout for the Dash app
# Create some random data

# Create some random data
np.random.seed(0)
df = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E'] * 200,
    'Value': np.random.rand(1000),
    'X': np.random.rand(1000),
    'Y': np.random.rand(1000),
})

# Define the layout
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.H1('COVID Dashboard (Real-Time from WHO)', style={'textAlign': 'center', 'padding': '15px'}),

    dcc.Graph(
        id='line-chart',
        figure={
            'data': [
                go.Scatter(x=df_1['week'], y=df_1['total_cases'], mode='lines', name='Line Chart')
            ],
        'layout': {
            'title': 'USA - Evolution of cases (Weekly)'
        }
        }
    ),
    dcc.Graph(
    id='line-chart2',
    figure={
        'data': [
            go.Scatter(
                x=df_2['week'],
                y=df_2['total_deaths'],
                mode='lines+markers',
                name='Line Chart',
                line=dict(color='firebrick', width=2),
                hovertemplate =
                '<i>Total deaths</i>: %{y}'+
                '<br><b>Week</b>: %{x}<br>',
                hoverinfo='name',
            )
        ],
    'layout': {
        'title': {
            'text': "France - Evolution of Deaths (Weekly)",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(
                family="Courier New, monospace",
                size=24,
                color="#7f7f7f"
            )
        },
        'xaxis': {
            'title': 'Week',
            'gridcolor': 'lightgrey',
        },
        'yaxis': {
            'title': 'Total cases',
            'gridcolor': 'lightgrey',
        },
        'plot_bgcolor': 'white',
        'showlegend': True
    }
    }
),
    dcc.Graph(
        id='bar-chart',
        figure={
            'data': [
                go.Bar(
                    x=df_3['Country'],
                    y=df_3['Cum_deathslatest'],
                    name='Bar Chart',
                    hovertemplate =
                    '<i>Total deaths</i>: %{y}'+
                    '<br><b>Country</b>: %{x}<br>',
                    hoverinfo='name',
                )
            ],
        'layout': {
            'title': {
                'text': "Top countries with most cumulated deaths",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(
                    family="Courier New, monospace",
                    size=24,
                    color="#7f7f7f"
                )
            },
            'xaxis': {
                'title': 'Country',
                'gridcolor': 'lightgrey',
            },
            'yaxis': {
                'title': 'Total deaths',
                'gridcolor': 'lightgrey',
            },
            'plot_bgcolor': 'white',
            'showlegend': True
        }
        }
    ),
        dcc.Graph(
        id='bar-chart2',
        figure={
            'data': [
                go.Bar(
                    x=df_4['Country'],
                    y=df_4['Incidence'],
                    name='Bar Chart',
                    hovertemplate =
                    '<i>Total deaths</i>: %{y}'+
                    '<br><b>Country</b>: %{x}<br>',
                    hoverinfo='name',
                )
            ],
        'layout': {
            'title': {
                'text': "Top countries with highest incidence of new cases last week",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(
                    family="Courier New, monospace",
                    size=24,
                    color="#7f7f7f"
                )
            },
            'xaxis': {
                'title': 'Country',
                'gridcolor': 'lightgrey',
            },
            'yaxis': {
                'title': 'Total deaths',
                'gridcolor': 'lightgrey',
            },
            'plot_bgcolor': 'white',
            'showlegend': True
        }
        }
    ),
    dcc.Graph(
        id='pie-chart',
        figure={
            'data': [
                go.Pie(
                    labels=df_5['Country'],
                    values=df_5['Total_vaccinations'],
                    name='Pie Chart',
                )
            ],
            'layout': {
                'title': {
                    'text': 'Total Vaccinations per Country',
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(
                        family="Courier New, monospace",
                        size=24,
                        color="#7f7f7f"
                    )
                },
                'plot_bgcolor': 'white',
                'showlegend': True
            }
        }
    ),
    dcc.Graph(
        id='box-plot',
        figure={
            'data': [
                go.Box(x=df['Category'], y=df['Value'], name='Box Plot')
            ],
        'layout': {
            'title': 'My Line Chart Title'
        }
        }
    ),
    dcc.Graph(
        id='heatmap',
        figure={
            'data': [
                go.Heatmap(z=df.corr(), x=df.columns, y=df.columns, name='Heatmap')
            ],
        'layout': {
            'title': 'My Line Chart Title'
        }
        }
    ),
    dcc.Graph(
        id='bubble-chart',
        figure={
            'data': [
                go.Scatter(x=df['X'], y=df['Y'], mode='markers',
                           marker=dict(size=df['Value']*100), name='Bubble Chart')  # Size of bubbles is scaled by 'Value'
            ],
        'layout': {
            'title': 'My Line Chart Title'
        }
        }
    ),
    dcc.Graph(
        id='area-chart',
        figure={
            'data': [
                go.Scatter(x=df['X'], y=df['Y'], mode='lines', fill='tozeroy', name='Area Chart')
            ],
        'layout': {
            'title': 'My Line Chart Title'
        }
        }
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)


'''
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

'''
