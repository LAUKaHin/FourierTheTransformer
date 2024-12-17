# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 00:21:46 2024

@author: Victor Mctrix
"""

# imports 
import os
import cv2
import sys
import time
import wave
import shutil
import datetime
import numpy as np
from pydub import AudioSegment
from moviepy import editor as mp
from scipy.fft import rfft, rfftfreq
from matplotlib import pyplot as plt

startTime = time.time()

#Set target mp3 and chose plt styling
target = sys.argv[1]
Style = __import__(sys.argv[2])

targetDir = target + "/"
audioDir = "Audio/"
outputDir = "Output/"

#Create project directory
if os.path.exists(targetDir)!=True:
    os.mkdir(targetDir)
if os.path.exists(targetDir+audioDir)!=True:
    os.mkdir(targetDir+audioDir)
    shutil.move(target+".mp3", targetDir+audioDir+target+".mp3")
if os.path.exists(targetDir+outputDir)!=True:
    os.mkdir(targetDir+outputDir)

sound = AudioSegment.from_mp3(targetDir+audioDir+target+".mp3")#Convert mp3 stereo to wav mono
sound = sound.set_channels(1)
sound.export(targetDir+audioDir+target+"Mono.wav", format="wav")

# reading the audio file 
raw = wave.open(targetDir+audioDir+target+"Mono.wav")
raw.getparams()

# reads all the frames  
# -1 indicates all or max frames 
signal = raw.readframes(-1) 
signal = np.frombuffer(signal, dtype ="int16") 

# gets the frame rate 
f_rate = raw.getframerate()

# to Plot the x-axis in seconds  
# you need get the frame rate  
# and divide by size of your signal 
# to create a Time Vector  
# spaced linearly with the size  
# of the audio file 
audioTime = np.linspace( 
    0, # start 
    len(signal) / f_rate, 
    num = len(signal) 
)

DURATION = 1/Style.fps  # 1/fps sec
frameDuration = int(f_rate*DURATION) # 1/fps
# Number of samples in normalized_tone
N = frameDuration
itter = 0

try:
    for i in np.arange(0, len(signal), frameDuration):
        # Note the extra 'r' at the front
        yf = rfft(signal[i:i+frameDuration])
        xf = rfftfreq(N, 1/f_rate)
        print("Processing frame: " + str(itter) + " of " + "{:.3f}".format(len(signal)/frameDuration-1) + " Which is " + "{:.3f}".format(itter*DURATION) + " seconds. Progress: " + "{:.3f}".format((i/len(signal))*100) + "% " + "Time taking on execution: " + str(datetime.timedelta(seconds=int(time.time()-startTime))), end='\r')
        plt.figure(figsize=Style.dimension, facecolor=Style.mbColor, num=1, clear=True)
        plt.axes().set_facecolor(Style.gbColor)
        plt.ylim(0.01, Style.ylim)
        plt.title(target, fontsize=64, **Style.font, weight='bold', color=Style.fontColor)
        plt.xlabel('Frequency (Hz)', fontsize=32, **Style.font, color=Style.fontColor)
        plt.ylabel('Magnitude', fontsize=32, **Style.font, color=Style.fontColor)
        #plt.plot(xf, np.abs(yf))#For normal view
        plt.semilogy(xf, np.abs(yf), color=Style.lineColor)#For log view
        plt.margins(x=0)
        plt.xticks(np.arange(24000, step=2000), fontsize=16, **Style.font, color=Style.fontColor)
        plt.yticks(np.logspace(-2,9,num=9+2+1, base=10,dtype='float'), fontsize=16, **Style.font, color=Style.fontColor)
        plt.grid(which='major', color=Style.majorGridColor, linewidth=1)
        plt.grid(which='minor', color=Style.minorGridColor, linestyle=":", linewidth=0.5)
        plt.minorticks_on()
        plt.savefig(targetDir+outputDir+target+str(itter), dpi=Style.resolution)
        #plt.clf()
        #plt.close()
        itter+=1
except Exception as e:
    print(e)
    pass

out_video_name = target +"FFT" + ".mp4"
out_video_full_path = targetDir+outputDir+out_video_name

pre_imgs = os.listdir(targetDir+outputDir)
#print(pre_imgs)
img = []

for i in range(0, len(pre_imgs), 1):
    filename = targetDir+outputDir+target+str(i)+".png"
    #print(i)
    img.append(filename)

# print(img)

cv2_fourcc = cv2.VideoWriter_fourcc(*'mp4v')

frame = cv2.imread(img[0])
size = list(frame.shape)
del size[2]
size.reverse()
# print(size)

video = cv2.VideoWriter(out_video_full_path, cv2_fourcc, Style.fps, size) #output video name, fourcc, fps, size

for i in range(len(img)): 
    video.write(cv2.imread(img[i]))
    print("Processing frame: " + str(i) + " of " + str(len(img)-1) + " Which is " + "{:.3f}".format(i/30) + " seconds. Progress: " + "{:.3f}".format((i/len(img))*100) + "%" + "Time taking on execution: " + str(datetime.timedelta(seconds=int(time.time()-startTime))), end='\r')

video.release()

#Add audio to video
video = mp.VideoFileClip(out_video_full_path)
audio = mp.AudioFileClip(targetDir+audioDir+target+".mp3")
if video.duration>audio.duration:
    video = video.subclip(0, audio.duration)
elif audio.duration>video.duration:
    audio = audio.subclip(0, video.duration)
video.audio = audio
video.write_videofile(targetDir+outputDir+target+".mp4")

print( "Program finnished, time taken: " + "Time taking on execution: " + str(datetime.timedelta(seconds=int(time.time()-startTime))))
