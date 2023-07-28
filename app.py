import yfinance as yf
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
from IPython.display import display
import base64
import io
from csvbox_importer_for_dash import CsvboxImporterForDash
import datetime


# Create Dash app
external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
server = app.server

# Define the layout
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Stock Analysis', value='tab-1', children=[
            html.H1("Stock Ticker Analysis", className="title"),
            html.Div([
                html.Label("Enter a stock ticker symbol:", className="input-label"),
                dcc.Input(
                    id="input-ticker",
                    type="text",
                    value="AAPL",  # Default ticker symbol
                    className="input-field"
                ),
            ], className="input-container"),
            html.Div([
                html.Label("Enter time series period:", className="input-label"),
                dcc.Dropdown(
                    id="input-number",
                    options=[
                        {'label': i, 'value': i} for i in range(1, 11)
                    ],
                    value=1,  # Default value
                    className="input-dropdown"
                ),
                dcc.Dropdown(
                    id="input-period",
                    options=[
                        {'label': 'Day(s)', 'value': 'd'},
                        {'label': 'Month(s)', 'value': 'mo'},
                        {'label': 'Year(s)', 'value': 'y'}
                    ],
                    value='y',  # Default value
                    className="input-dropdown"
                ),
            ], className="input-container"),
            html.Button("Submit", id="submit-button", className="submit-button"),
            dcc.Graph(id="price-graph", className="price-graph"),
            html.H3("Descriptive Statistics", className="statistics-title"),
            html.Div(id="statistics-output", className="statistics-output"),
            html.Button("Download statistics", className="submit-button"),
            dcc.Download(id="download-dataframe-csv"),
        ]),
        dcc.Tab(label='CSV Importer', value='tab-2', children=[
            dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.Div(id='output-data-upload'),
        ]),
        dcc.Tab(
        label='csvbox-importer2', 
        value='tab-3', 
        children=[
            CsvboxImporterForDash(
                id='my-csvbox-importer',
                licenseKey="VUSagg1Y5Jz4POcqNvIbC5B2gkbkfk",
                userId='default123'
            ),

        ]
    ),
    ])
], className="app-container")


# Define callback for updating the graph and statistics
@app.callback(
    [Output("price-graph", "figure"), Output("statistics-output", "children")],
    [Input("submit-button", "n_clicks")],
    [dash.dependencies.State("input-ticker", "value"),
     dash.dependencies.State("input-number", "value"),
     dash.dependencies.State("input-period", "value")]
)
def update_output(n_clicks, ticker, number, period):
    if ticker:
        # Concatenate the number and period to form the time series period string
        period = str(number) + period
        # Retrieve stock data from Yahoo Finance
        data = yf.download(ticker, period=period, progress=False)
        data.reset_index(inplace=True)
        # Create the price graph
        fig = {
            "data": [
                {"x": data['Date'], "y": data["Close"], "type": "line", "name": ticker}
            ],
            "layout": {
                "title": f"{ticker} Price Time Series"
            }
        }
        # Calculate descriptive statistics and round to 2 decimal places
        statistics = data.describe().transpose().reset_index()
        statistics = statistics.round(2)
        # Create the statistics table
        statistics_table = dash_table.DataTable(
            data=statistics.to_dict("records"),
            columns=[{"name": c, "id": c} for c in statistics.columns],
            style_as_list_view=True,
            style_cell={"padding": "5px"},
            style_header={"fontWeight": "bold"}
        )
        return fig, statistics_table
    else:
        return {}, ""

@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("btn_csv", "n_clicks")],
    [dash.dependencies.State("input-ticker", "value"),
     dash.dependencies.State("input-number", "value"),
     dash.dependencies.State("input-period", "value")]
)
def download_csv(n_clicks, ticker, number, period):
    if ticker:
        # Set the period based on number and period inputs
        period = str(number) + period
        # Retrieve stock data from Yahoo Finance
        data = yf.download(ticker, period=period, progress=False)
        data.reset_index(inplace=True)
        # Calculate descriptive statistics and round to 2 decimal places
        statistics = data.describe().transpose().reset_index()
        statistics = statistics.round(2)
        return dcc.send_data_frame(statistics.to_csv, "my_data.csv")
    return {}

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              dash.dependencies.State('upload-data', 'filename'),
              dash.dependencies.State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


# Run the app
if __name__ == "__main__":
    app.run_server()