import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import sqlite3
from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
import configurations as conf






external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"



# Dictionary of important locations in New York
loc_df = pd.read_csv(conf.existing_locations_csv)
list_of_locations = {value: {"lat": loc_df['Y'][index], "lon": loc_df['X'][index]}
                     for index, value in enumerate(loc_df['zone'])}
locations_dict = {loc_df['zone'][index]: loc_df['LocationID'][index] for index, _ in enumerate(loc_df['zone'])}
df = pd.read_csv(
    "yellow_tripdata_2017-04.csv",
    dtype=object,
)
# Remove Columns not used in the dataframe to improve performance
for column in conf.unused_columns:
    df.drop(column, axis=1, inplace=True)

df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"], format="%Y-%m-%d %H:%M:%S")
df.index = df["tpep_dropoff_datetime"]
date_series = df["tpep_dropoff_datetime"].dt.date
df.drop("tpep_dropoff_datetime", 1, inplace=True)


min_date = date_series.min()
max_date = date_series.max()
totalList = []
for month in df.groupby(df.index.month):
    dailyList = []
    for day in month[1].groupby(month[1].index.day):
        dailyList.append(day[1])
    totalList.append(dailyList)
totalList = np.array(totalList)

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.H2("Data Visualization Project"),
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[



                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(min_date.year, min_date.month, min_date.day),
                                    max_date_allowed=dt(2017, 4, 7),

                                    initial_visible_month=dt(min_date.year, min_date.month, min_date.day),
                                    date=dt(min_date.year, min_date.month, min_date.day).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="location-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_locations
                                            ],
                                            placeholder="Select a location",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="bar-selector",
                                            options=[
                                                {
                                                    "label": str(n) + ":00",
                                                    "value": str(n),
                                                }
                                                for n in range(24)
                                            ],
                                            multi=True,
                                            placeholder="Select certain hours",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.P(id="total-rides"),
                        html.P(id="total-rides-selection"),
                        html.P(id="date-value"),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph"),
                        html.H1("Passenger / time "),
                        dcc.Graph(id="line-chart"),
                        html.H1("Total amount / time"),
                        dcc.Graph(id="histogram"),

                    ],
                ),
            ],
        )
    ]
)

# Get the amount of rides per hour based on the time selected
# This also higlights the color of the histogram bars based on
# if the hours are selected


def get_selection(datePicked, selection, location):
    xVal = []
    yVal = []
    xSelected = []
    colorVal = [
        "#F4EC15",
        "#DAF017",
        "#BBEC19",
        "#9DE81B",
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#34D822",
        "#24D249",
        "#25D042",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2AC093",
        "#2BBCA4",
        "#2BB5B8",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4",
        "#3B2FA0",
        "#4E2F9C",
        "#603099",
    ]

    # Put selected times into a list of numbers xSelected
    xSelected.extend([int(x) for x in selection])

    for i in range(24):
        # If bar is selected then color it white
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#FFFFFF"
        xVal.append(i)
        # Get the number of rides at a particular time
    yVal = subset_hist_data(datePicked, location)
    return [np.array(xVal), np.array(yVal), np.array(colorVal)]



def get_selection2(datePicked, selection, location):
    xVal = []
    yVal = []
    xSelected = []
    colorVal = [
        "#F4EC15",
        "#DAF017",
        "#BBEC19",
        "#9DE81B",
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#34D822",
        "#24D249",
        "#25D042",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2AC093",
        "#2BBCA4",
        "#2BB5B8",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4",
        "#3B2FA0",
        "#4E2F9C",
        "#603099",
    ]

    # Put selected times into a list of numbers xSelected
    xSelected.extend([int(x) for x in selection])

    for i in range(24):
        # If bar is selected then color it white
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#FFFFFF"
        xVal.append(i)
        # Get the number of rides at a particular time
    yVal = subset_hist_data2(datePicked, location)
    return [np.array(xVal), np.array(yVal), np.array(colorVal)]


# Selected Data in the Histogram updates the Values in the DatePicker
@app.callback(
    Output("bar-selector", "value"),
    [Input("histogram", "selectedData"), Input("histogram", "clickData")],
)
def update_bar_selector(value, clickData):
    holder = []
    if clickData:
        holder.append(str(int(clickData["points"][0]["x"])))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])))
    return list(set(holder))


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    if clickData:
        return {"points": []}


# Update the total number of rides Tag
@app.callback(Output("total-rides", "children"), [Input("date-picker", "date")])
def update_total_rides(datePicked):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    return "Total Number of rides: {:,d}".format(
        len(totalList[date_picked.month - 4][date_picked.day - 1])
    )


# Update the total number of rides in selected times
@app.callback(
    [Output("total-rides-selection", "children"), Output("date-value", "children")],
    [Input("date-picker", "date"), Input("bar-selector", "value")],
)
def update_total_rides_selection(datePicked, selection):
    firstOutput = ""

    if selection is not None or len(selection) is not 0:
        date_picked = dt.strptime(datePicked, "%Y-%m-%d")
        totalInSelection = 0
        for x in selection:
            totalInSelection += len(
                totalList[date_picked.month - 4][date_picked.day - 1][
                    totalList[date_picked.month - 4][date_picked.day - 1].index.hour
                    == int(x)
                ]
            )
        firstOutput = "Total rides in selection: {:,d}".format(totalInSelection)

    if (
        datePicked is None
        or selection is None
        or len(selection) is 24
        or len(selection) is 0
    ):
        return firstOutput, (datePicked, " - showing hour(s): All")

    holder = sorted([int(x) for x in selection])

    if holder == list(range(min(holder), max(holder) + 1)):
        return (
            firstOutput,
            (
                datePicked,
                " - showing hour(s): ",
                holder[0],
                "-",
                holder[len(holder) - 1],
            ),
        )

    holder_to_string = ", ".join(str(x) for x in holder)
    return firstOutput, (datePicked, " - showing hour(s): ", holder_to_string)


# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [Input("date-picker", "date"), Input("bar-selector", "value"), Input("location-dropdown", "value")],
)
def update_histogram(datePicked, selection, location):

    [xVal, yVal, colorVal] = get_selection(datePicked, selection, location)

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="white"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal / 2,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,

            ),
        ],
        layout=layout,
    )



# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("bar-selector", "value"),
        Input("location-dropdown", "value"),
    ],
)
def update_graph(datePicked, selectedData, selectedLocation):
    zoom = 8.0
    latInitial = 40.7272
    lonInitial = -73.991251
    bearing = 0

    if selectedLocation:
        zoom = 15.0
        latInitial = list_of_locations[selectedLocation]["lat"]
        lonInitial = list_of_locations[selectedLocation]["lon"]

    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 4
    dayPicked = date_picked.day - 1

    return go.Figure(
        data=[
            # Data for all rides based on date and time
            # Plot of important locations on the map
            Scattermapbox(
                lat=[list_of_locations[i]["lat"] for i in list_of_locations],
                lon=[list_of_locations[i]["lon"] for i in list_of_locations],
                mode="markers",
                hoverinfo="text",
                text=[i for i in list_of_locations],
                marker=dict(size=8, color="#00ff00"),
            ),
        ],
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
                style="dark",
                bearing=bearing,
                zoom=zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 8,
                                        "mapbox.center.lon": "-73.991251",
                                        "mapbox.center.lat": "40.7272",
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )


def subset_hist_data(datePicked, location):

    # DB SQLite Connection
    conn = sqlite3.connect('TlcDB.db')
    cursor = conn.cursor()
    output_list = list()
    for i in range(24):
        query = conf.standard_query
        adjusted_hour = str(i) if int(i) > 9 else "0{0}".format(i)
        query += "tpep_dropoff_datetime LIKE '%{0} {1}:%'".format(datePicked, adjusted_hour)
        if location:
            query += " AND DOLocationID = {0} ".format(str(locations_dict[location]))
        cursor.execute(query)
        count = int(cursor.fetchone()[0])
        output_list.append(count)
    return output_list


def subset_hist_data2(datePicked, location):

    # DB SQLite Connection
    conn = sqlite3.connect('TlcDB.db')
    cursor = conn.cursor()
    output_list = list()
    for i in range(24):
        query = "SELECT COUNT(*) FROM 'yellow_tripdata_2017-04' WHERE  "
        adjusted_hour = str(i) if int(i) > 9 else "0{0}".format(i)
        query += "tpep_dropoff_datetime LIKE '%{0} {1}:%'".format(datePicked, adjusted_hour)
        if location:
            query += " AND DOLocationID = {0} ".format(str(locations_dict[location]))
        cursor.execute(query)
        count = int(cursor.fetchone()[0])
        output_list.append(count)
    return output_list






@app.callback(
    Output("line-chart", "figure"),
    [Input("date-picker", "date"), Input("bar-selector", "value"), Input("location-dropdown", "value")],
)
def update_histogram(datePicked, selection, location):

    [xVal, yVal, colorVal] = get_selection2(datePicked, selection, location)

    layout = go.Layout(
        #bargap=0.01,
        #bargroupgap=0,
        #barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text="",
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="white"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            #go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
            go.Scatter(

                x=xVal,
                y=yVal,

                mode="lines",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="octagon", size=40),
                visible=True,

            ),
        ],
        layout=layout,
    )



if __name__ == "__main__":
    app.run_server(debug=True)