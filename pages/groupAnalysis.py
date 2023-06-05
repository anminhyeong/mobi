import dash
import json
from dash import dcc, html, Input, Output
from server import app
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import os

#testing groups
groups = ['P0701', 'P0702', 'P0703']

#fig = px.pie(mov_stats, values = 'timedelta', names = mov_stats.index, hole = .9)
PATE = pd.DataFrame()
for person in groups:
    temp = pd.read_csv(f'data/Processed/{person}_PAT.csv')
    temp.start_time = pd.to_datetime(temp.start_time)
    temp.end_time = pd.to_datetime(temp.end_time)
    temp['duration'] = temp.end_time - temp.start_time
    temp['person'] = person
    PATE = PATE.append(temp)
group_mov_stats = PATE.groupby('actionType')['duration'].sum()
group_mov_stats = pd.concat([group_mov_stats, group_mov_stats.dt.components], axis = 1)
fig = go.Figure(data=[go.Pie(labels=group_mov_stats.index,
                             values=group_mov_stats['duration'], hole = .9)])
fig.update_traces(hoverinfo='label+percent+text', text = (group_mov_stats['days'] * 24 + group_mov_stats['hours']).astype(str) + 'h ' + group_mov_stats['minutes'].astype(str) + 'm ' + group_mov_stats['seconds'].astype(str) + 's', textinfo = 'label+text',
                  marker=dict(line=dict(color='#000000', width=2)))
fig.update_layout(width = 400, height = 400, legend = {'xanchor':'center', 'yanchor':'middle', 'y':0.5, 'x':0.5})

AUEE = pd.DataFrame()
for person in groups:
    temp = pd.read_csv(f'data/Processed/{person}_AUE.csv')
    temp.start_time = pd.to_datetime(temp.start_time)
    temp.end_time = pd.to_datetime(temp.end_time)
    temp['duration'] = temp.end_time - temp.start_time
    temp['person'] = person
    AUEE = AUEE.append(temp)
app_usage_stats = AUEE.groupby('name')['duration'].sum()
app_usage_stats = pd.concat([app_usage_stats, app_usage_stats.dt.components], axis = 1)

fig2 = go.Figure(data=[go.Pie(labels=app_usage_stats.index,
                             values=app_usage_stats['duration'], hole = .9)])
fig2.update_traces(hoverinfo='label+percent+text', text = (app_usage_stats['days'] * 24 + app_usage_stats['hours']).astype(str) + 'h ' + app_usage_stats['minutes'].astype(str) + 'm ' + app_usage_stats['seconds'].astype(str) + 's', textinfo = 'none',
                  marker=dict(line=dict(color='#000000', width=2)))
fig2.update_layout(width = 600, height = 400)

layout = html.Div([
    html.Div(html.P(html.B('Group Stats')), className='Header'),
    html.Div(children = [
        dcc.Graph(figure = fig),
        dcc.Graph(figure = fig2)
    ], style={'display':'inline-flex'}),
    html.Div(children = [
        dcc.Dropdown(id = 'x_axis',
                     options = [{'label' : i, 'value' : i} for i in PATE.actionType.unique()],
                     multi = True,
                     clearable = False,
                     value = None,
                     style = {'width' : '200pt'}),
        dcc.Dropdown(id = 'y_axis',
                     options = [{'label' : i, 'value' : i} for i in AUEE.name.unique()],
                     multi = True,
                     clearable = False,
                     value = None,
                     style = {'width' : '200pt'})
    ], style = {'display':'flex'}),
    html.Div(children = [
        dcc.Graph(id = 'graph', style = {'width':'600pt', 'height':'300pt'}),
        html.Div(id = 'click-data', style = {'width':'100pt', 'height':'300pt'}),
        #dcc.Link('test', href = '/indiv')
    ], style = {'display':'flex'}),
    #dash.page_container
], style = {'display' : 'flex', 'width' : '100%', 'flex-direction' : 'column', 'flex-wrap':'wrap'})

@app.callback(
    Output('graph', 'figure'),
    Input('x_axis', 'value'),
    Input('y_axis', 'value')
)
def update_graph(x_axis, y_axis):
    if not x_axis or not y_axis:
        fig = go.Figure(go.Scatter(x=pd.Series(dtype=object), y=pd.Series(dtype=object), mode="markers"))
        return fig
    zeros = pd.Series(pd.Timedelta(0), index = groups)   
    tmp = PATE[PATE['actionType'].isin(x_axis)].groupby(['person'])['duration'].sum().add(zeros, fill_value = 0)
    tmp2 = AUEE[AUEE['name'].isin(y_axis)].groupby(['person'])['duration'].sum().add(zeros, fill_value = 0)
    fig = px.scatter(x = tmp, y = tmp2)
    fig.update_traces(hoverinfo='x+y+text', text = groups)
    fig.update_layout(clickmode = 'event+select')
    return fig

@app.callback(
    Output('click-data', 'children'),
    Input('graph', 'clickData'))
def display_click_data(clickData):
    if clickData == None:
        return None
    return groups[clickData['points'][0]['pointIndex']]
