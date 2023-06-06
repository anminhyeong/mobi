import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from datetime import date
from datetime import datetime, timedelta
import datetime
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
    

    html.Div([
        "Select Start Date : ",
        dcc.DatePickerSingle(
        id='start-date',
        date=date(2019,5,8),
        initial_visible_month = date(2019,5,8)
        )
    ],
    ),

    html.Div([
        "Select End Date : ",
        dcc.DatePickerSingle(
        id='end-date',
        date=date(2019,5,8),
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
    Input('start-time', 'value'),
    Input('end-time', 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date')
)
def update_graph(user_id, starttime,endtime,startdate, enddate):
    file_name = 'data/Processed/' + user_id + '_PAT.csv'
    fig = go.Figure()
    if os.path.isfile(file_name) == False:
        return fig
    else:
        df = pd.read_csv(file_name)
        df.columns = ['Resource', 'Start', 'Finish']
        fig3 = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color = "Resource", range_x = [startdate+' '+starttime, enddate+' '+endtime], title = "Timeline")
        return fig3


@app.callback(
    Output('graph2', 'figure'),
    Input('person-id', 'value'),
    Input('start-time', 'value'),
    Input('end-time', 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date'),
)

def update_graph(user_id,starttime, endtime, startdate,enddate):
    file_name = 'data/Processed/' + user_id + '_PAT.csv'
    fig = go.Figure()
    if os.path.isfile(file_name) == False:
        return fig
    else:
        #print(startdate + ' ' +starttime)
        st = startdate + ' ' + starttime
        ed = enddate + ' ' + endtime
        start_range = datetime.datetime.strptime(st, '%Y-%m-%d %H:%M')
        end_range = datetime.datetime.strptime(ed, '%Y-%m-%d %H:%M')
        df = pd.read_csv(file_name)
        df.columns = ['name', 'start_time', 'end_time']
        name_time_sum = dict()
        for name, start, end in zip(df['name'], df['start_time'], df['end_time']):
            start_time = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S.%f')
            end_time = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S.%f')
            if start_time <= start_range and end_time >= end_range:
                time_duration = end_range - start_range
            elif start_time <= start_range <= end_time:
                time_duration = end_time - start_range
            elif start_time <= end_range <= end_time:
                time_duration = end_range - start_time
            elif start_range <= start_time <= end_time <= end_range:
                time_duration = end_time - start_time
            else:
                time_duration = datetime.timedelta(seconds = 0)

            if name in name_time_sum:
                name_time_sum[name] += time_duration
            else:
                name_time_sum[name] = time_duration
        for name, time_sum in name_time_sum.items():
            print(f"{name}: {time_sum}")
            '''
        for name in name_time_sum:
            temp = name_time_sum[name]
            tmep2 = datetime.datetime.strptime(temp, '')
            '''
        def convert(t):
            t = int(t)
            seconds = t % 60
            temp = t // 60
            minutes = temp % 60
            temp = temp // 60
            hours = temp
            return datetime.timedelta(hours = hours, minutes = minutes, seconds = seconds)
        newdf = pd.DataFrame(list(name_time_sum.items()), columns = ['moving_type', 'time'])
        newdf['hours'] = newdf['time'].apply(lambda x:x.total_seconds()/3600)
        fig2 = px.bar(newdf, x = 'moving_type', y = 'hours', color = 'moving_type')
        return fig2
