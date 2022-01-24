from botbuilder.dialogs import (ComponentDialog, DialogContext, DialogTurnResult, DialogTurnStatus, TextPrompt,
                                WaterfallDialog, WaterfallStepContext, ChoicePrompt, Choice, AttachmentPrompt)
from botbuilder.schema import ActivityTypes, HeroCard, InputHints, CardAction, ActionTypes, AttachmentData, Attachment, \
    CardImage
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts.prompt_options import PromptOptions
from botbuilder.dialogs.prompts import PromptValidatorContext
from botbuilder.dialogs.prompts import ConfirmPrompt
import requests
#Inserire bean
from botbuilder.core.card_factory import CardFactory
from typing import List
import time
import json
import re
from bs4 import BeautifulSoup
import urllib3
from colorthief import ColorThief

import utils_telegram
from config import DefaultConfig
from data_models import WishListBean
import colorsys
import random
from io import BytesIO
import requests
from data_models.databaseManager import UserDAO
from data_models.user_profile_bean import UserProfile
from .luis_color_dialog import LuisColorDialog

#Azure computer vision

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
from datetime import date, datetime

#Variabili Globali utili
# colori = ["Rosso", "Rosso Arancio", "Arancio", "Giallo Arancio",
#               "Giallo", "Giallo Verde", "Verde", "Blu Verde", "Blu",
#               "Blu Viola", "Viola", "Rosso Viola"]
colori = ["rosso", "cachi", "arancione", "giallo%20o%20arancione",
              "giallo", "giallo%20o%20verde", "verde", "blu%20o%20verde", "blu",
              "blu%20o%20viola", "viola", "rosso%20o%20viola"]
Array_corpo = []

Rosso = [255, 0, 0]
RossoArancio = [255, 63, 0]
Arancio = [255, 128, 0]
GialloArancio = [255, 191, 0]
Giallo = [255, 255, 0]
GialloVerde = [128, 255, 0]
Verde = [0, 255, 0]
BluVerde = [0, 255, 255]
Blu = [0, 0, 255]
BluViola = [128, 0, 255]
Viola = [128, 0, 128]
RossoViola = [255, 0, 128]

listaColoriItten = []
listaColoriItten.append(Rosso)
listaColoriItten.append(RossoArancio)
listaColoriItten.append(Arancio)
listaColoriItten.append(GialloArancio)
listaColoriItten.append(Giallo)
listaColoriItten.append(GialloVerde)
listaColoriItten.append(Verde)
listaColoriItten.append(BluVerde)
listaColoriItten.append(Blu)
listaColoriItten.append(BluViola)
listaColoriItten.append(Viola)
listaColoriItten.append(RossoViola)

CONFIG = DefaultConfig()
luis_color= LuisColorDialog()

computervision_client = ComputerVisionClient(CONFIG.COMP_VIS_Endpoint, CognitiveServicesCredentials(CONFIG.COMP_VIS_Subscription_key))

#class FindAMatchDialog(ExitValidateDialog):
class FindAMatchDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(FindAMatchDialog, self).__init__(dialog_id or FindAMatchDialog.__name__)

        self.luis_color_id = luis_color.id

        #print("prova: "+str(dialog_id))
        self.codice=str(dialog_id)
        self.wish=[]
        # self.add_dialog(TextPrompt("TextPromptSito", FindAMatchDialog.validateSite))
        # self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__, FindAMatchDialog.yes_noValidator))
        if str(dialog_id)=="abbina":
            self.add_dialog(
                WaterfallDialog(
                    "WFDialog", [self.first_step,
                                 self.sex_step,
                                 self.clothes_step,
                                 self.photo_step,
                                 self.confirm_step,
                                 self.match_step,
                                 self.save_or_end_step,

                                 ]
                )
            )
        else:
            self.add_dialog(
                WaterfallDialog(
                    "WFDialog", [self.first_step,
                                 self.sex_step,
                                 self.chose_color_step,
                                 self.redirect_step,
                                 self.match_step,
                                 self.save_or_end_step,

                                 ]
                )
            )
        self.add_dialog(TextPrompt("Vestito", FindAMatchDialog.validateScelta))
        #self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            AttachmentPrompt(
                AttachmentPrompt.__name__, FindAMatchDialog.picture_prompt_validator
            )
        )
        self.add_dialog(luis_color)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.initial_dialog_id = "WFDialog"

    async def first_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        #print("dove sono: " + str(self.codice))
        return await step_context.prompt(

            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Hai già un capo d'abbigliamento da cui partire?"),
                choices=[Choice("Si"), Choice("No")],
            ),
        )

    async def sex_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        risposta = step_context.result.value
        if risposta == "Si":
            if str(self.codice) == "crea":
                info_card = CardFactory.hero_card(HeroCard(text="Seleziona l'opzione 'Trova corrispondenza' ",
                                                           buttons=[
                                                               CardAction(
                                                                   type=ActionTypes.im_back,
                                                                   title="Torna al menu",
                                                                   value="menu"
                                                               )
                                                           ],
                                                           ))
                resp = MessageFactory.attachment(info_card)
                await step_context.context.send_activity(resp)
                # return await step_context.next([])
                return await step_context.end_dialog()
            else:
                return await step_context.prompt(
                    ChoicePrompt.__name__,
                    PromptOptions(
                        prompt=MessageFactory.text("Prima di iniziare indica il sesso del soggetto della foto"),
                        choices=[Choice("Uomo"), Choice("Donna")],

                    ),
                )
        elif risposta == "No":
            if str(self.codice) == "crea":
                return await step_context.prompt(
                    ChoicePrompt.__name__,
                    PromptOptions(
                        prompt=MessageFactory.text("Prima di iniziare, indica il sesso del soggetto per il quale stai creando l'abbigliamento"),
                        choices=[Choice("Uomo"), Choice("Donna")],

                    ),
                )
            else:
                info_card = CardFactory.hero_card(HeroCard(text="Seleziona l'opzione 'Crea outfit' ",
                                                           buttons=[
                                                               CardAction(
                                                                   type=ActionTypes.im_back,
                                                                   title="Torna al menu",
                                                                   value="menu"
                                                               )
                                                           ],
                                                           ))
                resp = MessageFactory.attachment(info_card)
                await step_context.context.send_activity(resp)
                # return await step_context.next([])
                return await step_context.end_dialog()

    async def clothes_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        sex = step_context.result.value
        if sex=="Uomo":
            step_context.values["sesso"]="?child_cat_id=2026"
        elif sex=="Donna":
            step_context.values["sesso"] = "?child_cat_id=2030"
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    "Seleziona a quale parte del corpo appartiene il vestito già in tuo possesso"),
                choices=[Choice("Gambe"), Choice("Busto"), Choice("Testa")],

            ),
        )

    async def photo_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["Zona_Corpo"] = step_context.result.value

        # WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt
        # Dialog.
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                "Invia una foto di te con il tuo capo d'abbigliamento indossato."
            ),
            retry_prompt=MessageFactory.text(
                "Il file deve essere jpeg/png."
            ),
        )
        return await step_context.prompt(AttachmentPrompt.__name__, prompt_options)

        # return await step_context.prompt(
        #     TextPrompt.__name__,
        #     PromptOptions(prompt=MessageFactory.text("Invia una foto del tuo capo d'abbigliamento")),
        # )
    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["picture"] = (
            None if not step_context.result else step_context.result[0]
        )
        step_context.values["url_picture"] = (
            None if not step_context.result else step_context.result[0].content_url
        )
        # await step_context.context.send_activity(
        #     MessageFactory.text(str(step_context.values["url_picture"]))
        # )
        # WaterfallStep always finishes with the end of the Waterfall or
        # with another dialog; here it is a Prompt Dialog.
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Va bene questa foto?")),
        )

    async def chose_color_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        sex = step_context.result.value
        if sex == "Uomo":
            step_context.values["sesso"] = "?child_cat_id=2026"
        elif sex == "Donna":
            step_context.values["sesso"] = "?child_cat_id=2030"
        card = HeroCard(
            text="Scegli un colore tra i seguenti, se non sai che colore scegliere, seleziona 'Sono indeciso'",
            buttons=[
                CardAction(
                    type=ActionTypes.im_back,
                    # il bot spiega all'utente in cosa è specializzato
                    title="Arancione",
                    value="Arancione"
                ),

                CardAction(
                    type=ActionTypes.im_back,
                    title="Blu",
                    value="Blu"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Giallo",
                    value="Giallo"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Rosso",
                    value="Rosso"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Verde",
                    value="Verde"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Viola",
                    value="Viola"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Bianco",
                    value="Bianco"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Nero",
                    value="Nero"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Sono Indeciso",
                    value="Indeciso"
                )

            ],
        )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )

    async def redirect_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # colori = ["Rosso", "Rosso Arancio", "Arancio", "Giallo Arancio",
        #               "Giallo", "Giallo Verde", "Verde", "Blu Verde", "Blu",
        #               "Blu Viola", "Viola", "Rosso Viola"]
        option = step_context.result
        if option == "Arancione":
            return await step_context.next(2)
        elif option == "Blu":
            return await step_context.next(8)
        elif option == "Giallo":
            return await step_context.next(4)
        elif option == "Rosso":
            return await step_context.next(0)
        elif option == "Verde":
            return await step_context.next(6)
        elif option == "Viola":
            return await step_context.next(10)
        if option == "Bianco":
            return await step_context.next(-1)
        if option == "Nero":
            return await step_context.next(-1)
        if option == "Indeciso":
            return await step_context.begin_dialog(self.luis_color_id)
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Opzione non esistente, sceglierne una corretta")
            )
            info_card = CardFactory.hero_card(HeroCard(
                                                       buttons=[
                                                           CardAction(
                                                               type=ActionTypes.im_back,
                                                               title="Ho capito",
                                                               value="restart"
                                                           )
                                                       ],
                                                       ))
            resp = MessageFactory.attachment(info_card)
            await step_context.context.send_activity(resp)
            # return await step_context.next([])
            return await step_context.end_dialog()

    async def match_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        indiceClasse = 0
        HSV = []
        corpo = ""
        if str(self.codice) == "abbina":
            if step_context.result:
                if step_context.values["picture"]:
                    await step_context.context.send_activity(
                        MessageFactory.attachment(
                            step_context.values["picture"], "Hai inviato questa foto"
                        )
                    )
                else:
                    await step_context.context.send_activity(
                        "L'immagine è stata salvata, ma non riesco a mostrarla"
                    )
            else:
                # await step_context.context.send_activity(
                #     MessageFactory.text("Verrai re-indirizzato al menu. La foto non verrà salvata")
                # )
                info_card = CardFactory.hero_card(HeroCard(text=utils_telegram.replace_escapes("Verrai re-indirizzato al menu. La foto non verrà salvata"),
                    buttons=[
                        CardAction(
                            type=ActionTypes.im_back,
                            title="Ho capito",
                            value="restart"
                        )
                    ],
                ))
                resp = MessageFactory.attachment(info_card)
                await step_context.context.send_activity(resp)
                return await step_context.end_dialog()

            #algoritmo itten con compressione pixcel
            file_name=round(time.time() * 1000)
            url=str(step_context.values["url_picture"])
            # image=step_context.values["picture"]
            #image=Image.open(url)


            response = requests.get(url)
            image = Image.open(BytesIO(response.content))


            temp_file_name=str(file_name)+str(random.randint(0,100))+".jpg"
            # image.thumbnail((150, 150))
            image.save(temp_file_name)

            # test 2
            local_image = open(temp_file_name, "rb")
            detect_objects_results_local = computervision_client.detect_objects_in_stream(local_image)

            stringa_AI_obj = ""
            crop_par=[]
            if (len(detect_objects_results_local.objects) == 0):
                await step_context.context.send_activity(
                    MessageFactory.text("In questa foto non riesco a capire bene se qualcuno sta indossando un vestito, la prossima volta invia una foto migliore(il bot continua...)")
                )
            else:
                for object in detect_objects_results_local.objects:
                    #(left, upper, right, lower)
                    crop_par.append(object.rectangle.x)
                    crop_par.append(object.rectangle.w)
                    crop_par.append(object.rectangle.y)
                    crop_par.append(object.rectangle.h)
                    stringa_AI_obj = stringa_AI_obj + "object at location x{}, w{}, y{}, h{}".format(object.rectangle.x,object.rectangle.x + object.rectangle.w,object.rectangle.y,object.rectangle.y + object.rectangle.h)
                    break



            local_image.close()

            if (len(detect_objects_results_local.objects) != 0):
                image = Image.open(temp_file_name)

                left = crop_par[0]
                top = crop_par[2]
                right = crop_par[0]+crop_par[1]
                bottom = crop_par[2]+crop_par[3]
                cropped_image = image.crop((left+int((crop_par[1]/12)), top, right-int((crop_par[1]/12)), bottom-int((crop_par[3]/20))))
                #image.resize((150, 150))
                cropped_image.save(temp_file_name)
                cropped_image.close()

                image = Image.open(temp_file_name)
                width, height = image.size

                corpo = step_context.values["Zona_Corpo"]
                if(corpo =="Gambe"):
                    cropped_image = image.crop((0, int(height / 2), width, height))
                elif(corpo== "Busto"):
                    cropped_image = image.crop((0, int(height / 5), width, int(height / 2)))
                elif (corpo == "Testa"):
                    cropped_image = image.crop((0,0, width, int(height/4)))

                cropped_image.save(temp_file_name)
                cropped_image.close()

            ###


            color_thief = ColorThief(temp_file_name)
            firstColor = color_thief.get_color(quality=1)
            # paletta = color_thief.get_palette(color_count=2, quality=1)
            ####################
            os.remove(temp_file_name)



        #itten
            indiceClasse = restituisciClasseItten(firstColor[0], firstColor[1], firstColor[2])
            HSV = restituisciLivelloHSV(firstColor[0], firstColor[1], firstColor[2])
        colore_itten=""
        colore_non_itten=""
        if str(self.codice) == "abbina":
            colore_itten=restituisciAbbinamento(HSV[0],HSV[1],indiceClasse)
            colore_non_itten=printColoreId(indiceClasse)
        elif str(self.codice) == "crea":
            colore_itten = restituisciAbbinamento(4, 4, int(step_context.result))
            colore_non_itten = printColoreId(int(step_context.result))


        #creo link shein
        # gambe: pantaloni, gonna, jeans, leggins
        # busto: maglietta, maglione, giacca, giubbotto, cappotto, camicia, smoking
        # testa: cappello, berretto, bandana, sciarpa
        #class images: image-fade-out \\ falcon-lazyload



        # today = date.today()
        # data_attuale = today.strftime("%d/%m/%Y")
        id_stagione=None#primavera:1, estate:2,autunno:3,inverno:4
        doy = datetime.today().timetuple().tm_yday
        # "day of year" ranges for the northern hemisphere
        spring = range(80, 172)
        summer = range(172, 264)
        fall = range(264, 355)
        # winter = everything else
        # primavera: #autunno: felpa, camicia, t-shirt
        # jeans, pantalone
        # cappello
        # estate:camicia, t-shirt
        # pantalon e jeans corti
        # leggins
        # inverno:giubbotto, cappotto, maglione, maglioncino, dolcevita
        #
        #
        array_indumenti_testa = []
        array_indumenti_busto = []
        array_indumenti_gambe = []
        if doy in spring:
            array_indumenti_testa.append("cappello")

            array_indumenti_busto.append("felpa")
            array_indumenti_busto.append("camicia")
            array_indumenti_busto.append("t-shirt")

            array_indumenti_gambe.append("jeans")
            array_indumenti_gambe.append("pantalone%20lungo")
        elif doy in summer:
            array_indumenti_testa.append("cappello")
            array_indumenti_testa.append("occhiali")

            array_indumenti_busto.append("camicia")
            array_indumenti_busto.append("t-shirt")

            array_indumenti_gambe.append("jeans")
            array_indumenti_gambe.append("pantaloncini")
        elif doy in fall:
            array_indumenti_testa.append("cappello")

            array_indumenti_busto.append("felpa")
            array_indumenti_busto.append("camicia")
            array_indumenti_busto.append("t-shirt")

            array_indumenti_gambe.append("jeans")
            array_indumenti_gambe.append("pantalone%20lungo")
        else:# winter
            array_indumenti_testa.append("cappello")

            array_indumenti_busto.append("giubbotto")
            array_indumenti_busto.append("cappotto")
            array_indumenti_busto.append("maglione")
            array_indumenti_busto.append("dolcevita")

            array_indumenti_gambe.append("jeans")
            array_indumenti_gambe.append("pantalone%20lungo")

        # inverno:giubbotto, cappotto, maglione, maglioncino, dolcevita
        # await step_context.context.send_activity(
        #     MessageFactory.text("Indice Classe:" + str(indiceClasse) + " - Colore riconosciuto: " + printColoreId(
        #         indiceClasse) + "\n" + "Abbinamento:" + "https://it.shein.com/pdsearch/uomo%20cappello%20" + colore_itten + "?tag_ids=4000691&sort=9"
        #                         )
        # cappello=pantalone e maglia diversa
        link_shein_init = "https://it.shein.com/pdsearch/"
        link_shein_end1=""
        link_shein_end2 = ""
        link_shein_mid1=""
        link_shein_mid2 = ""

        link_shein_end3 = ""
        link_shein_mid3 = ""
        if str(self.codice) == "abbina":
            if (corpo == "Testa"):#consiglio  busto con Itten e gambe con lo stesso colore di testa
                indice_busto=random.randint(0, len(array_indumenti_busto)-1)
                indice_gambe = random.randint(0, len(array_indumenti_gambe)-1)

                link_shein_mid1=array_indumenti_busto[indice_busto]
                link_shein_mid2=array_indumenti_gambe[indice_gambe]

                link_shein_end1 = "%20" + colore_itten + str(step_context.values["sesso"])
                link_shein_end2 = "%20" + colore_non_itten + str(step_context.values["sesso"])
            elif (corpo == "Busto"):#consiglio  gambe e testa con Itten
                indice_testa = random.randint(0, len(array_indumenti_testa) - 1)
                indice_gambe = random.randint(0, len(array_indumenti_gambe) - 1)

                link_shein_mid1 = array_indumenti_testa[indice_testa]
                link_shein_mid2 = array_indumenti_gambe[indice_gambe]

                link_shein_end1 = "%20" + colore_itten
                link_shein_end2 = "%20" + colore_itten + str(step_context.values["sesso"])
            elif (corpo == "Gambe"):#consiglio  busto con Itten e testa con lo stesso colore di gambe
                indice_testa = random.randint(0, len(array_indumenti_testa) - 1)
                indice_busto = random.randint(0, len(array_indumenti_busto) - 1)

                link_shein_mid1 = array_indumenti_testa[indice_testa]
                link_shein_mid2 = array_indumenti_busto[indice_busto]

                link_shein_end1 = "%20" + colore_non_itten
                link_shein_end2 = "%20" + colore_itten + str(step_context.values["sesso"])
        else:
            #crea outfit
            indice_testa = random.randint(0, len(array_indumenti_testa) - 1)
            indice_busto = random.randint(0, len(array_indumenti_busto) - 1)
            indice_gambe = random.randint(0, len(array_indumenti_gambe) - 1)

            link_shein_mid1 = array_indumenti_testa[indice_testa]
            link_shein_mid2 = array_indumenti_busto[indice_busto]
            link_shein_mid3 = array_indumenti_gambe[indice_gambe]
            if random.randint(0,1):
                link_shein_end1 = "%20" + colore_itten
                link_shein_end2 = "%20" + colore_non_itten + str(step_context.values["sesso"])
                link_shein_end3 = "%20" + colore_itten + str(step_context.values["sesso"])
            else:
                link_shein_end1 = "%20" + colore_non_itten
                link_shein_end2 = "%20" + colore_itten + str(step_context.values["sesso"])
                link_shein_end3 = "%20" + colore_non_itten + str(step_context.values["sesso"])




        link_shein_finale1 = link_shein_init + link_shein_mid1 + link_shein_end1
        link_shein_finale2 = link_shein_init + link_shein_mid2 + link_shein_end2
        #print(link_shein_finale1)
        #print(link_shein_finale2)
        link_shein_finale3=""
        if str(self.codice) == "crea":
            link_shein_finale3 = link_shein_init + link_shein_mid3 + link_shein_end3
            #print(link_shein_finale3)
        #da aggiustare

        #?child_cat_id=1977 maglione uomo
        #?child_cat_id=2030 abbigliamento donna
        #?child_cat_id=2026 uomo



        # http_pool = urllib3.connection_from_url(link_shein_end)
        # r = http_pool.urlopen('GET', link_shein_end)
        # pagina=r.data.decode('utf-8')
        i = 0
        array_results1 = None
        array_results2 = None
        array_results3 = None
        array_results1 = send_result_cards(link_shein_finale1,numero_stampe=3,indice_stampa=i)

        if not array_results1:
            array_results1 = None
            i=0
        else:
            i+=3

        array_results2 = send_result_cards(link_shein_finale2, numero_stampe=3,indice_stampa=i)
        #print(str(array_results1))
        #print(str(array_results2))
        if not array_results2:
            array_results2 = None
        else:
            i+=3

        if str(self.codice) == "crea":
            array_results3 = send_result_cards(link_shein_finale3, numero_stampe=3, indice_stampa=i)
            if not array_results3:
                array_results3 = None

        if((array_results1 is None) and  (array_results2 is None) and  (array_results3 is None)):
            no_results_card = CardFactory.hero_card(
                HeroCard(text=utils_telegram.replace_escapes("Non ho trovato dei prodotti che soddisfano i nostri criteri di colore :("),
                         buttons=[
                             CardAction(
                                 type=ActionTypes.im_back,
                                 title="Torna al menu",
                                 value="menu"
                             )
                         ],
                         ))
            resp = MessageFactory.attachment(no_results_card)
            await step_context.context.send_activity(resp)
            return await step_context.end_dialog()

        else:
            self.wish = []
            if array_results1 is not None:
                for wish in array_results1[1]:
                    self.wish.append(WishListBean(wish.__getattribute__("descrizione"),wish.__getattribute__("url_immagine"),wish.__getattribute__("url_href")))
                for stampa in array_results1[0]:

                    await step_context.context.send_activity(
                        stampa
                    )

            if array_results2 is not None:

                for wish in array_results2[1]:
                    self.wish.append(WishListBean(wish.__getattribute__("descrizione"),wish.__getattribute__("url_immagine"),wish.__getattribute__("url_href")))


                for stampa in array_results2[0]:
                    await step_context.context.send_activity(
                        stampa
                    )
            if array_results3 is not None:

                for wish in array_results3[1]:
                    self.wish.append(WishListBean(wish.__getattribute__("descrizione"),wish.__getattribute__("url_immagine"),wish.__getattribute__("url_href")))


                for stampa in array_results3[0]:
                    await step_context.context.send_activity(
                        stampa
                    )




        # return await step_context.next([])



        #pagina = requests.get("https://www.amazon.it/s?k=giubbotto+uomo").text
        # with open('text.txt', 'w', encoding='utf-8') as f:
        #     f.write(str(pagina))

        #return next step
        #return await self.save_or_end_step(step_context)

        choise_card = CardFactory.hero_card(
            HeroCard(text=utils_telegram.replace_escapes("Ti interessa proseguire?"),
                     buttons=[
                         CardAction(
                             type=ActionTypes.im_back,
                             title="Non mi interessa proseguire",
                             value="end"
                         )
                     ],
                     ))
        resp = MessageFactory.attachment(choise_card)
        # await step_context.context.send_activity(resp)
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=resp),
        )
        #return await step_context.next([])


    async def save_or_end_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if(step_context.result=="end"):
            info_card = CardFactory.hero_card(HeroCard(text=utils_telegram.replace_escapes("Verrai re-indirizzato al menu. "),
                                                       buttons=[
                                                           CardAction(
                                                               type=ActionTypes.im_back,
                                                               title="Ho capito",
                                                               value="restart"
                                                           )
                                                       ],
                                                       ))
            resp = MessageFactory.attachment(info_card)
            await step_context.context.send_activity(resp)
            return await step_context.end_dialog()
        elif str(step_context.result)[:8] == "wishlist":
            indice=int(str(step_context.result)[8:])

            selected_wish=self.wish.__getitem__(indice)

            descrizione=selected_wish.getDescrizione()
            urlImage = selected_wish.getUrlImmagine()
            urlHref = selected_wish.getUrlHref()

            id_user = step_context.context.activity.from_property.id
            user = UserDAO.searchUserById(str(id_user))
            user.wishlist.append([descrizione,urlImage,urlHref])
            utente_updated=UserProfile(id_user,user.name,user.wishlist)
            UserDAO.updateUserById(utente_updated)

            info_card = CardFactory.hero_card(HeroCard(text=utils_telegram.replace_escapes("Hai aggiunto: "+str(descrizione)+" correttamente alla wishlist"),
                                                       buttons=[
                                                           CardAction(
                                                               type=ActionTypes.im_back,
                                                               title="torna al menu",
                                                               value="menu"
                                                           )
                                                       ],
                                                       ))
            resp = MessageFactory.attachment(info_card)
            await step_context.context.send_activity(resp)
            return await step_context.end_dialog()
        else:
            info_card = CardFactory.hero_card(HeroCard(text=utils_telegram.replace_escapes("Comando non riconosciuto. Verrai re-indirizzato al menu. "),
                                                       buttons=[
                                                           CardAction(
                                                               type=ActionTypes.im_back,
                                                               title="Ho capito",
                                                               value="restart"
                                                           )
                                                       ],
                                                       ))
            resp = MessageFactory.attachment(info_card)
            await step_context.context.send_activity(resp)
            return await step_context.end_dialog()




    @staticmethod
    async def validateScelta(prompt_context: PromptValidatorContext) -> bool:
        return (
            prompt_context.recognized.succeeded
            and 3 <= len(prompt_context.recognized.value) <= 50
        )

    @staticmethod
    async def picture_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            await prompt_context.context.send_activity(
                "Nessuna immagine inviata, riprovare"
            )

            return False

        attachments = prompt_context.recognized.value

        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["image/jpeg", "image/png"]
        ]

        prompt_context.recognized.value = valid_images

        # If none of the attachments are valid images, the retry prompt should be sent.
        return len(valid_images) > 0

def send_result_cards(link_enb,numero_stampe,indice_stampa):
    pagina = requests.get(link_enb).text

    soup = BeautifulSoup(pagina, 'html.parser')

    all_links = soup.find_all("img", class_="falcon-lazyload", limit=numero_stampe)
    if len(all_links)==0:
        return []
    src_image = []#url immagine
    alt_name = []#nome prodotto
    href_links = []#url dove acquistare
    url_image_print = "https://img.ltwebstatic.com/"
    for img in all_links:
        src_image.append(url_image_print + str(img['data-src'])[22:None:None])
        alt_name.append(img['alt'])

    all_href = soup.find_all("a", class_="S-product-item__img-container j-expose__product-item-img")
    link_shein = "https://it.shein.com"
    i = 0
    for i in range(numero_stampe):
        href_links.append(link_shein + all_href.__getitem__(i)['href'])

    # array definitivo
    array_card_return = []
    array_wishlist_return = []
    for i in range(numero_stampe):
        array_card_return.append(create_wear_card(alt_name[i], href_links[i], src_image[i], i+indice_stampa))
        array_wishlist_return.append(WishListBean(alt_name[i], src_image[i],href_links[i]))

    return array_card_return,array_wishlist_return


def create_wear_card(title,link_acquisto,url_image,indice):
    subtitle = "Puoi acquistare il capo d'abbigliamento qui: "+link_acquisto
    image = CardImage(url=url_image)
    card = HeroCard(title=utils_telegram.replace_escapes(title), subtitle=subtitle, images=[image],
                    buttons=[
                        CardAction(
                            type=ActionTypes.im_back,
                            title="Aggiungi alla WishList",
                            value="wishlist"+str(indice)
                        )
                    ],
                    )

    activity = MessageFactory.attachment(CardFactory.hero_card(card))
    return activity

def restituisciLivelloHSV(r, g, b):
    hsv = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)  # Angolo, saturazione, luminosità
    saturazione = hsv[1]
    luminosità = hsv[2]
    lvlS = 0
    lvlL = 0
    if (saturazione <= 0.25):
        lvlS = 1
    elif (saturazione > 0.25 and saturazione <= 0.50):
        lvlS = 2
    elif (saturazione > 0.50 and saturazione <= 0.75):
        lvlS = 3
    elif (saturazione > 0.75):
        lvlS = 4

    if (luminosità <= 0.25):
        lvlL = 1
    elif (luminosità > 0.25 and luminosità <= 0.50):
        lvlL = 2
    elif (luminosità > 0.50 and luminosità <= 0.75):
        lvlL = 3
    elif (luminosità > 0.75):
        lvlL = 4

    return lvlS, lvlL

def printColoreId(i):
    if (i != -1):
        return colori[i]
    else:
        return "bianco%20o%20nero"

def restituisciClasseItten(r, g, b):
    # imposto saturazione e luminosità a 100%
    hsv = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
    # print("hsv"+ str(hsv))

    RGBnew = colorsys.hsv_to_rgb(hsv[0], 1, 1)
    r = round(RGBnew[0] * 255)
    g = round(RGBnew[1] * 255)
    b = round(RGBnew[2] * 255)
    # print("RGBnew: " + str(r) +" "+ str(g)+" "+ str(b))

    if (r == 255 and (g > 0 and g < 31) and (b >= 0 and b < 128)):
        return 0  # Rosso
    elif (r == 255 and (g >= 31 and g < 95) and b == 0):
        return 1  # Rosso Arancio
    elif (r == 255 and (g >= 95 and g < 159) and b == 0):
        return 2  # Arancio
    elif (r == 255 and (g >= 159 and g < 223) and b == 0):
        return 3  # Giallo Arancio
    elif ((r > 191 and r < 255) and g >= 223 and b == 0):
        return 4  # Giallo
    elif ((r > 63 and r <= 191) and g == 255 and b == 0):
        return 5  # Giallo Verde
    elif (r <= 63 and g == 255 and (b >= 0 and b < 127)):
        return 6  # Verde
    elif (r == 0 and g >= 127 and b >= 127):
        return 7  # Blu Verde
    elif ((r > 0 and r < 63) and (g >= 0 and g < 127) and b == 255):
        return 8  # Blu
    elif ((r > 63 and r < 128) and g == 0 and (b > 192 and b < 255)):
        return 9  # Blu Viola
    elif (r >= 128 and g == 0 and (b > 128 and b <= 192)):
        return 10  # Viola
    elif ((r > 128 and r < 256) and b == 0 and (b > 63 and b <= 128)):
        return 11  # Rosso Viola
    else:
        return -1  # Colore Bianco,Nero o non riconosciuto

def restituisciAbbinamento(livelloS, livelloL, classeColore):
    if (classeColore == -1):
        if (random.randint(0, 1)):
            return "bianco"
        else:
            return "nero"
    else:
        j = (classeColore + 6) % 12
        codS = ""
        codL = ""
        # controllo approfondito per un potenziale algoritmo
        # coloreReturn = listaColoriItten[j]
        # hsv = colorsys.rgb_to_hsv(coloreReturn[0] / 255., coloreReturn[1] / 255., coloreReturn[2] / 255.)
        # RGBnew = colorsys.hsv_to_rgb(hsv[0], livelloS * 0.25, livelloL * 0.25)
        # r = round(RGBnew[0] * 255)
        # g = round(RGBnew[1] * 255)
        # b = round(RGBnew[2] * 255)
        if (livelloL <= 2):
            codL = "scuro"
        elif (livelloS <= 2):
            codS = "chiaro"
        string_finale=codS+codL


        return printColoreId(j) +("" if string_finale=="" else "%20" + string_finale)

