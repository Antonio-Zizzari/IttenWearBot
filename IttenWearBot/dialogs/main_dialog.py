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
from botbuilder.schema import HeroCard, CardAction, ActionTypes, InputHints

import utils_telegram
from .find_a_match_dialog import FindAMatchDialog
from .wish_list_dialog import WishListDialog
from data_models.databaseManager import UserDAO
from data_models.user_profile_bean import UserProfile
from .find_place_dialog import FindPlaceDialog


findmatch1=FindAMatchDialog("abbina")
findmatch2=FindAMatchDialog("crea")
wishlist=WishListDialog()
findplace=FindPlaceDialog()

class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self.find_a_match_id1 = findmatch1.id  # nuovo dialog
        self.find_a_match_id2 = findmatch2.id  # nuovo dialog

        self.wish_list_id=wishlist.id
        self.find_place_id=findplace.id


        #controllo per il loop dello stesso messaggio
        self.add_dialog(TextPrompt("Continua", MainDialog.validateContinue))#da spostare sotto



        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.is_logged_step,
                    self.menu_step,
                    self.options_step,

                ],
            )
        )

        self.add_dialog(findmatch1)#nuovo dialog
        self.add_dialog(findmatch2)  # nuovo dialog
        self.add_dialog(wishlist)
        self.add_dialog(findplace)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        # self.add_dialog(
        #     NumberPrompt(NumberPrompt.__name__, MainDialog.age_prompt_validator)
        # )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            AttachmentPrompt(
                AttachmentPrompt.__name__, MainDialog.picture_prompt_validator
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def is_logged_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        id_user = step_context.context.activity.from_property.id
        user = UserDAO.searchUserById(str(id_user))
        step_context.values["user_name"] = None if not user else user.__getattribute__('name')
        if user is None:
            choise_card = CardFactory.hero_card(
                HeroCard(text="Non sei registrato, inserisci il tuo nome",
                         ))
            resp = MessageFactory.attachment(choise_card)
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=resp),
            )
        else:
            return await step_context.next([])


    async def menu_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # WaterfallStep always finishes with the end of the Waterfall or with another dialog;
        # here it is a Prompt Dialog. Running a prompt here means the next WaterfallStep will
        # be run when the users response is received.

        # iduser = step_context.context.activity.from_property.id
        # user = DatabaseManager.find_user_info(iduser)
        # step_context.values["user"] = user

        if step_context.values["user_name"] is None:
            utente=UserProfile(step_context.context.activity.from_property.id,str(step_context.result))
            UserDAO.insertUser(utente)
            step_context.values["user_name"]=str(step_context.result)

        card = HeroCard(
            text="Ciao "+str(step_context.values["user_name"])+ ", come posso aiutarti?",
            buttons=[
                CardAction(
                    type=ActionTypes.im_back,
                    #il bot spiega all'utente in cosa è specializzato
                    title="Info",
                    value="info"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Visualizza wishlist",
                    value="wishlist"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Trova corrispondenza",
                    value="Itten0"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Crea outfit",
                    value="Itten1"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Suggerisci luoghi foto",
                    value="photo"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title="Esci",
                    value="logout"
                )
            ],
        )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )

    async def options_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result

        if option == "info":
            info_card = self.create_info_card()
            resp = MessageFactory.attachment(info_card)
            await step_context.context.send_activity(resp)
            return await step_context.next([])
        elif option == "wishlist":
            return await step_context.begin_dialog(self.wish_list_id)
        elif option == "Itten0":
            return await step_context.begin_dialog(self.find_a_match_id1)
        elif option == "Itten1":
            return await step_context.begin_dialog(self.find_a_match_id2)
        elif option == "photo":
            return await step_context.begin_dialog(self.find_place_id)
        elif option == "logout":
            await step_context.context.send_activity("Spegnimento... per riprendere scrivi al bot")
            return await step_context.cancel_all_dialogs()
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
            # await step_context.context.send_activity("Testo errato, digitare qualsiasi cosa per riprendere")
            # return await step_context.end_dialog()
            #return await step_context.reprompt_dialog()




    def create_info_card(self):
        title = utils_telegram.replace_escapes("Ciao sono IttenWearBot")

        subtitle = utils_telegram.replace_escapes("Ecco cosa posso fare per te...")
        text = utils_telegram.replace_escapes('''Sono un bot dotato di AI che ti permette di:\n\n- Trovare un abbinamento basato su di un capo d'abbigliamento già in tuo possesso, analizzarne il colore, e trovare l'abbinamento adatto.\n- Creare una wishlist dove poter inserire tutti i possibili capi che ti interessano.\n- Nel caso in cui non si voglia specificare un capo d'abbigliamento, è possibile creare un outfit da zero scegliendo un colore di base dal quale partire.\n- Posso mantenere sotto osservazione i capi d'abbigliamento da acquistare della tua wishlist e avvisarti se cambiano di prezzo.\n- Posso indicarti suggerimenti su dei luoghi nei quali puoi scattare foto in base all'outfit e in base al luogo in cui ti trovi.\n\nPuoi partire utilizzando il bottone 'Continua'. :)''')
        card = CardFactory.hero_card(HeroCard(title=title, subtitle=subtitle, text=text,
                                              buttons=[
                                                  CardAction(
                                                      type=ActionTypes.im_back,
                                                      title="Continua",
                                                      value="continue"
                                                  )
                                              ],
                                              ))
        return card

    @staticmethod
    async def validateContinue(prompt_context: PromptValidatorContext) -> bool:
        return (
                prompt_context.recognized.succeeded
                #and prompt_context.recognized.value == "continue"
        )


    @staticmethod
    async def picture_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            await prompt_context.context.send_activity(
                "Nessuna foto inviata..."
            )

            # We can return true from a validator function even if recognized.succeeded is false.
            return True

        attachments = prompt_context.recognized.value

        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["image/jpeg", "image/png"]
        ]

        prompt_context.recognized.value = valid_images

        # If none of the attachments are valid images, the retry prompt should be sent.
        return len(valid_images) > 0
