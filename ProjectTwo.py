# Configure the necessary Python module imports for dashboard components
from dash import Dash
import dash_leaflet as dl
from dash import dcc
from dash import html
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import base64

# Configure OS routines
import os

# Configure the plotting routines
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#### FIX ME #####
# change animal_shelter and AnimalShelter to match your CRUD Python module file name and class name
from db_manip import AnimalShelter

###########################
# Data Manipulation / Model
###########################
# FIX ME update with your username and password and CRUD Python module name

username = "aacuser"
password = "password"

# Connect to database via CRUD Module
db = AnimalShelter(username, password)

# class read method must support return of list object and accept projection json input
# sending the read method an empty document requests all documents be returned
df = pd.DataFrame.from_records(db.read({}))

# MongoDB v5+ is going to return the '_id' column and that is going to have an 
# invlaid object type of 'ObjectID' - which will cause the data_table to crash - so we remove
# it in the dataframe here. The df.drop command allows us to drop the column. If we do not set
# inplace=True - it will reeturn a new dataframe that does not contain the dropped column(s)
#df.drop(columns=['_id'],inplace=True)

## Debug
# print(len(df.to_dict(orient='records')))
# print(df.columns)


#########################
# Dashboard Layout / View
#########################
app = Dash(__name__)

#FIX ME Add in Grazioso Salvare’s logo
image_filename = 'logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#FIX ME Place the HTML image tag in the line below into the app.layout code according to your design
#FIX ME Also remember to include a unique identifier such as your name or date
#html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))

app.layout = html.Div([
#    html.Div(id='hidden-div', style={'display':'none'}),
    html.Center(html.B(html.H1('Welcome'))),
    html.Hr(),
    html.Center(html.A(
        html.Img(
	    	id='Zach Beachy',
	    	src='data:image/png;base64,{}'.format(encoded_image.decode()),
	),
	href="https://www.snhu.edu",
	target='_blank'
    )),
    html.Div([
    #FIXME Add in code for the interactive filtering options. For example, Radio buttons, drop down, checkboxes, etc.
    dcc.RadioItems(
    	id='filter-type',
    	options=[
    		{'label':'Water Rescue','value':'Water Rescue'},
    		{'label':'Mountain/Wilderness Rescue','value':'Mountain/Wilderness Rescue'},
    		{'label':'Disaster Rescue or Individual Tracking','value':'Disaster Rescue or Individual Tracking'},
    		{'label':'Reset','value':'Reset'},
    		],
    		value='Reset', #Default value
    		labelStyle={'display':'inline-block'}
    ),
    ]),
    html.Hr(),
    dash_table.DataTable(
        id='datatable-id',
        columns=[{"name":i, "id":i, "deletable":False, "selectable":True} for i in df.columns],
        data = df.to_dict('records'),
        style_table={'overflowX':'auto','width':'100%'},
        row_selectable='single',
        selected_rows=[0],
        page_size=10,
    ),
    html.Br(),
    html.Hr(),
#This sets up the dashboard so that your chart and your geolocation chart are side-by-side
    html.Div(className='row',
         style={'display' : 'flex'},
             children=[
        html.Div(
            id='pie-chart-container',
            className='col s12 m6',
            children=[
                dcc.Graph(id='pie-chart'),
            ]
            ),
        html.Div(
            id='map-id',
            className='col s12 m6',
            children=[
                dcc.Graph(id='map-figure')
                ]
            )
        ])
])

#############################################
# Interaction Between Components / Controller
#############################################



    
@app.callback(Output('datatable-id','data'),
              [Input('filter-type', 'value')])
def update_dashboard(filter_type):
    if filter_type == 'Reset':
        #If reset is selected, return to original data
        return df.to_dict('records')
    elif filter_type is None:
        raise PreventUpdate #Keep data stale if nothing is selected
    else:
        #Where the fun happens. Different data queries depending on the selected
        # filter. I will build a db_query for each filter option then pass to
        # db_manip via the read function to get the data
        if filter_type == 'Water Rescue':
            query = {
                'breed':{'$in':['Labrador Retriever Mix', 'Chesapeake Bay Retriever', 'Newfoundland']},
                'sex_upon_outcome':'Intact Female',
                'age_upon_outcome_in_weeks':{'$gte':26, '$lte':156}
                }
        elif filter_type == 'Mountain/Wilderness Rescue':
            query = {
                'breed':{'$in':['German Shepherd', 'Alaskan Malamute', 'Old English Sheepdog', 'Siberian Husky', 'Rottweiler']},
                'sex_upon_outcome':'Intact Male',
                'age_upon_outcome_in_weeks':{'$gte':26, '$lte':156}
                }
        elif filter_type == 'Disaster Rescue or Individual Tracking':
            query = {
                'breed':{'$in':['Doberman Pinscher', 'German Shepherd', 'Golden Retriever', 'Bloodhound', 'Rottweiler']},
                'sex_upon_outcome':'Intact Male',
                'age_upon_outcome_in_weeks':{'$gte':20, '$lte':300}
                }
        else:
            #On the event that a nondefined filter is selected (perhaps due to future code changes)
            #return the original, unfiltered data
            return df.to_dict('records')
            
        #Now that we have defined a query based on the filter option selected, we can get the data via db_manip.py
        # with the read function and then return it in the expected format
        filtered_data = db.read(query)
        return filtered_data.to_dict('records')
    
## FIX ME Add code to filter interactive data table with MongoDB queries
#
#        
#        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns]
#        data=df.to_dict('records')
#       
#       
#        return (data,columns)


# Display the breeds of animal based on quantity represented in
# the data table
@app.callback(
    Output('pie-chart', "figure"),
    [Input('datatable-id', "derived_virtual_data")])
def update_graphs(viewData):
    
    if viewData is None:
        raise PreventUpdate
        
    dff = pd.DataFrame.from_dict(viewData)
    
    #Calculate the percentage of each dog reed in the filtered data
    breed_percentage = dff['breed'].value_counts(normalize=True) * 100

    figure = {
        'data':[
            {
                'labels':breed_percentage.index,
                'values':breed_percentage.values,
                'type':'pie',
                'hole':0.4,
            }
        ],
        'layout':{
            'title':'Breed Distribution',
        }
    }
    
    return figure
            
   
    
#This callback will highlight a cell on the data table when the user selects it
@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_styles(selected_columns):
    if selected_columns is None:
        raise PreventUpdate
        
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]


# This callback will update the geo-location chart for the selected data entry
# derived_virtual_data will be the set of data available from the datatable in the form of 
# a dictionary.
# derived_virtual_selected_rows will be the selected row(s) in the table in the form of
# a list. For this application, we are only permitting single row selection so there is only
# one value in the list.
# The iloc method allows for a row, column notation to pull data from the datatable
@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_data"),
     Input('datatable-id', "derived_virtual_selected_rows")])
def update_map(viewData, index):  
    if viewData is None or index is None or not index:
        raise PreventUpdate
    
    dff = pd.DataFrame.from_dict(viewData)
    # Because we only allow single row selection, the list can be converted to a row index here
    if index is None:
        row = 0
    else: 
        row = index[0]
        
    # Austin TX is at [30.75,-97.48]
    
    return [
        dl.Map(style={'width': '1000px', 'height': '500px'}, center=[30.75,-97.48], zoom=10, children=[
            dl.TileLayer(id="base-layer-id"),
            # Marker with tool tip and popup
            # Column 13 and 14 define the grid-coordinates for the map
            # Column 4 defines the breed for the animal
            # Column 9 defines the name of the animal
            dl.Marker(position=[dff.iloc[row,13],dff.iloc[row,14]], children=[
                dl.Tooltip(dff.iloc[row,4]),
                dl.Popup([
                    html.H1("Animal Name"),
                    html.P(dff.iloc[row,9])
                ])
            ])
        ])
    ]



app.run_server(debug=True)

