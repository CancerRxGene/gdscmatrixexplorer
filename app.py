import dash

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally=True
app.title = "GDSC²"

