#!/usr/bin/env python

## http://flask.pocoo.org/docs/1.0/quickstart/
import sys
sys.path.insert(0, '../src/')
import os
from glob import glob
import multiprocessing as mp
#from threading import Lock
from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask_socketio import SocketIO, emit, disconnect#, join_room, leave_room, close_room, rooms
from werkzeug.utils import secure_filename
from gensim.summarization import summarize

import scipy.io.wavfile
import numpy as np
from collections import OrderedDict
from utils import SoundToText
from utils import PrepareSound
from utils import text_clean
from utils import top_words

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, binary=True)
#socketio = SocketIO(app, async_mode=async_mode)
#thread = None
#thread_lock = Lock()

UPLOAD_FOLDER = 'tmp/'
ALLOWED_EXTENSIONS = set(['txt', 'wav', 'mp3'])

#def background_thread():
#    """Example of how to send server generated events to clients."""
#    count = 0
#    while True:
#        socketio.sleep(10)
#        count += 1
#        socketio.emit('my_response',
#                      {'data': 'Server generated event', 'count': count},
#                      namespace='/test')


@app.route('/audio')
def index():
    return render_template('index_audio.html')


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    #global thread
    #with thread_lock:
    #    if thread is None:
    #        thread = socketio.start_background_task(target=background_thread)
    session['audio'] = []
    emit('my_response', {'data': 'Recording', 'count': 0})

@socketio.on('sample_rate', namespace='/test')
def handle_my_sample_rate(sampleRate):
    session['sample_rate'] = sampleRate
    # send some message to front
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': "sampleRate : %s" % sampleRate, 'count': session['receive_count'] })

@socketio.on('audio', namespace='/test')
def handle_my_custom_event(audio):
    #session['audio'] += audio
    #session['audio'] += audio.values()
    values = OrderedDict(sorted(audio.items(), key=lambda t:int(t[0]))).values()
    session['audio'] += values

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    # my_audio = np.array(session['audio'], np.float32)
    # scipy.io.wavfile.write('tmp/out.wav', 44100, my_audio.view('int16'))
    #print(my_audio.view('int16'))

    # https://stackoverflow.com/a/18644461/466693
    sample_rate = session['sample_rate']
    my_audio = np.array(session['audio'], np.float32)
    sindata = np.sin(my_audio)
    scaled = np.round(32767*sindata)
    newdata = scaled.astype(np.int16)
    scipy.io.wavfile.write('tmp/out.wav', sample_rate, newdata)

    session['audio'] = []
    print('Audio recording finished', request.sid)

## uploading files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 ## max 16 Mb
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# @app.route('/audio', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # if user does not select file, browser also
#         # submit an empty part without filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('upload_file',
#                                     filename=filename))
#         else:
#             flash('No selected file')
#             return redirect(request.url)
#     return render_template('index_upload.html')

@app.route('/audio', methods=['POST'])
@socketio.on('mytext', namespace='/test')
def mytext(name=None):

    myaudio = ""
    if request.method == 'POST':
        if 'TestSample' in request.form:
            myaudio = 'tmp/chunk_s1.wav'
        else:
            myaudio = 'tmp/out.wav'
    infodic = {}
    infodic.update(PrepareSound(myaudio, silencesplit=True))

    inputtasks = glob(myaudio.replace(".wav", "_*.wav"))

    

    mytextdic = {}

    # ## parallel
    # print(" Running %s jobs on %s cores" % (len(inputtasks), mp.cpu_count()-2))
    # npool = min(len(inputtasks), mp.cpu_count() - 1)
    # pool  = mp.Pool(npool)
    # results = pool.map(SoundToText, inputtasks)
    # pool.close()
    # pool.join()
    # for result in results:
    #     mytextdic.update(result)

    # standard
    for j in inputtasks:
        print(j)
        result = SoundToText(j) #dictionary of values, plots
        mytextdic.update(result)

    ## clear the input files
    for k in inputtasks:
        os.remove(k)

    atext = ""
    for i in range(len(mytextdic.keys())):
        atext += mytextdic[myaudio.replace(".wav", "_" + str(i) + ".wav")] + ". "
    
    ## summrization keywords
    keytext = top_words(text_clean(atext))
    
    ## summrization sentence
    sentence = summarize(atext, ratio=0.2, split=True)

    ## for key sentence, make it italice and underline
    for s in sentence:
        print(s)
        atext = atext.replace(s, "<u><i>" + s + "</i></u>")

    ## for key words, make it yellow
    for j in keytext:
        atext = atext.replace(j, "<span style='background-color: #FFFF00'>" + j + "</span>")

    ## convert atext to a list again, with.
    atext = atext.split(".")

    ## get audio length
    audio_length = "%.1f sec" % infodic[myaudio]["duration"]
    return render_template("index_audio.html", output_summary=keytext, original_text=atext, audio_length=audio_length)

if __name__ == '__main__':
    socketio.run(app, debug=True)
