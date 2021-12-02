import configparser
import csv
import logging
import io
import json
import os

from cryptography.fernet import InvalidToken
from cryptography.fernet import Fernet

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

os.makedirs('logs', exist_ok=True)
import gui
from gui.DatabaseReader import DatabaseReader
from gui.EnterPaymentsScreen import EnterPaymentsScreen
from gui.EnterSecretsScreen import EnterSecretsScreen
from gui.FileChooserListScreen import FileChooserListScreen
from gui.MainMenuScreen import MainMenuScreen
from gui.ManagerRoninScreen import ManagerRoninScreen
from gui.PasswordScreen import PasswordScreen

from axie import AxieClaimsManager
from axie import AxiePaymentsManager
from axie.utils import load_json


class AppScreens(ScreenManager):

    config = None
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
            payments = load_json(self.config["DEFAULT"]["PAYMENTS_FILE"].strip(), self.encryptionKey)
            if (
                payments and
                "Manager" in payments.keys() and
                payments["Manager"]
            ):
                self.displayedScreen = ManagerRoninScreen(managerRoninID=payments["Manager"])
            else:
                self.displayedScreen = ManagerRoninScreen()
        elif nextScreenIn == "FileChooserListScreenASUJSON":
            self.displayedScreen = FileChooserListScreen(
                filters=["*.json"],
                openButtonLabel="Open Axie Scholar Utilities Payments JSON"
            )
        elif nextScreenIn == "EnterPaymentsScreen":
            payments = load_json(self.config["DEFAULT"]["PAYMENTS_FILE"].strip(), self.encryptionKey)
            self.displayedScreen = EnterPaymentsScreen(payments=payments)
        elif nextScreenIn == "EnterSecretsScreen":
            payments = load_json(self.config["DEFAULT"]["PAYMENTS_FILE"].strip(), self.encryptionKey)
            secrets = load_json(self.config["DEFAULT"]["SECRETS_FILE"].strip(), self.encryptionKey)
            self.displayedScreen = EnterSecretsScreen(payments=payments, secrets=secrets)
        self.add_widget(self.displayedScreen)

    def closeDisplayedScreen(self):
        self.remove_widget(self.displayedScreen)
        self.openMainMenuScreen()

    # This method needs to be rewritten according to new methods in CLI library.
    def runUpdate(
        self,
        managerRoninIDIn=None,
        scholarCSVRowsIn=[],
        paymentsJSONFileIn="",
        secretsJSONFileIn="",
        paymentsDictIn={},
        secretsDictIn={}
    ):
        cipher = Fernet(self.encryptionKey)

        if not os.path.exists(self.config["DEFAULT"]["SECRETS_FILE"].strip()):
            with open(self.config["DEFAULT"]["SECRETS_FILE"].strip(), 'wb') as f:
                f.write(cipher.encrypt(b"{}"))
        if not os.path.exists(self.config["DEFAULT"]["PAYMENTS_FILE"].strip()):
            with open(self.config["DEFAULT"]["PAYMENTS_FILE"].strip(), 'wb') as f:
                f.write(cipher.encrypt(b"{}"))

        payments = load_json(self.config["DEFAULT"]["PAYMENTS_FILE"].strip(), self.encryptionKey)
        secrets = load_json(self.config["DEFAULT"]["SECRETS_FILE"].strip(), self.encryptionKey)

        managerRoninID = None
        if managerRoninIDIn:
            managerRoninID = managerRoninIDIn
        elif "Manager" in payments.keys():
            managerRoninID = payments["Manager"]

        if paymentsJSONFileIn:
            paymentsIn = load_json(paymentsJSONFileIn)
            if not "Scholars" in payments.keys():
                payments["Scholars"] = []
            payments["Scholars"].extend(paymentsIn["Scholars"])
            with open(self.config["DEFAULT"]["PAYMENTS_FILE"].strip(), 'wb') as f:
                f.write(cipher.encrypt(json.dumps(payments, ensure_ascii=False, indent=4).encode("utf-8")))

        if secretsJSONFileIn:
            secretsIn = load_json(secretsJSONFileIn)
            secrets.update(secretsIn)
            with open(self.config["DEFAULT"]["SECRETS_FILE"].strip(), 'wb') as f:
                f.write(cipher.encrypt(json.dumps(secrets, ensure_ascii=False, indent=4).encode("utf-8")))

        if paymentsDictIn:
            if not "Scholars" in payments.keys():
                payments["Scholars"] = []
            payments["Scholars"] = paymentsDictIn["Scholars"]
            with open(self.config["DEFAULT"]["PAYMENTS_FILE"].strip(), 'wb') as f:
                f.write(cipher.encrypt(json.dumps(payments, ensure_ascii=False, indent=4).encode("utf-8")))

        if secretsDictIn:
            secrets = secretsDictIn
            with open(self.config["DEFAULT"]["SECRETS_FILE"].strip(), 'wb') as f:
                f.write(cipher.encrypt(json.dumps(secrets, ensure_ascii=False, indent=4).encode("utf-8")))

        if managerRoninIDIn or scholarCSVRowsIn:
            if not managerRoninID and "Manager" in payments.keys():
                managerRoninID = payments["Manager"]
            outputText = "Name,AccountAddress,"
            outputText += "ScholarPayoutAddress,ScholarPercent,ScholarPayout,"
            outputText += "TrainerPayoutAddress,TrainerPercent,TrainerPayout\n"
            for scholarItem in scholarCSVRowsIn:
                outputText += ",".join([columnItem for columnItem in scholarItem]) + "\n"
            if managerRoninID:
                self.generatePaymentsFile(
                    managerRoninID,
                    outputText,
                    self.config["DEFAULT"]["PAYMENTS_FILE"].strip(),
                    self.encryptionKey
                ) 

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
    title = "Axie Scholar Payments GUI v{}".format(gui.__version__)
    def build(self):
        return AppScreens()