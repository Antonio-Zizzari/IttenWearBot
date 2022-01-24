# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.schema import Attachment
import json


class WishListBean:
    def __init__(self, descrizione :str,url_immagine:str,url_href:str):
        self.descrizione = descrizione
        self.url_immagine = url_immagine
        self.url_href = url_href

    def getDescrizione(self):
        return self.descrizione
    def getUrlImmagine(self):
        return self.url_immagine
    def getUrlHref(self):
        return self.url_href

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
