# xG-Prediction Model

Idea is to calculate xG of each shot taken, given is the location of each shot taken from in x,y coordinates, and also by calculating angles of each shot towards the goal post.

The Field is divided to 120 x 80 units, and hence locating each shot from the Statsbomb open data.
the xG model her predicts from the data of 58k+ shots and draw some conclusions over it.

## Setup
To download the data and mounted in drive/MyDrive locattion.
Then create a directory /MyDrive/xg-model and here storing the data in the ./data/raw/ directory.
also creating a new directory in the /data/processed to store the processed data (csv) files, and then using these to access for further process.

## method
shot distance and angles are calculated from the goal post, and then scaling the data and on further caliberating it for realistic results.

## conclusion
The data model here predicts the xG model as seen in the following charts:
<img width="846" height="885" alt="image" src="https://github.com/user-attachments/assets/b3d06dd1-274b-4911-9f2d-b4da3240ad3e" />

## drawing shot map
I was very interested in the shot map as we see in the Fotmob, Sofascore and more such apps, so using this data I decided to build that too!
here are the results;
this is the shot map of all the data in events section (by the date it was formed):
<img width="1198" height="875" alt="image" src="https://github.com/user-attachments/assets/7425ed43-c430-4e36-80fb-9dece00754d5" />

here is one highlighting those which were shots on target (goals marked as blue):
<img width="1247" height="857" alt="image" src="https://github.com/user-attachments/assets/c83567de-220e-45bb-8032-47957abb954c" />


### ps: what a freak messi was!
this is the data for xG overperformers:
<img width="1172" height="605" alt="image" src="https://github.com/user-attachments/assets/9e461709-95b4-4e35-a484-fb9ccd95b76f" />
