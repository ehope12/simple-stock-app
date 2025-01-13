from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_mantine_components as dmc
import yfinance as yf
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# Style
external_stylesheets = [dbc.themes.SOLAR]
app = Dash(__name__, external_stylesheets=external_stylesheets)
load_figure_template('SOLAR')

app.layout = html.Div([
    dmc.Title('At A Glance: Stock Prices!', size='h1'),
    dmc.Title('Enter stock symbol:', size='p'),
    dcc.Input(
        # User can pick what company/ETF to view
        id='ticker',
        type='text',
        value='SPY',
    ),
    dbc.RadioItems(
        # User can pick what time range to view
        options=[
            {'label': '1 Day', 'value': '1d'},
            {'label': '5 Days', 'value': '5d'},
            {'label': '1 Month', 'value': '1mo'},
            {'label': '3 Months', 'value': '3mo'},
            {'label': '6 Months', 'value': '6mo'},
            {'label': 'YTD', 'value': 'ytd'},
            {'label': '1 Year', 'value': '1y'},
            {'label': '2 Years', 'value': '2y'},
            {'label': '5 Years', 'value': '5y'},
            {'label': '10 Years', 'value': '10y'},
            {'label': 'Max', 'value': 'max'},
        ],
        id='time_range',
        value='1d',
        inline=True,
        className='mb-2',
    ),
    dcc.Graph(id='time-series-chart'),
    # Not sure if the below really adds to the user experience
    # dmc.RadioGroup(
    #     # User can choose which price to see -- change this to a dropdown menu?
    #     # Add this on the graph? https://plotly.com/python/dropdowns/
    #     [dmc.Radio(i, value=i) for i in ['Open', 'Close', 'High', 'Low']],
    #     id='price',
    #     value='Close',
    #     size="sm"
    # ),
    dcc.Graph(id='candlestick-chart'),
    html.H2('Overview:'),
    html.Div([
        html.P(id='long_business_summary')
    ]),
],
style={'padding': '12px'} # Padding on the edges of the screen
)


@app.callback(
    [Output('time-series-chart', 'figure'),
     Output('candlestick-chart', 'figure'),
     Output('long_business_summary', 'children')],
    Input('ticker', 'value'),
    # Input('price', 'value'),
    Input('time_range', 'value')
)
def display_time_series(ticker, time_range): # Change to be "ticker, price_type, time_range" if you want the price_type option
    search = yf.Ticker(ticker)
    long_business_summary = search.info['longBusinessSummary']
    
    # Specify data intervals for different time range options
    if time_range == '1d':
        df = search.history(period=time_range, interval='1m')
    elif time_range == '5d':
        df = search.history(period=time_range, interval='30m')
    else:
        df = search.history(period=time_range)

    # Create a time series graph with dates on the x axis and price on the y axis
    time_series_fig = go.Figure()
    # Change y=df[price_type] if you want the price_type option and add "name=price_type" to the end of the line
    time_series_fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines'))

    # Generate time series graph for the ticker of the user's choice
    time_series_fig.update_layout(
        title=f'Time Series Graph: {search.info["longName"]}',
        xaxis_title='Date',
        yaxis_title='Stock Price',
        legend_title='Price Type'
    )

    # Only business hours/days shown on the 1d and 5d graph options
    if time_range == '1d' or time_range == '5d':
        time_series_fig.update_xaxes(
            rangebreaks=[
                dict(bounds=['sat', 'mon']),
                dict(bounds=[17, 9], pattern='hour'),
            ]
        )

    # Create a candlestick graph with dates on the x axis and price on the y axis
    candlestick_fig = go.Figure()
    candlestick_fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlesticks'))
    # Add Moving Average traces
    ma_50 = go.Scatter(x=df.index, y=df['Close'].rolling(window=50).mean(), name='50-day MA')
    ma_200 = go.Scatter(x=df.index, y=df['Close'].rolling(window=200).mean(), name='200-day MA')
    # Add traces to the existing figure
    candlestick_fig.add_trace(ma_50)
    candlestick_fig.add_trace(ma_200)
    candlestick_fig.update_layout(xaxis_rangeslider_visible=False)

    # Generate time series graph for the ticker of the user's choice
    candlestick_fig.update_layout(
        title=f'Candlestick Graph: {search.info["longName"]}',
        xaxis_title='Date',
        yaxis_title='Stock Price',
        legend_title='Price Information'
    )

    # Only business hours/days shown on the 1d and 5d graph options
    if time_range == '1d' or time_range == '5d':
        candlestick_fig.update_xaxes(
            rangebreaks=[
                dict(bounds=['sat', 'mon']),
                dict(bounds=[17, 9], pattern='hour'),
            ]
        )

    return time_series_fig, candlestick_fig, long_business_summary


app.run_server(debug=True)