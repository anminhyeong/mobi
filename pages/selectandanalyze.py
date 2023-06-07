import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
from server import app
import json
import plotly.express as px
import plotly.graph_objects as go
import os

user_info_updated_df = pd.read_csv('data/user_info_updated.csv')

groups = ['P0701', 'P0702', 'P0703']

#fig = px.pie(mov_stats, values = 'timedelta', names = mov_stats.index, hole = .9)


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
fig1 = go.Figure(data=[go.Pie(labels=group_mov_stats.index,
                             values=group_mov_stats['duration'], hole = .9)])
fig1.update_traces(hoverinfo='label+percent+text', text = (group_mov_stats['days'] * 24 + group_mov_stats['hours']).astype(str) + 'h ' + group_mov_stats['minutes'].astype(str) + 'm ' + group_mov_stats['seconds'].astype(str) + 's', textinfo = 'label+text',
                  marker=dict(line=dict(color='#000000', width=2)))
fig1.update_layout(width = 400, height = 400, legend = {'xanchor':'center', 'yanchor':'middle', 'y':0.5, 'x':0.5})

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

AUE_PAT = pd.DataFrame()
for person in groups:
    temp = pd.read_csv(f'data/Processed/{person}_AUEwithPAT.csv')
    temp.start_time = pd.to_datetime(temp.start_time)
    temp.end_time = pd.to_datetime(temp.end_time)
    temp['duration'] = temp.end_time - temp.start_time
    temp['person'] = person
    AUE_PAT = AUE_PAT.append(temp)

topappusing = AUE_PAT.groupby('name')['duration'].sum().sort_values(ascending=False).head(15)
topappusing = pd.concat([topappusing, topappusing.dt.components], axis = 1)
topappusing.hours = 24 * topappusing.days + topappusing.hours

fig3 = go.Figure(data = [go.Bar(name = 'AppUsed',
                                x = topappusing.index, 
                                y = topappusing['duration'], 
                                text = topappusing.hours.astype(str) + 'h ' + topappusing.minutes.astype(str) + 'm ' + topappusing.seconds.astype(str) + 's',
                                textposition = 'none',
                                hovertemplate = 'AppName : %{x}<br>Total App Used : %{text}')])
fig3.update_yaxes(visible=False)
    
top5app = AUE_PAT.groupby(['name','actionType'])['duration'].sum().loc[AUE_PAT.groupby('name')['duration'].sum().sort_values(ascending=False).head(5).index].reset_index(drop = False)
top5app = pd.concat([top5app, top5app.duration.dt.components], axis = 1)
top5app.hours = 24 * top5app.days + top5app.hours

fig4 = px.bar(top5app, x = 'name', y = 'duration', color = 'actionType', text=top5app.hours.astype(str) + 'h ' + top5app.minutes.astype(str) + 'm ' + top5app.seconds.astype(str) + 's', barmode = 'group')
fig4.update_layout(legend = dict(yanchor = 'bottom', y = 0.01, xanchor = 'right', x = 0.99))
fig4.update_traces(hovertemplate = "AppName : %{x}<br>AppUsingTime : %{text}", textposition = "none")
fig4.update_xaxes(categoryorder = 'total descending')
fig4.update_yaxes(autorange = 'reversed')
fig4.update_yaxes(visible=False)


select_layout = html.Div(
    [
        html.H2("Group Selection"),
        
        # Input for group name
        html.Div(
            [
                html.Label("Group Name"),
                dbc.Input(id="group-name-input", type="text", placeholder = "group name")
            ],
            style={"marginBottom": "1rem"}
        ),
        
        # Filter inputs for age, gender, movement time/fraction, phone usage time/fraction
        html.Div(
            [
                html.Label("Age"),
                dcc.RangeSlider(
                    id="age-range-slider",
                    min=user_info_updated_df['Age'].min(),
                    max=user_info_updated_df['Age'].max(),
                    marks={str(age): str(age) for age in range(user_info_updated_df['Age'].min(), user_info_updated_df['Age'].max() + 1, 5)},
                    step=1,
                    value=[user_info_updated_df['Age'].min(), user_info_updated_df['Age'].max()]
                ),
            ],
            style={"marginBottom": "1rem"}
        ),
        
        html.Div(
            [
                html.Label("Gender"),
                dcc.Dropdown(
                    id="gender-dropdown",
                    options=[
                        {"label": "Male", "value": "M"},
                        {"label": "Female", "value": "F"},
                    ],
                    multi=True
                ),
            ],
            style={"marginBottom": "1rem"}
        ),
        
        html.Div(
            [
                html.Label("Movement Time Fraction"),
                dcc.RangeSlider(
                    id="movement-fraction-range-slider",
                    min=0,
                    max=1,
                    marks={i/10: str(i/10) for i in range(0, 11)},
                    step=0.1,
                    value=[0, 1]
                ),
            ],
            style={"marginBottom": "1rem"}
        ),
        
        html.Div(
            [
                html.Label("Phone Usage Time Fraction"),
                dcc.RangeSlider(
                    id="usage-fraction-range-slider",
                    min=0,
                    max=1,
                    marks={i/10: str(i/10) for i in range(0, 11)},
                    step=0.1,
                    value=[0, 1]
                ),
            ],
            style={"marginBottom": "1rem"}
        ),
        
        # Button to submit the group selection
        #html.Button("Create Group", id="", n_clicks=0),
        
        dbc.Button("Create Group", color="primary", className="me-1", id="create-group-button", n_clicks=0),

        # Div to display selected group members
        html.Div(id="selected-group-members"),
        
        # Div to display message on successful group creation
        html.Div(id="group-creation-message")
    ]
)

group_layout = html.Div([
    html.Div(html.P(html.B('Group Stats')), className='Header'),
    html.Div(children = [
        html.Div(children = [
            html.Div(children = [
                dcc.Graph(id = 'fig1'),
                dcc.Graph(id = 'fig2'),
            ], style={'display':'inline-flex'}),
            html.Div(children = [
                dcc.Dropdown(id = 'x_axis',
                            options = [{'label' : i, 'value' : i} for i in PATE.actionType.unique()],
                            multi = True,
                            clearable = False,
                            value = None,
                            style = {'width' : '100%'}),
                dcc.Dropdown(id = 'y_axis',
                            options = [{'label' : i, 'value' : i} for i in AUEE.name.unique()],
                            multi = True,
                            clearable = False,
                            value = None,
                            style = {'width' : '100%'})
            ], style = {'display':'flex'}),
            html.Div(children = [
                dcc.Graph(id = 'graph', style = {'width':'85%', 'height':'300pt'}),
                html.Div(id = 'click-data', style = {'width':'100pt', 'height':'300pt'})
            ], style = {'display':'flex', 'flex-direction' : 'column'})
        ], style = {'display':'flex', 'witdh' : '60%', 'flex-direction' : 'column'}),
        html.Div(children = [
            dcc.Graph(id = 'fig3'),
            dcc.Graph(id = 'fig4')
        ], style={'display':'inline-flex', 'flex-direction' : 'column'})
    ], style = {'display' : 'flex', 'width' : '100%'})
    #dash.page_container
], style = {'display' : 'flex', 'width' : '100%', 'flex-direction' : 'column', 'flex-wrap':'wrap'})

layout = html.Div(
        dbc.Row(
            [dbc.Col(select_layout, width=3),
            dbc.Col(group_layout, width=9)]
        )
)

# Callback to filter participants and display selected group members
@app.callback(
    Output("selected-group-members", "children"),
    Input("create-group-button", "n_clicks"),
    Input("age-range-slider", "value"),
    Input("gender-dropdown", "value"),
    Input("movement-fraction-range-slider", "value"),
    Input("usage-fraction-range-slider", "value"),
    State("group-name-input", "value")
)
def filter_group_members(n_clicks, age_range, gender, movement_fraction_range, usage_fraction_range, group_name):
    if n_clicks > 0:
        selected_group_df = user_info_updated_df.copy()
        
        if not gender:
            return html.Div("Select Gender!")

        # Apply filters based on age, gender, movement time/fraction, and phone usage time/fraction
        selected_group_df = selected_group_df[
            (selected_group_df['Age'] >= age_range[0]) &
            (selected_group_df['Age'] <= age_range[1]) &
            (selected_group_df['Gender'].isin(gender)) &
            (selected_group_df['movement_fraction'] >= movement_fraction_range[0]) &
            (selected_group_df['movement_fraction'] <= movement_fraction_range[1]) &
            (selected_group_df['usage_fraction'] >= usage_fraction_range[0]) &
            (selected_group_df['usage_fraction'] <= usage_fraction_range[1])
        ]
        
        groups.clear()
        groups.extend(selected_group_df['UID'].tolist())
        
        num_members = len(selected_group_df)
        # Display selected group members
        if not selected_group_df.empty:
            return html.Div(f"{num_members} people selected for this group")
        else:
            return html.Div("No one meets the selected criteria.")
    
    return html.Div()

# Callback to display group creation message
@app.callback(
    Output("group-creation-message", "children"),
    Output("fig1", "figure"),
    Output("fig2", "figure"),
    Output("fig3", "figure"),
    Output("fig4", "figure"),
    Input("create-group-button", "n_clicks"),
    State("group-name-input", "value")
)
def create_group(n_clicks, group_name):
    if n_clicks > 0 and group_name and len(groups) > 0:
        # Perform group creation process here
        # You can save the selected group members to a new DataFrame or perform any other necessary actions
        PATE = pd.DataFrame()
        for person in groups:
            if len(str(person)) == 3:
                temp = pd.read_csv(f'data/Processed/P0{person}_PAT.csv')
            else:
                temp = pd.read_csv(f'data/Processed/P{person}_PAT.csv')
            temp.start_time = pd.to_datetime(temp.start_time)
            temp.end_time = pd.to_datetime(temp.end_time)
            temp['duration'] = temp.end_time - temp.start_time
            temp['person'] = person
            PATE = PATE.append(temp)
        group_mov_stats = PATE.groupby('actionType')['duration'].sum()
        group_mov_stats = pd.concat([group_mov_stats, group_mov_stats.dt.components], axis = 1)
        fig1 = go.Figure(data=[go.Pie(labels=group_mov_stats.index,
                                    values=group_mov_stats['duration'], hole = .9)])
        fig1.update_traces(hoverinfo='label+percent+text', text = (group_mov_stats['days'] * 24 + group_mov_stats['hours']).astype(str) + 'h ' + group_mov_stats['minutes'].astype(str) + 'm ' + group_mov_stats['seconds'].astype(str) + 's', textinfo = 'label+text',
                        marker=dict(line=dict(color='#000000', width=2)))
        fig1.update_layout(width = 400, height = 400, legend = {'xanchor':'center', 'yanchor':'middle', 'y':0.5, 'x':0.5})

        AUEE = pd.DataFrame()
        for person in groups:
            if len(str(person)) == 3:
                temp = pd.read_csv(f'data/Processed/P0{person}_AUE.csv')
            else:
                temp = pd.read_csv(f'data/Processed/P{person}_AUE.csv')
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

        AUE_PAT = pd.DataFrame()
        for person in groups:
            if len(str(person)) == 3:
                temp = pd.read_csv(f'data/Processed/P0{person}_AUEwithPAT.csv')
            else:
                temp = pd.read_csv(f'data/Processed/P{person}_AUEwithPAT.csv')
            temp.start_time = pd.to_datetime(temp.start_time)
            temp.end_time = pd.to_datetime(temp.end_time)
            temp['duration'] = temp.end_time - temp.start_time
            temp['person'] = person
            AUE_PAT = AUE_PAT.append(temp)

        topappusing = AUE_PAT.groupby('name')['duration'].sum().sort_values(ascending=False).head(15)
        topappusing = pd.concat([topappusing, topappusing.dt.components], axis = 1)
        topappusing.hours = 24 * topappusing.days + topappusing.hours

        fig3 = go.Figure(data = [go.Bar(name = 'AppUsed',
                                        x = topappusing.index, 
                                        y = topappusing['duration'], 
                                        text = topappusing.hours.astype(str) + 'h ' + topappusing.minutes.astype(str) + 'm ' + topappusing.seconds.astype(str) + 's',
                                        textposition = 'none',
                                        hovertemplate = 'AppName : %{x}<br>Total App Used : %{text}')])
        fig3.update_yaxes(visible=False)
            
        top5app = AUE_PAT.groupby(['name','actionType'])['duration'].sum().loc[AUE_PAT.groupby('name')['duration'].sum().sort_values(ascending=False).head(5).index].reset_index(drop = False)
        top5app = pd.concat([top5app, top5app.duration.dt.components], axis = 1)
        top5app.hours = 24 * top5app.days + top5app.hours

        fig4 = px.bar(top5app, x = 'name', y = 'duration', color = 'actionType', text=top5app.hours.astype(str) + 'h ' + top5app.minutes.astype(str) + 'm ' + top5app.seconds.astype(str) + 's', barmode = 'group')
        fig4.update_layout(legend = dict(yanchor = 'bottom', y = 0.01, xanchor = 'right', x = 0.99))
        fig4.update_traces(hovertemplate = "AppName : %{x}<br>AppUsingTime : %{text}", textposition = "none")
        fig4.update_xaxes(categoryorder = 'total descending')
        fig4.update_yaxes(autorange = 'reversed')
        fig4.update_yaxes(visible=False)
        
        return html.Div(f"Group '{group_name}' created successfully!"), fig1, fig2, fig3, fig4
    
    return html.Div(), fig1, fig2, fig3, fig4
    

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
