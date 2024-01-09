from db import db
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_auth
import plotly.graph_objects as go
import tab1
import tab2
import tab3


df = db()
df.merge()

USERNAME_PASSWORD = [['user', 'pass']]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD)

app.layout = html.Div([html.Div([dcc.Tabs(id='tabs', value='tab-1', children=[
    dcc.Tab(label='Sprzedaż globalna', value='tab-1'),
    dcc.Tab(label='Produkty', value='tab-2'),
    dcc.Tab(label='Kanaly sprzedazy', value='tab-3')
]),
    html.Div(id='tabs-content')
], style={'width': '80%', 'margin': 'auto'})],
    style={'height': '100%'})


@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):

    if tab == 'tab-1':
        return tab1.render_tab(df.merged)
    elif tab == 'tab-2':
        return tab2.render_tab(df.merged)
    elif tab == 'tab-3':
        return tab3.render_tab(df.merged)

# tab1 callbacks


@app.callback(Output('bar-sales', 'figure'),
              [Input('sales-range', 'start_date'), Input('sales-range', 'end_date')])
def tab1_bar_sales(start_date, end_date):

    truncated = df.merged[(df.merged['tran_date'] >= start_date) & (
        df.merged['tran_date'] <= end_date)]
    grouped = truncated[truncated['total_amt'] > 0].groupby([pd.Grouper(
        key='tran_date', freq='M'), 'Store_type'])['total_amt'].sum().round(2).unstack()

    traces = []
    for col in grouped.columns:
        traces.append(go.Bar(x=grouped.index, y=grouped[col], name=col, hoverinfo='text',
                             hovertext=[f'{y/1e3:.2f}k' for y in grouped[col].values]))

    data = traces
    fig = go.Figure(data=data, layout=go.Layout(
        title='Przychody', barmode='stack', legend=dict(x=0, y=-0.5)))

    return fig


@app.callback(Output('choropleth-sales', 'figure'),
              [Input('sales-range', 'start_date'), Input('sales-range', 'end_date')])
def tab1_choropleth_sales(start_date, end_date):

    truncated = df.merged[(df.merged['tran_date'] >= start_date) & (
        df.merged['tran_date'] <= end_date)]
    grouped = truncated[truncated['total_amt'] > 0].groupby(
        'country')['total_amt'].sum().round(2)

    trace0 = go.Choropleth(colorscale='Viridis', reversescale=True,
                           locations=grouped.index, locationmode='country names',
                           z=grouped.values, colorbar=dict(title='Sales'))
    data = [trace0]
    fig = go.Figure(data=data, layout=go.Layout(title='Mapa', geo=dict(
        showframe=False, projection={'type': 'natural earth'})))

    return fig

# tab2 callbacks


@app.callback(Output('barh-prod-subcat', 'figure'),
              [Input('prod_dropdown', 'value')])
def tab2_barh_prod_subcat(chosen_cat):

    grouped = df.merged[(df.merged['total_amt'] > 0) & (df.merged['prod_cat'] == chosen_cat)].pivot_table(
        index='prod_subcat', columns='Gender', values='total_amt', aggfunc='sum').assign(_sum=lambda x: x['F']+x['M']).sort_values(by='_sum').round(2)

    traces = []
    for col in ['F', 'M']:
        traces.append(
            go.Bar(x=grouped[col], y=grouped.index, orientation='h', name=col))

    data = traces
    fig = go.Figure(data=data, layout=go.Layout(
        barmode='stack', margin={'t': 20, }))
    return fig

# tab3 callbacks


@app.callback(Output('age-customers-bar', 'figure'),
              [Input('age-customers-range', 'value'), Input('store_type_dropdown', 'value')])
def tab3_age_customer_data(values, store_type_chosen):

    store_types_color = {
        "Flagship store": "red",
        "MBR": "green",
        "e-Shop": "blue",
        "TeleShop": "gray",
    }
    truncated = df.merged[(df.merged['age'] >= values[0]) & (
        df.merged['age'] <= values[1]) & (df.merged['Store_type'] == store_type_chosen)]

    grouped_customers_age = truncated[truncated['total_amt'] > 0].pivot_table(
        values='total_amt', columns=truncated['age'], index=truncated['Store_type'], aggfunc=sum)

    fig_customers_age = go.Figure(data=[
        go.Bar(name=store_type_chosen, x=grouped_customers_age.columns,
               y=[value for value in grouped_customers_age.values[0]], marker_color=store_types_color[store_type_chosen])
    ], layout=go.Layout(title='Sprzedaź w wybranym kanale sprzedazy z uwzglednieniem wieku klientów'))

    fig_customers_age.update_layout(showlegend=True)

    return fig_customers_age


@app.callback(Output('channel-sales-customers', 'figure'),
              [Input('store_type_dropdown', 'value')])
def tab3_customers_sex_sales_channel(store_type_chosen):

    store_types_color = {
        "Flagship store": "red",
        "MBR": "green",
        "e-Shop": "blue",
        "TeleShop": "gray",
    }

    truncated = df.merged[df.merged['Store_type'] == store_type_chosen]

    grouped_customers = truncated[truncated['total_amt'] > 0].pivot_table(
        values='total_amt', columns=truncated['Gender'], index=truncated['Store_type'], aggfunc=sum)

    fig_customers = go.Figure(data=[
        go.Bar(name=store_type_chosen, x=grouped_customers.columns,
               y=[value for value in grouped_customers.values[0]], marker_color=store_types_color[store_type_chosen])
    ], layout=go.Layout(title='Sprzedaź w wybranym kanale sprzedazy z uwzglednieniem płci klientów'))

    fig_customers.update_layout(showlegend=True)

    return fig_customers


if __name__ == '__main__':
    app.run_server(debug=True)
