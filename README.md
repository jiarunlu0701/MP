README

LIVE MODE / VIDEO MODE
- In the main.py line 19 allow to switch between live mode or video mode
   - cap = cv2.VideoCapture(0) # front camera on the screen
   - cap = cv2.VideoCapture(1) # back camera from your iPhone
   - cap = cv2.VideoCapture('video2.mp4') # change the input in the () into your video name under the file
 
How to place your camera
- The model can ONLY track ONE person at a time
- Make sure the camera can track your entire body (Stand front of the camera approximately 3 to 4 meters away

View your results
- Because the exercise classification model is not developed yet. There are certain false results, that are due to the fact the person is not actually doing a sqaut.
- The Window is showing the tracking parameters, the warnings are in the terminal of the IDE
- When choosing live mode, it is ideal if you have a bigger screen to see the live results (It doesn't have a audio result yet)
