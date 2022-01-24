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
from botbuilder.core import MessageFactory, UserState
from config import DefaultConfig
from bot_recognizer import BotRecognizer
from helpers.luis_helper_color import LuisHelper, Intent

CONFIG = DefaultConfig()

luis_recognizer = BotRecognizer(CONFIG)


class LuisColorDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(LuisColorDialog, self).__init__(dialog_id or LuisColorDialog.__name__)

        self._luis_recognizer = luis_recognizer
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

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Questo bot ti aiuta a capire il tuo colore preferito attraverso la psicologia dei colori. Descriviti brevemente, ed in base a ciò ti consiglierò gli abiti da indossare")),
        )

    async def result_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # chiamata a LUIS per interpretazione del testo
        intent = await LuisHelper.execute_luis_query(self._luis_recognizer, step_context.context)

        if intent == Intent.ARANCIONE.value:
            await step_context.context.send_activity("Il bot pensa che il colore più adatto alla tua personalità è: "+ str(Intent.ARANCIONE.value))
            return await step_context.end_dialog(2)

        elif intent == Intent.BIANCO.value:
            await step_context.context.send_activity(
                "Il bot pensa che il colore più adatto alla tua personalità è: " + str(Intent.BIANCO.value))
            return await step_context.end_dialog(-1)

        elif intent == Intent.BLU.value:
            await step_context.context.send_activity(
                "Il bot pensa che il colore più adatto alla tua personalità è: " + str(Intent.BLU.value))
            return await step_context.end_dialog(8)

        elif intent == Intent.GIALLO.value:
            await step_context.context.send_activity(
                "Il bot pensa che il colore più adatto alla tua personalità è: " + str(Intent.GIALLO.value))
            return await step_context.end_dialog(4)

        elif intent == Intent.NERO.value:
            await step_context.context.send_activity(
                "Il bot pensa che il colore più adatto alla tua personalità è: " + str(Intent.NERO.value))
            return await step_context.end_dialog(-1)

        elif intent == Intent.ROSSO.value:
            await step_context.context.send_activity(
                "Il bot pensa che il colore più adatto alla tua personalità è: " + str(Intent.ROSSO.value))
            return await step_context.end_dialog(0)

        elif intent == Intent.VERDE.value:
            await step_context.context.send_activity(
                "Il bot pensa che il colore più adatto alla tua personalità è: " + str(Intent.VERDE.value))
            return await step_context.end_dialog(6)

        elif intent == Intent.VIOLA.value:
            await step_context.context.send_activity(
                "Il bot pensa che il colore più adatto alla tua personalità è: " + str(Intent.VIOLA.value))
            return await step_context.end_dialog(10)

        else:
            await step_context.context.send_activity("Non ho capito bene la tua personalità, riscrivila meglio per favore")
            return await step_context.replace_dialog("WFMenu")
