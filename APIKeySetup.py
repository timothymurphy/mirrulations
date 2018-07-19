import requests
import os
import random
import string
from appJar import gui

app = gui("Regulations-BOINC")


def exit(buttonName):
    '''
    Closes an error window, called by buttons in error dialogs.
    :param buttonName: Passed by appJar when the method is called.
    :return:
    '''
    app.hideSubWindow("errorWindow")
    app.hideSubWindow("invalidKeyWindow")


def end(buttonName):
    '''
    Closes the GUI, called by a button in the final success dialog.
    :param buttonName: Passed by appJar when the method is called.
    :return:
    '''
    app.hideSubWindow("successWindow")
    app.stop()


#This code builds a window to display an error message.
#The window can be shown by calling: app.showSubWindow("errorWindow")
app.startSubWindow("errorWindow", "Error")

app.top = True
app.resizable = False
app.font = {'size': 18, 'family': 'Gill Sans'}

app.padding = (10, 8)
app.guiPadding = (10, 30)

app.addLabel("errorCode", "We weren't able to connect to regulations.gov.")
app.addLabel("errorMessage", "Please try again later.")

app.addButton("   Okay   ", exit)

app.stopSubWindow()
#Done building window.



''' 
This code builds a window to display an invalid API key message.
The window can be shown by calling: app.showSubWindow("invalidKeyWindow")
'''
app.startSubWindow("invalidKeyWindow", "Error")

app.top = True
app.resizable = False
app.font = {'size': 18, 'family': 'Gill Sans'}

app.padding = (50, 2)

app.addLabel("errorLabel1", "Invalid API Key!")
app.addLabel("errorLabel2", "Please visit:")
app.link("regulations.gov", "https://regulationsgov.github.io/developers/")
app.addLabel("errorLabel3", "for an API Key.")

app.addButton("   Back   ", exit)

app.stopSubWindow()
#Done building window.


'''
Builds a window for the final message, to be displayed if/when everything finishes correctly.
The window can be shown by calling: app.showSubWindow("successWindow")
'''
app.startSubWindow("successWindow", "Regulations-Boinc")

app.top = True
app.resizable = False
app.font = {'size': 18, 'family': 'Gill Sans'}

app.padding = (50, 2)

app.addLabel("successMessage", "Successfully stored API Key!")

app.addNamedButton("   Done   ", "doneButton", end)

app.stopSubWindow()
#Done building window


def writeAPIKey(key):
    '''
    Writes the user's API Key to ~/.env/regulationskey.txt
    :param key: APIKey to be written to the file.
    :return:
    '''


    fileDirectory = os.getenv("HOME") + "/.env"

    if not os.path.exists(fileDirectory):
        os.makedirs(fileDirectory)

    f = open(fileDirectory + "/regulationskey.txt", "r+")

    stuff = f.read()

    if stuff == "":
        #Writes the user's API key to the file, with a random string for the client's ID.
        f.write(key + "\n" + ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
    f.close()



#Below code builds the main window
submitName = "   Submit   "
cancelName = "   Cancel   "

app.top = True
app.resizable = False
app.font = {'size':18, 'family':'Gill Sans'}

app.padding = (10,8)
app.guiPadding = (10,30)

app.addLabel("header","Please enter your regulations.gov API Key.")

app.addLabelEntry("APIKey")


# Called when a button is pressed
def press(buttonName):

    if buttonName == cancelName:
        app.stop()
    elif buttonName == submitName:
        apiKey = app.getEntry("APIKey")

        try:
            r = requests.get("https://api.data.gov/regulations/v3/documents.json?api_key=" + apiKey)
        except requests.ConnectionError:
            app.showSubWindow("errorWindow")
            return

        '''
        Anything 300 & above is an error, but 429 is the error for a key that's run out of requests
        and 403 is the error for an invalid key
        '''
        if r.status_code > 299 and r.status_code != 429:

            if r.status_code == 403:
                app.showSubWindow("invalidKeyWindow")
            else:
                app.showSubWindow("errorWindow")

        else:
            writeAPIKey(apiKey)
            app.showSubWindow("successWindow")



app.addButtons([submitName, cancelName], press)

app.go()