import dash
import flask
import os

from dynamic_downloads import generate_download_file

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally=True
app.title = "GDSC²"

STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')


@server.route('/downloads/<resource>')
def serve_static(resource):
    return flask.send_from_directory(STATIC_PATH, resource)


@server.route('/downloads/<project_slug>/<data_type>')
def dynamic_download(project_slug, data_type):
    file_name = f"{project_slug}_{data_type}.csv.gz"
    file_path = STATIC_PATH + "/" + file_name

    if not os.path.isfile(file_path):
        generate_download_file(project_slug, data_type)

    response = flask.make_response(
        flask.send_from_directory(STATIC_PATH, file_name, as_attachment=True)
    )
    response.headers['cache-control'] = 'no-store'
    return response
