from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from server import app
from datetime import datetime, timedelta, date
import glob
import os
import pandas as pd

layout = dbc.Container(
        dbc.Row(
            dbc.Col(html.Div("Main"), width =16, style = {'background-color':'lightcyan'}))
)