import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash(
    __name__,
     external_stylesheets=[dbc.themes.BOOTSTRAP],
     requests_pathname_prefix='/car_dash/')

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink('Sobre', href='#')),
        dbc.NavItem(dbc.NavLink('Análise dos carros'))
    ],
    brand='Cowvin Cars',
    brand_href='#',
    color='primary',
    dark=True
)

app.layout = html.Div([
    navbar,
    html.Div([
        html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
        dcc.Dropdown(
            options=[{'label': country, 'value': country} for country in df.country.unique()],
            value='Canada',
            id='dropdown-selection'
        ),
        dcc.Graph(id='graph-content')
    ])
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')


if __name__ == '__main__':
    app.run(debug=True)