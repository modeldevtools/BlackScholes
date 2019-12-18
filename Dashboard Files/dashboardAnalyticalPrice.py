import dash
import dash_core_components as dcc
import dash_table as dt
import dash_html_components as html
import QuantLib as ql

from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
from black_scholes_ver10 import AnalyticBlackScholes
from scenario_generator import EquityModels
from greeks import GreeksParameters
from utilities import QuantLibConverter

import plotly.graph_objs as go
import pandas as pd
import os
import datetime

external_stylesheets = ['https://codepen.io/chridyp/pen/bWLgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([dcc.Textarea(value='Black Scholes World',
                                    style={'width': '100%', 'color': 'green', 'fontSize': 18,
                                           'background-color': 'yellow', 'border-style': 'dashed',
                                           'text-align': 'center'}),
                       dcc.Tabs(children=[
                           dcc.Tab(label='Analytical Price', style={'background-color': 'blue'},
                                   children=[html.Label(
                                       'Place provide the date for which you would like to price the contract'),
                                       html.Br(),
                                       dcc.DatePickerSingle(id='valuationDateAnalitical',
                                                            date=datetime.datetime(2019, 11, 25),
                                                            display_format='YYYY-MM-DD'),
                                       html.Hr(),
                                       html.Label('Place provide the termination the contract.'),
                                       html.Hr(),
                                       dcc.DatePickerSingle(id='endDateAnalitical',
                                                            date=datetime.datetime(2020, 2, 20),
                                                            display_format='YYYY-MM-DD'),
                                       html.Br(),
                                       dcc.Input(id='scheduleAnalitical', placeholder='Define Schedule',
                                                 value='Two Dates'),
                                       html.Hr(),
                                       dcc.Dropdown(id='conventionAnalitical',
                                                    placeholder='Chose Available Convention',
                                                    options=[{'label': 'Actual Actual', 'value': 'ActualActual'},
                                                             {'label': 'Actual360', 'value': 'Actual360'},
                                                             {'label': 'Actual365', 'value': 'Actual365'},
                                                             {'label': 'Thirty360', 'value': 'Thirty360'},
                                                             {'label': 'Business252', 'value': 'Business252'}],
                                                    value='ActualActual'),
                                       dcc.Dropdown(id='calendarAnalitical',
                                                    placeholder='Put the name of Country',
                                                    options=[{'label': 'UK', 'value': 'United Kingdom'},
                                                             {'label': 'United States', 'value': 'USA'},
                                                             {'label': 'Switzerland', 'value': 'Switzerland'},
                                                             {'label': 'Poland', 'value': 'Poland'}
                                                             ], value='United Kingdom'),

                                       dcc.Input(id='BusinessConventionAnalitical',
                                                 placeholder='Define Business Convention', value='Following'),
                                       dcc.Input(id='Termination Business ConventionAnalitical',
                                                 placeholder='Define Termination Business Convention',
                                                 value='Following'),
                                       dcc.Input(id='endOfMonthAnalitical', value='False'),
                                       dcc.Dropdown(id='optiontypeAnalitical',
                                                    options=[{'label': 'Call Option', 'value': 'call'},
                                                             {'label': 'Put Option', 'value': 'put'}],
                                                    value='call'),
                                       html.Hr(),
                                       dcc.Input(id='currentPriceAnalitical', value=90, type='number',
                                                 placeholder='Current Price'),
                                       dcc.Input(id='strikeAnalitical', value=92, type='number',
                                                 placeholder='Strike'),
                                       dcc.Input(id='riskFreeAnalitical', value=0.1, type='number',
                                                 placeholder='Risk Free Rate'),
                                       dcc.Input(id='volatilityAnalitical', value=0.23, type='number',
                                                 placeholder='Volatility'),
                                       dcc.Input(id='dividendAnalitical', value=0, type='number',
                                                 placeholder='Dividend'),
                                       html.Hr(),
                                       html.Button('Press to get year fraction', id='yearFractionButton',
                                                   style={'background-color': 'orange', 'fontSize': 20}),
                                       html.Hr(),
                                       ###################################----RESULT YEAR FRACTION----###############################################
                                       html.Div(id='yearFraction'),
                                       ###################################----RESULT YEAR FRACTION----###############################################
                                       html.Button('Press to get analytical price', id='AnalyticalPrice',
                                                   style={'background-color': 'red', 'fontSize': 20}),
                                       ###################################----RESULT OPTION PRICE----###############################################
                                       html.Div(id='optionPriceAnalitical', children=''),
                                       ###################################----RESULT OPTION PRICE----###############################################
                                       html.Hr(),

                                   ]

                                   ),
                           dcc.Tab(label='Monte Carlo Price', style={'background-color': 'green'},
                                   children=[
                                       html.Br(),
                                       dcc.DatePickerSingle(id='valuationDateMc', date=datetime.datetime(2019, 11, 25),
                                                            display_format='YYYY-MM-DD'),
                                       html.Br(),
                                       html.Label('Place provide the end of modeling.'),
                                       html.Br(),
                                       dcc.DatePickerSingle(id='endDateMc', date=datetime.datetime(2020, 2, 20),
                                                            display_format='YYYY-MM-DD'),
                                       html.Br(),
                                       dcc.Dropdown(id='scheduleMc', style={'background-color': 'orange'},
                                                    placeholder='Define Schedule',
                                                    value='Daily',
                                                    options=[{'label': 'Two Dates', 'value': 'Two Dates'},
                                                             {'label': 'Daily', 'value': 'Daily'},
                                                             {'label': 'Weekly', 'value': 'Weekly'},
                                                             {'label': 'Monthly', 'value': 'Monthly'},
                                                             {'label': 'Quarterly', 'value': 'Quarterly'},
                                                             {'label': 'Semiannual', 'value': 'Semiannual'},
                                                             {'label': 'Annual', 'value': 'Annual'},

                                                             ]),
                                       html.Br(),
                                       dcc.Dropdown(id='conventionMc', style={'background-color': 'purple'},
                                                    placeholder='Chose Available Convention',
                                                    options=[{'label': 'Actual Actual', 'value': 'ActualActual'},
                                                             {'label': 'Actual360', 'value': 'Actual360'},
                                                             {'label': 'Actual365', 'value': 'Actual365'},
                                                             {'label': 'Thirty360', 'value': 'Thirty360'},
                                                             {'label': 'Business252', 'value': 'Business252'}],
                                                    value='ActualActual'),
                                       dcc.Dropdown(id='calendarMc', placeholder='Put the name of Country',
                                                    options=[{'label': 'UK', 'value': 'United Kingdom'},
                                                             {'label': 'United States', 'value': 'USA'},
                                                             {'label': 'Switzerland', 'value': 'Switzerland'},
                                                             {'label': 'Poland', 'value': 'Poland'}
                                                             ], value='United Kingdom'),

                                       dcc.Input(id='Business ConventionMc', placeholder='Define Business Convention',
                                                 value='Following'),
                                       dcc.Input(id='Termination Business ConventionMc',
                                                 placeholder='Define Termination Business Convention',
                                                 value='Following'),
                                       dcc.Input(id='endOfMonthMc', value='False'),
                                       html.Br(),
                                       html.Label('Place provide the parameters for option'),
                                       dcc.Dropdown(id='optiontypeMc',
                                                    options=[{'label': 'Call Option', 'value': 'call'},
                                                             {'label': 'Put Option', 'value': 'put'}],
                                                    value='call'),
                                       html.Hr(),
                                       dcc.Input(id='currentPriceMc', value=90, type='number',
                                                 placeholder='Current Price'),
                                       dcc.Input(id='strikeMc', value=92, type='number', placeholder='Strike'),
                                       dcc.Input(id='riskFreeMc', value=0.1, type='number',
                                                 placeholder='Risk Free Rate'),
                                       dcc.Input(id='volatilityMc', value=0.23, type='number',
                                                 placeholder='Volatility'),
                                       dcc.Input(id='dividendMc', value=0, type='number', placeholder='Dividend'),
                                       html.Hr(),
                                       html.Label('Place provide the parameters for running simulation'),
                                       html.Br(),
                                       dcc.RadioItems(id='sampleMc',
                                                      options=[{'label': '1000', 'value': 1000},
                                                               {'label': '10000', 'value': 10000},
                                                               {'label': '100000', 'value': 100000}], value=1000),
                                       dcc.RadioItems(id='numberOfPathToDisplayMc',
                                                      options=[{'label': '10', 'value': 10},
                                                               {'label': '15', 'value': 15},
                                                               {'label': '25', 'value': 25},
                                                               {'label': '50', 'value': 50}],
                                                      value=15),
                                       # html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                                       # style={'text-align': 'center'}),

                                       html.Hr(),
                                       ###################################----RESULT----###############################################
                                       html.Div(id='MonteCarloPriceMc', children='')

                                   ]
                                   ),

                           dcc.Tab(label='Sensitivity Analysis', style={'background-color': 'pink'},
                                   # short
                                   children=[html.Div([
                                       html.Label('Short Term Contract',
                                                  style={'color': 'red', 'text-align': 'center'}),
                                       html.Br(),
                                       dcc.DatePickerSingle(id='valuationDateShort',
                                                            date=datetime.datetime(2019, 11, 25),
                                                            display_format='YYYY-MM-DD'),
                                       html.Br(),
                                       html.Label('Place provide the end of modeling.'),
                                       html.Br(),
                                       dcc.DatePickerSingle(id='endDateShort', date=datetime.datetime(2019, 12, 5),
                                                            display_format='YYYY-MM-DD'),
                                       html.Br(),
                                       dcc.Dropdown(id='scheduleShort', style={'background-color': 'orange'},
                                                    placeholder='Define Schedule',
                                                    value='Daily',
                                                    options=[{'label': 'Two Dates', 'value': 'Two Dates'},
                                                             {'label': 'Daily', 'value': 'Daily'},
                                                             {'label': 'Weekly', 'value': 'Weekly'},
                                                             {'label': 'Monthly', 'value': 'Monthly'},
                                                             {'label': 'Quarterly', 'value': 'Quarterly'},
                                                             {'label': 'Semiannual', 'value': 'Semiannual'},
                                                             {'label': 'Annual', 'value': 'Annual'},

                                                             ]),
                                       html.Br(),
                                       dcc.Dropdown(id='conventionShort', style={'background-color': 'purple'},
                                                    placeholder='Chose Available Convention',
                                                    options=[{'label': 'Actual Actual', 'value': 'ActualActual'},
                                                             {'label': 'Actual360', 'value': 'Actual360'},
                                                             {'label': 'Actual365', 'value': 'Actual365'},
                                                             {'label': 'Thirty360', 'value': 'Thirty360'},
                                                             {'label': 'Business252', 'value': 'Business252'}],
                                                    value='ActualActual'),
                                       dcc.Dropdown(id='calendarShort', placeholder='Put the name of Country',
                                                    options=[{'label': 'UK', 'value': 'United Kingdom'},
                                                             {'label': 'United States', 'value': 'USA'},
                                                             {'label': 'Switzerland', 'value': 'Switzerland'},
                                                             {'label': 'Poland', 'value': 'Poland'}
                                                             ], value='United Kingdom'),

                                       dcc.Input(id='Business ConventionShort',
                                                 placeholder='Define Business Convention',
                                                 value='Following'),
                                       dcc.Input(id='Termination Business ConventionShort',
                                                 placeholder='Define Termination Business Convention',
                                                 value='Following'),
                                       dcc.Input(id='endOfMonthShort', value='False'),
                                       html.Br(),
                                       html.Label('Place provide the parameters for option'),
                                       dcc.Dropdown(id='optionTypeShort',
                                                    options=[{'label': 'Call Option', 'value': 'call'},
                                                             {'label': 'Put Option', 'value': 'put'}],
                                                    value='call'),
                                       html.Hr(),
                                       dcc.Input(id='currentPriceShort', value=90, type='number',
                                                 placeholder='Current Price'),
                                       dcc.Input(id='strikeShort', value=92, type='number', placeholder='Strike'),
                                       dcc.Input(id='riskFreeShort', value=0.1, type='number',
                                                 placeholder='Risk Free Rate'),
                                       dcc.Input(id='volatilityShort', value=0.23, type='number',
                                                 placeholder='Volatility'),
                                       dcc.Input(id='dividendShort', value=0, type='number', placeholder='Dividend'),

                                       # html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                                       # style={'text-align': 'center'}),

                                       html.Hr(),

                                   ]),
                                       # medium
                                       html.Div([
                                           html.Label('Medium Term Contract',
                                                      style={'color': 'red', 'text-align': 'center'}),
                                           html.Br(),
                                           dcc.DatePickerSingle(id='valuationDateMedium',
                                                                date=datetime.datetime(2019, 11, 25),
                                                                display_format='YYYY-MM-DD'),
                                           html.Br(),
                                           html.Label('Place provide the end of modeling.'),
                                           html.Br(),
                                           dcc.DatePickerSingle(id='endDateShortMedium',
                                                                date=datetime.datetime(2020, 2, 20),
                                                                display_format='YYYY-MM-DD'),
                                           html.Br(),
                                           dcc.Dropdown(id='scheduleShortMedium', style={'background-color': 'orange'},
                                                        placeholder='Define Schedule',
                                                        value='Daily',
                                                        options=[{'label': 'Two Dates', 'value': 'Two Dates'},
                                                                 {'label': 'Daily', 'value': 'Daily'},
                                                                 {'label': 'Weekly', 'value': 'Weekly'},
                                                                 {'label': 'Monthly', 'value': 'Monthly'},
                                                                 {'label': 'Quarterly', 'value': 'Quarterly'},
                                                                 {'label': 'Semiannual', 'value': 'Semiannual'},
                                                                 {'label': 'Annual', 'value': 'Annual'},

                                                                 ]),
                                           html.Br(),
                                           dcc.Dropdown(id='conventionShortMedium',
                                                        style={'background-color': 'purple'},
                                                        placeholder='Chose Available Convention',
                                                        options=[{'label': 'Actual Actual', 'value': 'ActualActual'},
                                                                 {'label': 'Actual360', 'value': 'Actual360'},
                                                                 {'label': 'Actual365', 'value': 'Actual365'},
                                                                 {'label': 'Thirty360', 'value': 'Thirty360'},
                                                                 {'label': 'Business252', 'value': 'Business252'}],
                                                        value='ActualActual'),
                                           dcc.Dropdown(id='calendarShortMedium', placeholder='Put the name of Country',
                                                        options=[{'label': 'UK', 'value': 'United Kingdom'},
                                                                 {'label': 'United States', 'value': 'USA'},
                                                                 {'label': 'Switzerland', 'value': 'Switzerland'},
                                                                 {'label': 'Poland', 'value': 'Poland'}
                                                                 ], value='United Kingdom'),

                                           dcc.Input(id='Business ConventionShortMedium',
                                                     placeholder='Define Business Convention',
                                                     value='Following'),
                                           dcc.Input(id='Termination Business ConventionMedium',
                                                     placeholder='Define Termination Business Convention',
                                                     value='Following'),
                                           dcc.Input(id='endOfMonthMedium', value='False'),
                                           html.Br(),
                                           html.Label('Place provide the parameters for option'),
                                           dcc.Dropdown(id='optionTypeMedium',
                                                        options=[{'label': 'Call Option', 'value': 'call'},
                                                                 {'label': 'Put Option', 'value': 'put'}],
                                                        value='call'),
                                           html.Hr(),
                                           dcc.Input(id='currentPriceMedium', value=90, type='number',
                                                     placeholder='Current Price'),
                                           dcc.Input(id='strikeMedium', value=92, type='number', placeholder='Strike'),
                                           dcc.Input(id='riskFreeMedium', value=0.1, type='number',
                                                     placeholder='Risk Free Rate'),
                                           dcc.Input(id='volatilityMedium', value=0.23, type='number',
                                                     placeholder='Volatility'),
                                           dcc.Input(id='dividendMedium', value=0, type='number',
                                                     placeholder='Dividend'),

                                           # html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                                           # style={'text-align': 'center'}),

                                           html.Hr(),

                                       ]),
                                       # LONG
                                       html.Div([
                                           html.Label('Long Term Contract',
                                                      style={'color': 'red', 'text-align': 'center'}),
                                           html.Br(),
                                           dcc.DatePickerSingle(id='valuationDateLong',
                                                                date=datetime.datetime(2019, 11, 25),
                                                                display_format='YYYY-MM-DD'),
                                           html.Br(),
                                           html.Label('Place provide the end of modeling.'),
                                           html.Br(),
                                           dcc.DatePickerSingle(id='endDateShortLong',
                                                                date=datetime.datetime(2020, 11, 25),
                                                                display_format='YYYY-MM-DD'),
                                           html.Br(),
                                           dcc.Dropdown(id='scheduleShortLong', style={'background-color': 'orange'},
                                                        placeholder='Define Schedule',
                                                        value='Daily',
                                                        options=[{'label': 'Two Dates', 'value': 'Two Dates'},
                                                                 {'label': 'Daily', 'value': 'Daily'},
                                                                 {'label': 'Weekly', 'value': 'Weekly'},
                                                                 {'label': 'Monthly', 'value': 'Monthly'},
                                                                 {'label': 'Quarterly', 'value': 'Quarterly'},
                                                                 {'label': 'Semiannual', 'value': 'Semiannual'},
                                                                 {'label': 'Annual', 'value': 'Annual'},

                                                                 ]),
                                           html.Br(),
                                           dcc.Dropdown(id='conventionShortLong',
                                                        style={'background-color': 'purple'},
                                                        placeholder='Chose Available Convention',
                                                        options=[{'label': 'Actual Actual', 'value': 'ActualActual'},
                                                                 {'label': 'Actual360', 'value': 'Actual360'},
                                                                 {'label': 'Actual365', 'value': 'Actual365'},
                                                                 {'label': 'Thirty360', 'value': 'Thirty360'},
                                                                 {'label': 'Business252', 'value': 'Business252'}],
                                                        value='ActualActual'),
                                           dcc.Dropdown(id='calendarShortLong', placeholder='Put the name of Country',
                                                        options=[{'label': 'UK', 'value': 'United Kingdom'},
                                                                 {'label': 'United States', 'value': 'USA'},
                                                                 {'label': 'Switzerland', 'value': 'Switzerland'},
                                                                 {'label': 'Poland', 'value': 'Poland'}
                                                                 ], value='United Kingdom'),

                                           dcc.Input(id='Business ConventionLong',
                                                     placeholder='Define Business Convention',
                                                     value='Following'),
                                           dcc.Input(id='Termination Business ConventionLong',
                                                     placeholder='Define Termination Business Convention',
                                                     value='Following'),
                                           dcc.Input(id='endOfMonthLong', value='False'),
                                           html.Br(),
                                           html.Label('Place provide the parameters for option'),
                                           dcc.Dropdown(id='optionTypeLong',
                                                        options=[{'label': 'Call Option', 'value': 'call'},
                                                                 {'label': 'Put Option', 'value': 'put'}],
                                                        value='call'),
                                           html.Hr(),
                                           dcc.Input(id='currentPriceLong', value=90, type='number',
                                                     placeholder='Current Price'),
                                           dcc.Input(id='strikeLong', value=92, type='number', placeholder='Strike'),
                                           dcc.Input(id='riskFreelong', value=0.1, type='number',
                                                     placeholder='Risk Free Rate'),
                                           dcc.Input(id='volatilityLong', value=0.23, type='number',
                                                     placeholder='Volatility'),
                                           dcc.Input(id='dividendLong', value=0, type='number',
                                                     placeholder='Dividend'),

                                           # html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                                           # style={'text-align': 'center'}),

                                           html.Hr(),

                                       ]),
                                       dcc.Textarea(value='GREEKS',
                                                    style={'width': '100%', 'color': 'green', 'fontSize': 18,
                                                           'background-color': 'yellow', 'border-style': 'dashed',
                                                           'text-align': 'center'}),
                                       ###################################----RESULT Dynamic Slider----###############################################
                                       dcc.RangeSlider(id='defineSlider', min=50, max=130),
                                       html.Hr(),
                                       html.Button('Press to get greeks', id='greeksButton',
                                                   style={'background-color': 'brown', 'fontSize': 20}),
                                       ###################################----GREEK PARAMETERS----###############################################
                                       html.Div(id='greeks', children='')
                                       ###################################----GREEK PARAMETERS----###############################################

                                   ],

                                   )

                       ])

                       ]

                      )


#####################################################----ANALYTICAL PRICE CALLBACK----###########################################
#
@app.callback(
    Output('yearFraction', 'children'),
    [
        Input('valuationDateAnalitical', 'date'),
        Input('endDateAnalitical', 'date'),
        Input('scheduleAnalitical', 'value'),
        Input('conventionAnalitical', 'value'),
        Input('calendarAnalitical', 'value'),
        Input('optiontypeAnalitical', 'value'),
        Input('currentPriceAnalitical', 'value'),
        Input('strikeAnalitical', 'value'),
        Input('riskFreeAnalitical', 'value'),
        Input('volatilityAnalitical', 'value'),
        Input('dividendAnalitical', 'value'),
        Input('yearFractionButton', 'n_clicks')

    ])
def dashYearFraction(valDate, endDate, schedule, convention, calendar, optionType,
                     currentPrice, strike, riskFree, volatility, dividend, click):
    o_black_scholes = AnalyticBlackScholes(valuation_date=valDate,
                                           termination_date=endDate,
                                           schedule_freq=schedule,
                                           convention=convention,
                                           calendar=QuantLibConverter(calendar=calendar).mqlCalendar,
                                           business_convention=QuantLibConverter(
                                               calendar=calendar).mqlBusinessConvention,
                                           termination_business_convention=QuantLibConverter(
                                               calendar=calendar).mqlTerminationBusinessConvention,
                                           date_generation=QuantLibConverter(calendar=calendar).mqlDateGeneration,
                                           end_of_month=False,
                                           ##################################
                                           type_option=optionType,
                                           current_price=currentPrice,
                                           strike=strike,
                                           ann_risk_free_rate=riskFree,
                                           ann_volatility=volatility,
                                           ann_dividend=dividend)

    year_fraction = round(o_black_scholes.mf_yf_between_valu_date_and_maturity, 3)

    if click is None:
        raise PreventUpdate
    else:

        return html.Div([html.H4(f'Annuity for this contract  {year_fraction}'),
                         html.Hr(),

                         ])


@app.callback(
    Output('optionPriceAnalitical', 'children'),
    [
        Input('valuationDateAnalitical', 'date'),
        Input('endDateAnalitical', 'date'),
        Input('scheduleAnalitical', 'value'),
        Input('conventionAnalitical', 'value'),
        Input('calendarAnalitical', 'value'),
        Input('optiontypeAnalitical', 'value'),
        Input('currentPriceAnalitical', 'value'),
        Input('strikeAnalitical', 'value'),
        Input('riskFreeAnalitical', 'value'),
        Input('volatilityAnalitical', 'value'),
        Input('dividendAnalitical', 'value'),
        Input('AnalyticalPrice', 'n_clicks')

    ])
def dashOptionPrice(valDate, endDate, schedule, convention, calendar, optionType,
                    currentPrice, strike, riskFree, volatility, dividend, click):
    o_black_scholes = AnalyticBlackScholes(valuation_date=valDate,
                                           termination_date=endDate,
                                           schedule_freq=schedule,
                                           convention=convention,
                                           calendar=QuantLibConverter(calendar=calendar).mqlCalendar,
                                           business_convention=QuantLibConverter(
                                               calendar=calendar).mqlBusinessConvention,
                                           termination_business_convention=QuantLibConverter(
                                               calendar=calendar).mqlTerminationBusinessConvention,
                                           date_generation=QuantLibConverter(calendar=calendar).mqlDateGeneration,
                                           end_of_month=False,
                                           ##################################
                                           type_option=optionType,
                                           current_price=currentPrice,
                                           strike=strike,
                                           ann_risk_free_rate=riskFree,
                                           ann_volatility=volatility,
                                           ann_dividend=dividend)
    price = round(o_black_scholes.black_scholes_price_fun()[0], 3)

    if click is None:
        raise PreventUpdate
    else:

        return html.Div([

            dcc.Textarea(value=f'Analytical price of option {price}',
                         style={'width': '100%', 'color': 'red', 'fontSize': 18,
                                'background-color': 'blue', 'border-style': 'dashed',
                                'text-align': 'center'})

        ])


@app.callback(
    Output('defineSlider', 'value'),
    [
        Input('currentPriceAnalitical', 'value')
    ]
)
def defineDashboard(starpoint):
    values = [i for i in range(starpoint - 10, starpoint + 11)]
    return values


@app.callback(
    Output('defineSlider', 'marks'),
    [
        Input('currentPriceAnalitical', 'value')
    ]
)
def defineDashboard(starpoint):
    marks = {i: f'{i}' for i in range(starpoint - 40, starpoint + 41)}
    return marks


#
@app.callback(
    Output('greeks', 'children'),
    [
        Input('valuationDateAnalitical', 'date'),
        Input('endDateAnalitical', 'date'),
        Input('scheduleAnalitical', 'value'),
        Input('conventionAnalitical', 'value'),
        Input('calendarAnalitical', 'value'),
        Input('optiontypeAnalitical', 'value'),
        Input('currentPriceAnalitical', 'value'),
        Input('strikeAnalitical', 'value'),
        Input('riskFreeAnalitical', 'value'),
        Input('volatilityAnalitical', 'value'),
        Input('dividendAnalitical', 'value'),
        Input('greeksButton', 'n_clicks'),
        Input('defineSlider', 'value')

    ])
def getGreeks(valDate, endDate, schedule, convention, calendar, optionType,
              currentPrice, strike, riskFree, volatility, dividend, click, sliderRange):
    greeks = GreeksParameters(valuation_date=valDate,
                              termination_date=endDate,
                              schedule_freq=schedule,
                              convention=convention,
                              calendar=QuantLibConverter(calendar=calendar).mqlCalendar,
                              business_convention=QuantLibConverter(
                                  calendar=calendar).mqlBusinessConvention,
                              termination_business_convention=QuantLibConverter(
                                  calendar=calendar).mqlTerminationBusinessConvention,
                              date_generation=QuantLibConverter(calendar=calendar).mqlDateGeneration,
                              end_of_month=False,
                              ##################################
                              type_option=optionType,
                              current_price=currentPrice,
                              strike=strike,
                              ann_risk_free_rate=riskFree,
                              ann_volatility=volatility,
                              ann_dividend=dividend)

    delta = [greeks.delta() for greeks._S0 in sliderRange]

    if click is None:
        raise PreventUpdate
    else:

        return html.Div([html.H4(f'slider range {delta}'),
                         html.Hr(),

                         ])


#####################################################----ANALYTICAL PRICE CALLBACK----###########################################


#####################################################----MONTE CARLO CALL BACK----###########################################

@app.callback(

    Output('MonteCarloPriceMc', 'children'),

    [
        Input('valuationDateMc', 'date'),
        Input('endDateMc', 'date'),
        Input('scheduleMc', 'value'),
        Input('conventionMc', 'value'),
        Input('calendarMc', 'value'),
        Input('optiontypeMc', 'value'),
        Input('currentPriceMc', 'value'),
        Input('strikeMc', 'value'),
        Input('riskFreeMc', 'value'),
        Input('volatilityMc', 'value'),
        Input('dividendMc', 'value'),
        Input('sampleMc', 'value'),
        Input('numberOfPathToDisplayMc', 'value')

    ])
def optionPrice(valDate, endDate, schedule, convention, calendar, optionType,
                currentPrice, strike, riskFree, volatility, dividend, runs, display):
    equitySimulation = EquityModels(valuation_date=valDate,
                                    termination_date=endDate,
                                    schedule_freq=schedule,
                                    convention=convention,
                                    calendar=QuantLibConverter(calendar=calendar).mqlCalendar,
                                    business_convention=QuantLibConverter(
                                        calendar=calendar).mqlBusinessConvention,
                                    termination_business_convention=QuantLibConverter(
                                        calendar=calendar).mqlTerminationBusinessConvention,
                                    date_generation=QuantLibConverter(calendar=calendar).mqlDateGeneration,
                                    end_of_month=False,
                                    ##################################
                                    type_option=optionType,
                                    current_price=currentPrice,
                                    strike=strike,
                                    ann_risk_free_rate=riskFree,
                                    ann_volatility=volatility,
                                    ann_dividend=dividend,
                                    runs=runs)

    price = round(equitySimulation.mf_monte_carlo_price, 3)
    paths = equitySimulation.m_ar_equity_price
    lqlDates = list(equitySimulation.mListOfDates)
    ldtDates = [d.to_date() for d in lqlDates]

    return html.Div([
        dcc.Graph(figure=dict(data=
                              [dict(x=ldtDates,
                                    y=paths[:, i],
                                    name=f'Path{i}',
                                    marker=dict(color='')) for i in range(display)],
                              layout=dict(
                                  xaxis={'title': 'Dates'},
                                  yaxis={'title': 'Equity Price'},
                                  title='Equity simulation modeled by geometric brownian motion',
                                  showlegend=True,
                                  legend=dict(x=0,
                                              y=1.0),
                                  margin=dict(l=40, r=0, t=40, b=30),
                              )

                              ),
                  style={'height': 300}

                  ),

        dcc.Textarea(value=f'Monte Carlo Price price of option {price}',
                     style={'width': '100%', 'color': 'red', 'fontSize': 18,
                            'background-color': 'blue', 'border-style': 'dashed',
                            'text-align': 'center'})

    ])


#####################################################----MONTE CARLO CALL BACK----###########################################
if __name__ == '__main__':
    app.run_server(debug=True)
