import pandas as pd #
import numpy as np
import seaborn as sns
import matplotlib
#%matplotlib inline

import plotly.graph_objects as go
import matplotlib.pyplot as plt

#from plotly.subplots import make_subplots
from datetime import date

import plotly
# Import the necessaries libraries to work offline
#import plotly.offline as pyo
# Set notebook mode to work in offline
#pyo.init_notebook_mode()


#from jupyter_dash import JupyterDash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output, State

import dash
from dash import dash_table

# libraries to get files from the internet
import zipfile
from urllib.request import urlopen
import shutil
import os

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

#app = JupyterDash(__name__)

####################
######## To get the files from the internet
####################
'''
url = 'http://ergast.com/downloads/f1db_csv.zip'
file_name = 'f1db_csv.zip'

# extracting zipfile from URL
with urlopen(url) as response, open(file_name, 'wb') as out_file:
    shutil.copyfileobj(response, out_file)

# extracting required file from zipfile # indent to
with zipfile.ZipFile(file_name) as zf:
    zf.extract('seasons.csv')                    #
    zf.extract('circuits.csv')                   # 77
    zf.extract('status.csv')                     # 137
    zf.extract('constructors.csv')               # 211
    zf.extract('drivers.csv')                    # 853

    zf.extract('races.csv')                      # 1058
    zf.extract('pit_stops.csv')                  # 8374
    zf.extract('qualifying.csv')                 # 8873
    zf.extract('constructor_results.csv')        # 11820
    zf.extract('constructor_standings.csv')      # 12586

    zf.extract('results.csv')                    # 25140
    zf.extract('driver_standings.csv')           # 33125
    #zf.extract('lap_times.csv')                  # 501586

# deleting the zipfile from the directory
#os.remove('f1db_csv.zip')
'''
# loading data from the file
seasons = pd.read_csv('seasons.csv')
circuits = pd.read_csv('circuits.csv')
status = pd.read_csv('status.csv')
constructors = pd.read_csv('constructors.csv', names=['constructorId', 'constructorRef',
         'constructorName', 'constructorNationality', 'constructorUrl'],header=0)
drivers = pd.read_csv('drivers.csv',names=['driverId', 'driverRef', 'driverNumber', 'driverCode',
         'driverForename', 'driverSurname', 'driverDob','driverNationality', 'driverUrl'],header=0)
#races = pd.read_csv('races.csv', names=['raceId', 'raceYear', 'raceRound', 'raceCircuitId',
#         'raceName', 'raceDate', 'raceTime', 'raceUrl'],header=0)
races = pd.read_csv('races.csv', names=['raceId', 'raceYear', 'raceRound', 'raceCircuitId',
         'raceName', 'raceDate', 'raceTime', 'raceUrl','N1','N2','N3','N4','N5','N6','N7','N8','N9','N10'],header=0)
races=races[['raceId', 'raceYear', 'raceRound', 'raceCircuitId',
         'raceName', 'raceDate', 'raceTime', 'raceUrl']]
pit_stops = pd.read_csv('pit_stops.csv')
qualifying = pd.read_csv('qualifying.csv')
constructor_results = pd.read_csv('constructor_results.csv')
constructor_standings = pd.read_csv('constructor_standings.csv')
results = pd.read_csv('results.csv')
driver_standings = pd.read_csv('driver_standings.csv')
#lap_times = pd.read_csv('lap_times.csv')
sprint_results= pd.read_csv('sprint_results.csv', names=['resultId', 'raceId', 'driverId', 'constructorId',
        'number', 'sr_grid','position', 'positionText', 'sr_positionOrder', 'sr_points', 'sr_laps', 'sr_time',
       'milliseconds', 'fastestLap', 'fastestLapTime', 'statusId'],header=0)
sprint_results=sprint_results[['raceId','driverId','sr_grid','sr_laps','sr_time','sr_points']]
results = results.rename(columns={'rank': 'fastestLapRank'})

####################
##### to create the main dataframe called "df"
####################


#to create a new dataframe "df" merging parts of: results + races + drivers + constructors
df= pd.merge(results, races, on='raceId')
df= pd.merge(df, drivers, on='driverId')
df= pd.merge(df, constructors, on='constructorId')
df= pd.merge(df, sprint_results, on=['raceId','driverId'],how='left')
df['sr_points'] = df['sr_points'].fillna(0)
df['points']=df['points']+df['sr_points']

df = df.drop(['resultId', 'number','position', 'positionText', #'time',
              'raceUrl',
              'driverRef','driverCode','driverUrl',
              'constructorRef','constructorUrl'], axis = 1)

#to get the driver age at the date of the race
df['raceDate']=pd.to_datetime(df['raceDate'])
df['driverDob']=pd.to_datetime(df['driverDob'])
df['driverAge']=((df['raceDate'] - df['driverDob'])/ np.timedelta64(1, 'Y')).round(2)

df['driverName']=df['driverForename']+" "+df['driverSurname']

#to reformat the date
df['raceDate']=df['raceDate'].dt.strftime("%Y-%m-%d")
#df['driverDob']=df['driverDob'].dt.strftime("%Y-%m-%d")

#to reorganize the columns and remove: raceCircuitId & constructorId
df=df[['raceId','raceYear', 'raceRound', 'raceName', 'raceDate', 'raceTime',
       'driverId','driverNumber','driverName', 'driverDob', 'driverNationality', 'driverAge',
       'constructorName', 'constructorNationality',
       'grid', 'positionOrder',
       'points', 'laps', 'time','milliseconds', 'fastestLap', 'fastestLapRank',
       'fastestLapTime', 'fastestLapSpeed', 'statusId',
       'sr_grid','sr_laps','sr_time','sr_points']]

#lastqualiId=qualifying['raceId'][qualifying['raceId']==qualifying['raceId'].max()].iloc[0]
#lastqualyrace=races['raceDate'][races['raceId']==lastqualiId].values[0]
#print(f"Last Qualification: {lastqualyrace}")
#lastrace=df['raceDate'].max()
#print(f"Last Race: {lastrace}")
#df[df['raceDate']==lastrace].sort_values('positionOrder')


###########################
####### For driver Tabs
###########################

df0= df.groupby(['raceYear','driverName','driverNationality','driverDob','driverId','constructorName','constructorNationality'])['points'].sum().reset_index().sort_values(
                                    ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(3)
df0['count'] = df0['points'].ne(df0['raceYear'].shift(1)).cumsum()

#to identify the winning drivers
df0['place']= df0['count']-df0['raceYear'].apply(lambda y:df0[df0["raceYear"]==y].min()["count"])+1
df0=df0.drop(['count'], axis = 1)
df0['raceYear_place']=df0['raceYear'].astype(str)+"_"+df0['place'].astype(str)

mymap={1:'#e10600',2:'#e3a19f',3:'#e3dcdc'}
df0['color']=df0['place'].map(mymap)
df0=df0.sort_values(['raceYear','points'], ascending=[True,False])

####### For Charts Place per Season
#to get the data frame with Driver's place per season
dfp = df.groupby(['raceYear','driverName'])['points'].sum().reset_index().sort_values(
                                    ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(20)
dfp['count'] = dfp['points'].ne(dfp['raceYear'].shift(1)).cumsum()
dfp['place']= dfp['count']-dfp['raceYear'].apply(lambda y:dfp[dfp["raceYear"]==y].min()["count"])+1
dfp8=dfp.drop(['count'], axis = 1)

####### For Chart Constructors per Season
#to create a dataframe with a different random color per driver
dfcd=df.groupby(['driverName'])['points'].sum().reset_index()
dfcd['color']=np.random.uniform(0.8,1,len(dfcd))
dfcd=dfcd[['driverName','color']]

#to get the data frame with Driver's place per season
dfp = df.groupby(['raceYear','driverName','constructorName'])['points'].sum().reset_index().sort_values(
                                    ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(20)
dfp['count'] = dfp['points'].ne(dfp['raceYear'].shift(1)).cumsum()
dfp['place']= dfp['count']-dfp['raceYear'].apply(lambda y:dfp[dfp["raceYear"]==y].min()["count"])+1
dfp10=dfp.drop(['count'], axis = 1)

####### For Chart Youngest Drivers
dfy=df.copy()
dfy['raceDate']=pd.to_datetime(dfy['raceDate'])


###########################
####### For Constructor Tabs
###########################
df0c= df.groupby(['raceYear','constructorName','constructorNationality'])['points'].sum().reset_index().sort_values(
                                    ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(3)
df0c['count'] = df0c['points'].ne(df0c['raceYear'].shift(1)).cumsum()

#to identify the winning drivers
df0c['place']= df0c['count']-df0c['raceYear'].apply(lambda y:df0c[df0c["raceYear"]==y].min()["count"])+1
df0c=df0c.drop(['count'], axis = 1)
df0c['raceYear_place']=df0c['raceYear'].astype(str)+"_"+df0c['place'].astype(str)

mymap={1:'#e10600',2:'#e3a19f',3:'#e3dcdc'}
df0c['color']=df0c['place'].map(mymap)
df0c=df0c.sort_values(['raceYear','points'], ascending=[True,True])

####### For Charts Place per Season
#to get the data frame with Constructor's place per season
dfp = df.groupby(['raceYear','constructorName'])['points'].sum().reset_index().sort_values(
                                    ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(20)
dfp['count'] = dfp['points'].ne(dfp['raceYear'].shift(1)).cumsum()
dfp['place']= dfp['count']-dfp['raceYear'].apply(lambda y:dfp[dfp["raceYear"]==y].min()["count"])+1
dfp9=dfp.drop(['count'], axis = 1)

####### For Chart Drivers per Season
#to create a dataframe with a different random color per constructor
dfcc=df.groupby(['constructorName'])['points'].sum().reset_index()
dfcc['color']=np.random.uniform(0.8,1,len(dfcc))
dfcc=dfcc[['constructorName','color']]

#to get the data frame with Driver's place per season
dfp = df.groupby(['raceYear','driverName','constructorName'])['points'].sum().reset_index().sort_values(
                                    ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(20)
dfp['count'] = dfp['points'].ne(dfp['raceYear'].shift(1)).cumsum()
dfp['place']= dfp['count']-dfp['raceYear'].apply(lambda y:dfp[dfp["raceYear"]==y].min()["count"])+1
dfp11=dfp.drop(['count'], axis = 1)


###########################
####### for 'Formula 1 Dashboard'
###########################

years = [{'label': 'All', 'value': 'All'}]
for year in df['raceYear'].sort_values(ascending=False).unique():
    years.append({'label':str(year),'value':year})
del years[0]

topics = [{'label':'RACES','value':'RACES'}]
topics.append({'label':'DRIVERS','value':'DRIVERS'})
topics.append({'label':'TEAMS','value':'TEAMS'})
topics.append({'label':'FASTEST LAP','value':'FASTEST LAP'})


def create_table(iD):

    return dash_table.DataTable(id=iD,
                                 style_cell={'textAlign': 'left','border': 'none', 'color': '#808080'},
                                 style_header={
                                            'backgroundColor': 'white',
                                            'fontWeight': 'bold',
                                            'font-size': '16px',
                                        },
                                 style_data_conditional=[
                                        {
                                            'if': {'row_index': 'even'},
                                            'backgroundColor': '#f4f4f4',
                                        }]
                                    )

def cumtimepits(df, driver, stop):
    time = df['TIME'][(df['STOPS']<=stop)&(df['DRIVER']==driver)].sum()
    return time

def startingtime(q1,q2,q3):
    if q3 != "\\N":   time = q3
    elif q2 != "\\N": time = q2
    elif q1 != "\\N": time = q1
    else:             time = "\\N"
    return time

###########################
####### For driver Tabs
###########################
def dfdfp8(circuit):
    dfp=df[df['raceName']==circuit].copy()
    dfp = dfp.groupby(['raceYear','driverName'])['points'].sum().reset_index().sort_values(
                                    ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(20)
    dfp['count'] = dfp['points'].ne(dfp['raceYear'].shift(1)).cumsum()
    dfp['place']= dfp['count']-dfp['raceYear'].apply(lambda y:dfp[dfp["raceYear"]==y].min()["count"])+1
    dfp8=dfp.drop(['count'], axis = 1)
    return dfp8


def dfdf0(circuit):
    df0=df[df['raceName']==circuit].copy()
    df0= df0.groupby(['raceYear','driverName','driverNationality','driverDob',
                      'driverId','constructorName','constructorNationality'])['points'].sum().reset_index().sort_values(
                                    ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(3)
    df0['count'] = df0['points'].ne(df0['raceYear'].shift(1)).cumsum()

    #to identify the winning drivers
    df0['place']= df0['count']-df0['raceYear'].apply(lambda y:df0[df0["raceYear"]==y].min()["count"])+1
    df0=df0.drop(['count'], axis = 1)
    df0['raceYear_place']=df0['raceYear'].astype(str)+"_"+df0['place'].astype(str)

    mymap={1:'#e10600',2:'#e3a19f',3:'#e3dcdc'}
    df0['color']=df0['place'].map(mymap)
    df0=df0.sort_values(['raceYear','points'], ascending=[True,True])
    return df0

###########################
####### For Constructor Tabs
###########################
def dfdfp9(circuit):
    dfp=df[df['raceName']==circuit].copy()
    dfp = dfp.groupby(['raceYear','constructorName'])['points'].sum().reset_index().sort_values(
                                    ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(20)
    dfp['count'] = dfp['points'].ne(dfp['raceYear'].shift(1)).cumsum()
    dfp['place']= dfp['count']-dfp['raceYear'].apply(lambda y:dfp[dfp["raceYear"]==y].min()["count"])+1
    dfp9=dfp.drop(['count'], axis = 1)
    return dfp9

def dfdf0c (circuit):
    df0c=df[df['raceName']==circuit].copy()
    df0c= df0c.groupby(['raceYear','constructorName','constructorNationality'])['points'].sum().reset_index().sort_values(
                                        ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(3)
    df0c['count'] = df0c['points'].ne(df0c['raceYear'].shift(1)).cumsum()

    #to identify the winning drivers
    df0c['place']= df0c['count']-df0c['raceYear'].apply(lambda y:df0c[df0c["raceYear"]==y].min()["count"])+1
    df0c=df0c.drop(['count'], axis = 1)
    df0c['raceYear_place']=df0c['raceYear'].astype(str)+"_"+df0c['place'].astype(str)

    mymap={1:'#e10600',2:'#e3a19f',3:'#e3dcdc'}
    df0c['color']=df0c['place'].map(mymap)
    df0c=df0c.sort_values(['raceYear','points'], ascending=[True,True])
    return df0c

tickfont=12
barsColor = "#f55b68"
barsColor = '#385d7f'
barsColor = '#e10600'
style_dropdown= {'font-size': '14px', 'color':'#808080','font-family':"system-ui",}

rectangle = html.Div([
        html.Div([
                html.P(
                    "This Dashboard was made purely in Python using the Dash library from Plotly & with tons of love ♡",
                    style={'fontSize': 14},
                    className="row",
                )
            ],className="legend",)
    ],style={'width':'100%','display':'inline-block'})


app.layout = html.Div([
    html.Div([
        #html.Div([html.Img(src=app.get_asset_url("f1_logo.jpg"),className='logo')],
        #          style= {'width': '8%', 'display': 'inline-block'}),
        html.Div([html.H3("Miguel's Formula 1 Dashboard",className='dashboard-name')],
                 style= {'width': '100%', 'display': 'inline-block'}),
    ],className='dashboard-name'),
    rectangle,
    html.Br([],style= {'color': '#ffffff'}),
    html.Div([
    html.Div(id="mainTabsDiv",
            children=[
                    dcc.Tabs(id="mainTabs",
                        value = "Formula 1 Dashboard",
                        children=[
                        dcc.Tab(label='Driver Results', value='Driver Results',className='main-tab',selected_className='main-tab--selected'),
                        dcc.Tab(label='Constructor Results', value='Constructor Results',className='main-tab',selected_className='main-tab--selected'),
                        #dcc.Tab(label='Circuit Results', value='Circuit Results',className='main-tab',selected_className='main-tab--selected'),
                        dcc.Tab(label='Results per Nationality', value='Nationality Results',className='main-tab',selected_className='main-tab--selected'),
                        dcc.Tab(label='Formula 1 Dashboard', value='Formula 1 Dashboard',className='main-tab',selected_className='main-tab--selected'),
                    ])
            ]
    ),
    html.Br([]),
    html.Div([
                dcc.Tabs(id="secondaryTabs",vertical=True, className='custom-tabs')
            ],style= {'width': '18%', 'display': 'inline-block', 'vertical-align': 'top'}),
    html.Div([
        html.Div(id='filters', children=[

            #####filters_podiums
            html.Div(id="filters_podiums", children=[
                html.Div([
                    html.H5('Observations:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '60%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.RadioItems(
                            id='RadioItems',
                            options=[
                                {'label': '10', 'value': 10},
                                {'label': '20', 'value': 20},
                                {'label': '30', 'value': 30},
                            ],
                            value=10,
                            labelStyle = dict(display='block', color='#808080'),
                            style= {'display': 'inline-block'}
                        ),
                    ],style= {'width': '40%', 'display': 'inline-block',}),###################
                ],style= {'width': '17%', 'display': 'inline-block'}),

                html.Div([
                    html.H5('Select places:',
                          style= {'color':'#808080','font-weight':"bold",'width': '60%', 'display': 'inline-block'}),
                    dcc.Checklist(
                        id='Checklist',
                        options=[
                            {'label': '1st', 'value': '1'},
                            {'label': '2nd', 'value': '2'},
                            {'label': '3rd', 'value': '3'},
                        ],
                        value=['1','2','3'],
                        labelStyle = dict(display='block', color='#808080'),
                        style= {'width': '40%', 'display': 'inline-block'}
                    ),
                ],style= {'width': '17%', 'display': 'inline-block'}),

                html.Div(id="filters_nationality", children=[
                    html.H5('Select Nationality:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '40%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='Dropdown_Nationalities',
                            value='All',
                            style= style_dropdown)
                    ],style= {'width': '55%', 'display': 'inline-block',}),###################
                ],style= {'width': '30%', 'display': 'inline-block'}),
            ],style= {'width': '100%', 'display': 'inline-block'}),

            ######filters_placePerSeasonDrivers
            html.Div(id='filters_placePerSeasonDrivers', children=[
                html.Div([
                    html.H5('Select a Driver:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '33%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='DropdownDriver1',
                            value='Lewis Hamilton',
                            style= style_dropdown)
                    ],style= {'width': '60%', 'display': 'inline-block',}),###################
                ],style= {'width': '32%', 'display': 'inline-block'}),
                html.Div([
                    html.H5('Select a Driver:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '33%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='DropdownDriver2',
                            value='Sergio Pérez',
                            style= style_dropdown)
                    ],style= {'width': '60%', 'display': 'inline-block',}),###################
                ],style= {'width': '32%', 'display': 'inline-block'}),
            ],style= {'display': 'None'}),

            #####filters_placePerSeasonConstructors
            html.Div(id='filters_placePerSeasonConstructors', children=[
                html.Div([
                    html.H5('Select a Constructor:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '33%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='DropdownConstructor1',
                            value='Mercedes',
                            style= style_dropdown)
                    ],style= {'width': '60%', 'display': 'inline-block',}),###################
                ],style= {'width': '50%', 'display': 'inline-block'}),
                html.Div([
                    html.H5('Select a Constructor:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '33%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='DropdownConstructor2',
                            value='Red Bull',
                            style= style_dropdown)
                    ],style= {'width': '60%', 'display': 'inline-block',}),###################
                ],style= {'width': '50%', 'display': 'inline-block'}),
            ],style= {'display': 'None'}),

            #####filters_constructorsPerSeason
            html.Div(id='filters_constructorsPerSeason', children=[
                html.Div([
                    html.H5('Select a Driver:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '33%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='DropdownDriverCPS',
                            value='Sergio Pérez',
                            style= style_dropdown)
                    ],style= {'width': '60%', 'display': 'inline-block',}),###################
                ],style= {'width': '40%', 'display': 'inline-block'}),
                html.Div([
                    html.H5('Years to consider:',
                              style= {'color':'#808080','font-weight':"bold", 'width': '15%', 'display': 'inline-block'}),
                    html.Div(dcc.RangeSlider(
                        id='RangeSliderCPS',
                        min=df['raceYear'].min(),
                        max=df['raceYear'].max(),
                        value=[df['raceYear'].min(),df['raceYear'].max()],
                        tooltip={"placement": "top", "always_visible": True},
                        marks={
                            1950: '1950',
                            1960: '1960',
                            1970: '1970',
                            1980: '1980',
                            1990: '1990',
                            2000: '2000',
                            2010: '2010',
                            2020: '2020',
                        },
                        step=1,
                    ), style={'width': '85%','display': 'inline-block'}),
                ],style= {'width': '60%', 'display': 'inline-block'})
            ],style= {'width': '100%','display': 'None'}),

            #####filters_driversPerSeason
            html.Div(id='filters_driversPerSeason', children=[
                html.Div([
                    html.H5('Select a Constructor:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '33%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='DropdownConstructorDPS',
                            value='Mercedes',
                            style= style_dropdown)
                    ],style= {'width': '60%', 'display': 'inline-block',}),###################
                ],style= {'width': '40%', 'display': 'inline-block'}),
                html.Div([
                    html.H5('Years to consider:',
                              style= {'color':'#808080','font-weight':"bold", 'width': '15%', 'display': 'inline-block'}),
                    html.Div(dcc.RangeSlider(
                        id='RangeSliderDPS',
                        min=df['raceYear'].min(),
                        max=df['raceYear'].max(),
                        value=[df['raceYear'].min(),df['raceYear'].max()],
                        tooltip={"placement": "top", "always_visible": True},
                        marks={
                            1950: '1950',
                            1960: '1960',
                            1970: '1970',
                            1980: '1980',
                            1990: '1990',
                            2000: '2000',
                            2010: '2010',
                            2020: '2020',
                        },
                        step=1,
                    ), style={'width': '85%','display': 'inline-block'}),
                ],style= {'width': '60%', 'display': 'inline-block'})
            ],style= {'width': '100%','display': 'None'}),


            #####RangeSliderYears
            html.Div(id="RangeSliderDiv", children=[
                html.H5('Years to consider:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '15%', 'display': 'inline-block'}),
                html.Div(dcc.RangeSlider(
                    id='RangeSlider',
                    min=df['raceYear'].min(),
                    max=df['raceYear'].max(),
                    value=[df['raceYear'].min(),df['raceYear'].max()],
                    tooltip={"placement": "top", "always_visible": True},
                    marks={
                        1950: '1950',
                        1960: '1960',
                        1970: '1970',
                        1980: '1980',
                        1990: '1990',
                        2000: '2000',
                        2010: '2010',
                        2020: '2020',
                    },
                    step=1,
                ), style={'width': '49%','display': 'inline-block'}),
                html.Div(id="filters_circuit", children=[
                    html.H5('Select Circuit:',
                          style= {'color':'#808080','font-weight':"bold", 'width': '25%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='Dropdown_Circuits',
                            value='All',
                            style= style_dropdown)
                    ],style= {'width': '75%', 'display': 'inline-block',}),###################
                ],style= {'width': '36%', 'display': 'inline-block'}),
            ],style= {'width': '100%', 'display': 'inline-block'}),

        ], style={
            'width': '100%', 'display': 'inline-block',
            #'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '0px 5px',
        }), # End of id='filters'
        html.Div([
            dcc.Graph(id='Chart'),
            dcc.Graph(id='Chart2'),
            dcc.Markdown(id='nodata', style  = {'color':'#808080','font-weight':"bold"})
        ])
    ],style= {'width': '82%', 'display': 'inline-block'}),

    html.Div(id='tables', children=[
                html.Div([
                    html.Div([
                        html.H4('Select a year:',
                              style= {'color':'#ffffff','width': '33%', 'display': 'inline-block'}),
                        html.Div([
                            dcc.Dropdown(
                                id='Dropdown1',
                                options=years,
                                value=2022,
                                style= style_dropdown)
                        ],style= {'width': '60%', 'display': 'inline-block',}),###################
                    ],style= {'width': '33%', 'display': 'inline-block'}),
                    html.Div([
                        html.H4('Select Topic:',
                              style= {'color':'#ffffff', 'width': '33%', 'display': 'inline-block'}),
                        html.Div([
                            dcc.Dropdown(
                                id='Dropdown2',
                                options=topics,
                                value='RACES',
                                style= style_dropdown)
                        ],style= {'width': '60%', 'display': 'inline-block',}),###################
                    ],style= {'width': '33%', 'display': 'inline-block'}),
                    html.Div([
                        html.H4('Select:',
                              style= {'color':'#ffffff', 'width': '33%', 'display': 'inline-block'}),
                        html.Div([
                            dcc.Dropdown(
                                id='Dropdown3',
                                value='All',
                                style= style_dropdown)
                        ],style= {'width': '60%', 'display': 'inline-block',}),###################
                    ],style= {'width': '33%', 'display': 'inline-block'}),
                ], style={
                    #'borderBottom': 'thin lightgrey solid',
                    'padding-top': 25,
                    'padding-left': 25,
                    'backgroundColor': '#fa6b6b',

                }),


                html.Br([]),
                html.H2(id="headtext",style= {'color':'#808080','font-weight':"bold"}),
                html.Br([]),

                html.Div(id="maintable", children=[create_table("dashtable")]),
                html.Div([
                    html.Div(id="raceTabsDiv",
                            children=[
                                    dcc.Tabs(id="raceTabs",
                                        value = "RACE RESULT",
                                        children=[
                                        dcc.Tab(label='RACE RESULT', value='RACE RESULT',className='custom-tab',selected_className='custom-tab--selected'),
                                        dcc.Tab(label='FASTEST LAPS', value='FASTEST LAPS',className='custom-tab',selected_className='custom-tab--selected'),
                                        dcc.Tab(label='PIT STOP SUMMARY', value='PIT STOP SUMMARY',className='custom-tab',selected_className='custom-tab--selected'),
                                        dcc.Tab(label='STARTING GRID', value='STARTING GRID',className='custom-tab',selected_className='custom-tab--selected'),
                                        dcc.Tab(label='QUALIFYING', value='QUALIFYING',className='custom-tab',selected_className='custom-tab--selected'),
                                        #dcc.Tab(label='PRACTICE 3', value='PRACTICE 3',className='custom-tab'),
                                        #dcc.Tab(label='PRACTICE 2', value='PRACTICE 2',className='custom-tab'),
                                        #dcc.Tab(label='PRACTICE 1', value='PRACTICE 1',className='custom-tab')
                                    ],vertical=True)
                            ],style= {'display': 'none'}
                    )],style= {'width': '12%', 'display': 'inline-block'}),
                html.Div([],style= {'width': '5%', 'display': 'inline-block'}),
                html.Div([
                    html.Div(id="maintable2", children=[create_table("dashtable2")],style= {'display': 'none'}),
                    html.Div(id="Chart3Div", children=[dcc.Graph(id='Chart3'),],style= {'display': 'none'}),
                ],style= {'width': '83%', 'display': 'inline-block'}),
            ], style= {'width': '100%','display': 'None'}),

    ],className="cuerpo"),
    html.Br([]),
    html.Br([]),
    html.Div([
        html.Div([
            html.P("Data source: http://ergast.com/downloads",
                         style={'fontSize': 12},
                         className="row"),
            html.P("Code Github: https://github.com/MiguelG26/Public_Projects/tree/master/db-Formula1%20app",
                         style={'fontSize': 12},
                         className="row")
        ],className='legend2'),
    ],style={'width':'100%','display':'inline-block'}),
])


@app.callback(
     [Output('secondaryTabs', 'children'),
      Output('secondaryTabs', 'value')],
     Input('mainTabs', 'value'))
def funtion(tab):
    if tab == 'Driver Results':
        children=[
            dcc.Tab(label='Championship Podiums', value='Championship Podiums',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Race Podiums', value='Race Podiums',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Place per Season', value='Place per Season',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Constructors per Season', value='Constructors per Season',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Winners per Season', value='Winners per Season',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Youngest Drivers', value='Youngest Drivers',className='custom-tab',selected_className='custom-tab--selected'),
        ]
        value='Championship Podiums'

    elif tab == 'Constructor Results':
        children=[
            dcc.Tab(label='Championship Podiums', value='Championship Podiums',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Race Podiums', value='Race Podiums',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Place per Season', value='Place per Season',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Drivers per Season', value='Drivers per Season',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Winners per Season', value='Winners per Season',className='custom-tab',selected_className='custom-tab--selected'),
        ]
        value='Championship Podiums'

   # elif tab == 'Circuit Results':
   #     children=[
   #         dcc.Tab(label='Race Podiums', value='Race Podiums',className='custom-tab',selected_className='custom-tab--selected'),
   #         dcc.Tab(label='Place per Season - Driver', value='Place per Season Driver',className='custom-tab',selected_className='custom-tab--selected'),
   #         dcc.Tab(label='Place per Season - Team', value='Place per Season Team',className='custom-tab',selected_className='custom-tab--selected'),
   #         dcc.Tab(label='Winners per Season - Driver', value='Winners per Season Driver',className='custom-tab',selected_className='custom-tab--selected'),
   #         dcc.Tab(label='Winners per Season - Team', value='Winners per Season Team',className='custom-tab',selected_className='custom-tab--selected'),
   #     ]
   #     value='Race Podiums'

    elif tab == 'Nationality Results':
        children=[
            dcc.Tab(label='Championship Podiums', value='Championship Podiums',className='custom-tab',selected_className='custom-tab--selected'),
            dcc.Tab(label='Race Podiums', value='Race Podiums',className='custom-tab',selected_className='custom-tab--selected'),
        ]
        value='Championship Podiums'

    elif tab == 'Formula 1 Dashboard':
        children=[]
        value=''

    return children, value

@app.callback(
    [Output('DropdownDriver1', 'options'),
    Output('DropdownDriver2', 'options')],
    [Input('RangeSlider', 'value')])
def Dropdown1(years):
    df1=dfp8[(dfp8['raceYear']>=years[0])&(dfp8['raceYear']<=years[1])].copy()
    driverNames = [{'label': 'All', 'value': 'All'}]
    for driver in df1['driverName'].sort_values().unique():
        driverNames.append({'label':str(driver),'value':driver})
    del driverNames[0]

    return driverNames, driverNames

@app.callback(
    [Output('DropdownConstructor1', 'options'),
    Output('DropdownConstructor2', 'options')],
    [Input('RangeSlider', 'value')])
def Dropdown1(years):
    df1=dfp9[(dfp9['raceYear']>=years[0])&(dfp9['raceYear']<=years[1])].copy()
    constructorNames = [{'label': 'All', 'value': 'All'}]
    for constructor in df1['constructorName'].sort_values().unique():
        constructorNames.append({'label':str(constructor),'value':constructor})
    del constructorNames[0]

    return constructorNames, constructorNames

@app.callback(
    Output('DropdownDriverCPS', 'options'),
    [Input('RangeSliderCPS', 'value')])
def Dropdown1(years):
    df1=dfp10[(dfp10['raceYear']>=years[0])&(dfp10['raceYear']<=years[1])].copy()
    driverNames = [{'label': 'All', 'value': 'All'}]
    for driver in df1['driverName'].sort_values().unique():
        driverNames.append({'label':str(driver),'value':driver})

    return driverNames

@app.callback(
    Output('DropdownConstructorDPS', 'options'),
    [Input('RangeSlider', 'value')])
def Dropdown1(years):
    df1=dfp11[(dfp11['raceYear']>=years[0])&(dfp11['raceYear']<=years[1])].copy()
    constructorNames = [{'label': 'All', 'value': 'All'}]
    for constructor in df1['constructorName'].sort_values().unique():
        constructorNames.append({'label':str(constructor),'value':constructor})

    return constructorNames

@app.callback(
    Output('Dropdown_Nationalities', 'options'),
    [Input('Checklist', 'value'),
     Input('RangeSlider', 'value'),
     Input('mainTabs', 'value'),
     Input('secondaryTabs', 'value')])
def Dropdown_Nationalities(Checklist_options, years, tab, tab2):
    nationalities = [{'label': 'All', 'value': 'All'}]
    if tab=="Driver Results":
        if tab2=="Championship Podiums":
            df1=df0[df0['place'].isin(Checklist_options)].copy()
            df1=df1[(df1['raceYear']>=years[0])&(df1['raceYear']<=years[1])]
            nationalities = [{'label': 'All', 'value': 'All'}]
            for nationality in df1['driverNationality'].sort_values().unique():
                nationalities.append({'label':str(nationality),'value':nationality})

        if tab2=="Race Podiums":
            df1=df[(df['raceYear']>=years[0])&(df['raceYear']<=years[1])].copy()
            df1= df1[df1['positionOrder'].isin(Checklist_options)].groupby(['driverName','driverNationality','driverDob'
                                           ])['positionOrder'].count().reset_index().sort_values(
                                             by = 'positionOrder', ascending=False).rename(
                                             columns={'positionOrder': 'wins'})
            df1=df1[['driverName','driverNationality', 'driverDob','wins']]
            nationalities = [{'label': 'All', 'value': 'All'}]
            for nationality in df1['driverNationality'].sort_values().unique():
                nationalities.append({'label':str(nationality),'value':nationality})

    if tab=="Constructor Results":
        if tab2=="Championship Podiums":
            df1=df0[df0['place'].isin(Checklist_options)].copy()
            df1=df1[(df1['raceYear']>=years[0])&(df1['raceYear']<=years[1])]
            nationalities = [{'label': 'All', 'value': 'All'}]
            for nationality in df1['constructorNationality'].sort_values().unique():
                nationalities.append({'label':str(nationality),'value':nationality})

        if tab2=="Race Podiums":
            df1=df[(df['raceYear']>=years[0])&(df['raceYear']<=years[1])].copy()
            df1= df1[df1['positionOrder'].isin(Checklist_options)].groupby(['constructorName','constructorNationality'
                                           ])['positionOrder'].count().reset_index().sort_values(
                                             by = 'positionOrder', ascending=False).rename(
                                             columns={'positionOrder': 'wins'})
            df1=df1[['constructorName','constructorNationality', 'wins']]
            nationalities = [{'label': 'All', 'value': 'All'}]
            for nationality in df1['constructorNationality'].sort_values().unique():
                nationalities.append({'label':str(nationality),'value':nationality})

    return nationalities

@app.callback(
    Output('Dropdown_Circuits', 'options'),
    [Input('Checklist', 'value'),
     Input('RangeSlider', 'value'),
     Input('mainTabs', 'value'),
     Input('secondaryTabs', 'value')])
def Dropdown_Circuits(Checklist_options, years, tab, tab2):
    circuits = [{'label': 'All', 'value': 'All'}]
    df1=df[(df['raceYear']>=years[0])&(df['raceYear']<=years[1])].copy()
    circuits = [{'label': 'All', 'value': 'All'}]
    for circuit in df1['raceName'].sort_values().unique():
        circuits.append({'label':str(circuit),'value':circuit})
    return circuits

@app.callback(
     [Output('filters_podiums', 'style'),
      Output('filters_placePerSeasonDrivers', 'style'),
      Output('filters_placePerSeasonConstructors', 'style'),
      Output('filters_constructorsPerSeason', 'style'),
      Output('filters_driversPerSeason', 'style'),
      Output("filters_nationality", 'style'),
      Output("filters_circuit", 'style'),
      Output("tables", 'style'),
      Output('RangeSliderDiv', 'style'),
     ],
     [Input('mainTabs', 'value'),
      Input('secondaryTabs', 'value')])
def funtion(tab, tab2):
    stylePodiums= stylePPSD= stylePPSC=styleCPS=styleDPS =styleTables = {'width': '99%', 'display': 'none'}
    styleRangeSliderDiv={'width': '99%', 'display': 'inline-block'}
    styleNat={'width': '30%', 'display': 'inline-block'}
    styleCir={'width': '36%', 'display': 'inline-block'}

    if tab == 'Driver Results':
        if tab2 == 'Championship Podiums':
            stylePodiums= {'width': '99%', 'display': 'inline-block'}
            styleCir={'width': '36%', 'display': 'None'}
        elif tab2 == 'Race Podiums':
            stylePodiums= {'width': '99%', 'display': 'inline-block'}
        elif tab2 == 'Place per Season':
            stylePPSD= {'width': '99%', 'display': 'inline-block'}
            styleCir={'width': '36%', 'display': 'inline-block'}
        elif tab2 == 'Constructors per Season':
            styleCPS= {'width': '99%', 'display': 'inline-block'}
            styleRangeSliderDiv={'width': '99%', 'display': 'None'}
    elif tab == 'Constructor Results':
        if tab2 == 'Championship Podiums':
            stylePodiums= {'width': '99%', 'display': 'inline-block'}
            styleCir={'width': '36%', 'display': 'None'}
        elif tab2 == 'Race Podiums':
            stylePodiums= {'width': '99%', 'display': 'inline-block'}
        elif tab2 == 'Place per Season':
            stylePPSC= {'width': '99%', 'display': 'inline-block'}
        elif tab2 == 'Drivers per Season':
            styleDPS= {'width': '99%', 'display': 'inline-block'}
            styleRangeSliderDiv={'width': '99%', 'display': 'None'}
    elif tab == 'Nationality Results':
        styleNat={'width': '33%', 'display': 'None'}
        stylePodiums= {'width': '99%', 'display': 'inline-block'}
        if tab2 == 'Championship Podiums':
            styleCir={'width': '36%', 'display': 'None'}


    elif tab == 'Formula 1 Dashboard':
        stylePodiums= {'width': '99%', 'display': 'none'}
        styleRangeSliderDiv={'width': '99%', 'display': 'None'}
        styleTables = {'width': '100%','display': 'inline-block'}

    return stylePodiums, stylePPSD, stylePPSC, styleCPS, styleDPS, styleNat, styleCir, styleTables, styleRangeSliderDiv


@app.callback(
    [Output('Dropdown3', 'options'),
     Output('Dropdown3', 'value'),
     Output('Dropdown3', 'style')],
    [Input('Dropdown1', 'value'),
     Input('Dropdown2', 'value'),
     Input('Dropdown3', 'value')])
def funtion(year, topic, subtopic):
    value="All"
    style={'font-size': '14px', 'color':'#808080','font-family':"system-ui",'display': 'block'}
    df1=df.copy()
    df1=df1[df1['raceYear']==year]
    if topic == "RACES":
        if len(df1[df1["raceName"]==subtopic])>0:
            value = subtopic
        options=np.array(df1.groupby(['raceRound','raceName'])['points'].sum().reset_index()['raceName'])
        dictionary = [{'label': 'All', 'value': 'All'}]
        for item in options:
            dictionary.append({'label':str(item),'value':item})
        return dictionary, value, style

    if topic == "DRIVERS":
        if len(df1[df1["driverName"]==subtopic])>0:
            value = subtopic
        options=df1['driverName'].sort_values().unique()
        dictionary = [{'label': 'All', 'value': 'All'}]
        for item in options:
            dictionary.append({'label':str(item),'value':item})
        return dictionary, value, style

    if topic == "TEAMS":
        if len(df1[df1["constructorName"]==subtopic])>0:
            value = subtopic
        options=df1['constructorName'].sort_values().unique()
        dictionary = [{'label': 'All', 'value': 'All'}]
        for item in options:
            dictionary.append({'label':str(item),'value':item})
        return dictionary, value, style

    if topic == "FASTEST LAP":
        style={'display': 'none'}
        return years, value, style
@app.callback(
    [Output('Chart', 'style'),
     Output('nodata', 'children'),
     Output('Chart', 'figure'),
     Output('Chart2', 'style'),
     Output('Chart2', 'figure')],
    [Input('Checklist', 'value'),
     Input('Dropdown_Nationalities', 'value'),
     Input('Dropdown_Circuits', 'value'),
     Input('RadioItems', 'value'),
     Input('RangeSlider', 'value'),
     Input('mainTabs', 'value'),
     Input('secondaryTabs', 'value'),
     Input('DropdownDriver1', 'value'),
     Input('DropdownDriver2', 'value'),
     Input('DropdownConstructor1', 'value'),
     Input('DropdownConstructor2', 'value'),
     Input('DropdownDriverCPS', 'value'),
     Input('RangeSliderCPS', 'value'),
     Input('DropdownConstructorDPS', 'value'),
     Input('RangeSliderDPS', 'value'),
    ])
def Chart1(Checklist_options, nationality,circuit,observations, years, tab,
           tab2,drivername1, drivername2, constructorName1, constructorName2,
           driverNameCPS, yearsCPS, constructorNameDPS, yearsDPS):

    style  = {'display': 'none'}
    children = ""
    figure = {}
    style2  = {'display': 'none'}
    figure2 = {}
    if tab == 'Driver Results':
        if tab2 == 'Championship Podiums':
            df1=df0[df0['place'].isin(Checklist_options)].copy()
            df1=df1[(df1['raceYear']>=years[0])&(df1['raceYear']<=years[1])]
            if nationality != "All":
                df1=df1[df1['driverNationality']==nationality]
            df1=df1.groupby(['driverName','driverNationality','driverDob'])['points'].count().reset_index().sort_values(
                                            ['points'], ascending=[False]).rename(
                                             columns={'points': 'ChampionshipPodiums'}).reset_index(drop=True)

            df1=df1.head(observations).copy().sort_values('ChampionshipPodiums', ascending=[True])

            if len(df1)> 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"
            figure = {
                'data':[
                    go.Bar(y=df1['driverName']+ " | " + df1['driverNationality']+"  ",
                           x=df1['ChampionshipPodiums'],
                           text="Podiums: " + df1['ChampionshipPodiums'].astype(str),orientation="h",
                           textposition='auto',marker_color=barsColor),
                ],
                'layout':go.Layout(height=600+observations*20-200,
                          template="simple_white", showlegend=False,
                          xaxis =dict(visible=False),
                          yaxis =dict(showline=False,ticks='',color='#808080'),
                          font_family="system-ui"
                            )
                    }
        if tab2 == 'Race Podiums':
            df1=df[(df['raceYear']>=years[0])&(df['raceYear']<=years[1])].copy()
            if circuit != "All":
                df1=df1[df1['raceName']==circuit]

            df1= df1[df1['positionOrder'].isin(Checklist_options)].groupby(['driverName','driverNationality','driverDob'
                                           ])['positionOrder'].count().reset_index().sort_values(
                                             by = 'positionOrder', ascending=False).rename(
                                             columns={'positionOrder': 'wins'})
            df1=df1[['driverName','driverNationality', 'driverDob','wins']]
            if nationality != "All":
                df1=df1[df1['driverNationality']==nationality]
            df1=df1.head(observations).sort_values(by='wins',ascending=True)

            if len(df1)> 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"
            figure = {
                'data':[
                    go.Bar(y=df1['driverName']+ " | " + df1['driverNationality']+"  ",
                           x=df1['wins'],
                           text="Podiums: " + df1['wins'].astype(str),orientation="h",
                           textposition='auto',marker_color=barsColor),
                ],
                'layout':go.Layout(height=600+observations*20-200,
                          template="simple_white", showlegend=False,
                          xaxis =dict(visible=False),
                          yaxis =dict(showline=False,ticks='',color='#808080'),
                          font_family="system-ui"
                            )
                    }
        if tab2 == 'Place per Season':
            if circuit != "All":
                dfx=dfdfp8(circuit)
                dfx=dfx[(dfx['raceYear']>=years[0])&(dfx['raceYear']<=years[1])]
            else:
                dfx=dfp8[(dfp8['raceYear']>=years[0])&(dfp8['raceYear']<=years[1])]

            df1=dfx[dfx['driverName']==drivername1]
            df2=dfx[dfx['driverName']==drivername2]

            if len(df1) + len(df2) > 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"

            if len(df1['raceYear'].unique()) <7 & len(df2['raceYear'].unique()) <7:
                xaxisDict = dict(showline=False, ticks='', dtick=1,color='#808080')
            else:
                xaxisDict = dict(showline=False, ticks='',color='#808080')

            figure={
                'data':[
                    go.Scatter(y=df1['place'], x=df1['raceYear'],name=drivername1,
                               text=df1['place'].astype(str), marker_color='#808080'),
                    go.Scatter(y=df2['place'], x=df2['raceYear'],name=drivername2,
                               text=df2['place'].astype(str), marker_color='#f55b68'),
                ],
                'layout':go.Layout(height=600,template="simple_white",
                          legend=dict(orientation="h", yanchor="bottom",y=1.02),
                          xaxis =xaxisDict,
                          yaxis =dict(showline=False,ticks='',range=[20.1, 0], color='#808080',
                                      zeroline=True, zerolinecolor='#ededed',zerolinewidth=0.5),
                          font_family="system-ui"
                          )
                    }
        if tab2 == 'Constructors per Season':
            #to create the dataframe for the chart
            dfx=dfp10[(dfp10['raceYear']>=yearsCPS[0])&(dfp10['raceYear']<=yearsCPS[1])]
            if driverNameCPS !="All":
                dfx=dfx[dfx['driverName']==driverNameCPS]
            df1=pd.merge(dfx,dfcd, on='driverName')
            df1=df1.sort_values(['driverName','raceYear'], ascending=[False, True])

            figHeight=len(df1)*7
            tickFont = 7
            if figHeight <400:
                figHeight=500
                tickFont = 10

            if len(df1) > 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"

            if len(df1['raceYear'].unique()) <6:
                xaxisDict = dict(showline=False, ticks='',color='#808080',side='top', dtick=1)
            else:
                xaxisDict = dict(showline=False, ticks='',color='#808080',side='top')

            figure= {
                'data':[
                    go.Scatter(y=[df1['driverName'],df1['constructorName']], x=df1['raceYear'],
                             text="Constructor: " + df1['constructorName'] + "| Place: " + df1['place'].astype(str),
                             mode='markers',
                             marker_color=df1['color'],
                             ),
                ],
                'layout':go.Layout(
                          height=figHeight+200, template="simple_white", showlegend=False,
                          xaxis =xaxisDict,
                          yaxis =dict(showline=False,ticks='',color='#808080',tickfont=dict(size=tickFont)),
                          font_family="system-ui"
                          )
                    }
        if tab2 == 'Winners per Season':
            if circuit != "All":
                df1=dfdf0(circuit)
                df1=df1[(df1['raceYear']>=years[0])&(df1['raceYear']<=years[1])]
            else:
                df1=df0[(df0['raceYear']>=years[0])&(df0['raceYear']<=years[1])]

            if len(df1)> 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"

            tickFont = 12
            figHeight=400+len(df1)*25

            figure={
                'data':[
                    go.Bar(y=[df1['raceYear'], df1['place']],
                           x=df1['points'],
                             text=df1['driverName']+ " | " + df1['driverNationality'] + " | " + df1['constructorName']
                                   +" | "+"Points: "+df1['points'].astype(str),
                             marker_color=df1['color'],orientation="h",textposition='auto', hoverinfo = 'text')
                ],
                'layout':go.Layout(height=figHeight, template="simple_white", showlegend=False,
                          xaxis =dict(showline=False, ticks='',color='#808080',title="Points"),
                          yaxis =dict(showline=False,ticks='',color='#808080',title="Season_Place",tickfont=dict(size=tickFont)),
                          title=dict(text='<b>Drivers in first 3 places per season</b>',font_color='#808080'),
                          font_family="system-ui")
                    }
        if tab2 == 'Youngest Drivers':
            style  = {'display': 'block'}
            if circuit != "All":
                dfz=dfy[(dfy['raceYear']>=years[0])&(dfy['raceYear']<=years[1])]
                dfz=dfz[dfz['raceName']==circuit].copy()
            else:
                dfz=dfy[(dfy['raceYear']>=years[0])&(dfy['raceYear']<=years[1])]

            df1=dfz[dfz['positionOrder']==1].groupby(['driverAge','driverName','driverNationality','constructorName','raceDate', 'raceName'
                                           ])['positionOrder'].sum().reset_index().sort_values(
                                            by = 'driverAge').head(40).drop(['positionOrder'], axis = 1)
            df2=df1.groupby(['driverName'])['driverAge'].min().reset_index().sort_values(by = 'driverAge', ascending=False)
            df1= pd.merge(df2, df1[['driverAge','driverNationality','raceDate','raceName','constructorName']],on="driverAge")
            df1=df1[['driverName','driverAge', 'driverNationality','constructorName','raceDate','raceName']].tail()

            figure={
                'data':[
                    go.Bar(y=df1['driverName']+"  ", x=df1['driverAge'],
                             text="Age: " + df1['driverAge'].round(1).astype(str)+" | "+ df1['raceName']+" | "+df1['raceDate'].astype(str),
                             orientation="h",marker_color='#e10600')
                ],
                'layout':go.Layout(height=400,template="simple_white", showlegend=False,
                          xaxis =dict(showline=False, ticks='',color='#808080',side='top',title="Age", range=[0,30]),
                          yaxis =dict(showline=False,ticks='',color='#808080'),
                          title=dict(text='<b>Youngest drivers winning a race</b>',font_color='#808080'),
                          font_family="system-ui")
                    }

            style2  = {'display': 'block'}
            #to get a dataframe (dfdatefinal) with the date of the final race in the season
            dfdatefinal=dfy.groupby(['raceYear'])['raceDate'].max().reset_index()

            #to get a dataframe (df1) with the champion-drivers per season
            df1= dfy.groupby(['raceYear','driverName','driverNationality','driverDob','constructorName'])['points'].sum().reset_index().sort_values(
                                                ['raceYear','points'], ascending=[False,False]).groupby('raceYear').head(1)

            #to expand df1 with the driver's age at the moment of becoming champion
            df1= pd.merge(df1, dfdatefinal, on='raceYear')
            df1['driverAge']=((df1['raceDate'] - df1['driverDob'])/ np.timedelta64(1, 'Y')).round(2)

            #to get a dataframe (df2) with the first champioship per driver and expand it with other useful columns
            df2=df1.groupby(['driverName'])['driverAge'].min().reset_index().sort_values(by = 'driverAge', ascending=False)
            df1= pd.merge(df2, df1[['driverName','raceYear', 'driverNationality','constructorName', 'points', 'raceDate', 'driverAge']],on=['driverName',"driverAge"]).sort_values(by = 'driverAge', ascending=True).head(10).sort_values(by = 'driverAge', ascending=False)
            df1=df1.tail()

            figure2={
                'data':[
                    go.Bar(y=df1['driverName']+"  ", x=df1['driverAge'],
                             text="Age: " + df1['driverAge'].round(1).astype(str)+" | "+df1['raceYear'].astype(str)
                             ,orientation="h",marker_color='#e10600')
                ],
                'layout':go.Layout(height=400, template="simple_white", showlegend=False,
                                  xaxis =dict(showline=False, ticks='',color='#808080',side='top',title="Age", range=[0,30]),
                                  yaxis =dict(showline=False,ticks='',color='#808080'),
                                  title=dict(text='<b>Youngest drivers winning a Championship</b>',font_color='#808080'),
                                  font_family="system-ui")
                    }






    elif tab == 'Constructor Results':
        if tab2 == 'Championship Podiums':
            df1=df0[df0['place'].isin(Checklist_options)].copy()
            df1=df1[(df1['raceYear']>=years[0])&(df1['raceYear']<=years[1])]
            if nationality != "All":
                df1=df1[df1['constructorNationality']==nationality]
            df1=df1.groupby(['constructorName','constructorNationality'])['points'].count().reset_index().sort_values(
                                            ['points'], ascending=[False]).rename(
                                             columns={'points': 'ChampionshipPodiums'}).reset_index(drop=True)

            df1=df1.head(observations).copy().sort_values('ChampionshipPodiums', ascending=[True])

            if len(df1)> 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"
            figure={
                'data':[
                    go.Bar(y=df1['constructorName']+ " | " + df1['constructorNationality']+"  ",
                           x=df1['ChampionshipPodiums'],
                           text="Podiums: " + df1['ChampionshipPodiums'].astype(str),orientation="h",
                           textposition='auto',marker_color=barsColor),
                ],
                'layout':go.Layout(height=600+observations*20-200,
                          template="simple_white", showlegend=False,
                          xaxis =dict(visible=False),
                          yaxis =dict(showline=False,ticks='',color='#808080'),
                          font_family="system-ui"
                            )
                }
        if tab2 == 'Race Podiums':
            df1=df[(df['raceYear']>=years[0])&(df['raceYear']<=years[1])].copy()
            if circuit != "All":
                df1=df1[df1['raceName']==circuit]

            df1= df1[df1['positionOrder'].isin(Checklist_options)].groupby(['constructorName','constructorNationality'
                                           ])['positionOrder'].count().reset_index().sort_values(
                                             by = 'positionOrder', ascending=False).rename(
                                             columns={'positionOrder': 'wins'})
            df1=df1[['constructorName','constructorNationality','wins']]
            if nationality != "All":
                df1=df1[df1['constructorNationality']==nationality]
            df1=df1.head(observations).sort_values(by='wins',ascending=True)

            if len(df1)> 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"

            figure= {
                'data':[
                    go.Bar(y=df1['constructorName']+ " | " + df1['constructorNationality']+"  ",
                           x=df1['wins'],
                           text="Podiums: " + df1['wins'].astype(str),orientation="h",
                           textposition='auto',marker_color=barsColor),
                ],
                'layout':go.Layout(height=600+observations*20-200,
                          template="simple_white", showlegend=False,
                          xaxis =dict(visible=False),
                          yaxis =dict(showline=False,ticks='',color='#808080'),
                          font_family="system-ui"
                            )
                    }
        if tab2 == 'Place per Season':
            if circuit != "All":
                dfx=dfdfp9(circuit)
                dfx=dfx[(dfx['raceYear']>=years[0])&(dfx['raceYear']<=years[1])]
            else:
                dfx=dfp9[(dfp9['raceYear']>=years[0])&(dfp9['raceYear']<=years[1])]

            df1=dfx[dfx['constructorName']==constructorName1]
            df2=dfx[dfx['constructorName']==constructorName2]

            if len(df1) + len(df2) > 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"

            if len(df1['raceYear'].unique()) <6 & len(df2['raceYear'].unique()) <6:
                xaxisDict = dict(showline=False, ticks='', dtick=1,color='#808080')
            else:
                xaxisDict = dict(showline=False, ticks='',color='#808080')

            figure={
                'data':[
                    go.Scatter(y=df1['place'], x=df1['raceYear'],text=df1['place'].astype(str),
                               name=constructorName1, marker_color='#808080'),
                    go.Scatter(y=df2['place'], x=df2['raceYear'],text=df2['place'].astype(str),
                               name=constructorName2, marker_color='#f55b68'),
                ],
                'layout':go.Layout(height=600, template="simple_white",
                          legend=dict(orientation="h", yanchor="bottom",y=1.02),
                          xaxis =xaxisDict,
                          yaxis =dict(showline=False,ticks='',range=[20.1, 0],color='#808080',
                                      zeroline=True, zerolinecolor='#ededed',zerolinewidth=0.5),
                          font_family="system-ui"
                          )
                }
        if tab2 == 'Drivers per Season':
            #to create the dataframe for the chart
            dfx=dfp11[(dfp11['raceYear']>=yearsDPS[0])&(dfp11['raceYear']<=yearsDPS[1])]
            dfx=dfx.sort_values(['constructorName','raceYear',], ascending=[False,True])
            if constructorNameDPS !="All":
                dfx=dfx[dfx['constructorName']==constructorNameDPS]
            df1=pd.merge(dfx,dfcc, on='constructorName')
            df1=df1.sort_values(['raceYear','constructorName',], ascending=[True,False])

            figHeight=len(df1)*7
            tickFont = 7
            if figHeight <400:
                figHeight=500
                tickFont = 10

            if len(df1) > 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"

            if len(df1['raceYear'].unique()) <6:
                xaxisDict = dict(showline=False, ticks='',color='#808080',side='top', dtick=1)
            else:
                xaxisDict = dict(showline=False, ticks='',color='#808080',side='top')

            figure= {
                'data':[
                    go.Scatter(y=[df1['constructorName'],df1['driverName']], x=df1['raceYear'],
                             text="Driver: " + df1['driverName'] + "| Place: " + df1['place'].astype(str),
                             mode='markers',
                             marker_color=df1['color'],
                             ),
                ],
                'layout':go.Layout(
                          height=figHeight+200, width=700,template="simple_white", showlegend=False,
                          xaxis =xaxisDict,
                          yaxis =dict(showline=False,ticks='',color='#808080',tickfont=dict(size=tickFont)),
                          font_family="system-ui"
                          )
            }
        if tab2 == 'Winners per Season':

            if circuit != "All":
                df1=dfdf0c(circuit)
                df1=df1[(df1['raceYear']>=years[0])&(df1['raceYear']<=years[1])]
            else:
                df1=df0c[(df0c['raceYear']>=years[0])&(df0c['raceYear']<=years[1])]

            if len(df1)> 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"

            tickFont = 12
            figHeight=400+len(df1)*25

            figure={
                'data':[
                    go.Bar(y=[df1['raceYear'], df1['place']],
                           x=df1['points'],
                             text=df1['constructorName']+ " | " + df1['constructorNationality']
                                   +" | "+"Points: "+df1['points'].astype(str),
                             marker_color=df1['color'],orientation="h",textposition='auto', hoverinfo = 'text')
                ],
                'layout':go.Layout(height=figHeight, template="simple_white", showlegend=False,
                          xaxis =dict(showline=False, ticks='',color='#808080',title="Points"),
                          yaxis =dict(showline=False,ticks='',color='#808080',title="Season_Place",tickfont=dict(size=tickFont)),
                          title=dict(text='<b>Constructors in first 3 places per season</b>',font_color='#808080'),
                          font_family="system-ui")
                    }


    elif tab == 'Nationality Results':
        if tab2 == 'Championship Podiums':
            df1=df0[df0['place'].isin(Checklist_options)].copy()
            df1=df1[(df1['raceYear']>=years[0])&(df1['raceYear']<=years[1])]
            df1=df1.groupby(['driverNationality'])['points'].count().reset_index().sort_values(
                                            ['points'], ascending=[False]).rename(
                                             columns={'points': 'ChampionshipPodiums'}).reset_index(drop=True)

            df1=df1.head(observations).copy().sort_values('ChampionshipPodiums', ascending=[True])

            if len(df1) > 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"

            figure= {
                'data':[
                    go.Bar(y=df1['driverNationality']+"  ",
                           x=df1['ChampionshipPodiums'],
                           text="Podiums: " + df1['ChampionshipPodiums'].astype(str),orientation="h",
                           textposition='auto',marker_color=barsColor),
                ],
                'layout':go.Layout(height=600+observations*20-200,
                          template="simple_white", showlegend=False,
                          xaxis =dict(visible=False),
                          yaxis =dict(showline=False,ticks='',color='#808080'),
                          font_family="system-ui"
                            )
                }
        if tab2 == 'Race Podiums':
            df1=df[(df['raceYear']>=years[0])&(df['raceYear']<=years[1])].copy()
            if circuit != "All":
                df1=df1[df1['raceName']==circuit]
            df1= df1[df1['positionOrder'].isin(Checklist_options)].groupby(['driverNationality'
                                           ])['positionOrder'].count().reset_index().sort_values(
                                             by = 'positionOrder', ascending=False).rename(
                                             columns={'positionOrder': 'wins'})
            df1=df1.head(observations).copy().sort_values('wins', ascending=[True])

            if len(df1) > 0:
                style  = {'display': 'block'}
                children = ""
            else:
                style  = {'display': 'none'}
                children = "### Upsi... There is no data with the selected parameters!"

            figure= {
                'data':[
                    go.Bar(y=df1['driverNationality']+"  ",
                           x=df1['wins'],
                           text="Podiums: " + df1['wins'].astype(str),orientation="h",
                           textposition='auto',marker_color=barsColor),
                ],
                'layout':go.Layout(height=600+observations*20-200,
                          template="simple_white", showlegend=False,
                          xaxis =dict(visible=False),
                          yaxis =dict(showline=False,ticks='',color='#808080'),
                          font_family="system-ui"
                            )
                    }

    return style, children, figure, style2, figure2


@app.callback(
    [Output('dashtable', 'data'),
     Output('dashtable', 'columns'),
     Output('dashtable2', 'data'),
     Output('dashtable2', 'columns'),
     Output('headtext', 'children'),
     Output('maintable', 'style'),
     Output('raceTabsDiv', 'style'),
     Output('maintable2', 'style'),

     Output('Chart3Div', 'style'),
     Output('Chart3', 'figure')],
    [Input('Dropdown1', 'value'),
     Input('Dropdown2', 'value'),
     Input('Dropdown3', 'value'),
     Input('raceTabs', 'value')])
def funtion(year, topic, subtopic, tab):
    style_mt= {'display': 'block'}
    style_rt= styleChart3Div = {'display': 'none'}
    chart3 = {}
    if topic == "RACES" and subtopic != "All":
        style_mt= {'display': 'none'}
        style_rt= {'display': 'block'}
        headtext ="Formula 1 "+ subtopic + " - Race Results"

        #df1=df[['raceRound','raceName','raceDate','driverName','constructorName','laps','time']].copy()[0:10]
        #data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
        if tab == 'RACE RESULT':
            df1=df.copy()
            df1=df1[(df1['raceYear']==year)&(df1['raceName']==subtopic)].sort_values('positionOrder')
            df1=df1[['positionOrder','driverName','constructorName','laps','time','points']]
            df1.columns=['POS','DRIVER','CAR','LAPS','TIME/RETIRED','POINTS']
            data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
        elif tab == 'FASTEST LAPS':
            df1=df.copy()
            df1=df1[(df1['raceYear']==year)&(df1['raceName']==subtopic)].sort_values('fastestLapTime')
            df1=df1[['fastestLapRank','driverNumber','driverName',
                     'constructorName','fastestLap','fastestLapTime','fastestLapSpeed']]
            df1.columns=['POS','NO','DRIVER','CAR','LAP','TIME','SPEED']
            data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
        elif tab == 'PIT STOP SUMMARY':
            df1=df.copy()
            df1=df1[(df1['raceYear']==year)&(df1['raceName']==subtopic)]
            raceId=df1['raceId'].iloc[0]

            df1=pit_stops[pit_stops['raceId']==raceId]
            df1=pd.merge(df1,df[['raceId','driverId','driverNumber','driverName','constructorName']], on=['raceId','driverId']).sort_values('time')
            df1=df1[['stop','driverNumber','driverName','constructorName','lap','time','duration']]
            df1.columns=['STOPS','NO','DRIVER','CAR','LAP','TIME OF DAY','TIME']
            df1['TIME']=pd.to_numeric(df1['TIME'], errors='coerce').round(3)

            df1['TOTAL']=df1.apply(lambda x: cumtimepits(df1,x['DRIVER'],x['STOPS']),axis=1).round(3)
            df1['TOTAL']=df1['TOTAL'].apply(lambda x: pd.to_datetime(x, unit='s').strftime("%M:%S.%f")[:-3] if x>60 else x)
            data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
        elif tab == 'STARTING GRID':
            df1=df.copy()
            df1=df1[(df1['raceYear']==year)&(df1['raceName']==subtopic)].sort_values('grid')

            #to replace, if needed, grid positions indicated as zero with the skipped grid position
            df1['x']=np.arange(len(df1)) == df1['grid']
            if df1['grid'].iloc[0] == 0:
                missingPOS=df1['grid'][df1['x']==False].iloc[0]-1
                df1['grid'].iloc[0]=missingPOS

            #to get the column TIME from the qualifying dataset
            raceId=df1['raceId'].iloc[0]
            dfq = qualifying[qualifying['raceId']==raceId].copy()
            dfq['TIME']=dfq.apply(lambda x: startingtime(x['q1'],x['q2'],x['q3']),axis=1)
            df1=pd.merge(df1,dfq, on=['raceId','driverId']).sort_values('grid')

            #to select only the needed columns and rename columns
            df1=df1[['grid','driverNumber','driverName','constructorName','TIME']].sort_values('grid')
            df1.columns=['POS','NO','DRIVER','CAR','TIME']
            data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
        elif tab == "QUALIFYING":
            #to get the subset of df needed & the raceId
            df1=df.copy()
            df1=df1[(df1['raceYear']==year)&(df1['raceName']==subtopic)].sort_values('grid')
            raceId=df1['raceId'].iloc[0]

            #to get the qualifying dataset and join it with the df1
            dfq = qualifying[qualifying['raceId']==raceId].copy()
            df1=pd.merge(df1,dfq, on=['raceId','driverId']).sort_values('position')

            #to select only the needed columns and rename columns
            df1=df1[['position','driverNumber','driverName','constructorName','q1','q2','q3']].sort_values('position')
            df1.columns=['POS','NO','DRIVER','CAR','Q1','Q2','Q3']
            data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
        return data1, col1, data1, col1, headtext,style_mt,style_rt,style_rt, styleChart3Div, chart3
    else:
        if topic == "RACES":
            headtext = str(year) + " Race Results"
            df1=df.copy()
            df1=df1[df1['raceYear']==year]
            df1=df1.groupby(['raceRound','raceName','raceDate','driverName','constructorName','laps','time'])['positionOrder'].min().reset_index()#['raceName']
            df1=df1[df1['positionOrder']==1]
            df1=df1[['raceName','raceDate','driverName','constructorName','laps','time']]
            df1.columns=['GRAND PRIX','DATE','WINNER','CAR','LAPS','TIME']
            df1=df1.reset_index().drop(['index'], axis = 1)
            df1['GRAND PRIX'] = df1['GRAND PRIX'].str[:-11]
            data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
            return data1, col1, data1, col1, headtext,style_mt,style_rt,style_rt, styleChart3Div, chart3

        if topic == "DRIVERS":
            if subtopic=="All":
                headtext = str(year) + " Driver Standings"
                df1=df.copy()
                df1=df1[df1['raceYear']==year]
                df1=df1.groupby(['driverName','driverNationality','constructorName'])['points'].sum().reset_index().sort_values(
                    by='points',ascending=False)
                df1=df1.reset_index().reset_index().drop(['index'], axis = 1)
                df1['level_0']=df1['level_0']+1
                df1.columns=['POS','DRIVER','NATIONALITY','CAR','PTS']
            else:
                headtext =str(year) + " Driver Standings: " + subtopic
                driver=subtopic
                df1=df.copy()
                df1=df1[df1['raceYear']==year]
                df1=df1[df1['driverName']==driver]
                df1=pd.merge(df1,status, on="statusId")
                df1=df1[['raceName','raceDate','constructorName','positionOrder','status','points']].sort_values('raceDate')
                df1.columns=['GRAND PRIX','DATE','CAR','RACE POSITION', 'STATUS','PTS']
                df1['GRAND PRIX'] = df1['GRAND PRIX'].str[:-11]

                styleChart3Div = {'display': 'block'}


                xaxisDict = dict(title = "Circuit", showline=False, ticks='',color='#808080')

                chart3={
                'data':[
                    go.Scatter(y=df1['RACE POSITION'], x=df1['GRAND PRIX'],
                               text="Race Position: " + df1['RACE POSITION'].astype(str), marker_color='#f55b68'),
                ],
                'layout':go.Layout(height=600,template="simple_white",
                          #legend=dict(orientation="h", yanchor="bottom",y=1.02),
                          title= dict(text=f'{year} Driver Standings per Circuit: <b>{subtopic}</b>',font_color='#808080'),
                          xaxis =xaxisDict,
                          yaxis =dict(showline=False,ticks='',range=[20.1, 0], color='#808080',
                                      title = "Race Position",
                                      zeroline=True, zerolinecolor='#ededed',zerolinewidth=0.5),

                          )
                    }

            data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
            return data1, col1, data1, col1,headtext,style_mt,style_rt,style_rt, styleChart3Div, chart3

        if topic == "TEAMS":
            if subtopic=="All":
                headtext = str(year) + " Constructor Standings"
                df1=df.copy()
                df1=df1[df1['raceYear']==year]
                df1=df1.groupby(['constructorName'])['points'].sum().reset_index().sort_values(
                    by='points',ascending=False)
                df1=df1.reset_index().reset_index().drop(['index'], axis = 1)
                df1['level_0']=df1['level_0']+1
                df1.columns=['POS','TEAM','PTS']
            else:
                headtext = str(year) + " Constructor Standings: " + subtopic
                team=subtopic
                df1=df.copy()
                df1=df1[df1['raceYear']==year]
                df1=df1[df1['constructorName']==team]
                df1=df1.groupby(['raceRound','raceName','raceDate'])['points'].sum().reset_index()
                df1=df1[['raceName','raceDate','points']]
                df1.columns=['GRAND PRIX','DATE','PTS']
                df1['GRAND PRIX'] = df1['GRAND PRIX'].str[:-11]

                styleChart3Div = {'display': 'block'}


                xaxisDict = dict(title = "Circuit", showline=False, ticks='',color='#808080')

                chart3={
                'data':[
                    go.Scatter(y=df1['PTS'], x=df1['GRAND PRIX'],
                               text="PTS: " + df1['PTS'].astype(str), marker_color='#f55b68'),
                ],
                'layout':go.Layout(height=600,template="simple_white",
                          #legend=dict(orientation="h", yanchor="bottom",y=1.02),
                          title= dict(text=f'{year} Constructor Standings per Circuit: <b>{subtopic}</b>',font_color='#808080'),
                          xaxis =xaxisDict,
                          yaxis =dict(showline=False,ticks='', color='#808080',
                                      title = "Points",
                                      zeroline=True, zerolinecolor='#ededed',zerolinewidth=0.5),

                          )
                    }

            data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
            return data1, col1, data1, col1, headtext,style_mt,style_rt,style_rt, styleChart3Div, chart3

        if topic == "FASTEST LAP":
            headtext = str(year) + " Fastest Lap"
            df1=df.copy()
            df1=df1[df1['raceYear']==year]
            df1=df1.groupby(['raceRound','raceName','driverName','fastestLapTime','fastestLap','fastestLapSpeed'])['fastestLapRank'].sum().reset_index()
            df1=df1[df1['fastestLapRank']=="1"]
            df1=df1[['raceName', 'driverName', 'fastestLapTime', 'fastestLap','fastestLapSpeed']]
            df1.columns=['GRAND PRIX','DRIVER','TIME','LAP','SPEED']
            df1['GRAND PRIX'] = df1['GRAND PRIX'].str[:-11]
            data1, col1 =df1.to_dict('records'), [{"name": i, "id": i} for i in df1.columns]
            return data1, col1, data1, col1, headtext,style_mt,style_rt,style_rt, styleChart3Div, chart3

# Add the server clause:
if __name__ == '__main__':
    app.run_server(debug=True)
