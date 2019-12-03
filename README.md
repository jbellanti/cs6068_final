# cs6068_final
____
(Python 3) Code for the Parallel Computing final project

Project Name: Multimedia Keyword Search in Parallel

Members: 

- Kevin Farley
- Jordan Bellanti
- Emma Romstadt
- Joseph Weisbrod

____
### Set up Google Cloud Speech to Text
The following was derived from [google's cloud's getting started page](https://cloud.google.com/speech-to-text/docs/reference/libraries#client-libraries-install-python)

DISCLAIMER: the following instructions were designed for / tested on Windows but Linux etc. should be similar enough

- set up a google cloud account: https://cloud.google.com/free/
  - if you guys have trouble with this i can look into sharing my instances
- install [gcloud sdk](https://cloud.google.com/sdk/)
- via the installer gui create a project i.e. `speech2text-cs6068`
- now execute the following in a command prompt post-install
```batch
REM NOTE: use whatever admin/project name you want just replace admin-speech2text/speech2text-cs6068 accordingly
gcloud iam service-accounts create admin-speech2text
gcloud projects add-iam-policy-binding speech2text-cs6068 --member "serviceAccount:admin-speech2text@speech2text-cs6068.iam.gserviceaccount.com" --role "roles/owner"
gcloud iam service-accounts keys create admin-speech2text-cs6068.json --iam-account admin-speech2text@speech2text-cs6068.iam.gserviceaccount.com
REM add the json file to your environment variables. temporarily you can do:
set GOOGLE_APPLICATION_CREDENTIALS=<current path>\admin-speech2text-cs6068.json
```
- go ahead and try to run this code 
```batch
python3 main.py -h
python3 main.py -v
```
- you may see a 403 error, if so you need to enable the api and billing
  - don't worry the billing will take from the $300 provided with your trial account
  - read the error message and go to the web link it describes to enable the api
- re run `python3 main.py -v`
- you should then see the following among other program output
```
Transcript: testing 1 2 3 test recording for Google Cloud
Transcript:  yep
```
