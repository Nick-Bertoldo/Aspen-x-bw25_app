# plotly dash libraries
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback, MATCH, ALL, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# libraries for graphs
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
load_figure_template(["minty"])

import base64
import datetime
import io

import pandas as pd

# brightway 2.5 libraries
import bw2analyzer as ba
import bw2data as bd
import bw2calc as bc
import bw2io as bi
import matrix_utils as mu
import bw_processing as bp

# bw project setup
bd.projects.set_current("<name of your project with ecoinvent>")
ei_db = bd.Database("<ecoinvent database name>")
bio_db = bd.Database("<biosphere database name>")
# impact assessment method used for the computation of LCA impacts
EF_select = [met for met in bd.methods if met[0] == 'EF v3.1']

def get_sheet_data(sheets, sheet_name):
    if sheet_name in sheets:
        return sheets[sheet_name].iloc[:, 2:]
    else:
        print(f'{sheet_name} sheet is missing!')
        return pd.DataFrame()

# list of conversion factors from Aspen to brightway
conversion_factors = {
    'kg/hr': 1,  # Assuming kg/hr stays as kg/hr, no conversion needed
    'l/min': 0.001 * 60 , # Convert l/min to cubic meters per hour (m³/hr)
    'tonne/year': 1000/(365*24), # Convert tonne/year to kg per hour (kg/hr)
    'MJ/hr' : 1
}

# calculate the flow amounts, considering the correct units, for setting up the LCA computation
def calculate_amount(row, ref_mass_flow):
    if row['Act unit'] == 'kilogram':
        return row['Mass Flows'] / ref_mass_flow
    elif row['Act unit'] == 'cubic meter':
        return row['Volume Flow'] / ref_mass_flow
    elif row['Act unit'] == 'megajoule':
        return row['Duty'] / ref_mass_flow
    elif row['Act unit'] =='kilowatt hour':
        return (row['Duty']/3.6) / ref_mass_flow # to convert MJ in kWh
    else:
        return 0.0
    
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME])
server = app.server

# app layout
# materials upload part
material_jumbotron = dbc.Col(
    html.Div(
        [
            dbc.Row(
                [
                    dcc.Upload(
                        id='upload-material',
                        children=html.Div([
                            html.Span(
                                children=[
                                    "Drag and Drop or",
                                    html.Br(),  # Optional line break for better spacing
                                    html.A('Select file with MATERIALS from Aspen', href="#")
                                ],
                                style={
                                    "display": "flex",
                                    "flex-direction": "column",  # Stack text vertically
                                    "justify-content": "center",
                                    "align-items": "center",
                                    "height": "100px",
                                    "width": "100%",
                                    "font-size": 25,
                                    "border-width": "3px",
                                    "border-style": "dashed",
                                    "border-radius": "50px",
                                    "cursor": "pointer"
                                }
                            )
                        ])
                    )
                ],
                style={
                    # 'display': 'flex',
                    'justifyContent': 'center',
                    # 'alignItems': 'center',
                    # 'height': '100vh'  # Adjust this to fit your design
                }
            ),
            html.Br(),
            dbc.Row(
                [
                    html.Div(id = 'material-data-upload', children = []),
                ]
            ),
            # dcc.Store(id = 'materials-store'),
            dcc.Store(id = 'input-flows-store'),
            dcc.Store(id = 'output-flows-store'), 
            html.Br(),
            dbc.Row(
                [
                    html.Div(id = 'output-type-error', children = []),
                ]
            ),
        ],
        className="h-100 p-5 text-black border rounded-3",
    ),
    md=6,
)

# utilities upload part
utilities_jumbotron = dbc.Col(
    html.Div(
        [
            dbc.Row(
                [
                    dcc.Upload(
                        id='upload-utility',
                        children=html.Div([
                            html.Span(
                                children=[
                                    "Drag and Drop or",
                                    html.Br(),  # Optional line break for better spacing
                                    html.A('Select file with UTILITIES from Aspen', href="#")
                                ],
                                style={
                                    "display": "flex",
                                    "flex-direction": "column",  # Stack text vertically
                                    "justify-content": "center",
                                    "align-items": "center",
                                    "height": "100px",
                                    "width": "100%",
                                    "font-size": 25,
                                    "border-width": "3px",
                                    "border-style": "dashed",
                                    "border-radius": "50px",
                                    "cursor": "pointer"
                                }
                            )
                        ])
                    )
                ],
                style={
                    'justifyContent': 'center',
                }
            ),
            html.Br(),
            dbc.Row(
                [
                    html.Div(id = 'utility-data-upload', children = []),
                ]
            ),
            dcc.Store(id = 'utilities-store'),
        ],
        className="h-100 p-5 text-black border rounded-3",
    ),
    md=6,
)

jumbotron = dbc.Row(
    [
        material_jumbotron, utilities_jumbotron],
    className="align-items-md-stretch",
)

app.layout = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.Img(src='assets/Poli.png', style={'height': 'auto', 'width': '50%'}),
                    width=2,
                    className="d-flex justify-content-center"
                ),
                dbc.Col(
                    html.Img(src='assets/BW_all_black_transparent_landscape.svg', style={'height': 'auto', 'width': '50%'}),
                    width=2,
                    className="d-flex justify-content-center"
                ),
                dbc.Col(
                    html.Img(src='assets/AspenPlus.png', style={'height': 'auto', 'width': '35%'}),
                    width=2,
                    className="d-flex justify-content-center"
                ),
            ],
            justify="center",
            className="align-items-center"
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    width=1
                ), 
                dbc.Col(
                    html.Div(
                        [
                            html.H1("Integrating Aspen Plus Simulations with Brightway 2.5 for Sustainable Process Design", style={'fontSize': 45, 'textAlign': 'center', 'color':'secondary'}),
                        ]#, style={'border': '2px solid black'}
                        , className="h-80 p-5 rounded-5" #className="h-100 p-5 bg-primary border-black rounded-5",
                    ), 
                    width=10
                ),
                dbc.Col(
                    width=1
                ), 
            ]
        ),
        html.Br(),
        jumbotron,  
        dcc.Store(id ='lca-setup'),
        html.Br(),
        html.Div(
            id='toggle-category',
            children=[
                dbc.Row(
                    [
                        dbc.Col(md=3),
                        dbc.Col(
                            [
                                html.H5('Select impact category'),
                                dcc.Dropdown(options = [{'label': EF_select[i][1], 'value': EF_select[i][1]} for i in range(len(EF_select))],
                                            id = 'impact-category',)
                            ],md=6,
                        ),
                        dbc.Col(md=3),
                    ],
                    className="align-items-md-stretch",
                ), 
            ], style={'display': 'none'},   
        ),
        html.Br(),
        dbc.Row(
            [ 
                dbc.Col(md=3),
                dbc.Col(
                    dcc.Loading(
                            id="load-total",
                                children=[
                                    html.Div(id='tot-impact', children=[]),
                                ],
                            type='circle',
                    ),
                    md=2),
                dbc.Col(
                    [
                        dcc.Loading(
                            id="load-graph",
                                children=[
                                    html.Div(
                                        [
                                            dcc.Graph(id='graph', style={'display': 'none'})
                                        ]
                                    )
                                ],
                            type="graph",
                        ),
                    ],md=4
                ),
                dbc.Col(md=3),
            ],
            # justify="center", 
            # align="center", 
            className="align-items-md-stretch",
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(md=5),
                dbc.Col(
                    [
                        dcc.Store(id='lca-results'),
                        html.Button("Download results", id="btn-download", style={'display':'none'}),
                        dcc.Download(id="download-lcia"),
                    ], md = 4,
                ),                        
                dbc.Col(md=3),
            ]
        ),
        html.Br(),
    ],
    fluid=True,
)

    

@callback(
    Output('material-data-upload', 'children'),
    Output('input-flows-store', 'data'),
    Output('output-flows-store', 'data'),
    Output('toggle-category', 'style', allow_duplicate=True),
    Input('upload-material', 'contents'),
    State('upload-material', 'filename'),
    State('upload-material', 'last_modified'),
    prevent_initial_call=True,
)
def materials_upload(content, filename, date):
    if content is None:
        return html.Div(), None, None, None

    content_type, content_string = content.split(',')

    try:
        decoded = base64.b64decode(content_string)
        if 'xlsx' in filename:
            material_df = pd.read_excel(io.BytesIO(decoded), skiprows=3, sheet_name='Material').iloc[:,2:]
            

            if not material_df.empty:
                material_df_t = material_df.set_index('Stream Name').T

                # Filter the columns based on the conditions
                outputs = (material_df_t['From'].notna()) & (material_df_t['To'].isna())
                output_df_t = material_df_t.loc[outputs,:]
                inputs = (material_df_t['From'].isna()) & (material_df_t['To'].notna())
                input_df_t = material_df_t.loc[inputs,:]

                # Transpose back to the original format
                output_tot_df = output_df_t.T.reset_index()
                output_df=pd.concat([output_tot_df.loc[(output_tot_df['Stream Name']=='Mass Flows')].iloc[[0]], output_tot_df.loc[(output_tot_df['Stream Name']=='Volume Flow')].iloc[[0]]]).reset_index(drop=True)
                input_tot_df = input_df_t.T.reset_index()
                input_df=pd.concat([input_tot_df.loc[(input_tot_df['Stream Name']=='Mass Flows')].iloc[[0]], input_tot_df.loc[(input_tot_df['Stream Name']=='Volume Flow')].iloc[[0]]]).reset_index(drop=True)
            
                unit_df = pd.concat([material_df.loc[(material_df['Stream Name']=='Mass Flows')].iloc[[0]], material_df.loc[(material_df['Stream Name']=='Volume Flow')].iloc[[0]]])[['Stream Name', 'Units']].reset_index(drop=True)
                


                children = [html.H5(f'Uploaded file: {filename}'), html.Br(), html.H2('Input flows:'),] + [
                    html.Div(
                        children=[
                            html.Br(),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H4(f'{input_df.columns[i]}', id={'type': 'input-name', 'index': i}),
                                            dbc.RadioItems(
                                                id = {'type':"flow-type-input",'index': i},
                                                options=[
                                                    {'label': 'Technosphere', 'value': 'Technosphere'},
                                                    {'label': 'Biosphere', 'value': 'Biosphere'},
                                                    {'label': 'No impact', 'value': 'No impact'}
                                                ],
                                                style={'columnCount': 1},
                                            ),
                                            html.Br(),
                                        ], md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Div(
                                                children=[],
                                                id={'type': 'input-element', 'index': i},
                                            ),
                                        ], md=9,
                                    ),
                                ],
                                className="align-items-md-stretch",
                            ),
                        ]
                    ) for i in range(1, len(input_df.columns))
                ] + [html.Br(), html.H2('Output flows:')] + [
                    html.Div(
                        children=[
                            html.Br(),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H4(f'{output_df.columns[j]}', id={'type': 'output-name', 'index': j}),
                                            # html.Br(),
                                            dcc.RadioItems(
                                                id={'type': 'output-type', 'index': j},
                                                options=[
                                                    {'label': 'Reference flow', 'value': 'Reference flow'},
                                                    {'label': 'Waste flow', 'value': 'Waste flow'},
                                                    {'label': 'By-product', 'value': 'By-product'},
                                                    {'label': 'Biosphere flow', 'value': 'Biosphere flow'},
                                                ],
                                                style={'columnCount': 1},
                                            ),
                                        ], md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Div(
                                                children=[],
                                                id={'type': 'output-element', 'index': j},
                                            ),
                                        ], md=9,
                                    ),
                                ],
                                className="align-items-md-stretch",
                            ),
                        ]
                    ) for j in range(1, len(output_df.columns))
                ]

                style = {'display': 'block'}

                in_df = input_df.set_index('Stream Name').T
                in_df_reset = in_df.reset_index()
                out_df = output_df.set_index('Stream Name').T
                out_df_reset = out_df.reset_index()

                mass_unit = unit_df[unit_df['Stream Name'] == 'Mass Flows']['Units'].values[0]
                volume_unit = unit_df[unit_df['Stream Name'] == 'Volume Flow']['Units'].values[0]

                in_df_reset['Mass Flows'] = in_df_reset['Mass Flows'] * conversion_factors[mass_unit]
                in_df_reset['Volume Flow'] = in_df_reset['Volume Flow'] * conversion_factors[volume_unit]
                out_df_reset['Mass Flows'] = out_df_reset['Mass Flows'] * conversion_factors[mass_unit]
                out_df_reset['Volume Flow'] = out_df_reset['Volume Flow'] * conversion_factors[volume_unit]

                input_data = in_df_reset.to_dict("records")
                output_data = out_df_reset.to_dict("records") #dfff.to_dict("records")

                return children, input_data, output_data,  style

    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file. Upload only .xlsx file']), None, None, {'display': 'None'}


@callback(Output({'type':'input-element', 'index':MATCH}, 'children'),
              Input({'type': 'flow-type-input', 'index': MATCH}, 'value'),
              prevent_initial_call=True) 

def input_element(type):
    if type is None:
        raise PreventUpdate
    elif type == 'Technosphere':
        index = ctx.triggered_id['index']
        children = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.I("Technosphere flow:"),
                            dbc.Input(
                                id={'type': 'search-ecoinvent', 'index': index},
                                type="text",
                                placeholder="search technosphere",
                            ),
                        ], md=4,
                    ),
                    dbc.Col(
                        [
                            html.Br(),
                            dcc.Dropdown(
                                options=[],
                                id={'type': 'ecoinvent-input', 'index': index},
                                optionHeight=120,
                            ),
                            html.I(id= {'type': 'ecoinvent-input-name', 'index': index}),
                        ], md=8,
                    ),
                ]
            ),
        ]
        return children
    
    elif type == 'Biosphere':
        index = ctx.triggered_id['index']
        children = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.I("Biosphere flow:"),
                            dbc.Input(
                                id={'type': 'search-bio', 'index': index},
                                type="text",
                                placeholder="search biosphere",
                            ),
                        ], md=4,
                    ),
                    dbc.Col(
                        [
                            html.Br(),
                            dcc.Dropdown(
                                options=[],
                                id={'type': 'bio-input', 'index': index},
                                optionHeight=120,
                            ),
                        ], md=8,
                    ),
                ]
            ),
        ]
        return children
    
    else: 
        return []


@callback(Output({'type': 'ecoinvent-input', 'index':MATCH}, 'options'),
          Input({'type': 'search-ecoinvent', 'index':MATCH}, 'value'),
          prevent_initial_call=True
)

def search_ecoinvent_activity(name):
    if name is None:
        raise PreventUpdate
    else:
        flow_list = ei_db.search(name, limit=50)
        options = [{'label': f"{item['name']}, {item['location']}", 'value': item[1]} for item in flow_list]
        return options
    
@callback(Output({'type': 'bio-input', 'index':MATCH}, 'options'),
          Input({'type': 'search-bio', 'index':MATCH}, 'value'),
          prevent_initial_call=True
)

def search_biosphere(name):
    if name is None:
        raise PreventUpdate
    else:
        flow_list = bio_db.search(f'natural {name}', limit=50)
        options = [{'label': f"{item['name']}, {item['categories']}", 'value': item[1]} for item in flow_list]
        return options

@callback(Output({'type': 'ecoinvent-input-name', 'index': MATCH}, 'children'),
          Input({'type': 'ecoinvent-input', 'index':MATCH}, 'value'),
          prevent_initial_call=True
)

def print_ei_name(ei_act):
    if ei_act is None:
        raise PreventUpdate
    else:
        ref_product = bd.get_node(code = ei_act)['reference product']
        return f"Reference product: {ref_product}"

@callback(Output({'type':'output-element', 'index':MATCH}, 'children'),
              Input({'type': 'output-type', 'index': MATCH}, 'value'),
              prevent_initial_call=True) 

def output_element(type):
    if type is None:
        raise PreventUpdate
    elif type == 'Reference flow':
        return []
    elif type == 'Waste flow':
        index = ctx.triggered_id['index']
        children = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Br(),
                            dbc.Input(
                                id={'type': 'waste', 'index': index},
                                type="text",
                                placeholder="Search waste",
                                # persistence=True,
                                # persistence_type='session',
                            ),
                        ], md=4,
                    ),
                    dbc.Col(
                        [
                            html.Br(),
                            dcc.Dropdown(
                                options = [],
                                id={'type': 'ecoinvent-waste', 'index': index},
                                optionHeight=120,
                                # persistence=True,
                                # persistence_type='session',
                            ),
                            html.I(id= {'type': 'waste-name', 'index': index}),
                        ], md=8,
                    ),
                ]
            )
        ]
        return children
    elif type == 'Biosphere flow':
        index = ctx.triggered_id['index']
        children = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Br(),
                            dbc.Input(
                                id={'type': 'bio', 'index': index},
                                type="text",
                                placeholder="Search emission",
                                # persistence=True,
                                # persistence_type='session',
                            ),
                        ], md=4,
                    ),
                    dbc.Col(
                        [
                            html.Br(),
                            dcc.Dropdown(
                                options = [],
                                id={'type': 'emission', 'index': index},
                                optionHeight=120,
                                # persistence=True,
                                # persistence_type='session',
                            ),
                        ], md=8,
                    ),
                ]
            )
        ]
        return children


@callback(Output('output-type-error', 'children'),
              Input({'type': 'output-type', 'index': ALL}, 'value'),
              prevent_initial_call=True) 

def ref_alert(types):
    if None in types:
        raise PreventUpdate
    elif 'Reference flow' not in types:
        children = [dbc.Alert("One of the output must be the reference flow", color="danger"),]
        return children

@callback(Output({'type': 'ecoinvent-waste', 'index':MATCH}, 'options'),
          Input({'type': 'waste', 'index':MATCH}, 'value'),
          prevent_initial_call=True
)

def search_waste_activity(waste):
    if waste is None:
        raise PreventUpdate
    else:
        ei_waste_list = ei_db.search(waste, limit=50)
        options = [{'label': f"{item['name']}, {item['location']}", 'value': item[1]} for item in ei_waste_list]
        return options
    

@callback(Output({'type': 'waste-name', 'index': MATCH}, 'children'),
          Input({'type': 'ecoinvent-waste', 'index':MATCH}, 'value'),
          prevent_initial_call=True
)

def print_waste_name(waste_act):
    if waste_act is None:
        raise PreventUpdate
    else:
        print(waste_act)
        ref_product = bd.get_node(code = waste_act)['reference product']
        return f"Reference product: {ref_product}"


@callback(Output({'type': 'emission', 'index':MATCH}, 'options'),
          Input({'type': 'bio', 'index':MATCH}, 'value'),
          prevent_initial_call=True
)

def search_emission(bio):
    if bio is None:
        raise PreventUpdate
    else:
        emission_list = bio_db.search(bio, limit=50)
        options = [{'label': f"{item['name']}, {item['categories']}", 'value': item[1]} for item in emission_list]
        return options


@callback(Output('utility-data-upload', 'children'),
          Output('utilities-store', 'data'),
          Output('toggle-category', 'style', allow_duplicate=True),
              Input('upload-utility', 'contents'),
              State('upload-utility', 'filename'),
              State('upload-utility', 'last_modified'),
              prevent_initial_call=True,
              ) 

def utility_upload(content, filename, date):
    content_type, content_string = content.split(',')


    try:
        decoded = base64.b64decode(content_string)
        if 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            utility_import_df = pd.read_excel(io.BytesIO(decoded)).rename(columns={'Utility ID':'Stream Name', 'Unnamed: 1':'Units'})
            
            # Create new DataFrames based on 'From' and 'To' conditions if material_df is not empty
            if not utility_import_df.empty:
                utility_df = utility_import_df.loc[(utility_import_df['Stream Name']=='Utility type')|(utility_import_df['Stream Name']=='Ultimate fuel source')|(utility_import_df['Stream Name']=='Mass flow')|(utility_import_df['Stream Name']=='Duty')].reset_index(drop=True)
                utility_flows = [
                    html.Div(
                        children=[
                            html.Br(),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H4(f'{utility_df.columns[i]}', id={'type':'utility-name', 'index': i}),
                                            html.H5(f"type: {utility_df[utility_df['Stream Name']=='Utility type'].iloc[0,i]}"),
                                            html.H5(f"source: {utility_df[utility_df['Stream Name'] == 'Ultimate fuel source'].iloc[0,i]}"),
                                            html.Br(),
                                        ],md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            html.I('Ecoinvent activity:'),
                                            dbc.Input(
                                                id={'type': 'search-utility', 'index': i},
                                                type="text",
                                                placeholder="Search ecoinvent activity",
                                                
                                                # persistence=True,
                                                # persistence_type='session',
                                            ),
                                        ], md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Br(),
                                            dcc.Dropdown(
                                                options = [],
                                                id={'type': 'ecoinvent-utility', 'index': i},
                                                optionHeight=120,
                                                # persistence=True,
                                                # persistence_type='session',
                                            ),
                                            html.I(id= {'type': 'utility-ecoinvent-name', 'index': i}),
                                        ], md=6,
                                    ),
                                ],
                                className="align-items-md-stretch",
                            ),
                        ]
                    ) for i in range(2, len(utility_df.columns))
                ]

                children = [html.H5(f'Uploaded file: {filename}'),html.Br(),] + utility_flows
                style = {'display': 'block'}

                util_unit_df=utility_df.iloc[1:, :2]
                util_df = utility_df.iloc[1:, :].drop(columns=['Units']).set_index('Stream Name').T
                util_df.rename(columns={'Mass flow':'Mass Flows'}, inplace=True)
                mass_unit = util_unit_df[util_unit_df['Stream Name'] == 'Mass flow']['Units'].values[0]
                energy_unit = util_unit_df[util_unit_df['Stream Name'] == 'Duty']['Units'].values[0]
                util_df['Type'] = 'Utility'
                util_df_reset = util_df.reset_index()
                util_df_reset['Mass flow'] = util_df_reset['Mass Flows'] * conversion_factors[mass_unit]
                util_df_reset['Duty'] = util_df_reset['Duty'] * conversion_factors[energy_unit]

                

                return children, util_df_reset.to_dict("records"), style
            
            else:
                children = [
                    html.Div([
                        html.H5(f'Uploaded file: {filename}'),
                        html.Div("The utility sheet is empty, select another file")

                    ])
                ]
                style = {'display': 'None'}
                utlity_data = None
                
                return children, utlity_data, style

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file. Upload only .xlsx file'
        ]), None, {'display': 'None'}
    
@callback(Output({'type': 'ecoinvent-utility', 'index':MATCH}, 'options'),
          Input({'type': 'search-utility', 'index':MATCH}, 'value'),
          prevent_initial_call=True
)

def search_ecoinvent_utility(name):
    if name is None:
        raise PreventUpdate
    else:
        ei_activity_list = ei_db.search(name, limit=50)
        options = [{'label': f"{item['name']}, {item['location']}", 'value': item[1]} for item in ei_activity_list]
        return options
    

@callback(Output({'type': 'utility-ecoinvent-name', 'index': MATCH}, 'children'),
          Input({'type': 'ecoinvent-utility', 'index':MATCH}, 'value'),
          prevent_initial_call=True
)

def print_util_ei_name(util_act):
    if util_act is None:
        raise PreventUpdate
    else:
        ref_product = bd.get_node(code = util_act)['reference product']
        return f"Reference product: {ref_product}"


@callback(
    Output('lca-setup', 'data'),
    Output('graph', 'style'),
    Input({'type': 'ecoinvent-input', 'index':ALL}, 'value'),
    Input({'type': 'bio-input', 'index':ALL}, 'value'),
    Input({'type':"flow-type-input",'index': ALL}, 'value'),
    Input({'type': 'output-type', 'index': ALL}, 'value'),
    Input({'type': 'ecoinvent-waste', 'index':ALL}, 'value'),
    Input({'type': 'emission', 'index':ALL}, 'value'),
    Input({'type': 'ecoinvent-utility', 'index':ALL}, 'value'),
    State('input-flows-store', 'data'),
    State('output-flows-store', 'data'),
    State('utilities-store', 'data'),
    prevent_initial_call=True
)

def lca_calc(act_in, bio_in, in_type, out_type, act_waste, emission, act_util, in_data, out_data, util_data):
    if 'Reference flow' not in out_type:
        raise PreventUpdate
    
    else:
        in_df = pd.DataFrame(in_data)
        in_df.rename(columns={'index':'Stream Name'}, inplace = True)
        
        in_df['Type']= None
        if len(in_type) != len(in_df['Type']):
            raise PreventUpdate
        else:
            in_df['Type']= in_type
            in_df['Activity'] = None
            in_df.loc[in_df['Type']=='Technosphere','Activity'] = act_in
            in_df.loc[in_df['Type']=='Biosphere','Activity'] = bio_in
            in_df['Act unit'] = None
            for i in range(len(in_df)):
                if in_df.loc[i, 'Type'] == 'No impact':
                    in_df.loc[i,'Act unit'] = None
                else:
                    in_df.loc[i,'Act unit'] = bd.get_node(code=in_df.loc[i, 'Activity'])['unit']
            out_df = pd.DataFrame(out_data)
            out_df.rename(columns={'index':'Stream Name'}, inplace = True)
            out_df['Type']=None
            out_df['Type']=out_type
            out_df['Activity'] = None
            out_df.loc[out_df['Type']=='Waste flow', 'Activity'] = act_waste
            out_df.loc[out_df['Type']=='Biosphere flow', 'Activity'] = emission
            out_df['Act unit'] = None
            for i in range(len(out_df)):
                if out_df.loc[i, 'Type']== "Waste flow":
                    if out_df.loc[i, 'Activity'] is None:
                        out_df.loc[i,'Act unit'] = None
                    else:
                        out_df.loc[i,'Act unit'] = bd.get_node(code=out_df.loc[i, 'Activity'])['unit']
                        if bd.get_node(code=out_df.loc[i, 'Activity'])['production amount']<0:
                            out_df.loc[i, 'Mass Flows'] *=(-1)
                            out_df.loc[i, 'Volume Flow'] *=(-1)
                else:
                    out_df.loc[i,'Act unit'] = "kilogram"

            util_df = pd.DataFrame(util_data)
            util_df.rename(columns={'index':'Stream Name'}, inplace = True)
            util_df['Activity'] = None
            util_df['Activity'] = act_util
            util_df['Act unit'] = None
            for i in range(len(util_df)):
                if util_df.loc[i, 'Activity'] is None:
                    util_df.loc[i,'Act unit'] = None
                else:
                    util_df.loc[i,'Act unit'] = bd.get_node(code=util_df.loc[i, 'Activity'])['unit']
            

            reference_mass_flow=out_df.loc[out_df['Type'] == "Reference flow",'Mass Flows']

            out_df['Amount'] = out_df.apply(calculate_amount, axis=1, ref_mass_flow=reference_mass_flow)
            in_df['Amount'] = in_df.apply(calculate_amount, axis=1, ref_mass_flow=reference_mass_flow)
            util_df['Amount'] = util_df.apply(calculate_amount, axis=1, ref_mass_flow=reference_mass_flow)

            act_df = pd.concat([in_df, out_df])
            act_df.loc[act_df['Type']=='Reference flow', 'Activity']=act_df.loc[act_df['Type']=='Reference flow', 'Stream Name']

            act_dff = act_df[~act_df['Type'].str.contains('Biosphere', na=False)]
            
            LCA_setting_df = pd.concat([act_dff, util_df])[['Stream Name', 'Type', 'Activity','Act unit','Amount']]

            style = {'display':'block'}

            return LCA_setting_df.to_dict("records"), style

@callback(
    Output('graph', 'figure'),
    Output('tot-impact', 'children'),
    Output('lca-results', 'data'),
    Output("btn-download", "style"),
    Input('impact-category', 'value'),
    State('lca-setup', 'data'),
    prevent_initial_call = True
)

def update_graph(category, lca_data):
    if category is None:
        raise PreventUpdate
    else:
        lca_setting_df = pd.DataFrame(lca_data)
        lca_setting_clean_df=lca_setting_df.dropna(subset=['Activity']).reset_index(drop=True)
        LCIA_df_list=[]
        lca_df=lca_setting_clean_df.copy()

        for i in range(len(EF_select)):
            lca_df=lca_setting_clean_df.copy()
            lca_df['Impact category']=EF_select[i][1]
            lca_df['Impact unit']=str(bd.methods[EF_select[i]]["unit"])
            LCIA_df_list.append(lca_df)

        lca_df=pd.concat(LCIA_df_list)
        lca_df['Impact'] = 0.0
        lca_df.reset_index(inplace=True, drop=True)

        activity = bd.get_node(code = lca_setting_clean_df['Activity'][0])
        lca = bc.LCA({activity:lca_setting_clean_df['Amount'][0]}, EF_select[0])
        lca.lci()

        for j in range(len(lca_setting_clean_df)):
                activity =bd.get_node(code = lca_setting_clean_df['Activity'][j])

                lca.redo_lci({activity.id:lca_setting_clean_df['Amount'][j]})
                for i in range(len(EF_select)):
                        lca.switch_method(EF_select[i])
                        lca.lcia()
                        lca_df.loc[(lca_df['Impact category']==EF_select[i][1]) 
                                        &  (lca_df['Activity']==lca_setting_clean_df['Activity'][j]) ,'Impact']=lca.score

        tot_impact = lca_df.loc[lca_df['Impact category']==category, 'Impact'].sum()
        unit = lca_df.loc[lca_df['Impact category']==category, 'Impact unit'].iloc[0]
        fig = px.bar(lca_df.loc[lca_df['Impact category']==category], x = "Impact category", 
                     y = 'Impact', color = "Stream Name", template="minty", barmode='stack', width=400, height=600)
        fig.update_yaxes(title={'text':''},tickfont={'size':18}, tickformat='.1e')

        fig.update_xaxes(matches=None, showticklabels=False, title="")


        fig.update_traces(
            marker=dict(line_color="black")#, pattern_fillmode="replace")
        )

        children = [
            html.H3("Total impact:"),
            html.Br(),
            html.H4(f"{tot_impact:.1e} {unit}")
        ]

        return fig, children, lca_df.to_dict('records'), {'display': 'block'}


@callback(
    Output("download-lcia", "data"),
    Input("btn-download", "n_clicks"),
    State('lca-results', 'data'),
    prevent_initial_call=True,
)

def func(n_clicks, lca_data):
    lcia_df = pd.DataFrame(lca_data)
    if not lcia_df.empty:
        return dcc.send_data_frame(lcia_df.to_excel, "lca_results.xlsx", index = False)

if __name__ == "__main__":
    app.run(debug=False, dev_tools_hot_reload=False, )

