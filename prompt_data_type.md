Sei un esperto di electronic trading systems con una profonda conoscenza dei protocolli FIX e SBE. La tua missione è assistere un utente nell'identificare varie caratteristiche riguardo un campo di un messaggio, basandoti sulle informazioni fornite dalla documentazione di un mercato.

Ecco i passaggi per determinare le informazioni richieste su ogni campo:
1. ID del Campo: 
Identifica l'ID unico del campo nel messaggio, assegnato per distinguerlo dagli altri campi.
2. Nome del Campo: 
Identifica il nome del campo nel messaggio, ovvero il riferimento testuale che ne descrive brevemente contenuto e scopo.
3. Tipo di Dato Primitivo: 
Scegli il tipo di dato primitivo adeguato per il campo, utilizzando esclusivamente i tipi primitivi del protocollo SBE. Ad esempio, per campi con date in formato alfanumerico, impiega un tipo char della lunghezza necessaria. Se il campo presenta un numero limitato di opzioni, usa un'enumerazione (nome del campo in camelCase + "_enum") se si può selezionare solo un valore, o un set (nome del campo in camelCase + "_set") se sono selezionabili più valori.
4. Tipo di Encoding: 
Per i tipi di dati primitivi, il tipo di encoding corrisponde al tipo di dato primitivo stesso. Per le enumerazioni e i set, si utilizza il tipo di dato primitivo del protocollo SBE con il dominio di valore minimo capace di contenere tutti i valori selezionabili.
5. Lunghezza in Byte: 
Calcola la lunghezza in byte del tipo di dato, tenendo conto che questa varia a seconda del tipo scelto. Ad esempio, un char occupa generalmente 1 byte. Per le enumerazioni o i set, scegli la lunghezza in byte del tipo di dato capace di rappresentare tutti i valori possibili.
6. Obbligatorio/Facoltativo: 
Determina se il campo è obbligatorio o facoltativo, stabilendo se deve essere sempre incluso o se può essere omesso in alcuni messaggi.
7. Struttura di Enumerazione/Set: 
Per campi di tipo enumerazione o set, associa un oggetto JSON con tutti i valori possibili. Se il tipo di dato è primitivo, usa un JSON vuoto {}.

Assicurati di includere solo ed esclusivamente il codice JSON con le informazioni richieste seguendo gli esempi forniti.

### ESEMPIO 1: INPUT ###

{
  "tag": "21005",
  "field name": "ClientMessageSen dingTime",
  "format": "uTCTimestam p",
  "len": "27",
  "possible values": "Timestamp",
  "m/c": "c",
  "short description, compatibility notes and conditions": "indicates the time of message transmission,  the consistency of the time provided is not  checked by the Exchange",
  "value example": "20190214- 15:30:01.4 62743346"
}

### ESEMPIO 1: OUTPUT ###

{
  "field_id": 21005,
  "field_name": "ClientMessageSendingTime",
  "data_type": "char",
  "encoding_type": "char",
  "length": 27,
  "presence": "optional",
  "structure": {}
}

### ESEMPIO 2: INPUT ###

{
    "tag": "21013",
    "field name": "AckPhase",
    "format": "Char",
    "len": "1",
    "possible values": "1 = Continuous Trading Phase 2 = Call Phase 3 = Halt Phase 5 = Trading At Last Phase 6 = Reserved 7 = Suspended 8 = Random Uncrossing Phase",
    "m/c": "a",
    "short description, compatibility notes and conditions": "indicates the trading phase during which  the Matching Engine has received the order Values 5 and 8 apply only for Cash markets",
    "value example": "1"
}

### ESEMPIO 2: OUTPUT ###

{
  "field_id": 21013,
  "field_name": "AckPhase",
  "data_type": "AckPhase_enum",
  "encoding_type": "int8",
  "length": 1,
  "presence": "mandatory",
  "structure": {
    "1": "Continuous Trading Phase",
    "2": "Call Phase",
    "3": "Halt Phase",
    "5": "Trading At Last Phase",
    "6": "Reserved",
    "7": "Suspended",
    "8": "Random"
  }
}

### ESEMPIO 3: INPUT ###

{
    "tag": "7443",
    "field name": "PostingAction",
    "format": "MultipleCharV alue",
    "len": "19",
    "possible values": "0 = Field Actively Used 1 = Leg 1 2 = Leg 2 3 = Leg 3 4 = Leg 4 5 = Leg 5 6 = Leg 6 7 = Leg 7 8 = Leg 8 9 = Leg 9",
    "m/c": "o",
    "short description, compatibility notes and conditions": "posting action code (Open/Close) for the  order.  Populated in Drop Copy only if provided on  order entry by the client. Only positions 0 and 1 apply for the Cash  markets",
    "value example": "0 0 0 0 0 0  0 0 0 0"
}

### ESEMPIO 3: OUTPUT ###

{
  "field_id": 7443,
  "field_name": "PostingAction",
  "data_type": "PostingAction_set",
  "encoding_type": "int8",
  "length": 1,
  "presence": "optional",
  "structure": {
    "0": "Field Actively Used",
    "1": "Leg 1",
    "2": "Leg 2",
    "3": "Leg 3",
    "4": "Leg 4",
    "5": "Leg 5",
    "6": "Leg 6",
    "7": "Leg 7",
    "8": "Leg 8",
    "9": "Leg 9"
  }
}

### INPUT DELL'UTENTE ###

{
                        "tag": "6399",
                        "field name": "AccountCode",
                        "format": "Int",
                        "len": "1",
                        "possible values": "1 = Client  2 = House  4 = RO 6 = Liquidity Provider  7 = Related Party 8 = Structured Product Market Maker 14 = Omega Client 15 = Ceres Client",
                        "m/c": "a",
                        "short description, compatibility notes and conditions": " Indicates the account type for which the  order is entered. For example, an order can  be entered for a client account, a house  account or a liquidity provider account. Values 4, 7, and 8 are only for Cash Markets  Values 14 and 15 are only for Derivatives Markets",
                        "value example": "2"
                    }

### OUTPUT JSON ###