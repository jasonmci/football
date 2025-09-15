import sounddevice as sd

print("Opening mic for 3 seconds... speak into it.")
recording = None
try:
    recording = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Done. Recorded shape:", recording.shape)
except Exception as e:
    print("Error:", e)

# play back the recording
if recording is not None:
    sd.play(recording, samplerate=16000)
    sd.wait()  # Wait until playback is finished
    print("Playback finished.")