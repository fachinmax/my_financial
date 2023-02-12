# Financial managerial
Progetto realizzato per permettere agli utenti di ricevere una certa tipologia di token e di gestirli in maniera programmata per far fronte alle proprie spese.
In pratica è come se fosse un diario nel quale ognuno puo impostare per ogni tipologia di spesa una quantità massima di token che non puo eccedere.
Inoltre è stato realizzato col ottica nella quale ogni azienda è proprietaria di un proprio token che li utilizza per vendere i propri prodotti e pagare i propri dipendenti: ogni persona puo' acquistare un prodotto di un azienda acquistandolo esclusivamente con il token dell'azineda stessa

## Funzionamento
Ogni utente accede al sito attraverso il suo indirizzo e chiave privata (la quale non viene salvata in nessun database); successivamente vengono riportate tutte le informazioni inerenti i token che ha disposizione: token inviati allo smart contract, token non inviati e quindi non vincolati che ha ricevuto, centri di costo e la ripartizione dei token in questi. Inoltre ci sono varie funzionalità che gli permettono di adattare la propria distribuzione e di inviare i propri token ad altri utenti.
Lo smart contract realizzato per gestire i token si basa su un token con standard ERC20 e per questo motivo ogni utente puo gestire una sola tipologia di token attraverso la pagina.
Questo progetto è adatto anche alle aziende in quanto lo smart contract che gestsce i token si basa su un solo token e ogni azienda ha il proprio token. Per questo motivo è stata implementata la funzionalità che nel caso acceda l'utente amministratore gli verranno mostrate tutti i guadagni e avrà la possibilità di creare attraverso un solo pulsante i centri di costo per ogni dipendente. Nel momento che accede un utente verrà salvato il suo indirizzo in quanto considerato dipendente dell'azienda. Inoltre in maniera simile agli utenti anche l'amministratore potrà inviare i token guadagnati ai propri dipendenti o ad altri utenti.

## Tecnologie
Per questo progetto ho utilizzato i seguenti software:
“*” Ganache
“*” MongoDB
“*” Brownie
“*” Django
e i seguenti linguaggi:
“*” python
“*” solidity
Ho utilizzato la rete Ganache come rete dove pubblicare i due smart contract: uno che utilizza lo standart ERC20 e gestisce i token dell'azienda e il secondo che funge da gestore finanziario sulla ripartizone delle spese dei token dell'utente. Mentre ho utilizzato il framework Django per la realizzazione di un sito internet che potesse far comunicare l'utente con Ganache, MongoDB come database dove salvare gli indirizzi degli utenti e degli eventi generati dai smart contract infine Brownie per la realizzazione e il test dei smart contract.

## Insallazione ed avvio
Per poter eseguire il programma bisogna installare MongoDB attraverso brew e avviare il server, successivamente bisogna pubblicare gli smart contract su Ganache attraverso Brownie e infine avviare il server di Django.
Per installare MongoDB e avviarlo lascio il link di un video che ne descive il procedimento: https://www.youtube.com/watch?v=s1WQ0eEpqqg&ab_channel=HiteshChoudhary