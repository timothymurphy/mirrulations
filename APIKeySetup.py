import requests
import os
import random
import string
import json
from appJar import gui
from pathlib import Path

''' Set this to true to have the GUI prompt the user for a config everytime it is opened
 This will overwrite the config. If set to false, the GUI will only prompt the user for
 config input if no config file is found.'''
overwrite_config = False

submitName = "   Submit   "
cancelName = "   Cancel   "

config_ip_submitName = " Enter IP "
config_port_submitName = " Enter Port "

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

def writeAPIKey(key, directory):
    '''
    Writes the user's API Key to ~/.env/regulationskey.txt
    :param key: APIKey to be written to the file.
    :return:
    '''

    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        f = open(directory + "/regulationskey.txt", "r")
        contents = f.read()
        f.close()
    except FileNotFoundError:
        contents = ""

    if contents == "":
        #Writes the user's API key to the file, with a random string for the client's ID.
        file = open(directory + "/regulationskey.txt", "w")
        file.write(key + "\n" + ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
        file.close()

# Called when a button is pressed on the API key window
def press(buttonName):
    '''
    Runs when one of the two buttons on the api window is clicked. Does all of the work of processing the API key they gave.
    :param buttonName: Passed by appJar when the method is called.
    :return:
    '''


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
        Anything 300 & above is an error
        429 is the error for a key that's run out of requests
        403 is the error for an invalid key
        '''
        if r.status_code > 299 and r.status_code != 429:

            if r.status_code == 403:
                app.showSubWindow("invalidKeyWindow")
            else:
                app.showSubWindow("errorWindow")

        else:
            writeAPIKey(apiKey, os.getenv("HOME") + "/.env")
            app.showSubWindow("successWindow")

def configPress(buttonName):
    '''
    Called when the button of the config setup window is pressed
    :param buttonName: Passed by appJar when the method is called.
    :return:
    '''
    if buttonName == config_ip_submitName:
        f = open("config.json", "w")
        f.write("{\n" + '\"ip\":' + "\"" + app.getEntry("IP") + "\",\n")
        f.close()
        app.hideSubWindow("config_ip_window")
        app.showSubWindow("config_port_window")
    if buttonName == config_port_submitName:
        f = open("config.json", "a")
        f.write('\"port\":' + "\"" + app.getEntry("Port") + "\"\n}")
        f.close()
        app.hideSubWindow("config_port_window")
        app.showSubWindow("api_key_window")

if __name__ == "__main__":
    app = gui("Mirrulations")

    # This code builds a window to display an error message.
    # The window can be shown by calling: app.showSubWindow("errorWindow")
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
    # Done building window.


    # This code builds a window to display an invalid API key message.
    # The window can be shown by calling: app.showSubWindow("invalidKeyWindow")

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
    # Done building window.


    # Builds a window for the final message, to be displayed if/when everything finishes correctly.
    # The window can be shown by calling: app.showSubWindow("successWindow")

    app.startSubWindow("successWindow", "Mirrulations")

    app.top = True
    app.resizable = False
    app.font = {'size': 18, 'family': 'Gill Sans'}

    app.padding = (50, 2)

    app.addLabel("successMessage", "Successfully stored API Key!")

    app.addNamedButton("   Done   ", "doneButton", end)

    app.stopSubWindow()
    # Done building window

    # Below code builds the API key window
    app.startSubWindow("api_key_window")

    app.top = True
    app.resizable = False
    app.font = {'size': 18, 'family': 'Gill Sans'}

    app.padding = (10, 8)
    app.guiPadding = (10, 30)

    app.addLabel("header", "Please enter your regulations.gov API Key.")

    app.addLabelEntry("APIKey")

    app.addButtons([submitName, cancelName], press)

    app.stopSubWindow()
    # Done building API key window


    #Below code builds the config ip setup window
    app.startSubWindow("config_ip_window")

    app.top = True
    app.resizable = False
    app.font = {'size': 18, 'family': 'Gill Sans'}

    app.padding = (10, 8)
    app.guiPadding = (10, 30)

    app.addLabel("config_header_ip", "   Please enter the IP of the server \n        you wish to connect to.")

    app.addLabelEntry("IP")

    app.addButton(config_ip_submitName, configPress)

    app.stopSubWindow()
    # Done building config setup window

    # Below code builds the config port setup window
    app.startSubWindow("config_port_window")

    app.top = True
    app.resizable = False
    app.font = {'size': 18, 'family': 'Gill Sans'}

    app.padding = (10, 8)
    app.guiPadding = (10, 30)

    app.addLabel("config_header_port", "    Please enter the port of the server \n        you wish to connect on.")

    app.addLabelEntry("Port")

    app.addButton(config_port_submitName, configPress)

    app.stopSubWindow()
    # Done building config setup window

    if Path("config.json").exists() and not overwrite_config:
        try:
            print("Okay")
            contents = json.loads(open("config.json", "r").read())
            print("Okay2")
            contents["ip"]
            print("Okay3")
            contents["port"]
            print("Okay4")
        except:
            print("Exceptional")
            app.showSubWindow("config_ip_window")
        else:
            app.showSubWindow("api_key_window")
    else:
        app.showSubWindow("config_ip_window")

    app.go()

