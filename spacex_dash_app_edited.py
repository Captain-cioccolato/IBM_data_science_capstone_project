# Create an app layout
import pandas as pd
import dash
import dash.html as html
import dash.dcc as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create unique launch site
uniquelaunchsite = spacex_df['Launch Site'].unique().tolist()

# Create dropdown options
dropdownoptions = [{'label': 'All', 'value': 'All'}]
dropdownoptions += [{'label': site, 'value': site} for site in uniquelaunchsite] # more concise 

# Group by launch site for successful launches
groupby_launchsite = spacex_df[spacex_df['class'] == 1].groupby(by='Launch Site').size().reset_index(name='counts')

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    html.Br(),
    html.Label("Launch Site Selection:"),
    dcc.Dropdown(
        id='site-dropdown', # assign id
        options=dropdownoptions,
        value='All',
        placeholder='Select a launch site'
    ),
    html.Br(),
    html.Div(id='success-pie-chart'),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        min=min_payload, 
        max=max_payload, 
        step=1, 
        value=[min_payload, max_payload], 
        id='payload-slider'
    ),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')) # assign id
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='children'), 
    Input(component_id='site-dropdown', component_property='value')
)
def success_chart_display(input_launch_site):
    if input_launch_site == 'All':
        fig = px.pie(groupby_launchsite, values='counts', names='Launch Site', title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == input_launch_site]
        success_fail = filtered_df['class'].value_counts().reset_index()
        success_fail.columns = ['class', 'counts']
        fig = px.pie(success_fail, values='counts', names='class', title=f'Success vs. Failure for site {input_launch_site}')
    return dcc.Graph(figure=fig)

# Callback for scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def success_payload_scatter(input_launch_site, input_payload):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= input_payload[0]) &
                            (spacex_df['Payload Mass (kg)'] <= input_payload[1])]
    
    if input_launch_site != 'All':
        filtered_df = filtered_df[filtered_df['Launch Site'] == input_launch_site]

    fig2 = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category',
        title='Payload vs. Success'
    )
    return fig2

# Run the app
if __name__ == '__main__':
    app.run_server()
