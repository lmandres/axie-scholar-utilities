import configparser
import csv
import io

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from gui import __version__
from gui.DatabaseReader import DatabaseReader
from gui.DisplayImageScreen import DisplayImageScreen
from gui.DisplayLoggingScreen import DisplayLoggingScreen
from gui.FileChooserListScreen import FileChooserListScreen
from gui.MainMenuScreen import MainMenuScreen
from gui.ManagerRoninScreen import ManagerRoninScreen
from gui.ManageTableScreen import ManageTableScreen
from gui.PasswordScreen import PasswordScreen

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from axie.qr_code import QRCode
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

        # if not os.path.exists(self.config["DEFAULT"]["SECRETS_FILE"]):
        #    self.openNewPasswordScreen()
        # else:
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
            pass

            # try:
            #    root.parent.encryptionKey = root.getEncryptionKey(root.password.text)
            #    root.parent.runUpdate()
            #    root.parent.closeUnlockScreen()
            # except InvalidToken:
            #    root.errorLabel.text = "Invalid password."

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
            if teamName is None:
                teamName = ""
            managerAddress = self.dbreader.getSetting("Manager Address")
            if managerAddress is None:
                managerAddress = ""
            self.displayedScreen = ManagerRoninScreen(
                teamName=teamName,
                managerAddress=managerAddress
            )
        elif nextScreenIn == "FileChooserListScreenPaymentsASUJSON":

            def fileCallback(filePath):

                try:
                    records = load_json(filePath)

                    scholarsList = []
                    trainersList = []
                    paymentsList = []

                    for scholarItem in records["Scholars"]:
                        if (
                            "Name" in scholarItem.keys() and
                            "AccountAddress" in scholarItem.keys() and
                            "ScholarPayoutAddress" in scholarItem.keys()
                        ):
                            newDict = {
                                "scholarName": scholarItem["Name"],
                                "scholarAddress": scholarItem["AccountAddress"],
                                "scholarPayoutAddress": scholarItem["ScholarPayoutAddress"]
                            }
                            newDict["scholarPayout"] = None
                            if "ScholarPayout" in scholarItem.keys():
                                newDict["scholarPayout"] = scholarItem["ScholarPayout"]
                            newDict["scholarPercent"] = 30
                            if "ScholarPercent" in scholarItem.keys():
                                newDict["scholarPercent"] = scholarItem["ScholarPercent"]
                            scholarsList.append(newDict)

                        if "TrainerPayoutAddress" in scholarItem.keys():
                            newDict = {
                                "trainerName": "",
                                "trainerPayoutAddress": scholarItem["TrainerPayoutAddress"]
                            }
                            newDict["trainerPayout"] = None
                            if "TrainerPayout" in scholarItem.keys():
                                newDict["trainerPayout"] = scholarItem["TrainerPayout"]
                            newDict["trainerPercent"] = 1
                            if "TrainerPercent" in scholarItem.keys():
                                newDict["trainerPercent"] = scholarItem["TrainerPercent"]
                            trainersList.append(newDict)

                        if "AccountAddress" in scholarItem.keys():
                            newDict = {
                                "scholarAddress": scholarItem["AccountAddress"]
                            }
                            newDict["trainerPayoutAddress"] = None
                            if "TrainerPayoutAddress" in scholarItem.keys():
                                newDict["trainerPayoutAddress"] = scholarItem["TrainerPayoutAddress"]
                            paymentsList.append(newDict)

                    self.dbreader.updateScholarsFromFile(scholarsList)
                    self.dbreader.updateTrainersFromFile(trainersList)
                    self.dbreader.updatePaymentsFromFile(paymentsList)

                except Exception as e:
                    raise(e)

            self.displayedScreen = FileChooserListScreen(
                filters=["*.json"],
                openButtonLabel="Open Axie Scholar Utilities Payments JSON",
                chooseFileCallback=fileCallback
            )

        elif nextScreenIn == "FileChooserListScreenPaymentsASUCSV":

            def fileCallback(filePath):

                try:

                    scholars_list = []
                    with open(filePath, "r", encoding='utf-8') as csvFileIn:
                        reader = csv.DictReader(csvFileIn)
                        for row in reader:
                            clean_row = {k: v for k, v in row.items() if v is not None and v != ''}
                            integer_row = {k: int(v) for k, v in clean_row.items() if v.isdigit()}
                            clean_row.update(integer_row)
                            scholars_list.append(clean_row)

                    scholarsList = []
                    trainersList = []
                    paymentsList = []

                    for scholarItem in scholars_list:
                        if (
                            "Name" in scholarItem.keys() and
                            "AccountAddress" in scholarItem.keys() and
                            "ScholarPayoutAddress" in scholarItem.keys()
                        ):
                            newDict = {
                                "scholarName": scholarItem["Name"],
                                "scholarAddress": scholarItem["AccountAddress"],
                                "scholarPayoutAddress": scholarItem["ScholarPayoutAddress"]
                            }
                            newDict["scholarPayout"] = None
                            if "ScholarPayout" in scholarItem.keys():
                                newDict["scholarPayout"] = scholarItem["ScholarPayout"]
                            newDict["scholarPercent"] = 30
                            if "ScholarPercent" in scholarItem.keys():
                                newDict["scholarPercent"] = scholarItem["ScholarPercent"]
                            scholarsList.append(newDict)

                        if "TrainerPayoutAddress" in scholarItem.keys():
                            newDict = {
                                "trainerName": "",
                                "trainerPayoutAddress": scholarItem["TrainerPayoutAddress"]
                            }
                            newDict["trainerPayout"] = None
                            if "TrainerPayout" in scholarItem.keys():
                                newDict["trainerPayout"] = scholarItem["TrainerPayout"]
                            newDict["trainerPercent"] = 1
                            if "TrainerPercent" in scholarItem.keys():
                                newDict["trainerPercent"] = scholarItem["TrainerPercent"]
                            trainersList.append(newDict)

                        if "AccountAddress" in scholarItem.keys():
                            newDict = {
                                "scholarAddress": scholarItem["AccountAddress"]
                            }
                            newDict["trainerPayoutAddress"] = None
                            if "TrainerPayoutAddress" in scholarItem.keys():
                                newDict["trainerPayoutAddress"] = scholarItem["TrainerPayoutAddress"]
                            paymentsList.append(newDict)

                    self.dbreader.updateScholarsFromFile(scholarsList)
                    self.dbreader.updateTrainersFromFile(trainersList)
                    self.dbreader.updatePaymentsFromFile(paymentsList)

                except Exception as e:
                    raise(e)

            self.displayedScreen = FileChooserListScreen(
                filters=["*.csv"],
                openButtonLabel="Open Axie Scholar Utilities Payments CSV",
                chooseFileCallback=fileCallback
            )

        elif nextScreenIn == "FileChooserListScreenSecretsASUCSV":

            def fileCallback(filePath):
                try:
                    new_secrets = {}
                    with open(filePath, "r", encoding='utf-8') as csv_file:
                        csv_reader = csv.reader(csv_file, delimiter=',')
                        for row in csv_reader:
                            new_secrets[row[0]] = row[1]
                    self.dbreader.updateSecretsFromFile(new_secrets)
                except Exception as e:
                    raise(e)

            self.displayedScreen = FileChooserListScreen(
                filters=["*.csv"],
                openButtonLabel="Open Axie Scholar Utilities Payments JSON",
                chooseFileCallback=fileCallback
            )

        elif nextScreenIn == "FileChooserListScreenSecretsASUJSON":

            def fileCallback(filePath):
                try:
                    records = load_json(filePath)
                    self.dbreader.updateSecretsFromFile(records)
                except Exception as e:
                    raise(e)

            self.displayedScreen = FileChooserListScreen(
                filters=["*.json"],
                openButtonLabel="Open Axie Scholar Utilities Payments JSON",
                chooseFileCallback=fileCallback
            )

        elif nextScreenIn == "ManageScholarsScreen":

            def generateQRCode(root, rowData):

                def closeScreen(screenRoot):
                    root.remove_widget(imageScreen)
                    root.add_widget(self.displayedScreen)

                qrCode = QRCode(
                    account=rowData["scholarAddress"],
                    private_key=rowData["scholarPrivateKey"],
                    acc_name=rowData["scholarName"]
                ).get_qr()

                data = io.BytesIO()
                qrImage = qrCode.get_image()
                image = Image.new("1", (qrImage.size[0], qrImage.size[1]+60,), color=1)
                image.paste(qrImage, (0, 0,))
                imageDraw = ImageDraw.Draw(image)
                imageFont = ImageFont.truetype("fonts\\RobotoMono-Regular.ttf", 24)
                textSize = imageDraw.textsize(rowData["scholarName"], font=imageFont)
                imageDraw.text((int((qrImage.size[0]-textSize[0])/2), qrImage.size[1],), rowData["scholarName"], font=imageFont, fill=0)

                imageScreen = DisplayImageScreen(
                    image=image,
                    closeCallback=closeScreen
                )
                self.remove_widget(self.displayedScreen)
                root.add_widget(imageScreen)

            self.displayedScreen = ManageTableScreen(
                keyItems=[
                    ("scholarName", "textinput",),
                    ("scholarAddress", "addressinput",),
                    ("scholarPayoutAddress", "addressinput",),
                    ("scholarPercent", "textinput",),
                    ("scholarPayout", "textinput",),
                    ("scholarPrivateKey", "passwordinput",),
                    ("", "button", "Generate QR Code", generateQRCode,),
                    ("", "deletebutton",)
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
                    ("trainerPayout", "textinput",),
                    ("", "deletebutton",)
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
                    ("trainerID", "dropdownbutton", trainers,),
                    ("", "deletebutton",)
                ],
                rowIDColumn="paymentID",
                rowData=self.dbreader.getPayments(),
                updateCallback=self.dbreader.updatePayments,
                deleteCallback=self.dbreader.deletePayments
            )

        elif nextScreenIn == "RunClaimsAndAutoPayouts":
            self.displayedScreen = DisplayLoggingScreen()

        self.add_widget(self.displayedScreen)

    def closeDisplayedScreen(self):
        self.remove_widget(self.displayedScreen)
        self.openMainMenuScreen()


class AxieGUIApp(App):

    title = "Axie Scholar Payments GUI v{}".format(__version__)

    def build(self):
        return AppScreens()
