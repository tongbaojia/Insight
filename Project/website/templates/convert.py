from pydub import AudioSegment
import sys

file = sys.argv[0]
f = AudioSegment.from_mp3(file)
f.export(file.repalce('.mp3', '.wav'), format="wav")
print("Done!")