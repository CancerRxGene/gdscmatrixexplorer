import dash_core_components as dcc


class ClickablePlotsRegister:

    def __init__(self):
        self._register = set()

    def register_plot(self, plot_id):
        self._register.add(plot_id)

    def generate_plots(self, display=None, generate_others=True):
        result = []
        if display is None:
            display = set()
        if isinstance(display, str):
            display = set([display])
        else:
            display = set(display)

        for plot_id in self._register:
            if plot_id in display:
                result.append(dcc.Graph(id=plot_id))
            elif generate_others:
                result.append(dcc.Graph(id=plot_id, style={'display':'none'}))
        return result

    def plot_ids(self):
        return self._register


cpr = ClickablePlotsRegister()