## for speech to text
import speech_recognition as sr
import string, re, spacy
from pydub import AudioSegment ##for audio spliting
from pydub.silence import split_on_silence
from collections import Counter, OrderedDict
import uuid


def PrepareSound(file="", fixsplit=False, silencesplit=True):
    '''input is a file path; can be mp3 or wav; 
        will recognise file; 
        then has the option to split the file or not;
        output is a wav file, or splitted wav files;
        with a dictionary of each wav file's information.'''
    if ".wav" in file:
        sound_file = AudioSegment.from_wav(file)
    if ".mp3" in file:
        sound_file = AudioSegment.from_mp3(file)
    if ".ogg" in file:
        sound_file = AudioSegment.from_ogg(file)
    
    unique_filename = str(uuid.uuid4())
    info = OrderedDict()
    def getinfo(schunk):
        return {"dBFS": schunk.dBFS, 
                "max_dBFS": schunk.max_dBFS, 
                "duration": schunk.duration_seconds, 
                "rms": schunk.rms, 
                "max": schunk.max}
    
    if ".mp3" in file:
        file = file.replace(".mp3", ".wav")
        if (not fixsplit) and (not silencesplit):
            print("convert mp3!")
            sound_file.export(file, format="wav")
    if ".ogg" in file:
        file = file.replace(".ogg", ".wav")
        if (not fixsplit) and (not silencesplit):
            print("convert ogg!")
            sound_file.export(file, format="wav")
    
    ## keep the whole file info
    ##info[file] = getinfo(sound_file)
        
    if fixsplit:
        ##split into 20 second chunks
        for i, chunk in enumerate(sound_file[::100 * 1000]):
            out_file = file.replace(".wav", unique_filename + "_" + str(i) +  ".wav")
            with open(out_file, "wb") as f:
                chunk.export(f, format="wav")
            info[out_file] = getinfo(chunk)
        print("fix split!")
    elif silencesplit:
        ## https://github.com/jiaaro/pydub/blob/master/pydub/silence.py
        audio_chunks = split_on_silence(sound_file, 
            # must be silent for at least half a second; in ms
            min_silence_len=500,
            # keep a part of silence so there is no cutoff ; in ms                           
            keep_silence=250,
            # seek_step ; in ms                           
            seek_step=20,
            # consider it silent; roughly this is 10dB, intensity 1/10 of the ave
            silence_thresh= (sound_file.dBFS * 1.5 - sound_file.max_dBFS/2))
        for i, chunk in enumerate(audio_chunks):
            out_file = file.replace(".wav", unique_filename + "_" + str(i) + ".wav")
            chunk.export(out_file, format="wav")
            info[out_file] = getinfo(chunk)
        #print("silent split!")
    
    del sound_file
    return info


def SoundToText(file="", useGoogle=False, path="../"):
    '''Uses Sphinx builtin. 
    Input is a dic contained as config.
    Output is a dic with filename as key and text as content '''
    if file != "":
        #print(file)
        test = sr.AudioFile(file)
        Recon  = sr.Recognizer()
        with test as source:
            test_au = Recon.record(source)
            ## test_length = test.DURATION
            
        if not useGoogle:
            try: 
                text = Recon.recognize_sphinx(test_au, language='en-US')
            except sr.UnknownValueError:
                print("cannot recognize ", file)
                text = ""
        else:
            ## google API requires internet connection
            ## https://cloud.google.com/speech-to-text/
            #text = Recon.recognize_google(test_au, language='en-US')
            ## only takes texts < 60 seconds!
            f = open(path + 'Project/src/tony-test-fa962b69f1fb.json', 'r')
            #print(json.loads(f))
            GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()
            try:
                text = Recon.recognize_google_cloud(test_au, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
            except sr.UnknownValueError:
                print("cannot recognize ", file)
                text = ""
            f.close()
        
        del test
        del test_au
        del Recon
        return {file: text}
    else:
        print('STH is wrong!')
        return ""
    
def text_clean(input_text):
    '''clean and remove some common words'''
    # replace . from sphinx, this is very tricky
    output_text = input_text.replace(". ", "")
    
    table = str.maketrans('', '', string.punctuation)
    # get rid of punctuation
    output_text = output_text.translate(table)
    
    # get rid of newlines
    output_text = output_text.strip().replace("\n", ". ").replace("\r", ".")
    
    # replace twitter @mentions
    mentionFinder = re.compile(r"@[a-z0-9_]{1,15}", re.IGNORECASE)
    output_text = mentionFinder.sub("@MENTION", output_text)
    
    # replace HTML symbols
    output_text = output_text.replace("&amp;", "and").replace("&gt;", ">").replace("&lt;", "<")
    
    # lowercase
    output_text = output_text.lower()

    return output_text


def top_words(input_data, keeptype=["NOUN", "PROPN", "NUM", "ADJ", "ADV"], doalpha=True, dostop=True, nwords=5):
    # List of symbols we don't care about
    nlp = spacy.load('en')
    data = nlp("".join(input_data))
    SYMBOLS = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve", "\n", "", " ", "\n\n", "npr"]
    tokens = []
    for tok in data:
        
        # stoplist the tokens
        if dostop:
            ##check if the token is stopword
            if not tok.is_stop:
                pass
            else:
                continue
        else:
            pass
        
        # stoplist symbols
        if tok.text not in SYMBOLS:
            pass
        else: 
            continue
        
        ##check if the token is alpha
        if doalpha:
            if tok.is_alpha:
                pass
            else:
                continue
        else:
            pass
        
        ##check if the token is noun
        if len(keeptype) > 1:
            if tok.pos_ in keeptype:
                pass
            else:
                continue
        else:
            pass
    
        # lemmatize
        if tok.lemma_ != "-PRON-" :
            tokens.append(tok.lemma_.lower().strip())
        else:
            tokens.append(tok.lower_)
    
    common_words = [w[0] for w in Counter(tokens).most_common(nwords)]
    ##sort them in order of the text
    common_words.sort(key=lambda x: tokens.index(x))

    # remove large strings of whitespace
    return common_words


def wer(ref, hyp ,debug=False):
    
    '''https://web.archive.org/web/20171215025927/
    http://progfruits.blogspot.com/2014/02/word-error-rate-wer-and-word.html'''
    
    r = ref.split()
    h = hyp.split()
    #costs will holds the costs, like in the Levenshtein distance algorithm
    costs = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]
    # backtrace will hold the operations we've done.
    # so we could later backtrace, like the WER algorithm requires us to.
    backtrace = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]
 
    OP_OK = 0
    OP_SUB = 1
    OP_INS = 2
    OP_DEL = 3
    
    DEL_PENALTY = 1
    # First column represents the case where we achieve zero
    # hypothesis words by deleting all reference words.
    for i in range(1, len(r)+1):
        costs[i][0] = DEL_PENALTY*i
        backtrace[i][0] = OP_DEL
    
    INS_PENALTY = 1
    # First row represents the case where we achieve the hypothesis
    # by inserting all hypothesis words into a zero-length reference.
    for j in range(1, len(h) + 1):
        costs[0][j] = INS_PENALTY * j
        backtrace[0][j] = OP_INS
     
    # computation
    SUB_PENALTY = 1
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            if r[i-1] == h[j-1]:
                costs[i][j] = costs[i-1][j-1]
                backtrace[i][j] = OP_OK
            else:
                substitutionCost = costs[i-1][j-1] + SUB_PENALTY # penalty is always 1
                insertionCost    = costs[i][j-1] + INS_PENALTY   # penalty is always 1
                deletionCost     = costs[i-1][j] + DEL_PENALTY   # penalty is always 1
                 
                costs[i][j] = min(substitutionCost, insertionCost, deletionCost)
                if costs[i][j] == substitutionCost:
                    backtrace[i][j] = OP_SUB
                elif costs[i][j] == insertionCost:
                    backtrace[i][j] = OP_INS
                else:
                    backtrace[i][j] = OP_DEL
                 
    # back trace though the best route:
    i = len(r)
    j = len(h)
    numSub = 0
    numDel = 0
    numIns = 0
    numCor = 0
    if debug:
        print("OP\tREF\tHYP")
        lines = []
    while i > 0 or j > 0:
        if backtrace[i][j] == OP_OK:
            numCor += 1
            i-=1
            j-=1
            if debug:
                lines.append("OK\t" + r[i]+"\t"+h[j])
        elif backtrace[i][j] == OP_SUB:
            numSub +=1
            i-=1
            j-=1
            if debug:
                lines.append("SUB\t" + r[i]+"\t"+h[j])
        elif backtrace[i][j] == OP_INS:
            numIns += 1
            j-=1
            if debug:
                lines.append("INS\t" + "****" + "\t" + h[j])
        elif backtrace[i][j] == OP_DEL:
            numDel += 1
            i-=1
            if debug:
                lines.append("DEL\t" + r[i]+"\t"+"****")
    if debug:
        lines = reversed(lines)
        for line in lines:
            print(line)
        print("#cor " + str(numCor))
        print("#sub " + str(numSub))
        print("#del " + str(numDel))
        print("#ins " + str(numIns))
    
    wer_result = round( (numSub + numDel + numIns) / (float) (len(r)), 4)
    return wer_result
    #return {'WER':wer_result, 'Cor':numCor, 'Sub':numSub, 'Ins':numIns, 'Del':numDel}