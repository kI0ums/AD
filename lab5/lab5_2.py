import numpy as np
import plotly.graph_objs as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

amplitude_init = 1.0
frequency_init = 0.5
phase_init = 0.0
noise_mean_init = 0.0
noise_covariance_init = 0.2
window_size_init = 50

t = np.linspace(0, 10, 1000)

initial_noise = np.random.normal(noise_mean_init, noise_covariance_init, len(t))


def harmonic(t, amplitude, frequency, phase):
    harmonic = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    return harmonic


# Медіанний фільтр
def apply_median_filter(signal, window_size):
  filtered_signal = []
  for i in range(len(signal)):
    start = max(0, i - window_size // 2)
    end = min(len(signal), i + window_size // 2 + 1)
    window_sum = sum(signal[start:end])
    window_average = window_sum / (end - start)
    filtered_signal.append(window_average)
  return filtered_signal


signal = harmonic(t, amplitude_init, frequency_init, phase_init)
filtered_signal = apply_median_filter(signal + initial_noise, window_size_init)

# Dash App
app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='main-graph'),
    html.Div([
        dcc.Dropdown(
            id='signal-dropdown',
            options=[
                {'label': 'Clean Signal', 'value': 'clean_signal'},
                {'label': 'Signal with Noise', 'value': 'signal_with_noise'},
                {'label': 'Filtered Signal', 'value': 'filtered_signal'}
            ],
            value='clean_signal'
        )
    ]),
    dcc.Graph(id='secondary-graph'),
    html.Div([
        html.Label('Amplitude'),
        dcc.Slider(id='amplitude', min=0.1, max=2.0, step=0.1, value=amplitude_init),
        html.Label('Frequency'),
        dcc.Slider(id='frequency', min=0.0, max=2.0, step=0.1, value=frequency_init),
        html.Label('Phase'),
        dcc.Slider(id='phase', min=-2 * 3.14, max=2 * 3.14, step=0.2, value=phase_init),
        html.Label('Noise Mean'),
        dcc.Slider(id='noise_mean', min=-0.5, max=0.5, step=0.05, value=noise_mean_init),
        html.Label('Noise Covariance'),
        dcc.Slider(id='noise_covariance', min=0.0, max=1, step=0.05, value=noise_covariance_init),
        html.Label('Window Size'),
        dcc.Slider(id='window_size', min=1, max=100, step=1, value=window_size_init),
        html.Label('Show Noise'),
        dcc.Checklist(id='show_noise', options=[{'label': 'Show Noise', 'value': 'show'}], value=['show'])
    ])
])


@app.callback(
    [Output('main-graph', 'figure'),
     Output('secondary-graph', 'figure')],
    [Input('amplitude', 'value'),
     Input('frequency', 'value'),
     Input('phase', 'value'),
     Input('noise_mean', 'value'),
     Input('noise_covariance', 'value'),
     Input('window_size', 'value'),
     Input('show_noise', 'value'),
     Input('signal-dropdown', 'value')]
)
def update_graph(amplitude, frequency, phase, noise_mean, noise_covariance, window_size, show_noise, selected_signal):
    global initial_noise, noise_mean_init, noise_covariance_init

    if noise_mean != noise_mean_init or noise_covariance != noise_covariance_init:
        initial_noise = np.random.normal(noise_mean, noise_covariance, len(t))
        noise_mean_init = noise_mean
        noise_covariance_init = noise_covariance

    signal = harmonic(t, amplitude, frequency, phase)
    filtered_signal = apply_median_filter(signal + initial_noise, window_size)

    main_fig = go.Figure()
    secondary_fig = go.Figure()

    main_fig.add_trace(go.Scatter(x=t, y=signal, mode='lines', name='Clean Signal', line=dict(color='blue')))
    if 'show' in show_noise:
        main_fig.add_trace(go.Scatter(x=t, y=signal + initial_noise, mode='lines', name='Signal with Noise', line=dict(color='orange')))
    main_fig.add_trace(go.Scatter(x=t, y=filtered_signal, mode='lines', name='Filtered Signal', line=dict(color='green')))

    if selected_signal == 'clean_signal':
        secondary_fig.add_trace(go.Scatter(x=t, y=signal, mode='lines', name=selected_signal, line=dict(color='blue')))
    elif selected_signal == 'signal_with_noise':
        secondary_fig.add_trace(go.Scatter(x=t, y=signal + initial_noise, mode='lines', name=selected_signal, line=dict(color='orange')))
    elif selected_signal == 'filtered_signal':
        secondary_fig.add_trace(go.Scatter(x=t, y=filtered_signal, mode='lines', name=selected_signal, line=dict(color='green')))

    main_fig.update_layout(
        height=400,
        title_text='Main Graph',
        xaxis=dict(range=[0, 10]),
        yaxis=dict(range=[-3, 3])
    )

    secondary_fig.update_layout(
        height=400,
        title_text='Secondary Graph',
        xaxis=dict(range=[0, 10]),
        yaxis=dict(range=[-3, 3])
    )

    return main_fig, secondary_fig


if __name__ == '__main__':
    app.run_server(debug=True)
