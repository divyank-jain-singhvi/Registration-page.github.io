from flask import Flask, render_template,request, redirect, url_for
import pyttsx3
import speech_recognition as sr
import threading
import sounddevice as sd
import soundfile as sf
import firebase_admin
import speaker_verification_toolkit.tools as svt
import librosa
import numpy as np
import pandas as pd
import shutil
import os
import re
import tkinter as tk
from tkinter import filedialog
from sklearn.svm import SVC
from firebase_admin import credentials, storage
from firebase import firebase
from tkinter import *

app = Flask(__name__)
app = Flask(__name__, static_url_path='/static', static_folder='static')
firebase=firebase.FirebaseApplication("https://login-699da-default-rtdb.firebaseio.com/Users",None)
cred = credentials.Certificate("D:\divyank\login form html css\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"storageBucket": "login-699da.appspot.com"})
email_pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
answer=''
sample_rate = 44100 
duration = 5

file=1
data={}

user_email_input=''
user_password_input=''
user_confirm_password_input=''
user_phone_no_input=''
user_country_input=''
user_state_input=''
greets='WELCOME'
def frequency_test(value):
    value=value.replace('@gmail.com','')
    audio_files_test=os.listdir('./audio')
    print(audio_files_test)
    df_list_test=[]
    for i, file_path in enumerate(audio_files_test):
        print(i,file_path)
        data_test, sr_test = librosa.load('./audio/'+file_path, sr=16000, mono=True)
        data_test = svt.rms_silence_filter(data_test)
        data_test = svt.extract_mfcc(data_test)
        for i in data_test:
            df_test = pd.DataFrame({'MFCC_Coefficients': [i], 'Speaker': [i]})  
            df_list_test.append(df_test)
            
    df_test = pd.concat(df_list_test, ignore_index=True)
    test_features = np.array(df_test['MFCC_Coefficients'].tolist())
    test_labels = np.array(df_test['Speaker'].apply(lambda x: x[0]).tolist(), dtype=int)
    os.remove('./audio/user audio1.wav')
    print(df_test)
    
    print('from file')
    bucket = storage.bucket()
    blob = bucket.blob(f'{value}/user audio1.wav')
    blob.download_to_filename('./audio/user audio1.wav')
    blob.download_to_filename('./audio/user audio2.wav')
    audio_files = os.listdir('./audio')
    
    
    df_list = []
    for i, file_path in enumerate(audio_files):
        data, sr = librosa.load('./audio/'+file_path, sr=16000, mono=True)
        data = svt.rms_silence_filter(data)
        data = svt.extract_mfcc(data)
        for i in data:
            df = pd.DataFrame({'MFCC_Coefficients': [i], 'Speaker': [i]}) 
            df_list.append(df)
    
    df = pd.concat(df_list, ignore_index=True)
    features = np.array(df['MFCC_Coefficients'].tolist())
    labels = np.array(df['Speaker'].apply(lambda x: x[0]).tolist(), dtype=int)
    

    model = SVC(kernel='linear')  
    model.fit(features,labels)
    accuracy = model.score(test_features, test_labels)
    print(df)
    print("Model Accuracy:", accuracy)
    del df_test,df
    if accuracy*100 >= 22:
        return True
    else:
        return False



def system_speech(audio):
    engine = pyttsx3.init('sapi5')
    engine.setProperty('rate', 140)
    engine.say(audio)
    engine.runAndWait()

def thread_recording():
    
    thread2 = threading.Thread(target=user_input)
    thread3= threading.Thread(target=record_audio)
    thread2.start()
    thread3.start()
    thread2.join()
    thread3.join()

def record_audio():
    
    global duration,sample_rate,file
    output_file=f'audio/user audio{file}.wav'
    audio1 = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    sf.write(output_file, audio1, sample_rate)
    print('downloarded')

def user_input():
    global answer
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, phrase_time_limit=5)
        try:
            answer = r.recognize_google(audio)
            print("the query is printed='", answer, "'")
        except Exception as e:
            answer=''

def registration_detail(input_speach,input_type,value):
    global data
    value=value.replace('@gmail.com','')
    system_speech(input_speach)
    user_input()
    detail=answer.strip()
    detail= ''.join(char for char in detail if char != ' ')
    print(len(detail))
    if input_type=='phone no':
        if len(detail)==10:
            firebase.put('https://login-699da-default-rtdb.firebaseio.com/Users_data/'+value,input_type,detail)
            data[input_type]=detail
            return detail
        
    if input_type=='country':
        firebase.put('https://login-699da-default-rtdb.firebaseio.com/Users_data/'+value,input_type,detail)
        data[input_type]=detail
        return detail
    
    if input_type=='state':
        firebase.put('https://login-699da-default-rtdb.firebaseio.com/Users_data/'+value,input_type,detail)
        data[input_type]=detail
        return detail
    
    system_speech(f'incorrect {input_type}')
    registration_detail(input_speach, input_type,value)

def upload_file_to_firebase(value):
    for i in range(len(os.listdir('./audio/'))):
        value=value.replace('@gmail.com','')
        file_path = f"audio/user audio{i+1}.wav"
        destination_path = f"{value}/user audio{i+1}.wav"
        print(file_path,destination_path)
        bucket = storage.bucket()
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(file_path)
    
    if os.path.exists('./audio/'):
        shutil.rmtree('./audio/')
        print('dir del1')
        
@app.route('/page1', methods=['GET', 'POST'])
def page1():
    return render_template('index1.html')
@app.route('/', methods=['GET', 'POST'])
def index6():
    global user_email_input,user_password_input,user_confirm_password_input,user_phone_no_input,user_country_input,user_state_input,greets
    return render_template('index.html',user_password_input =user_password_input,user_email_input=user_email_input,user_confirm_password_input=user_confirm_password_input,user_phone_no_input=user_phone_no_input,user_country_input=user_country_input,user_state_input=user_state_input,greets=greets)


# @app.route('/downloard', methods=['GET','POST'])
# def downloard_file():
#     global data,greets
#     try:
#         file_data=''
#         for key,value in data.items():
#             file_data=f'{key}:{value}\n'+file_data
#         file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
#         if file_path:
#             with open(file_path, "w") as file:
#                 file.write(file_data)
#                 print("File generated and saved successfully.")
#     except (TypeError,ValueError):
#         greets='no data inserted'
            
            
@app.route('/sign in', methods=['GET', 'POST'])
def sign_in_input():
    global user_email_input,user_confirm_password_input,user_password_input,user_phone_no_input,user_state_input,user_country_input,greets
    data=firebase.get('https://login-699da-default-rtdb.firebaseio.com/Users','')
    try:
        for key,value in data.items():
            if (value == user_email_input):
                if (re.match(email_pattern,user_email_input)) and (user_email_input!='@gmail.com') and (user_password_input!=''):
                    #welcome.config(text='You Are Already A User')
                    gteets='You Are Already A User'
                  
                else:
                  
                    #welcome.config(text='Invalid Email ID or Password')
                    greets='Invalid Email ID or Password'
            else:
                if (re.match(email_pattern,user_email_input)) and (user_email_input!='@gmail.com') and (user_password_input!=''):
                    
                    # user_phone_no_input=registration_detail('say your phone number','phone no',user_email_input)
                    # print(user_phone_no_input)
                    # #user_phone_lable_blank.config(text=user_phone_no_input)
                    
                    
                    # user_country_input=registration_detail('say your country name','country',user_email_input)
                    # #user_country_lable_blank.config(text=user_country_input)
                    
                    # user_state_input=registration_detail('say your state name','state',user_email_input)
                    # #user_state_lable_blank.config(text=user_state_input)
                    
                    firebase.put('https://login-699da-default-rtdb.firebaseio.com/Users',user_password_input,user_email_input)
                    #welcome.config(text='your new account is created')
                    greets='your new account is created'
                    upload_file_to_firebase(user_email_input)
                else:
                    #welcome.config(text='Invalid Email ID or Password')
                    greets='Invalid Email ID or Password'
    except AttributeError:
        if (re.match(email_pattern,user_email_input)) and (user_email_input!='@gmail.com') and (user_password_input!=''):
    
            # user_phone_no_input=registration_detail('say your phone number','phone no',user_email_input)
            # print(user_phone_no_input)
            #user_phone_lable_blank.config(text=user_phone_no_input)
            
            # user_country_input=registration_detail('say your country name','country',user_email_input)
            # # user_country_lable_blank.config(text=user_country_input)
            
            # user_state_input=registration_detail('say your state name','state',user_email_input)
            # #user_state_lable_blank.config(text=user_state_input)
            
            firebase.put('https://login-699da-default-rtdb.firebaseio.com/Users',user_password_input,user_email_input)
            # welcome.config(text='Your New Account Is Created')
            greets='Your New Account Is Created'
            upload_file_to_firebase(user_email_input)
        else:
            # welcome.config(text='Invalid Email ID or Password')
            greets='Invalid Email ID or Password'
    if os.path.exists('./audio/'):
        shutil.rmtree('./audio/')
    user_email_input=''
    user_password_input=''
    user_confirm_password_input=''
    user_phone_no_input=''
    user_country_input=''
    user_state_input=''
    return redirect(url_for('index6'))
    

@app.route('/login', methods=['GET', 'POST'])
def login_input():
    global email_pattern,answer,file,user_email_input,user_confirm_password_input,user_password_input,greets
    try:
        file=1
        if not os.path.exists('./audio'):
            print('dir 1')
            os.mkdir('./audio')
        data=firebase.get('https://login-699da-default-rtdb.firebaseio.com/Users','')
    #     system_speech('say your email')
    #     thread_recording()
    #     user_email_input=answer.strip()
    #     user_email_input= ''.join(char for char in user_email_input if char != ' ')
    #     user_email_input=user_email_input+'@gmail.com'
    #     #user_email_lable_blank.config(text=user_email_input)
    #     print(user_email_input)
    #     system_speech('password')
    #     thread_recording()
    #     user_password_input=answer.strip()
    #     user_password_input= ''.join(char for char in user_password_input if char != ' ')
    #     print(user_password_input)
    #     #user_password_lable_blank.config(text=user_password_input)
        if frequency_test(user_email_input)==True:
            try:
                for key,value in data.items():
                    if (value == user_email_input) and (key == user_password_input):
                        if (re.match(email_pattern,user_email_input)) and (user_email_input!='@gmail.com') and (user_password_input!=''):
                            if os.path.exists('./audio/'):
                               shutil.rmtree('./audio/')
                            # greets='WELCOME'
                            return redirect(url_for('page1'))
    #                         # system_speech('speek to input data')
    #                         # user_input()
    #                         # user_data=answer
    #                         # if user_data=='':
    #                         #     user_data='none'
    #                         # data_to_firebase(user_password_input ,user_email_input,user_data)
    #                         #home.pack_forget()
    #                         #login.pack()
    #                         #break
                        else:
    #                        # welcome.config(text='Invalid Email ID or Password')
                            greets='Invalid Email ID or Password'
    #                        print()
                    else:
    #                    # welcome.config(text='Wrong Email or Password / Dont Have An Account')
    #                    print()
                        greets='Wrong Email or Password / Dont Have An Account'
            except AttributeError:
    #           #  welcome.config(text='No Such Account Available')
                greets='No Such Account Available'
    #           print()
        else:
    #         #welcome.config(text='Your voice does not matched')
            greets='Your voice does not matched'
    #         print()
        if os.path.exists('./audio/'):
            shutil.rmtree('./audio/')
            
        user_email_input=''
        user_password_input=''
        user_confirm_password_input=''
        user_phone_no_input=''
        user_country_input=''
        user_state_input=''
        return redirect(url_for('index6'))
    except ValueError :
        user_email_input=''
        user_password_input=''
        user_confirm_password_input=''
        user_phone_no_input=''
        user_country_input=''
        user_state_input=''
        greets='no account exist'
        return redirect(url_for('index6'))

@app.route('/email', methods=['GET', 'POST'])
def email():
    global user_email_input
    try:
        system_speech('speak in silent place')
        system_speech('say your email')
        user_input()
        user_email_input=answer.strip()
        user_email_input= ''.join(char for char in user_email_input if char != ' ')
        user_email_input=user_email_input+'@gmail.com'
        return redirect(url_for('index6'))
    except RuntimeError:
        return redirect(url_for('index6'))
        
@app.route('/password', methods=['GET', 'POST'])
def password():
    global user_password_input,file
    try:
        if not os.path.exists('./audio/'):
            os.mkdir('./audio')
        file=1
        system_speech('say your password')
        thread_recording()
        user_password_input=answer.strip()
        user_password_input= ''.join(char for char in user_password_input if char != ' ')
        return redirect(url_for('index6'))
    except RuntimeError:
        return redirect(url_for('index6'))

@app.route('/confirm_password', methods=['GET', 'POST'])
def confirm_password():
    global user_confirm_password_input,file,user_password_input
    try:
        system_speech('Confirm your password')
        file=2
        thread_recording()
        if user_password_input !=answer:
            system_speech('your passwerd does not matched')
            confirm_password()
        user_confirm_password_input=answer
        return redirect(url_for('index6'))
    except RuntimeError:
        return redirect(url_for('index6'))

@app.route('/phone', methods=['GET', 'POST'])
def phone():
    global user_phone_no_input
    try:
        user_phone_no_input=registration_detail('say your phone number','phone no',user_email_input)
        return redirect(url_for('index6'))
    except RuntimeError:
        return redirect(url_for('index6'))
    
@app.route('/country', methods=['GET', 'POST'])
def country():
    global user_country_input
    try:
        user_country_input=registration_detail('say your country name','country',user_email_input)
        return redirect(url_for('index6'))
    except RuntimeError:
        return redirect(url_for('index6'))

@app.route('/state', methods=['GET', 'POST'])
def state():
    global user_state_input
    try:
        user_state_input=registration_detail('say your state name','state',user_email_input)
        return redirect(url_for('index6'))
    except RuntimeError:
        return redirect(url_for('index6'))

if __name__ == '__main__':
    app.run()