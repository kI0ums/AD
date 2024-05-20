import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt

amplitude_init = 1.0
frequency_init = 0.5
phase_init = 0.0
noise_mean_init = 0.0
noise_covariance_init = 0.2
cutoff_frequency_init = 2.0

last_noise_mean = noise_mean_init
last_noise_covariance = noise_covariance_init

t = np.linspace(0, 10, 1000)

noise_data = np.random.normal(noise_mean_init, noise_covariance_init, len(t))


def harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    global noise_data, last_noise_mean, last_noise_covariance

    if noise_mean != last_noise_mean or noise_covariance != last_noise_covariance:
        noise_data = np.random.normal(noise_mean, noise_covariance, size=len(t))
        last_noise_mean = noise_mean
        last_noise_covariance = noise_covariance

    harmonic = amplitude * np.sin(2 * np.pi * frequency * t + phase)

    if show_noise:
        return harmonic, harmonic + noise_data
    else:
        return harmonic, harmonic


def apply_lowpass_filter(signal, cutoff_frequency, fs):
    nyquist = 0.5 * fs
    normalized_cutoff_frequency = cutoff_frequency / nyquist
    b, a = butter(4, normalized_cutoff_frequency, btype='low')
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal


fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(0, 10)
ax.set_ylim(-3, 3)
plt.subplots_adjust(left=0.25, bottom=0.4)

harmonic, noise = harmonic_with_noise(t, amplitude_init, frequency_init, phase_init, noise_mean_init,
                                      noise_covariance_init, True)
filtered_signal = apply_lowpass_filter(noise, cutoff_frequency_init, fs=len(t)/(t[-1]-t[0]))

line_clean, = ax.plot(t, harmonic, label='Clean Harmonic', alpha=1, linewidth=2, zorder=4, linestyle='--')
line_noise, = ax.plot(t, noise, label='Harmonic with Noise', alpha=1, linewidth=2, zorder=2)
line_filtered, = ax.plot(t, filtered_signal, label='Filtered Signal', alpha=1, linewidth=2, zorder=3)

ax.legend(loc='upper right')

axcolor = 'lightgoldenrodyellow'
ax_amplitude = plt.axes([0.25, 0.3, 0.65, 0.03], facecolor=axcolor)
ax_frequency = plt.axes([0.25, 0.25, 0.65, 0.03], facecolor=axcolor)
ax_phase = plt.axes([0.25, 0.2, 0.65, 0.03], facecolor=axcolor)
ax_noise_mean = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
ax_noise_covariance = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
ax_cutoff_frequency = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)

s_amplitude = Slider(ax_amplitude, 'Amplitude', 0.1, 2.0, valinit=amplitude_init)
s_frequency = Slider(ax_frequency, 'Frequency', 0.0, 2.0, valinit=frequency_init)
s_phase = Slider(ax_phase, 'Phase', -2 * np.pi, 2 * np.pi, valinit=phase_init)
s_noise_mean = Slider(ax_noise_mean, 'Noise Mean', -0.5, 0.5, valinit=noise_mean_init)
s_noise_covariance = Slider(ax_noise_covariance, 'Noise Covariance', 0.0, 0.6, valinit=noise_covariance_init)
s_cutoff_frequency = Slider(ax_cutoff_frequency, 'Cutoff Frequency', 0.1, 5.0, valinit=cutoff_frequency_init)

rax = plt.axes([0.025, 0.5, 0.15, 0.15], facecolor=axcolor)
check = CheckButtons(rax, ['Show Noise'], [True])


def update(val):
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val
    noise_mean = s_noise_mean.val
    noise_covariance = s_noise_covariance.val
    cutoff_frequency = s_cutoff_frequency.val
    show_noise = check.get_status()[0]

    harmonic, noise = harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise)
    filtered_signal = apply_lowpass_filter(harmonic + noise_data, cutoff_frequency, fs=len(t) / (t[-1] - t[0]))

    line_clean.set_ydata(harmonic)
    line_noise.set_ydata(noise)
    line_filtered.set_ydata(filtered_signal)

    fig.canvas.draw_idle()


s_amplitude.on_changed(update)
s_frequency.on_changed(update)
s_phase.on_changed(update)
s_noise_mean.on_changed(update)
s_noise_covariance.on_changed(update)
s_cutoff_frequency.on_changed(update)
check.on_clicked(update)

resetax = plt.axes([0.8, 0.005, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')


def reset(event):
    s_amplitude.reset()
    s_frequency.reset()
    s_phase.reset()
    s_noise_mean.reset()
    s_noise_covariance.reset()
    s_cutoff_frequency.reset()


button.on_clicked(reset)

plt.show()
