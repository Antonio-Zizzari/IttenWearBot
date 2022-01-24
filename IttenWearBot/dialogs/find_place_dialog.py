from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState, CardFactory
from botbuilder.schema import CardImage, HeroCard, CardAction, ActionTypes, Attachment, AttachmentLayoutTypes

import utils_telegram
from config import DefaultConfig
import requests

CONFIG = DefaultConfig()


class FindPlaceDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(FindPlaceDialog, self).__init__(dialog_id or FindPlaceDialog.__name__)


        self.add_dialog(
            WaterfallDialog(
                'WFMenu',
                [
                    self.init_step,
                    self.result_step,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))

        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        self.initial_dialog_id = 'WFMenu'

    async def init_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity(
            MessageFactory.text("Questo bot ti consiglia dato un luogo, dove sono i posti migliori per fare una foto. Ed in base alle condizioni metereologiche ti consiglia se indossare abiti pesanti o leggeri")
        )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Dammi il luogo dove vorresti andare, o dove ti trovi:")),
        )

    async def result_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        locality=step_context.result
        url = f'https://atlas.microsoft.com/search/fuzzy/json?api-version=1.0&query=attrazioni%20turistiche%20{locality}&subscription-key={CONFIG.MAPS_KEY}&language=it-IT&countrySet=IT&limit=3'

        response = requests.get(url).json()
        response=response["results"]

        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.list
        for attraction in response:
            try:
                address = attraction["address"]["freeformAddress"]
            except:
                address = ""
            try:
                name = attraction["poi"]["name"]
            except:
                name = "Nome attrazione turistica non disponibile"
            card = self.create_attrazioni_card(
                name,
                address,
            )
            reply.attachments.append(card)


        await step_context.context.send_activity(reply)
        await step_context.context.send_activity(
            MessageFactory.attachment(self.create_help_card(locality))
        )
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



    def create_attrazioni_card(self, name, address) -> Attachment:
        card = HeroCard(
            title = utils_telegram.replace_escapes(name),
            text = utils_telegram.replace_escapes('Indirizzo: ' + address),
            buttons=[
                CardAction(
                    type = ActionTypes.open_url,
                    title = "Apri in Google Maps",
                    value = 'https://www.google.com/maps/dir/?api=1&destination=' + str(name).replace(' ','+') + '+' + str(address).replace(' ','+')
                )]
        )
        return CardFactory.hero_card(card)

    def create_help_card(self, locality) -> Attachment:
        url = f'https://atlas.microsoft.com/search/address/json?subscription-key={CONFIG.MAPS_KEY}&api-version=1.0&query={locality}&limit=1'
        response = requests.get(url).json()
        response = response["results"]
        lat = ""
        lon = ""
        for x in response:
            lat = str(x["position"]["lat"])
            lon = str(x["position"]["lon"])
        url=f'https://atlas.microsoft.com/weather/currentConditions/json?subscription-key={CONFIG.MAPS_KEY}&api-version=1.0&query={lat},{lon}'
        response = requests.get(url).json()
        response = response["results"]
        celsius=""
        humidity=""
        wind=""
        phrase=""
        for x in response:
            phrase=x["phrase"]
            celsius = x["realFeelTemperature"]["value"]
            humidity = x["relativeHumidity"]
            wind = x["wind"]["speed"]["value"]
            break


        risposta=""
        #caldo 26
        #tiepido 11< <25
        #freddo 10
        #wind
        #humidity
        temp_c=celsius
        risk=0
        if wind <=1:
            temp_c-=0
        elif wind <=9:
            temp_c-=1
        elif wind <= 19:
            temp_c-=3
        else:
            risk=1

        if humidity <=25:
            temp_c-=0
        elif humidity <=50:
            temp_c-=1
        elif humidity <= 75:
            temp_c-=2
        else:
            temp_c-=4

        if temp_c<-10:
            risk=1
        elif temp_c<10:
            risposta="freddo"
        elif temp_c<26:
            risposta="tiepida"
        elif temp_c<50:
            risposta="caldo"
        else:
            risk=1

        frase_finale=""

        if risk==1:
            frase_finale="Ti sconsiglio di uscire di casa o di recarti nel posto selezionato, poiché le condizioni meteo sono fuori dalla norma"
        elif risposta=="freddo":
            frase_finale="Fa freddo, ti consiglio di vestirti molto pesante"
        elif risposta=="tiepida":
            frase_finale="L'aria è tiepida, ti consiglio di vestirti leggero o con una felpa"
        elif risposta=="caldo":
            frase_finale="Fa caldo, ti consiglio di vestirti molto leggero"

        # +"C°"  +"%"   +"km/h"
        card = HeroCard(text=utils_telegram.replace_escapes(frase_finale),
                        subtitle=utils_telegram.replace_escapes(phrase+" t:"+str(celsius)+"C° umd:"+str(humidity)+"% vento:"+str(wind)+"km/h")
                     )
        return CardFactory.hero_card(card)
