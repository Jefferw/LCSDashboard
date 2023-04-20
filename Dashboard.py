import pandas as pd
import re
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, dash_table  # pip install dash (version 2.0.0 or higher)

#Dashboard created by Jefferson Williams 2023
#data courtesy of oracleselixer.com

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_csv('LCS 2023 Spring Patch 13.01 to 13.05.csv')
initial_active_cell = {"row": 0, "column": 0}

#create data for initial table where patch == 13.01 and league == LCS
gamesdf = pd.read_csv('MajorRegion Regular Season Games.csv')
default_league = 'LCS'
default_patch = 13.01
default_champ_name = 'Please select a champion from the left table'
patchdf = df[df['Patch'] == default_patch]
patchdf = df[['Champion', 'Pos', 'GP', 'P+B%']][:8]
patchdf.columns = ['Champion', 'Role', 'Games Picked', 'Presence']


# ------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id="select_patch",
                        options=[
                            {"label": "13.01", "value": 13.01},
                            {"label": "13.03", "value": 13.03},
                            {"label": "13.04", "value": 13.04},
                            {"label": "13.05", "value": 13.05}],
                        multi=False,
                        value=13.01,
                        )
                    ], width =2)   
            ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(id = 'pick_table', data=patchdf.to_dict('records'), 
                style_cell = {
                    'textAlign' : 'center',
                    'height': '60px',
                    'width': '20%',
                    'whiteSpace': 'normal', 'autoWidth': False},
                active_cell= initial_active_cell),
        ], width = 3),

        dbc.Col([
            dbc.Alert(id='tbl_out', children = 'Select a Champion'),
            dash_table.DataTable(id = 'champ_table', data=None),
            dcc.Graph(id='presence_graph')
        ], width = 5),



        dbc.Col([
            html.Img(id = 'champ_splash', src = None, style = {'height': '90%'})
        ], width = 4)
    ]),
    
    html.Br(),


], fluid = True)

# callbacks
#--------------------------------------------------------------------------------
@app.callback(
    Output(component_id='pick_table', component_property='data'),
    Input(component_id='select_patch', component_property='value')
)

def update_table(option_patch):
    
    #returns new data to left table when patch option is change
    picks_data = df.copy()
    picks_data = picks_data[picks_data['Patch'] == option_patch]
    picks_data = picks_data[['Champion', 'Pos', 'GP', 'P+B%']][:8]
    picks_data.columns = ['Champion', 'Role', 'Games Picked', 'Presence (As Percent)']


    return picks_data.to_dict('records')

@app.callback(
    Output(component_id = 'tbl_out', component_property='children'),
    Output(component_id = 'champ_table', component_property = 'data'),
    Output(component_id = 'champ_splash', component_property = 'src'),
    Output(component_id='presence_graph', component_property = 'figure'),
    Input(component_id= 'pick_table', component_property= 'active_cell'),
    State(component_id = 'select_patch', component_property = 'value')
)

def update_champ_name(active_cell, option_patch):
    #returns new data to champion table and line chart when champion name is click on the left table

    #create copies of df to alter based on input
    champ_history = df.copy()
    picks_data = df.copy()
    champ_data = df.copy()

    #set cell_value = to the contents of the cell selected
    picks_data = picks_data[picks_data['Patch'] == option_patch].reset_index()
    data_row= active_cell['row']
    data_col_id = active_cell['column_id']
    cell_value = picks_data.loc[data_row, data_col_id]
    
    #creates df based on champ and patch selected
    champ_data = champ_data[(champ_data['Patch'] == option_patch) & (champ_data['Champion'] == cell_value)]
    champ_data = champ_data[['Pos', 'P%', 'B%', 'W%']]
    champ_data.columns = ['Role', 'Pick %', 'Ban %', 'Win Rate']

    #for some reason url for wukong is MonkeyKing instead of his name
    if cell_value == 'Wukong':
        splash_url =  ('https://ddragon.leagueoflegends.com/cdn/img/champion/loading/MonkeyKing_0.jpg')

    #strips apostrophes and spaces from champion name so they can be fed into the url 
    else:  
        champ_name_for_url = re.sub("'", '', cell_value)
        champ_name_for_url = re.sub(" ", '', champ_name_for_url)
        splash_url =  ('http://ddragon.leagueoflegends.com/cdn/img/champion/loading/' + champ_name_for_url + '_0.jpg')

    #creates df from champion name on presence per patch
    champ_history = champ_history[champ_history['Champion'] == cell_value]
    champ_history = champ_history[['Patch', 'P+B%']]
    champ_history.columns = ['Patch', 'Presence']

    #creates a line plot with the above data
    fig = px.line(champ_history, x="Patch", y="Presence", title= f'{cell_value} Presence by Patch')
    fig.update_xaxes(type = 'category')

    return str(cell_value), champ_data.to_dict('records'), splash_url, fig
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
