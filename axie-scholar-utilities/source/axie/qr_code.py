import os
import sys
import logging
from datetime import datetime

import qrcode

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from axie.utils import AxieGraphQL, load_json


def createQRImage(rowData):

    qrCode = None
    if (
        "scholarAddress" in rowData.keys() and
        "scholarPrivateKey" in rowData.keys() and
        "scholarName" in rowData.keys() and
        rowData["scholarAddress"] and
        rowData["scholarPrivateKey"]  and
        rowData["scholarName"]
     ):
        qrCode = QRCode(
            account=rowData["scholarAddress"],
            private_key=rowData["scholarPrivateKey"],
            acc_name=rowData["scholarName"]
        ).get_qr()

    image = None
    qrImage = None
    if not qrCode:
        image = Image.new("1", (770, 830,), color=1)
    else:
        qrImage = qrCode.get_image()
        image = Image.new("1", (qrImage.size[0], qrImage.size[1]+60,), color=1)
        image.paste(qrImage, (0, 0,))

    imageDraw = ImageDraw.Draw(image)
    imageFont = ImageFont.truetype("fonts\\RobotoMono-Regular.ttf", 24)
    qrCodeValid = False

    if not qrImage:
        textStr = (
            "Invalid data was passed to QR Code.\n" +
            "Please ensure that scholarName, scholarAddress,\n" +
            "and scholarPrivateKey are filled in\n" +
            "and are valid."
        )
        textSize = imageDraw.multiline_textsize(
            textStr,
            font=imageFont
        )
        imageDraw.multiline_text(
            (int((770-textSize[0])/2), int((830-textSize[1])/2),),
            textStr,
            font=imageFont,
            fill=0
        )
    else:
        textSize = imageDraw.textsize(rowData["scholarName"], font=imageFont)
        imageDraw.text(
            (int((qrImage.size[0]-textSize[0])/2), qrImage.size[1],),
            rowData["scholarName"],
            font=imageFont,
            fill=0
        )
        qrCodeValid = True

    return (image, qrCodeValid)


class QRCode(AxieGraphQL):

    def __init__(self, **kwargs):
        self.acc_name = kwargs.pop("acc_name", None)
        self.path = kwargs.pop("path", "")
        super().__init__(**kwargs)

    def get_qr(self):
        jwt = self.get_jwt()
        logging.info('Create QR Code')
        qr = qrcode.make(jwt)
        return qr

    def generate_qr(self):
        self.path = os.path.join(self.path, f'{self.acc_name.lower()}-{int(datetime.timestamp(datetime.now()))}.png')
        logging.info(f'Saving QR Code for account {self.acc_name} at {self.path}')
        self.get_qr().save(self.path)


class QRCodeManager:

    def __init__(self, payments_file, secrets_file):
        self.secrets_file, self.acc_names = self.load_secrets_and_acc_name(secrets_file, payments_file)
        self.path = os.path.dirname(secrets_file)

    def load_secrets_and_acc_name(self, secrets_file, payments_file):
        secrets = load_json(secrets_file)
        payments = load_json(payments_file)
        refined_secrets = {}
        acc_names = {}
        for scholar in payments['Scholars']:
            key = scholar['AccountAddress']
            refined_secrets[key] = secrets[key]
            acc_names[key] = scholar['Name']
        return refined_secrets, acc_names

    def verify_inputs(self):
        validation_success = True
        # Check secrets file is not empty
        if not self.secrets_file:
            logging.warning("No secrets contained in secrets file")
            validation_success = False
        # Check keys and secrets have proper format
        for acc in self.secrets_file:
            if not acc.startswith("ronin:"):
                logging.critical(f"Public address {acc} needs to start with ronin:")
                validation_success = False
            if len(self.secrets_file[acc]) != 66 or self.secrets_file[acc][:2] != "0x":
                logging.critical(f"Private key for account {acc} is not valid, please review it!")
                validation_success = False
        if not validation_success:
            sys.exit()
        logging.info("Secret file correctly validated")

    def execute(self):
        qrcode_list = [
            QRCode(
                account=acc,
                private_key=self.secrets_file[acc],
                acc_name=self.acc_names[acc],
                path=self.path
            ) for acc in self.secrets_file
        ]
        for qr in qrcode_list:
            qr.generate_qr()
