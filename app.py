import dash

external_stylesheets = ["https://stackpath.bootstrapcdn.com/bootswatch/4.1.3/simplex/bootstrap.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True
