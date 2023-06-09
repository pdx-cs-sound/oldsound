import sounddevice, sys
import numpy as np
from scipy import io, signal

sample_rate = 44100

(sample_rate, track) = io.wavfile.read(sys.argv[1])
track = track.astype(np.float64) / 32768.0

# Antialiasing filter
filter = signal.iirfilter(
    8,
    1000,
    btype='lowpass',
    fs=sample_rate,
)
track = signal.lfilter(filter[0], filter[1], track)

# Oversampling
acc = []
pwm_table = [
    [-1, -1, -1, -1],
    [-1, 1, -1, -1],
    [-1, -1, 1, -1],
    [-1, 1, -1, 1],
    [1, -1, 1, -1],
    [1, 1, -1, 1],
    [1, -1, 1, 1],
    [1, 1, 1, 1],
]
for i in range(0, len(track) - 4, 4):
    block = track[i:i+4]
    val = int(np.floor(3 * np.sum(block) + 0.5))
    acc += pwm_table[np.clip(val, 0, 7)]
track = np.array(acc)

# "Square off" track
track = np.sign(track)

# Reconstruction filter
filter = signal.iirfilter(
    2,
    1000,
    btype='lowpass',
    fs=sample_rate,
)
track = signal.lfilter(filter[0], filter[1], track) / 2

nargs = len(sys.argv)
if nargs > 2:
    io.wavfile.write(args[2], sample_rate, track)
else:
    sounddevice.play(track, samplerate=sample_rate, blocking=True)
