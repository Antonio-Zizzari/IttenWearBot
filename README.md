# IttenWearBot
**Autori**: 
- Antonio Zizzari
- Simone Giglio

**IttenWearBot** è un bot intelligente dotato di
sofisticate tecniche di machile learning che aiuta
gli utenti che lo utilizzano a vestirsi bene consigliando
dei vestiti da acquistare secondo alcuni criteri.

Il bot ha molte funzionalità e permette di:

-   **Trova corrispondenza**: Trovare un abbinamento basato su di un 
    capo d'abbigliamento già in tuo possesso, analizzarne il colore, 
    e trovare l'abbinamento adatto.
-   **Crea outfit**: Nel caso in cui non si voglia specificare un capo
    d'abbigliamento, è possibile creare un outfit da zero scegliendo un 
    colore di base dal quale partire.
-   **Visualizza wishlist**: Mostra i capi d'abbigliamento salvati in 
    precedenza. Permette la visualizzazione e l'eliminazione dei capi nella
    wishlist
-   **Suggerisci luoghi foto**: Suggerisce all'utente dei luoghi nei quali 
    puoi scattare foto in base al meteo del luogo in cui si trova.
## Architettura
<p align="center"><img src="./images/architettura.png"/></p>

Il bot è stato sviluppato in Python ed è stato pubblicato sul canale
Telegram ed utilizza i seguenti servizi:

-   **AppService**: Per effettuare hosting dell'applicazione su cloud.
-   **BotService**: Per sviluppare, testare e pubblicare il bot
    in Azure.
-   **Azure Cosmos DB**: Per conservare i dati persistenti relativi agli utenti
    e alle wishlist associate.    
-   **LUIS**: Per riconoscere ed interpretare la psicologia dei colori in crea outfit.
-   **Azure Computer Vision**: Per elaborare le immagini della funzione trova
    corrispondenza ed ottenere sia chi sono gli oggetti nella foto che il colore principale
-   **AzureMaps**: Quando viene suggerito un luogo incui fare le foto il servizio utilizza delle richieste https per ricevere informazioni sul posto inviato dall'utente
