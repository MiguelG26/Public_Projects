import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
import datetime
from datetime import date, timedelta
from dash.dependencies import Input, Output

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server# only for heroku
#

red='#cc1f04'
yellow='#e0d907'
green='#059907'

#new data on a weekly basis
df = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/nationalcasedeath/csv/data.csv')

df.columns=['countriesAndTerritories', 'countryterritoryCode', 'continent', 'popData2019', 'indicator',
       'weekly_count', 'year_week', 'rate_14_day', 'cumulative_count','source','note']

df=df[['year_week','countriesAndTerritories', 'countryterritoryCode', 'popData2019', 'continent' , 'indicator','weekly_count']]

cases=list(df[df['indicator']=="cases"]['weekly_count'])
df=df[df['indicator']=="deaths"]
df['cases']=cases
df = df.rename(columns={'weekly_count': 'deaths','continent': 'continentExp'})

df['dateRep']=df.apply(lambda x: datetime.datetime.strptime(x['year_week'] + '-1', "%Y-%W-%w"),axis=1)
df['year']=df['dateRep'].dt.year

mymap={1:'01',2:'02',3:'03',4:'04',5:'05',6:'06',7:'07',8:'08',9:'09',10:'10',11:'11',12:'12'}
df['month']=df['dateRep'].dt.month.map(mymap)
df['year_month']=df['year'].astype(str)+"_"+df['month']
df['month']=df['dateRep'].dt.month #to bring the column "month" back to integer
df['week']=df['year_week'].str[5:].astype(int)
df=df[['dateRep','year', 'month', 'week', 'year_month' , 'cases','deaths','countriesAndTerritories','popData2019','continentExp']]

#to remove the rows including aggregated data from continents
no_countries=['Africa (total)','America (total)','Asia (total)','EU/EEA (total)','Europe (total)','Oceania (total)']
df= df[~df['countriesAndTerritories'].isin (no_countries)]

data=df.copy()

country_options = [{'label': 'All', 'value': 'All'}]
for country in data['countriesAndTerritories'].unique():
    country_options.append({'label':str(country),'value':country})
country_options.append({'label':str(country),'value':country})

def data_continent(start_date, end_date):
    df= data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    df=df.groupby(['countriesAndTerritories','continentExp'])[['cases','deaths']].sum().sort_values('cases',ascending=False)
    df =df.reset_index()

    df.index=df['countriesAndTerritories']
    df=df.drop('countriesAndTerritories', axis=1)

    dfpop=data.groupby('countriesAndTerritories')[['popData2019']].mean().round(0) # to get the population per country
    df=pd.concat([df,dfpop],axis=1)

    dfpop=df.groupby('continentExp')[['popData2019']].sum().round(0)
    df=df.groupby(['continentExp'])[['cases','deaths']].sum()
    df=pd.concat([df,dfpop],axis=1)

    df['%All_Cases']=(df['cases']/df['cases'].sum()*100).round(2)
    df['%All_Deaths']=(df['deaths']/df['deaths'].sum()*100).round(2)
    df['Mortality_rate']=(df['deaths']/df['cases']*100).round(2)

    df=df[['popData2019','cases', 'deaths', '%All_Cases', '%All_Deaths','Mortality_rate']]

    df['Deaths_by_population']=(df['deaths']/df['popData2019']*100).round(3)
    df['Cases_by_population']=(df['cases']/df['popData2019']*100).round(2)

    df=df.sort_values('cases',ascending=False).head(5)
    return df

def data_country(start_date, end_date, cont="All", country="Germany"):
    if start_date== None:
        start_date==date(2020, 1, 1)

    df= data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if cont != None and cont != "All":
        df = df[df['continentExp']==cont]
    if cont!= None and country!= None:
        cont_country=data['continentExp'][data['countriesAndTerritories']==country].iloc[0]
    else:
        cont_country="All"
    #######################################################################
    df=df.groupby(['countriesAndTerritories','continentExp'])[['cases','deaths']].sum().sort_values('cases',ascending=False)
    df =df.reset_index()
    df.index=df['countriesAndTerritories']
    df=df.drop('countriesAndTerritories', axis=1)

    dfpop=data.groupby('countriesAndTerritories')[['popData2019']].mean().round(0)
    df['%All_Cases']=(df['cases']/df['cases'].sum()*100).round(2)
    df['%All_Deaths']=(df['deaths']/df['deaths'].sum()*100).round(2)
    df['Mortality_rate']=(df['deaths']/df['cases']*100).round(2)

    df=pd.concat([df,dfpop],axis=1)
    df['Deaths_by_population']=(df['deaths']/df['popData2019']*100).round(4)
    df['Cases_by_population']=(df['cases']/df['popData2019']*100).round(2)

    df=df.dropna()
    df=df[df['popData2019']>999999]

    #To get the List of the top 3 countries by deaths
    if cont != "Oceania" and cont != None:
        if cont== "All" or cont_country == cont:
            df1=df.sort_values('Deaths_by_population',ascending=False).head(3)
            if sum(df1.index==country)==0:
              df1=df1.append(df[df.index==country])
        else:
            df1=df.sort_values('Deaths_by_population',ascending=False).head(4)
    else:
    #    if cont== "All" or cont_country == cont:
    #        df1=df.sort_values('Deaths_by_population',ascending=False).head(3)
    #        if sum(df1.index==country)==0:
    #          df1=df1.append(df[df.index==country])
    #    else:
            df1=df.sort_values('Deaths_by_population',ascending=False).head(3)


    df1=df1.sort_values('Deaths_by_population',ascending=True)
    countries_deaths=list(df1.index)

    #To get the List of the top 3 countries by cases

    #if cont_country == cont:
    #    df1=df.sort_values('Deaths_by_population',ascending=False).head(3)
    #    if sum(df1.index==country)==0:
    #      df1=df1.append(df[df.index==country])
    #else:
    #    df1=df.sort_values('Deaths_by_population',ascending=False).head(4)

    if cont != "Oceania" and cont != None:
        if cont== "All" or cont_country == cont:
            df1=df.sort_values('Cases_by_population',ascending=False).head(3)
            if sum(df1.index==country)==0:
              df1=df1.append(df[df.index==country])
        else:
            df1=df.sort_values('Cases_by_population',ascending=False).head(4)
    else:
#        if cont== "All" or cont_country == cont:
#            df1=df.sort_values('Cases_by_population',ascending=False).head(3)
#            if sum(df1.index==country)==0:
#              df1=df1.append(df[df.index==country])
#        else:
            df1=df.sort_values('Cases_by_population',ascending=False).head(3)

    df1=df1.sort_values('Cases_by_population',ascending=True)
    countries_cases=list(df1.index)

    return country, df, countries_deaths, countries_cases, cont_country

def data_country_PercPop(start_date, end_date, cont="All"):
    date_start = '2020-01-01'
    dfc=data.copy()
    if cont != "All":
        dfc = dfc[dfc['continentExp']==cont]
    dfc=dfc[dfc['dateRep']>date_start]#!!!!!!!!!!!!!!!!

    dfc= dfc[(dfc['dateRep']>=start_date)&(dfc['dateRep']<=end_date)].copy()
    dfc=dfc.groupby(['year_month','countriesAndTerritories','popData2019'])[['cases','deaths']].sum()
    dfc =dfc.reset_index()
    dfc.index=dfc['year_month']
    dfc=dfc.drop('year_month', axis=1)
    dfc['perc_deaths']=dfc['deaths']/dfc['popData2019']
    dfc['perc_cases']=dfc['cases']/dfc['popData2019']
    return dfc

rectangle = html.Div([
        html.Br([]),
        html.Div([
                html.P(
                    "This Covid-19 Dashboard was made purely\
                    in Python using the Dash library from Plotly & with tons of love ♡",
                    style={"color": "#ffffff",'fontSize': 15},
                    className="row",
                )
            ],className="product",)
    ],style={'width':'100%','display':'inline-block'})

filters=html.Div([
        html.Br([]),
        html.Div([
            html.Div([html.H6('Select a time interval:', style= {'color':'#959a99','font-weight':"bold"})],className="six columns"),
            html.Div([html.H6('Select a Continent:', style= {'color':'#959a99','font-weight':"bold", 'float': 'left'})],className="three columns"),
            html.Div([html.H6('Select a Country:', style= {'color':'#959a99','font-weight':"bold", 'float': 'left', 'padding-left': '40px'})],className="three columns"),
            ],className="row"), #'font-family': 'sans-serif'
        html.Div([
                html.Div([
                    html.P(dcc.DatePickerRange(
                            id = "DatePickerRange",
                            min_date_allowed=date(2020, 1, 1),
                            max_date_allowed=date(2021, 12, 31),
                            start_date=date(2020,3,1),
                            end_date=date(2021,12,31),
                            calendar_orientation='vertical',
                            ),style= {'width': '80%','float': 'left', 'margin-bottom': '20px'}
                    ),
                    ],className="three columns" ),
                html.Div([
                    html.P(dcc.Dropdown(
                                id = "Dropdown_daterange",
                                options=[
                                    #{'label': 'Last Week', 'value': 'Last_7'},
                                    {'label': 'Last 30 Days', 'value': 'Last_30'},
                                    {'label': 'Last 90 Days', 'value': 'Last_90'},
                                    {'label': 'All', 'value': 'All'}
                                ],
                                value='All'
                            ),style= {'padding-left': '60px'}
                    ),
                    ],className="three columns" ),
                html.Div([
                    html.P(dcc.Dropdown(
                                id = "RadioItems_Cont",
                                options=[
                                    {'label': 'America', 'value': 'America'},
                                    {'label': 'Europe', 'value': 'Europe'},
                                    {'label': 'Asia', 'value': 'Asia'},
                                    {'label': 'Africa', 'value': 'Africa'},
                                    {'label': 'Oceania', 'value': 'Oceania'},
                                    {'label': 'All', 'value': 'All'}
                                ],
                                value='All'
                            ),style= {'padding-left': '60px'}
                    ),
                    ],className="three columns"),

                html.Div([
                    html.P(
                    dcc.Dropdown(id='country_picker',options=country_options,value='Germany'),
                    style= {'width': '70%', 'float': 'right'}
                    ),
                    ],className="three columns"),
            ],style={'width':'100%','display':'inline-block', 'background': '#ffffff'}),
    ])

header = html.Div([
            html.Div(
                [
                    html.Div(
                        [
                            html.H4("COVID-19 Dashboard", style= {'display': 'flex','align-items': 'right'}),
                        ],className="seven columns main-title",
                    ),
                    html.Div(
                        [
                            html.Img(
                                src=app.get_asset_url("Covid19_foto1.jpg"),
                                className="logo_right",
                            ),
                        ]
                    ),
                ],style={'width':'100%','display':'inline-block'}
            ),
            rectangle,
            filters,
    ],className="header_bar",
)

body=html.Div([
        #Row 2
        html.Div([
            html.Div([
                    html.Div([
                            html.Div([html.H5(id='totaldeaths'), html.P("Total Deaths")],className="eleven columns"),
                        ],className="eight columns mini_container",),
                    html.Div([
                            html.Div([html.H5(id='totalcases'), html.P("Total Cases")],className="eleven columns"),
                        ],className="eight columns mini_container",),
                    html.Div([
                            html.Div([html.H5(id='total_mor_rate'), html.P("Mortality Rate")],className="eleven columns"),
                        ],className="eight columns mini_container",),
                ],className="two columns",),
            html.Div([
                    html.Div(dcc.Graph(id='Gr_deathsWW'), className="six columns",),
                    html.Div(dcc.Graph(id='Gr_casesWW'), className="six columns",),
                ],className="ten columns",)
            ],className="row"),

        #Row 3
        html.Hr(),
        html.Div([
            html.Div([
                    html.Div([
                            html.Div([html.H5(id='totaldeaths_country'), html.P("Total Deaths")],className="eleven columns"),
                        ],className="eight columns mini_container",),
                    html.Div([
                            html.Div([html.H5(id='totalcases_country'), html.P("Total Cases")],className="eleven columns"),
                        ],className="eight columns mini_container",),
                    html.Div([
                            html.Div([html.H5(id='total_mor_rate_country'), html.P("Mortality Rate")],className="eleven columns"),
                        ],className="eight columns mini_container",),
                ],className="two columns",),
            html.Div([
                    html.Div(dcc.Graph(id='Gr_deaths_country'), className="six columns",),
                    html.Div(dcc.Graph(id='Gr_cases_country'), className="six columns",),
                ],className="ten columns",)
            ],className="row"),

        #Row 5
        html.Hr(),
        html.Div([
            html.Div(dcc.Graph(id='Gr_country_deaths'), className="six columns"),
            html.Div(dcc.Graph(id='Gr_country_cases'), className="six columns"),
            ],className="row"),

        #Row 6
        html.Div([
            html.Div(dcc.Graph(id='Gr_country_deaths_Pro'), className="six columns"),
            html.Div(dcc.Graph(id='Gr_country_cases_Pro'), className="six columns"),
            ],className="row"),

        #Row 7
        html.Hr(),
        html.Div(dcc.Graph(id='Gr_PercPop_deaths'), className="row"),

        #Row 8
        html.Div(dcc.Graph(id='Gr_PercPop_cases'), className="row"),

        html.Div([
            html.Br([]),
            html.Div([
                    html.P(
                        "Source: https://opendata.ecdc.europa.eu/covid19/nationalcasedeath/csv/data.csv",
                        style={"color": "#ffffff",'fontSize': 12},
                        className="row",
                    )
            ],className="product",)
    ],style={'width':'100%','display':'inline-block'})


        #Row 9
        #html.Hr(),
        #html.Div([
        #    html.Div(dcc.Graph(id='Gr_continent_deaths'), className="six columns"),
        #    html.Div(dcc.Graph(id='Gr_continent_cases'), className="six columns"),
        #    ],className="row"),

        #Row 4
        #html.Div([
        #    html.Div(dcc.Graph(id='Gr_continent_deaths_Pro'), className="six columns"),
        #    html.Div(dcc.Graph(id='Gr_continent_cases_Pro'), className="six columns"),
        #    ],className="row"),

    ],className="cuerpo",)


app.layout = html.Div([header,body],className="page")


#"""
#  Callbacks
#"""

@app.callback(
    Output('DatePickerRange', 'start_date'),
    [Input('Dropdown_daterange', 'value')])
def RadioItems(value):
    #if value == 'Last_7':
    #    return date(2020,12,31)- timedelta(7)
    if value == 'Last_30':
        return date.today()- timedelta(30)
    if value == 'Last_90':
        return date.today()- timedelta(90)
    if value == 'All':
        return date(2020, 1, 1)
    if value == None:
        return date(2020, 1, 1)


######Row #2
######totaldeaths#####
@app.callback(
    Output('totaldeaths', 'children'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value')])
def totaldeaths(start_date, end_date, cont):
    df= data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if cont != None and cont != "All":
        df=df[df['continentExp']==cont]
    df=df.groupby('countriesAndTerritories')[['cases','deaths']].sum().sort_values('deaths',ascending=False)
    totaldeaths = df['deaths'].sum()
    return '{:,}'.format(totaldeaths)

######totalcases#####
@app.callback(
    Output('totalcases', 'children'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value')])
def totalcases(start_date, end_date, cont):
    df= data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if cont != None and cont != "All":
        df=df[df['continentExp']==cont]
    df=df.groupby('countriesAndTerritories')[['cases','deaths']].sum().sort_values('deaths',ascending=False)
    totalcases = df['cases'].sum()
    return '{:,}'.format(totalcases)

######total_mor_rate#####
@app.callback(
    Output('total_mor_rate', 'children'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value')])
def total_mor_rate(start_date, end_date, cont):
    df= data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if cont != None and cont != "All":
        df=df[df['continentExp']==cont]
    df=df.groupby('countriesAndTerritories')[['cases','deaths']].sum().sort_values('deaths',ascending=False)
    total_mor_rate = round(df['deaths'].sum()/df['cases'].sum()*100,1)
    return '{:.2f} %'.format(total_mor_rate)

#####Gr_deathsWW#####
@app.callback(
    Output('Gr_deathsWW', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value')])
def upd_Gr_deathsWW(start_date, end_date, cont):
    df=data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if cont != None and cont != "All":
        df=df[df['continentExp']==cont]
    df=df.groupby('dateRep')[['cases','deaths']].sum()
    return {
        'data':[
            go.Bar(x=df.index, y=df['deaths'],showlegend=False,marker_color='#959a99'),
        ],
        'layout':go.Layout(
        title ={'text': '<b>Deaths</b> due to Covid-19 per week in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
        xaxis={'title':'CW', 'showgrid': False, 'color':'#959a99'},
        yaxis={'title':'Cases', 'showgrid': False, 'rangemode':'tozero', 'color':'#959a99'},
        )
    }

#####Gr_casesWW#####
@app.callback(
    Output('Gr_casesWW', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value')])
def upd_Gr_casesWW(start_date, end_date, cont):
    df=data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if cont != None and cont != "All":
        df=df[df['continentExp']==cont]
    df=df.groupby('dateRep')[['cases','deaths']].sum()
    return {
        'data':[
            go.Bar(x=df.index, y=df['cases'],showlegend=False,marker_color='#385d7f'),
        ],
        'layout':go.Layout(
        title ={'text': 'Covid-19 <b>Cases</b> per week in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
        xaxis={'title':'CW', 'showgrid': False, 'color':'#959a99'},
        yaxis={'title':'Cases', 'showgrid': False, 'rangemode':'tozero', 'color':'#959a99'},
        )
    }

######Row #3
######totaldeaths_country#####
@app.callback(
    Output('totaldeaths_country', 'children'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('country_picker', 'value')])
def totaldeaths_country(start_date, end_date, country):
    df= data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if country != None:
        df=df[df['countriesAndTerritories']==country]
    df=df.groupby('countriesAndTerritories')[['cases','deaths']].sum().sort_values('deaths',ascending=False)
    totaldeaths = df['deaths'].sum()
    return '{:,}'.format(totaldeaths)

######totalcases_country#####
@app.callback(
    Output('totalcases_country', 'children'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('country_picker', 'value')])
def totalcases_country(start_date, end_date, country):
    df= data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if country != None:
        df=df[df['countriesAndTerritories']==country]
    df=df.groupby('countriesAndTerritories')[['cases','deaths']].sum().sort_values('deaths',ascending=False)
    totalcases = df['cases'].sum()
    return '{:,}'.format(totalcases)

######total_mor_rate_country#####
@app.callback(
    Output('total_mor_rate_country', 'children'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('country_picker', 'value')])
def total_mor_rate_country(start_date, end_date, country):
    df= data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if country != None:
        df=df[df['countriesAndTerritories']==country]
    df=df.groupby('countriesAndTerritories')[['cases','deaths']].sum().sort_values('deaths',ascending=False)
    total_mor_rate = round(df['deaths'].sum()/df['cases'].sum()*100,1)
    return '{:.2f} %'.format(total_mor_rate)

#####Gr_deaths_country#####
@app.callback(
    Output('Gr_deaths_country', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('country_picker', 'value')])
def upd_Gr_deaths_country(start_date, end_date, country):
    df=data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if country != None:
        df=df[df['countriesAndTerritories']==country]
    df=df.groupby('dateRep')[['cases','deaths']].sum()
    return {
        'data':[
            go.Bar(x=df.index, y=df['deaths'],showlegend=False,marker_color='#959a99'),
        ],
        'layout':go.Layout(
        title ={'text': '<b>Deaths</b> due to Covid-19 per week in country: <b>{}</b>'.format(country), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
        xaxis={'title':'CW', 'showgrid': False, 'color':'#959a99'},
        yaxis={'title':'Deaths', 'showgrid': False, 'rangemode':'tozero', 'color':'#959a99'},
        )
    }

#####Gr_cases_country#####
@app.callback(
    Output('Gr_cases_country', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('country_picker', 'value')])
def upd_Gr_cases_country(start_date, end_date, country):
    df=data[(data['dateRep']>=start_date)&(data['dateRep']<=end_date)].copy()
    if country != None:
        df=df[df['countriesAndTerritories']==country]
    df=df.groupby('dateRep')[['cases','deaths']].sum()
    return {
        'data':[
            go.Bar(x=df.index, y=df['cases'],showlegend=False,marker_color='#385d7f'),
        ],
        'layout':go.Layout(
        title ={'text': 'Covid-19 <b>Cases</b> per week in country: <b>{}</b>'.format(country), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
        xaxis={'title':'CW', 'showgrid': False, 'color':'#959a99'},
        yaxis={'title':'Cases', 'showgrid': False, 'rangemode':'tozero', 'color':'#959a99'},
        )
    }

######Row #5
######Gr_country_deaths#####
@app.callback(
    Output('Gr_country_deaths', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value'),
     Input('country_picker', 'value')])

def Gr_country_deaths(start_date, end_date, cont, country):
    country, df, _, _, cont_country = data_country(start_date, end_date, cont, country)
    head_quantity=10

    df1=df.sort_values('deaths',ascending=False).head(head_quantity)
    if sum(df1.index==country)==0:
      df1=df1.append(df[df.index==country])
    df1=df1.sort_values('deaths',ascending=True)

    return {
        'data':[
            go.Bar(y=df1.index +"  ", x=df1['deaths'], text=df1['deaths'], textposition='auto',
            textfont_color="white",
            texttemplate='%{text:.2s}', orientation="h", showlegend=False, marker_color='#959a99'),
        ],
        'layout':go.Layout(
        template="simple_white",height=450, width=900,
        title ={'text': '<b>Deaths</b> per country due to Covid-19 in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
        xaxis={'showticklabels': False, 'showline':False, 'ticks':'','color':'#959a99'},
        yaxis={'showline': False, 'zeroline':False, 'ticks':'','color':'#959a99'},
        )
    }

######Gr_country_cases#####
@app.callback(
    Output('Gr_country_cases', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value'),
     Input('country_picker', 'value')])
def Gr_country_cases(start_date, end_date, cont, country):
    country, df, _, _,cont_country = data_country(start_date, end_date, cont, country)
    head_quantity=10

    df1=df.sort_values('cases',ascending=False).head(head_quantity)
    if sum(df1.index==country)==0:
      df1=df1.append(df[df.index==country])
    df1=df1.sort_values('cases',ascending=True)

    return {
        'data':[
            go.Bar(y=df1.index +"  ", x=df1['cases'], text=df1['cases'], textposition='auto',
            textfont_color="white",
            texttemplate='%{text:.2s}', orientation="h", showlegend=False, marker_color='#385d7f'),
        ],
        'layout':go.Layout(
        template="simple_white",height=450, width=900,
        title ={'text': 'Covid-19 <b>Cases</b> per country in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
        xaxis={'showticklabels': False, 'showline':False, 'ticks':'','color':'#959a99'},
        yaxis={'showline': False, 'zeroline':False, 'ticks':'','color':'#959a99'},
        )
    }

######Row #6
######Gr_country_deaths_Pro#####
@app.callback(
    Output('Gr_country_deaths_Pro', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value'),
     Input('country_picker', 'value')])
def Gr_country_deaths_Pro(start_date, end_date, cont, country):
    country, df, _, _, cont_country = data_country(start_date, end_date, cont, country)
    head_quantity=10

    df1=df.sort_values('Deaths_by_population',ascending=False).head(head_quantity)
    if sum(df1.index==country)==0:
      df1=df1.append(df[df.index==country])
    df1=df1.sort_values('Deaths_by_population',ascending=True)

    return {
        'data':[
            go.Bar(y=df1.index +"  ", x=df1['Deaths_by_population'], text=df1['Deaths_by_population'].round(3),
            textposition='auto', textfont_color="white",
            orientation="h", showlegend=False, marker_color='#959a99'),
        ],
        'layout':go.Layout(
        template="simple_white",height=450, width=900,
        title ={'text': '% of <b>Deaths</b> by population per country due to Covid-19 in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
        xaxis={'showticklabels': False, 'showline':False, 'ticks':'','color':'#959a99'},
        yaxis={'showline': False, 'zeroline':False, 'ticks':'','color':'#959a99'},
        )
    }

######Gr_country_cases_Pro#####
@app.callback(
    Output('Gr_country_cases_Pro', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value'),
     Input('country_picker', 'value')])
def Gr_country_cases_Pro(start_date, end_date, cont, country):
    country, df, _, _, cont_country = data_country(start_date, end_date, cont, country)
    head_quantity=10

    df1=df.sort_values('Cases_by_population',ascending=False).head(head_quantity)
    if sum(df1.index==country)==0:
      df1=df1.append(df[df.index==country])
    df1=df1.sort_values('Cases_by_population',ascending=True)

    return {
        'data':[
            go.Bar(y=df1.index +"  ", x=df1['Cases_by_population'], text=df1['Cases_by_population'],
            textposition='auto', textfont_color="white",
            orientation="h", showlegend=False, marker_color='#385d7f'),
        ],
        'layout':go.Layout(
        template="simple_white",height=450, width=900,
        title ={'text': '% of Covid-19 <b>Cases</b> by population per country in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
        xaxis={'showticklabels': False, 'showline':False, 'ticks':'','color':'#959a99'},
        yaxis={'showline': False, 'zeroline':False, 'ticks':'','color':'#959a99'},
        )
    }

######Row #7
######Gr_PercPop_deaths#####
@app.callback(
    Output('Gr_PercPop_deaths', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value'),
     Input('country_picker', 'value')])
def Gr_PercPop_deaths(start_date, end_date, cont, country):
    #To avoid an error due to some countries having data only since March, 2020.
    if start_date =='2020-01-01':
        start_date='2020-03-01'

    _, _, countries_deaths, _, cont_country = data_country(start_date, end_date, cont, country)
    dfc=data_country_PercPop(start_date, end_date, cont)
    colors=list(px.colors.sequential.Blues)[1:]
    dfc_deaths=dfc[dfc['countriesAndTerritories'].isin(countries_deaths)]
    index=dfc_deaths[dfc_deaths['countriesAndTerritories']==countries_deaths[0]].index
    y = {}
    for num, name in enumerate(countries_deaths):
        y[num] = list(dfc_deaths['perc_deaths'][dfc_deaths['countriesAndTerritories']==name])
    if cont == 'Oceania' or country == None or cont == None:
        chart={
            'data':[
                    go.Scatter(x=index, y=y[2],mode='lines',name=countries_deaths[2],line=dict(color=colors[7],width=9)),
                    go.Scatter(x=index, y=y[1],mode='lines',name=countries_deaths[1],line=dict(color=colors[5],width=7)),
                    go.Scatter(x=index, y=y[0],mode='lines',name=countries_deaths[0],line=dict(color=colors[3],width=5)),
            ],
            'layout':go.Layout(
            template="simple_white",height=400,
            title ={'text': '<b>Deaths1</b> per country per month due to Covid-19 in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
            yaxis={'title':'% of <b>Deaths</b> by population','showline': False, 'zeroline':False,'color':'#959a99'},
            xaxis={'title':'Month', 'showgrid': False,'color':'#959a99', 'linecolor':'#959a99'},
            )
        }
    else:
        if cont == "All" or cont_country == cont:
            chart={
                'data':[
                        go.Scatter(x=index, y=y[3],mode='lines',name=countries_deaths[3],line=dict(color=colors[7],width=9)),
                        go.Scatter(x=index, y=y[2],mode='lines',name=countries_deaths[2],line=dict(color=colors[5],width=7)),
                        go.Scatter(x=index, y=y[1],mode='lines',name=countries_deaths[1],line=dict(color=colors[3],width=5)),
                        go.Scatter(x=index, y=y[0],mode='lines',name=countries_deaths[0],line=dict(color='#c94f5f',width=3,dash='dot')),
                ],
                'layout':go.Layout(
                template="simple_white",height=400,
                title ={'text': '<b>Deaths</b> per country per month due to Covid-19 in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
                yaxis={'title':'% of <b>Deaths</b> by population','showline': False, 'zeroline':False,'color':'#959a99'},
                xaxis={'title':'Month', 'showgrid': False,'color':'#959a99', 'linecolor':'#959a99'},
                )
            }
        else:
            chart={
                'data':[
                        go.Scatter(x=index, y=y[3],mode='lines',name=countries_deaths[3],line=dict(color=colors[7],width=9)),
                        go.Scatter(x=index, y=y[2],mode='lines',name=countries_deaths[2],line=dict(color=colors[5],width=7)),
                        go.Scatter(x=index, y=y[1],mode='lines',name=countries_deaths[1],line=dict(color=colors[3],width=5)),
                ],
                'layout':go.Layout(
                template="simple_white",height=400,
                title ={'text': '<b>Deaths3</b> per country per month due to Covid-19 in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
                yaxis={'title':'% of <b>Deaths3</b> by population','showline': False, 'zeroline':False,'color':'#959a99'},
                xaxis={'title':'Month', 'showgrid': False,'color':'#959a99', 'linecolor':'#959a99'},
                )
            }
    return chart

######Row #8
######Gr_PercPop_cases#####
@app.callback(
    Output('Gr_PercPop_cases', 'figure'),
    [Input('DatePickerRange', 'start_date'),
     Input('DatePickerRange', 'end_date'),
     Input('RadioItems_Cont', 'value'),
     Input('country_picker', 'value')])
def Gr_PercPop_cases(start_date, end_date, cont, country):
    #To avoid an error due to some countries having data only since March, 2020.
    if start_date =='2020-01-01':
        start_date='2020-03-01'

    _, _, countries_deaths, countries_cases, cont_country = data_country(start_date, end_date, cont, country)
    dfc=data_country_PercPop(start_date, end_date, cont)
    colors=list(px.colors.sequential.Blues)[1:]
    dfc_cases=dfc[dfc['countriesAndTerritories'].isin(countries_cases)]
    index=dfc_cases[dfc_cases['countriesAndTerritories']==countries_cases[0]].index
    y = {}
    for num, name in enumerate(countries_cases):
        y[num] = list(dfc_cases['perc_cases'][dfc_cases['countriesAndTerritories']==name])
    if cont == 'Oceania' or country == None or cont == None:
        chart={
            'data':[
                    go.Scatter(x=index, y=y[2],mode='lines',name=countries_cases[2],line=dict(color=colors[7],width=9)),
                    go.Scatter(x=index, y=y[1],mode='lines',name=countries_cases[1],line=dict(color=colors[5],width=7)),
                    go.Scatter(x=index, y=y[0],mode='lines',name=countries_cases[0],line=dict(color=colors[3],width=5)),
            ],
            'layout':go.Layout(
            template="simple_white",height=400,
            title ={'text': 'Covid-19 <b>Cases</b> per country per month in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
            yaxis={'title':'% of <b>Cases</b> by population','showline': False, 'zeroline':False,'color':'#959a99'},
            xaxis={'title':'Month', 'showgrid': False,'color':'#959a99', 'linecolor':'#959a99'},
            )
        }
    else:
        if cont == "All" or cont_country == cont:
            chart={
                'data':[
                        go.Scatter(x=index, y=y[3],mode='lines',name=countries_cases[3],line=dict(color=colors[7],width=9)),
                        go.Scatter(x=index, y=y[2],mode='lines',name=countries_cases[2],line=dict(color=colors[5],width=7)),
                        go.Scatter(x=index, y=y[1],mode='lines',name=countries_cases[1],line=dict(color=colors[3],width=5)),
                        go.Scatter(x=index, y=y[0],mode='lines',name=countries_cases[0],line=dict(color='#c94f5f',width=3,dash='dot')),
                ],
                'layout':go.Layout(
                template="simple_white",height=400,
                title ={'text': 'Covid-19 <b>Cases</b> per country per month in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
                yaxis={'title':'% of <b>Cases</b> by population','showline': False, 'zeroline':False,'color':'#959a99'},
                xaxis={'title':'Month', 'showgrid': False,'color':'#959a99', 'linecolor':'#959a99'},
                )
            }
        else:
            chart={
                'data':[
                        go.Scatter(x=index, y=y[3],mode='lines',name=countries_cases[3],line=dict(color=colors[7],width=9)),
                        go.Scatter(x=index, y=y[2],mode='lines',name=countries_cases[2],line=dict(color=colors[5],width=7)),
                        go.Scatter(x=index, y=y[1],mode='lines',name=countries_cases[1],line=dict(color=colors[3],width=5)),
                ],
                'layout':go.Layout(
                template="simple_white",height=400,
                title ={'text': 'Covid-19 <b>Cases</b> per country per month in Continent: <b>{}</b>'.format(cont), 'xanchor':'left', 'x':0,'xref':'paper', 'font_color':'#959a99'},
                yaxis={'title':'% of <b>Cases</b> by population','showline': False, 'zeroline':False,'color':'#959a99'},
                xaxis={'title':'Month', 'showgrid': False,'color':'#959a99', 'linecolor':'#959a99'},

                )
            }

    return chart

# Add the server clause:
if __name__ == '__main__':
    app.run_server(debug=True)
