
import dash
import flask
import json
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output,State
from datetime import datetime
import dash_table
import pandas as pd
import dash_bootstrap_components as dbc
from jupyter_dash import JupyterDash
#from flask_caching import Cache
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_app_route = '/'
dash_app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])
app = dash_app.server

df_delay=pd.read_csv('July2019_DepDelay.csv')
services=df_delay['AIRLINE'].unique()

df=pd.read_csv('delaypred_July312019.csv')
df.loc[df['DELAY_PREDICTION']=='Small Delay(<15 mins)','DELAY_PREDICTION']='Short Delay(<15 mins)'

#Controls and Styles
tabs_styles = {'margin-left': '20%','height': '20px'}
box_styles = {'height': '20px','margin-left': '2%','margin-right': '2%','background':''}
tabmenu = html.Div([                       
        dcc.Tabs(id="all-tabs-inline", value='tab-1',parent_className='custom-tabs',
        className='custom-tabs-container',
            children=[
            dcc.Tab(label='Departure delay prediction', value='tab-1',className='custom-tab',
                selected_className='custom-tab--selected'),
            dcc.Tab(label='Departure delay by Airlines', value='tab-2',className='custom-tab',
                selected_className='custom-tab--selected'),
            # dcc.Tab(label='ServiceClass Drilldown', value='tab-2',className='custom-tab',
            #     selected_className='custom-tab--selected'),
            ]),
            html.Div(id='graph_output')                       
    ])
CONTENT_STYLE = {'margin-left': '2%','margin-right': '2%'}
controls = dbc.Form(
    [
        dbc.FormGroup(
            [   dbc.Row([
                    dbc.Col([
                    dbc.Label("Select Airlines", className="mr-2"),                    
                    html.Div([dcc.Dropdown(id='dropdown_ser',options=[{'label':name, 'value':name} for name in services],value = 'American Airlines Inc.',multi=False)],),
                    ],width=4),
                    dbc.Col([ 
                    html.Br(),
                    html.Br(),                    
                    html.Div([dbc.Label("Departure delays for Outgoing flights across US State Airports - July 2019", className="mr-3"),])
                    ],width=8),
                ]),
            ],
        ),
    ])  

Topmenu=dbc.Card(dbc.CardBody([controls]))
# App and app layout with Tabs
app.layout = html.Div([tabmenu])


@dash_app.callback(
    Output('graph_6', 'figure'),    
    [Input('dropdown_ser', 'value')]
    )
def update_graph_6(dropdown_ser_value):

    ### TargetClass
    #if dropdown_ser_value==['American Airlines']:
    #data_grp=df.groupby(['AIRLINE','AIRPORT_x','CITY_x','ORIGIN_STATE_NM'])['DEP_DELAY'].mean()
    print(dropdown_ser_value)
    print(df_delay.shape)
    data_grp=df_delay[df_delay['AIRLINE']==dropdown_ser_value]
    print("grouping")

    data_grp['text'] = data_grp['AIRPORT_x'] + '' + data_grp['CITY_x'] + ', ' + data_grp['ORIGIN_STATE_NM'] + '' + 'Arrivals: ' + data_grp['DEP_DELAY'].astype(str)
    fig = go.Figure(data=go.Scattergeo(
        lon = data_grp['LONGITUDE_x'],
        lat = data_grp['LATITUDE_x'],
        text = data_grp['text'],
        mode = 'markers',
        marker = dict(
        size = 10,
        opacity = 0.9,
        reversescale = True,
        autocolorscale = False,
        symbol = 'circle',
        line = dict(
            width=1,
            color='rgba(102, 102, 102)'
        ),
        colorscale = 'Greens',
        #cmin = data_grp['DEP_DELAY'].min(),
        color = data_grp['DEP_DELAY'],
        #cmax = data_grp['DEP_DELAY'].max(),
        colorbar_title="Outgoing flights<br>July 2019 departure delay(in minutes)<br>Hover for airport names)"
    ) ,    
    ))
    fig.update_layout(
            #title = 'American Airlines Delays<br>(Hover for airport names)',
            geo_scope='usa',
            margin=dict(r=10, l=10, t=30, b=0),
            template='plotly_dark'
        )
    return fig

@dash_app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
    )
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@dash_app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)
    

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["CITY"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["DELAY_PREDICTION"] if column in dff
    ]



######################################################### Main Tab code #####################################################

@dash_app.callback([Output('graph_output', 'children')],
              [Input('all-tabs-inline', 'value')]              
            )
# @cache.memoize(timeout=20) 
def render_content(tab):    
    graph_output = ''
    if   tab=='tab-2':  
        graph_output= html.Div([
        html.Div([Topmenu]),
        html.Br(),        
        html.Div([
                    dbc.Row([
                        dbc.Col([
                                dbc.Row([dbc.Col([dcc.Graph(id='graph_6')], width=12),], align='center'),
                                ], width=12),                        
                    ],align='center'),                   
                ],),
                ],style=CONTENT_STYLE)       
    elif tab=='tab-1':
        
        graph_output= html.Div([
        dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
        ),
        html.Div(id='datatable-interactivity-container')
        ])
            
    return [graph_output]

if __name__ == '__main__':
    #app.run_server(debug=True,use_reloader=False)
    dash_app.run_server(debug=False,port=80)
