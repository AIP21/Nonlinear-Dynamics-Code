import time
import sounddevice
import numpy


SAMPLE_RATE = 44100
orbit = {complex(440, 1000): 0}


def callback(outdata: numpy.ndarray, frames: int, time, status) -> None:
    # Write the sound data to two channels
    resultChannel1 = None
    resultChannel2 = None
    
    # Both channels
    for frequency, start_index in orbit.items():
        t = (start_index + numpy.arange(frames)) / SAMPLE_RATE
        t = t.reshape(-1, 1)

        wave = numpy.sin(2 * numpy.pi * frequency.real * t)

        if resultChannel1 is None:
            resultChannel1 = wave
        else:
            resultChannel1 += wave

        wave2 = numpy.sin(2 * numpy.pi * frequency.imag * t)

        if resultChannel2 is None:
            resultChannel2 = wave2
        else:
            resultChannel2 += wave2

        orbit[frequency] += frames

    # Normalize the result
    resultChannel1 /= max(abs(resultChannel1))
    resultChannel2 /= max(abs(resultChannel2))
    
    # Write the result to the output
    outdata[:, 0] = resultChannel1.flatten()
    outdata[:, 1] = resultChannel2.flatten()


stream = sounddevice.OutputStream(channels=2, blocksize=SAMPLE_RATE, samplerate=SAMPLE_RATE, callback=callback)
stream.start()

# while True:
time.sleep(4)

stream.stop()