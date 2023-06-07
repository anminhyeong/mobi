'''
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
from server import app

# Load the updated user_info.csv with the additional columns
user_info_updated_df = pd.read_csv('data/user_info_updated.csv')

# Define the layout for the selectgr page
layout = html.Div(
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
    Input("create-group-button", "n_clicks"),
    State("group-name-input", "value")
)
def create_group(n_clicks, group_name):
    if n_clicks > 0 and group_name:
        # Perform group creation process here
        # You can save the selected group members to a new DataFrame or perform any other necessary actions
        
        return html.Div(f"Group '{group_name}' created successfully!")
    
    return html.Div()
    '''