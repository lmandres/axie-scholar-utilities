import configparser
import csv
import logging
import io
import json
import os

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

os.makedirs('logs', exist_ok=True)
from gui import __version__
from gui.DatabaseReader import DatabaseReader
from gui.EnterPaymentsScreen import EnterPaymentsScreen
from gui.EnterSecretsScreen import EnterSecretsScreen
from gui.FileChooserListScreen import FileChooserListScreen
from gui.MainMenuScreen import MainMenuScreen
from gui.ManagerRoninScreen import ManagerRoninScreen
from gui.ManageTableScreen import ManageTableScreen
from gui.PasswordScreen import PasswordScreen

from axie import AxieClaimsManager
from axie import AxiePaymentsManager
from axie.utils import load_json


class AppScreens(ScreenManager):

    config = None
    dbreader = None
    displayedScreen = None
    mainMenuScreen = None
    unlockScreen = None
    encryptionKey = None

    def __init__(self):
        super(AppScreens, self).__init__()

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.dbreader = DatabaseReader(self.config["DEFAULT"]["DATABASE_FILE"])
        self.dbreader.createDatabaseTables()

        Window.maximize()
        self.openMainMenuScreen()

        #if not os.path.exists(self.config["DEFAULT"]["SECRETS_FILE"]):
        #    self.openNewPasswordScreen()
        #else:
        #    self.openUnlockScreen()

    def openNewPasswordScreen(self, errorText=""):

        def onTextEnter(root):
            root.parent.encryptionKey = root.getEncryptionKey(root.password.text)
            root.parent.closeNewPasswordScreen()

        self.unlockScreen = PasswordScreen(
            label="Enter New Password",
            error=errorText,
            callback=onTextEnter
        )
        self.add_widget(self.unlockScreen)

    def closeNewPasswordScreen(self):
        self.remove_widget(self.unlockScreen)
        self.openConfirmPasswordScreen()

    def openConfirmPasswordScreen(self):

        def onTextEnter(root):
            confirmKey = root.getEncryptionKey(root.password.text)
            if root.parent.encryptionKey != confirmKey:
                root.parent.encryptionKey = None
            root.parent.closeConfirmPasswordScreen()

        self.unlockScreen = PasswordScreen(
            label="Confirm New Password",
            callback=onTextEnter
        )
        self.add_widget(self.unlockScreen)

    def closeConfirmPasswordScreen(self):
        if not self.encryptionKey:
            self.remove_widget(self.unlockScreen)
            self.openNewPasswordScreen(errorText="Passwords Do Not Match")
        else:
            self.runUpdate()
            self.closeUnlockScreen()
        
    def openUnlockScreen(self):

        def onTextEnter(root):
            try:
                root.parent.encryptionKey = root.getEncryptionKey(root.password.text)
                root.parent.runUpdate()
                root.parent.closeUnlockScreen()
            except InvalidToken:
                root.errorLabel.text = "Invalid password."

        self.unlockScreen = PasswordScreen(
            label="Password",
            callback=onTextEnter
        )
        self.add_widget(self.unlockScreen)

    def closeUnlockScreen(self):
        self.remove_widget(self.unlockScreen)
        self.openMainMenuScreen()

    def openMainMenuScreen(self):
        self.mainMenuScreen = MainMenuScreen()
        self.add_widget(self.mainMenuScreen)

    def closeMainMenuScreen(self):
        self.remove_widget(self.mainMenuScreen)

    def openDisplayedScreen(self, nextScreenIn=None):
        if nextScreenIn == "ManagerRoninScreen":
            teamName = self.dbreader.getSetting("Team Name")
            if teamName == None:
                teamName = ""
            managerAddress = self.dbreader.getSetting("Manager Address")
            if managerAddress == None:
                managerAddress = ""
            self.displayedScreen = ManagerRoninScreen(
                teamName=teamName,
                managerAddress=managerAddress
            )
        elif nextScreenIn == "FileChooserListScreenASUJSON":
            self.displayedScreen = FileChooserListScreen(
                filters=["*.json"],
                openButtonLabel="Open Axie Scholar Utilities Payments JSON"
            )
        elif nextScreenIn == "ManageScholarsScreen":
            self.displayedScreen = ManageTableScreen(
                keyItems=[
                    ("scholarName", "textinput",),
                    ("scholarAddress", "addressinput",),
                    ("scholarPayoutAddress", "addressinput",),
                    ("scholarPercent", "textinput",),
                    ("scholarPayout", "textinput",)
                ],
                rowIDColumn="scholarID",
                rowData=self.dbreader.getScholars(),
                updateCallback=self.dbreader.updateScholars,
                deleteCallback=self.dbreader.deleteScholars
            )
        elif nextScreenIn == "ManageTrainersScreen":
            self.displayedScreen = ManageTableScreen(
                keyItems=[
                    ("trainerName", "textinput",),
                    ("trainerPayoutAddress", "addressinput",),
                    ("trainerPercent", "textinput",),
                    ("trainerPayout", "textinput",)
                ],
                rowIDColumn="trainerID",
                rowData=self.dbreader.getTrainers(),
                updateCallback=self.dbreader.updateTrainers,
                deleteCallback=self.dbreader.deleteTrainers
            )
        elif nextScreenIn == "EnterPaymentsScreen":
            scholars = [(None, "--",)]
            for scholar in self.dbreader.getScholars():
                scholars.append((scholar["scholarID"], scholar["scholarName"],))
            trainers = [(None, "--",)]
            for trainer in self.dbreader.getTrainers():
                trainers.append((trainer["trainerID"], trainer["trainerName"],))
            self.displayedScreen = ManageTableScreen(
                keyItems=[
                    ("scholarID", "dropdownbutton", scholars,),
                    ("trainerID", "dropdownbutton", trainers,)
                ],
                rowIDColumn="paymentID",
                rowData=self.dbreader.getPayments(),
                updateCallback=self.dbreader.updatePayments,
                deleteCallback=self.dbreader.deletePayments
            )
        elif nextScreenIn == "EnterSecretsScreen":
            payments = load_json(self.config["DEFAULT"]["PAYMENTS_FILE"].strip(), self.encryptionKey)
            secrets = load_json(self.config["DEFAULT"]["SECRETS_FILE"].strip(), self.encryptionKey)
            self.displayedScreen = EnterSecretsScreen(payments=payments, secrets=secrets)
        self.add_widget(self.displayedScreen)

    def closeDisplayedScreen(self):
        self.remove_widget(self.displayedScreen)
        self.openMainMenuScreen()

    def generatePaymentsFile(self, managerRoninID, csvFileStr, payments_file_path, encryptionKey):
        scholars_list = []
        cipher = Fernet(encryptionKey)
        if not os.path.exists(payments_file_path):
            with open(payments_file_path, 'wb') as f:
                f.write(cipher.encrypt(b"{}"))

        with io.StringIO(csvFileStr) as csvFileIO:
            reader = csv.DictReader(csvFileIO)
            for row in reader:
                clean_row = {k: v for k, v in row.items() if v is not None and v != ''}
                integer_row = {k: int(v) for k, v in clean_row.items() if v.isdigit()}
                clean_row.update(integer_row)
                scholars_list.append(clean_row)

        payments_dict = {"Manager": managerRoninID, "Scholars": scholars_list}
        with open(payments_file_path, 'wb') as f:
            f.write(cipher.encrypt(json.dumps(payments_dict, ensure_ascii=False, indent=4).encode("utf-8")))

        logging.info('New payments file saved')
            
  

class AxieGUIApp(App):
    title = "Axie Scholar Payments GUI v{}".format(__version__)
    def build(self):
        return AppScreens()