import argparse
import json
import os
import pprint
from typing import Dict

import requests
from django.conf import settings

from cl.lib.command_utils import VerboseCommand, logger


def split_tiffs(options: Dict) -> None:
    """Combine multiple page tiffs in a directory into one single PDF and extract the content.

    :param options:
    :type options: Dict
    :return:
    """
    filepath = options["filepath"]

    disclosures = [
        {
            "paths": [
                "Armstrong-SB J3. 09. CAN_R_11_Page_1.tiff",
                "Armstrong-SB J3. 09. CAN_R_11_Page_2.tiff",
                "Armstrong-SB J3. 09. CAN_R_11_Page_3.tiff",
                "Armstrong-SB J3. 09. CAN_R_11_Page_4.tiff",
                "Armstrong-SB J3. 09. CAN_R_11_Page_5.tiff",
                "Armstrong-SB J3. 09. CAN_R_11_Page_6.tiff"
            ],
            "key": "financial-disclosures/2011/A-E/Armstrong-SB J3. 09. CAN_R_11",
            "person_id": "126"
        }
    ]

    for data in disclosures:
        bucket = "storage.courtlistener.com"
        path = data['key']
        urls = [f"https://{bucket}/{path}/{p}" for p in data['paths']]

        logger.info(f"Processing images")

        pdf_response = requests.post(
            settings.BTE_URLS["urls-to-pdf"],
            json=json.dumps({"urls": urls}),
        )
        logger.info(f"Conversion completed. \n Beginning Extraction")

        extractor_response = requests.post(
            settings.BTE_URLS["extract-disclosure"],
            files={"file": ("", pdf_response.content)},
            timeout=60 * 60,
        )

        logger.info("Processing extracted data")
        pprint.pprint(extractor_response.json())


def single_tiff(options: Dict) -> None:
    """

    :param options:
    :type options: Dict
    :return:
    """
    filepath = options["filepath"]
    disclosures = [
        {
            "path": "Urbanski-MF.%20J3.%2004.%20VAW%20_SPE_R_18.tiff",
            "key": "financial-disclosures/2018",
            "person_id": "3289",
        }
    ]
    # https://storage.courtlistener.com/financial-disclosures/2018/Urbanski-MF.%20J3.%2004.%20VAW%20_SPE_R_18.tiff
    for data in disclosures:
        person_id = data["person_id"]
        bucket = "com-courtlistener-storage.s3-us-west-2.amazonaws.com"
        path = data['key']
        tiff_url = f"https://{bucket}/{path}/{data['path']}"

        logger.info(f"Preparing to process url: {tiff_url}")
        pdf_response = requests.post(
            settings.BTE_URLS["image-to-pdf"],
            params={"tiff_url": tiff_url},
            timeout=5 * 60,
        )
        logger.info(f"Conversion completed. \n Beginning Extraction")
        extractor_response = requests.post(
            settings.BTE_URLS["extract-disclosure"],
            files={"file": ("", pdf_response.content)},
            timeout=60 * 60,
        )

        logger.info("Processing extracted data")
        pprint.pprint(extractor_response.json())



def judicial_watch(options: Dict) -> None:
    """

    :param options:
    :type options: Dict
    :return:
    """
    filepath = options["filepath"]

    # url = ""
    # j = json.load(filepath)

    # -------------- ** ** ** *--------------
    # Temporary data
    disclosures = [
        {
            "path": "financial-disclosures/judicial-watch/Adalberto%20J%20Jordan%20Financial%20Disclosure%20Report%20for%202010.pdf",
            "person_id": "1905",
        }
    ]
    # -------------- ******* --------------

    for data in disclosures:
        person_id = data["person_id"]
        bucket = "com-courtlistener-storage.s3-us-west-2.amazonaws.com"
        aws_url = f"https://{bucket}/{data['path']}"
        pdf_bytes = requests.get(aws_url).content
        extractor_response = requests.post(
            settings.BTE_URLS["extract-disclosure"],
            files={"file": ("", pdf_bytes)},
            timeout=60 * 60,
        )
        # print(extractor_response.json())
        pprint.pprint(extractor_response.json())


class Command(VerboseCommand):
    help = "Add financial disclosures to CL database."

    def valid_actions(self, s):
        if s.lower() not in self.VALID_ACTIONS:
            raise argparse.ArgumentTypeError(
                "Unable to parse action. Valid actions are: %s"
                % (", ".join(self.VALID_ACTIONS.keys()))
            )
        return self.VALID_ACTIONS[s]

    def add_arguments(self, parser):
        parser.add_argument(
            "--action",
            type=self.valid_actions,
            required=True,
            help="The action you wish to take. Valid choices are: %s"
            % (", ".join(self.VALID_ACTIONS.keys())),
        )
        parser.add_argument(
            "--filepath",
            required=True,
            help="Filepath to json identifiy documents to process",
        )

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        options["action"](options)

    VALID_ACTIONS = {
        "split-tiffs": split_tiffs,
        "single-tiff": single_tiff,
        "judicial-watch": judicial_watch,
    }
