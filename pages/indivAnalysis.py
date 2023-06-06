import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from datetime import date
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from server import app
import os

layout = html.Div(children=[
    html.Header(className='header2', children='Individual Statistics'),
    html.Br(),
    html.Div([
        "Person ID : ",
        dcc.Input(
        id='person-id',
        value = 'P0701',
        type = 'text'
        )
    ],),
    html.Div(id = 'check-person'),
    html.Div(
        [
            dcc.Dropdown(
                id="User",
                options = [
                    {'label' : "User A", 'value' : "UA"},
                    {'label' : "User B", 'value' : "UB"}
                ],
                value = "UA",
                ),
        ],
        style={'width': '25%',
               'display': 'inline-block'}),

    html.Div([
        "Select Start Date : ",
        dcc.DatePickerSingle(
        id='start-date',
        date=date(2023,3,1),
        initial_visible_month = date(2019,5,8)
        )
    ],
    ),

    html.Div([
        "Select End Date : ",
        dcc.DatePickerSingle(
        id='end-date',
        date=date(2023,3,1),
        initial_visible_month = date(2019,5,8)
        )
    ],

    ),

    html.Div([
        "Select Start Time : ",
        dcc.Input(id = 'start-time', value = '06:00', type = 'text'),
        " ex) 12:30 or 12:30:00"
    ],
    style={'position' : 'relative',
           'left' : '300px',
           'bottom' : '80px'}),
    html.Br(),
    html.Div([
        "Select End Time : ",
        dcc.Input(id = 'end-time', value = '18:00', type = 'text')
    ],
    style={'position' : 'relative',
           'left' : '300px',
           'bottom' : '80px'}),
    
    
    dcc.Graph(id='graph1'),
    dcc.Graph(id='graph2'),
])

@app.callback(
    Output('check-person', 'children'),
    Input('person-id', 'value')
)
def if_person(user_id):
    file_name = 'data/Processed/' + user_id + '_PAT.csv'
    if os.path.isfile(file_name) == False:
        return "Person ID is wrong"
    else:
        return "This is "+user_id+"'s information"


@app.callback(
    Output('graph1', 'figure'),
    Input('person-id', 'value'),
    Input('User', 'value'),
    Input('start-time', 'value'),
    Input('end-time', 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date')
)
def update_graph(user_id,User, starttime,endtime,startdate, enddate):
    file_name = 'data/Processed/' + user_id + '_PAT.csv'
    fig = go.Figure()
    if os.path.isfile(file_name) == False:
        return fig
    else:
        df = pd.read_csv(file_name)
        df.columns = ['Resource', 'Start', 'Finish']
        fig3 = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color = "Resource", range_x = [startdate+' '+starttime, enddate+' '+endtime], title = "Timeline")
        return fig3
    df1 = pd.DataFrame([
    dict(Resource="Walk", Start='2023-03-01 12:00:00', Finish='2023-03-01 15:00:00'),
    dict(Resource="App A", Start='2023-03-01 10:00:00', Finish='2023-03-01 13:00:00'),
    dict(Resource="App Usage", Start='2023-03-01 11:00:00', Finish='2023-03-01 12:00:00'),
    dict(Resource="Walk", Start='2023-03-01 09:00:00', Finish='2023-03-01 11:00:00'),
    dict(Resource="Walk", Start='2023-03-02 13:00:00', Finish='2023-03-02 14:00:00'),
    dict(Resource="Walk", Start='2023-03-02 16:00:00', Finish='2023-03-02 17:00:00'),
    dict(Resource="App Usage", Start='2023-03-02 11:00:00', Finish='2023-03-02 12:00:00'),
    dict(Resource="App Usage", Start='2023-03-02 14:30:00', Finish='2023-03-02 15:30:00'),
    dict(Resource="App A", Start='2023-03-02 14:40:00', Finish='2023-03-02 15:00:00'),
    ])
    
    fig1 = px.timeline(df1, x_start="Start", x_end="Finish", y="Resource", color = "Resource", range_x = [startdate+' '+starttime, enddate+' '+endtime],title = "Timeline")
    fig1.update_yaxes(autorange="reversed") 
    df2 = pd.DataFrame([
    dict(Resource="Walk", Start='2023-03-01 10:00:00', Finish='2023-03-01 11:00:00'),
    dict(Resource="Walk", Start='2023-03-01 13:00:00', Finish='2023-03-01 14:00:00'),
    dict(Resource="App Usage", Start='2023-03-01 10:30:00', Finish='2023-03-01 11:00:00'),
    dict(Resource="App Usage", Start='2023-03-01 12:30:00', Finish='2023-03-01 12:20:00'),
    dict(Resource="App B", Start='2023-03-01 13:30:00', Finish='2023-03-01 14:30:00'),
    dict(Resource="Walk", Start='2023-03-02 13:00:00', Finish='2023-03-02 13:20:00'),
    dict(Resource="Walk", Start='2023-03-02 13:30:00', Finish='2023-03-02 13:40:00'),
    dict(Resource="App Usage", Start='2023-03-02 13:00:00', Finish='2023-03-02 15:00:00'),
    dict(Resource="App B", Start='2023-03-02 13:10:00', Finish='2023-03-02 13:30:00'),
    dict(Resource="App B", Start='2023-03-02 14:20:00', Finish='2023-03-02 15:00:00'),
    
    ])
    fig2 = px.timeline(df2, x_start="Start", x_end="Finish", y="Resource", color = "Resource", range_x = [startdate+' '+starttime, enddate+' '+endtime], title = "Timeline")
    fig2.update_yaxes(autorange="reversed") 
    if User == "UA":
        return fig1
    return fig2


@app.callback(

    Output('graph2', 'figure'),
    Input('User', 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date')
)

def update_graph(user,startdate,enddate):
    dates = pd.date_range(startdate,enddate)
    newdates = list(map(str, dates))
    df1 = pd.DataFrame([
    dict(date="2023-03-01 00:00:00", App = 1.5 , Walk = 2.5),
    dict(date="2023-03-02 00:00:00", App = 2 , Walk = 2),
    dict(date="2023-03-03 00:00:00", App = 2.5 , Walk = 0.5),
    dict(date="2023-03-04 00:00:00", App = 0.5 , Walk = 3),
    dict(date="2023-03-05 00:00:00", App = 1.5 , Walk = 0.5),
    ])
    df2 = pd.DataFrame([
    dict(date="2023-03-01 00:00:00", App = 3.0 , Walk = 0.5),
    dict(date="2023-03-02 00:00:00", App = 2.5, Walk = 1),
    dict(date="2023-03-03 00:00:00", App = 3.5 , Walk = 0.5),
    dict(date="2023-03-04 00:00:00", App = 2 , Walk = 1),
    dict(date="2023-03-05 00:00:00", App = 3 , Walk = 1.5),
    ])
    df11 = df1[df1['date'].isin(newdates)]
    df22 = df2[df2['date'].isin(newdates)]
    fig1 = px.line(df11, x = 'date', y = ['App', 'Walk'], markers = True, width = 800, title = "Line Graph")
    fig2 = px.line(df22, x = newdates, y = ['App', 'Walk'], markers = True, width = 800, title = "Line Graph")
    if user == "UA":
        return fig1
    return fig2
