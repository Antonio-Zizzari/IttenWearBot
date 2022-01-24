# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
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
from botbuilder.core import MessageFactory, TurnContext, CardFactory, UserState, BotFrameworkAdapter
from botbuilder.schema import HeroCard, CardAction, ActionTypes, InputHints, CardImage

import utils_telegram
from data_models.databaseManager import UserDAO
from data_models.user_profile_bean import UserProfile


class WishListDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(WishListDialog, self).__init__(dialog_id or WishListDialog.__name__)
        self.wish=[]
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.view_wish,
                    self.end_or_remove,

                ],
            )
        )

        self.add_dialog(TextPrompt(TextPrompt.__name__))


        self.initial_dialog_id = WaterfallDialog.__name__

    async def view_wish(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        id_user = step_context.context.activity.from_property.id
        user = UserDAO.searchUserById(str(id_user))
        i=0
        if len(user.wishlist):
            self.wish=user.wishlist
            for wear in user.wishlist:
                await step_context.context.send_activity(
                    create_wear_card(wear[0],wear[1],wear[2],i)
                )
                i+=1

            choise_card = CardFactory.hero_card(
                HeroCard(text="Ti interessa proseguire?",
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
        else:
            choise_card = CardFactory.hero_card(
                HeroCard(text="La tua wishlist è vuota",
                         buttons=[
                             CardAction(
                                 type=ActionTypes.im_back,
                                 title="Torna al menu",
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


    async def end_or_remove(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        if (step_context.result == "end"):
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

            selected_wish = self.wish.__getitem__(indice)

            descrizione = selected_wish[0]

            id_user = step_context.context.activity.from_property.id
            user = UserDAO.searchUserById(str(id_user))
            user.wishlist.pop(indice)
            utente_updated = UserProfile(id_user, user.name, user.wishlist)
            UserDAO.updateUserById(utente_updated)

            info_card = CardFactory.hero_card(HeroCard(text="Hai rimosso: "+str(descrizione)+" correttamente alla wishlist",
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

def create_wear_card(title,url_image,link_acquisto,indice):
    subtitle = utils_telegram.replace_escapes("Puoi acquistare il capo d'abbigliamento qui: ")+link_acquisto
    image = CardImage(url=url_image)
    card = HeroCard(title=utils_telegram.replace_escapes(title), subtitle=subtitle, images=[image],
                    buttons=[
                        CardAction(
                            type=ActionTypes.im_back,
                            title="Rimuovi dalla WishList",
                            value="wishlist"+str(indice)
                        )
                    ],
                    )

    activity = MessageFactory.attachment(CardFactory.hero_card(card))
    return activity