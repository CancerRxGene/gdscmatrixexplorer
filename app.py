import dash
from clickable_plots_register import cpr

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

