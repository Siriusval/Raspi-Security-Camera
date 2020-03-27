# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 22:57:34 2020

@author: Valentin
"""


# --- LIBRARIES ---
#OpenCV, for video feed
import cv2 
#scikit-image, for comparison, SSIM algorithm
from skimage.metrics import structural_similarity
# Twilio, for sending messages, like SMS
from twilio.rest import Client
#import constant values, such as Twilio credentials and target phone
from env import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_PHONE,PHONE_NUMBER 


# --- VARS ---
#Threshold, if the error is under it, we trigger an alert
#1 is perfect match between 2 images
#Found that we had to lower it to deal with noise and micro movements
similarityValue = 0.90

#Difference between highest and lowest value of picture
#min=0, max = 255
data_range = 255


# --- FUNCTIONS ---
#return error between 2 images/matrix, identical if 1 is returned
def ssim(A,B):
    return structural_similarity(A, B, data_range=data_range)

# --- MAIN ---
#Twilio client initialisation
client = Client(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)

#Capture the video flux with openCV (We can change 0 to 1,2,... if multiple cameras)
video_capture = cv2.VideoCapture(0)

# First, we need to initialise the stored frame
# right now it's empty so we have nothing to compare to

# Get the actual frame
_,buffer_frame = video_capture.read() 

#Transform picture to GrayScale, easier to compare
buffer_frame = cv2.cvtColor(buffer_frame, cv2.COLOR_BGR2GRAY) #Gray
      
#Store actual frame, so now we can start comparing
previous_frame = buffer_frame

#We do not need to compare all the frames
#let's compare every 10 frames (Approx every ~0.4s for a 24fps camera)
comparison_frequency = 10

#Counter for video frames, we already got 1 image, so init at 1
image_counter = 1

#Counter for printing events with number
event_counter = 0

#Boolean so we don't spam the phone at each event, we send the message only once
#TODO: Add a reset after a certain time
is_first_message = True

#Main loop, runinng unless of CTRL+C or keyboard input
while True:
    try:
        #Read the next frame into buffer
        _,buffer_frame = video_capture.read() # First frame
    
        #If we don't have images anymore, exit
        if buffer_frame is None:
            break
        
        #Switch to gray
        buffer_frame = cv2.cvtColor(buffer_frame, cv2.COLOR_BGR2GRAY)
    
        #Compare every 10 frames
        if image_counter == comparison_frequency:
            #Get error value
            ssim_index = ssim(previous_frame, buffer_frame)
        
            #If error under threshold, trigger warning
            if ssim_index < similarityValue:
                event_counter +=1
                print('Event'+str(event_counter)+' : Intruder Pepper Spray!')   
                
                #Send message if first warning
                if (is_first_message):
                    #send text message
                    #client.messages.create(body='Intruder Alert!',from_=TWILIO_PHONE,to=PHONE_NUMBER)
                    is_first_message = False
            
            #Store current frame as new reference for comparison
            previous_frame = buffer_frame
           
            #Display captured frame, so we can see what is happening
            cv2.imshow('Raspi Security Camera', buffer_frame)
            cv2.waitKey(1) # Image not displayed if line removed
            
            #if comparison happened, reset frame counter
            image_counter=0
            
        #Increment at each loop / captured frame
        image_counter+=1
    
    #Avoid error when stopping program
    except KeyboardInterrupt:
        print('All done')
        break
        
#Stop video feed and close window
video_capture.release()
cv2.destroyAllWindows()
