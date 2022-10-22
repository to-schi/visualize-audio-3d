import base64
from urllib import request

import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from matplotlib import mlab
from pydub import AudioSegment

UPLOADED = "uploads/uploaded."
ASSETS = "assets/another."

app = Dash(
    __name__,
    # external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
)
server = app.server
app.title = "Visualize Audio in 3D"


def load_audio(filepath):
    """
    Load a local file and return data as file uri.
    """
    encoded_audio = base64.b64encode(open(filepath, "rb").read())
    src = "data:audio/mpeg;base64,{}".format(encoded_audio.decode())
    return src


def save_file(contents):
    """
    Read data from file uri and save as file.
    """
    filetype = check_filetype(contents)
    with request.urlopen(contents) as response:
        data = response.read()
    with open(UPLOADED + filetype, "wb") as f:
        f.write(data)


def check_filetype(contents):
    """
    get filetype from contents string (e.g. "data:audio/mpeg;base64,...")
    """
    filetype = contents.split(";")[0].split("/")[-1]
    if filetype == "mpeg":
        filetype = "mp3"
    return filetype


def plot_audio_3d(filepath, color_scheme="Jet", nfft=256):
    audioseg = AudioSegment.from_file(filepath)
    sr = audioseg.frame_rate
    audioseg = audioseg.set_channels(1)
    audiodata = audioseg.get_array_of_samples()

    spectrum, freqs, t = mlab.specgram(audiodata, Fs=sr, NFFT=nfft)

    ref = np.median(spectrum)
    z = spectrum / ref
    z = 10 * np.log10(z)  # , where=z != 0)

    fig = go.Figure(
        data=[go.Surface(x=t, y=freqs, z=z, colorscale=color_scheme, showscale=False)]
    )
    fig.update_layout(
        title=None,
        autosize=True,
        width=900,
        height=500,
        margin=dict(l=8, r=2, b=2, t=2),  # autoexpand=True
        showlegend=False,
        # paper_bgcolor="rgba(30,15,5,100)",
        # plot_bgcolor="rgba(55,25,5,100)",
        # bgcolor="rgba(100,255,0,0)",
        template="plotly_dark",
        scene=dict(
            xaxis=dict(autorange="reversed", showline=True, showgrid=True),
            yaxis=dict(showline=True, showgrid=True),
            zaxis=dict(
                visible=True, showticklabels=True, showline=True, showgrid=True,
            ),
            xaxis_title="time (s)",
            yaxis_title="frequency (Hz)",
            zaxis_title="amplitude (db)",
            aspectmode="manual",
            aspectratio=dict(x=1.5, y=1, z=1),
        ),
    )
    return fig


width = "900px"


app.layout = html.Div(
    [
        # header
        html.Div(
            [
                html.Div(
                    [
                        html.H4(
                            "Visualize Audio Data in 3D", className="app__header__title"
                        ),
                        html.A(
                            "(source code)",
                            className="app__header__title--grey",
                            href="https://github.com/to-schi",
                        ),
                    ],
                    className="app__header__desc",
                ),
            ],
            className="app__header",
        ),
        # body
        dcc.Graph(
            id="audio_graph",
            style={"width": width, "margin": "0px"},  # , "display": "inline-block"},
        ),
        html.Audio(
            id="audio_player",
            src="",
            controls=True,
            autoPlay=False,
            style={"width": width, "margin": "10px",},
        ),
        dcc.Upload(
            id="upload_audio",
            children=html.Div(["Drag and Drop ", html.A("wav or mp3")]),
            style={
                # "display": "inline-block",
                "width": width,
                "height": "40px",
                "lineHeight": "45px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=False,
        ),
    ],
    style={"width": "100%", "height": "640"},  # , "display": "inline-block"},  #
)


@app.callback(
    Output("audio_graph", component_property="figure"),
    Output("audio_player", component_property="src"),
    Output("audio_player", component_property="autoPlay"),
    Input("upload_audio", component_property="contents"),
    # Input("audio_graph", component_property="clickData")
)
def update_chart(contents):  # , clickData):
    filetype = "mp3"
    plot_src = ASSETS + filetype
    src = ASSETS + filetype
    autoplay = False

    if contents:
        save_file(contents)
        filetype = check_filetype(contents)
        plot_src = UPLOADED + filetype
        src = load_audio(UPLOADED + filetype)
        autoplay = True

    # if clickData:
    #     logging.critical(clickData["points"][0]["x"])
    #     X = clickData["points"][0]["x"]
    #     skipto = max(0, X - 0.5)
    #     # give uri timerange:
    #     src = f"{UPLOADED+filetype}"  ##t={skipto},{skipto+1}"
    #     autoplay = True

    return (
        plot_audio_3d(plot_src, color_scheme="Jet", nfft=256),
        src,
        autoplay,
    )


if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_hot_reload=False)

