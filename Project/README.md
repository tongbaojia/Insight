# MeetingTextMemo

Welcome to Tony's project code page! This web API converts audio to text summaries.
It translates an audio to English sentences using Sphinx and Pyaudio;
And presents the highlight sentences using spacy and gensim;
Also supports keywords and full transcript.

## Project website: [MeetingMemo](http://meetingmemo.com)

## Structure

* The Data folder contains our data information;
* The Plot folder contains validation plots;
* The src folder contains the speech recognition and text processing code; all of them are in utils.py;
* The website folder contains the .html and .py for the webApp; to run it: python audio.py;

For the notebooks:
* Download(etc).ipynb shows the web-scraping and audio to conversion;
* MVP().ipynb shows studies of the pipeline engineering;
* SummaryStudies.ipynb shows the summarization studies;

### Prerequisites

Python 3.6

```
sudo apt-get install swig
sudo apt-get install gcc
sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt-get install ffmpeg libav-tools
pip install msgpack
pip install pyaudio

sudo apt-get install bison autoconf libtool-bin swig libpulse-dev
pip install pocketSphinx

pip install flask
pip install flask_socketio
pip install scipy

pip install spacy
python -m spacy download en 

pip install SpeechRecognition
pip install pydub
pip install gensim
```

## Authors

* **Tony Tong** - *Initial work* 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to Insight Data science fellows and mentors!