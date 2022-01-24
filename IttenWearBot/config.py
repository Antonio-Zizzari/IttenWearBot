#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    COMP_VIS_Subscription_key = os.environ.get("CompVisKey", "")
    COMP_VIS_Endpoint = os.environ.get("CompVinsEnd","")

    COSMOS_uri = ''
    COSMOS_key = ''
    COSMOS_database_name = ''
    COSMOS_container_name = ''

    LUIS_APP_ID=''
    LUIS_API_KEY=''
    LUIS_API_HOST_NAME=""

    MAPS_ID=""
    MAPS_KEY=""
