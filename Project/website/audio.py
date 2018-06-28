#!/usr/bin/env python

## http://flask.pocoo.org/docs/1.0/quickstart/
import sys
topdir = '/Users/renormalization/Git/Insight/'
#topdir = '/home/ubuntu/Insight/'
#sys.path.insert(0, '/home/ubuntu/Insight/Project/src/')
sys.path.insert(0, topdir + 'Project/src/')
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
#socketio = SocketIO(app, binary=True)

#thread = None
#thread_lock = Lock()

UPLOAD_FOLDER = topdir + 'Project/website/tmp/'
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'ogg'])
## uploading files
app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024 ## max 16 Mb
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def homeindex():
    return render_template('index.html')

@app.route('/index')
def alsohomeindex():
    return render_template('index.html')

@app.route('/example')
def exampleindex():
    return render_template('index_example.html')


@app.route('/upload')
def uploadindex():
    return render_template('index_upload.html')
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file',filename=filename))
        else:
            flash('No selected file')
            return redirect(request.url)
    return render_template('index_upload.html')


@app.route('/record')
def recordindex():
    return render_template('index_record.html')


@app.route('/summary')
def summaryindex():
    tmpfiles = [str(i).replace(UPLOAD_FOLDER, "") for i in glob(UPLOAD_FOLDER + "*.wav")]
    tmpfiles += [str(i).replace(UPLOAD_FOLDER, "") for i in glob(UPLOAD_FOLDER + "*.mp3")]
    tmpfiles += [str(i).replace(UPLOAD_FOLDER, "") for i in glob(UPLOAD_FOLDER + "*.ogg")]
    return render_template('index_summary.html', tmpfiles=tmpfiles)

@app.route('/summary', methods=['GET', 'POST'])
#@socketio.on('mytext', namespace='/test')
def mytext(name=None):

    tmpfiles = [str(i).replace(UPLOAD_FOLDER, "") for i in glob(UPLOAD_FOLDER + "*.wav")]
    tmpfiles += [str(i).replace(UPLOAD_FOLDER, "") for i in glob(UPLOAD_FOLDER + "*.mp3")]
    tmpfiles += [str(i).replace(UPLOAD_FOLDER, "") for i in glob(UPLOAD_FOLDER + "*.ogg")]
    
    myaudio = ""
    if request.method == 'POST':
        myaudio = UPLOAD_FOLDER + str(request.form.get('TranslateFile'))
        # if 'TestSample' in request.form:
        #     myaudio = UPLOAD_FOLDER + 'speech.wav'
        # else:
        #     myaudio = UPLOAD_FOLDER + 'out.wav'
    
    infodic = {}
    #myaudio = UPLOAD_FOLDER + "20180622_me_latest_on_immigration_politics.mp3"
    print("processing", myaudio)

    infodic.update(PrepareSound(myaudio, silencesplit=True))

    inputtasks = infodic.keys() ## this is the ordered files

    mytextdic = {}
    ## parallel
    print(" Running %s jobs on %s cores" % (len(inputtasks), mp.cpu_count()-2))
    npool = min(len(inputtasks), mp.cpu_count() - 2)
    pool  = mp.Pool(npool)
    results = pool.map(SoundToText, inputtasks)
    pool.close()
    pool.join()
    for result in results:
        mytextdic.update(result)
    # # standard
    # for j in inputtasks:
    #     print(j)
    #     result = SoundToText(j) #dictionary of values, plots
    #     mytextdic.update(result)

    ## clear the input files
    for k in inputtasks:
        os.remove(k)

    atext = "" ##initalize the output text
    atime = 0 ##initalize the output time
    outtext = ""
    for temp_name in infodic.keys():
        temp_time = "[" + "%.0f s" % atime  + "]  "
        atime   += infodic[temp_name]["duration"]
        cleanedtext = text_clean(mytextdic[temp_name])
        atext   +=  cleanedtext.capitalize() + ". "
        outtext +=  temp_time + cleanedtext.capitalize() + ". "
    
    ## summrization keywords; on atext the string
    keytext = top_words(atext, nwords=5)
    
    ## summrization sentence; on atext the string
    try:
        sentence = summarize(atext, ratio=0.2, split=True)
    except ValueError:
        sentence = [atext.split(".")[0]]

    ## for key sentence, make it italice and underline
    for s in sentence:
        print(s)
        outtext = outtext.replace(s, "<span style='background-color: #ccffcc'>" + s + "</span>")
    ## for key words, make it yellow
    for j in keytext:
        outtext = outtext.replace(j, "<u><i><b>" + j + "</b></i></u>")

    ## convert outtext to a list again, with.
    outtext = outtext.split(".")

    # for k in outtext:
    #     print(k)
    # for k in inputtasks:
    #     print(infodic[k]["duration"])

    ## get audio length: full audio length with silence here!
    ## audio_length = "%.1f sec" % infodic[myaudio]["duration"]
    audio_length = "%.1f sec" % atime
    return render_template("index_summary.html", output_text=keytext, output_sentence=sentence, original_text=outtext, audio_length=audio_length, tmpfiles=tmpfiles)


if __name__ == '__main__':
    #socketio.run(app, debug=True, host='0.0.0.0')
    app.run(debug=True, host='0.0.0.0')
