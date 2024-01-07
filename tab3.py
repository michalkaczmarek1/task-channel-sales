from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd


def render_tab(df):

    dates = pd.to_datetime(df['tran_date'], format='mixed')
    grouped = df[df['total_amt'] > 0].pivot_table(
        values='total_amt', columns=dates.dt.weekday.map({0: 'Poniedziałek', 1: 'Wtorek', 2: 'Środa',
                                                          3: 'Czwartek', 4: 'Piątek', 5: 'Sobota', 6: 'Niedziela'}), index='Store_type', aggfunc=sum
    )

    fig = go.Figure(data=[
        go.Bar(name='Flagship store', x=grouped.columns,
               y=[value for value in grouped.values[0]]),
        go.Bar(name='MBR', x=grouped.columns, y=[
               value for value in grouped.values[1]]),
        go.Bar(name='TeleShop', x=grouped.columns, y=[
               value for value in grouped.values[2]]),
        go.Bar(name='e-Shop', x=grouped.columns,
               y=[value for value in grouped.values[3]])
    ], layout=go.Layout(title='Sprzedaź w poszczególnych kanałach sprzedazy z podziałem na dni tygodnia'))

    fig.update_xaxes(categoryorder='array', categoryarray= ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'])

    grouped_customers = df[df['total_amt'] > 0].pivot_table(
        values='total_amt', columns=df['Gender'], index=df['Store_type'], aggfunc=sum)

    fig_customers = go.Figure(data=[
        go.Bar(name='Flagship store', x=grouped_customers.columns,
               y=[value for value in grouped_customers.values[0]]),
        go.Bar(name='MBR', x=grouped_customers.columns, y=[
               value for value in grouped_customers.values[1]]),
        go.Bar(name='TeleShop', x=grouped_customers.columns, y=[
               value for value in grouped_customers.values[2]]),
        go.Bar(name='e-Shop', x=grouped_customers.columns,
               y=[value for value in grouped_customers.values[3]])
    ], layout=go.Layout(title='Sprzedaź w poszcz. kanałach sprzedazy z uwzglednieniem płci klientów'))

    layout = html.Div([html.H2('Zestawienia dotyczącze kanałów sprzedazy', style={'text-align': 'center'}),
                       html.Div([html.Div([dcc.Graph(id='channel-sales', figure=fig)], style={'width': '50%'}),
                                 ]),
                       html.Div([html.Div([dcc.Graph(
                           id='channel-sales-customers', figure=fig_customers)], style={'width': '50%'})]),
                       html.Div([html.Div([dcc.Graph(id='age-customers-bar')], style={'width': '50%'})]),
                       dcc.RangeSlider(id='age-customers-range',
                                       min=df['age'].min(),
                                       max=df['age'].max(),
                                       step=1,
                                       value=[df['age'].min(), df['age'].max()]),
                       ])

    return layout
