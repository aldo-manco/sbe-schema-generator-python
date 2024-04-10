Sei un esperto in sistemi di trading elettronico con una profonda conoscenza dei protocolli FIX e SBE. La tua missione e identificare varie caratteristiche riguardo una lista di campi di un messaggio, basandoti sulle informazioni fornite dalla documentazione di un mercato.

Ecco i passaggi per determinare le informazioni richieste per ogni campo:
1. ID del Campo: 
Identifica l'ID unico del campo nel messaggio, assegnato per distinguerlo dagli altri campi.
2. Nome del Campo: 
Identifica il nome del campo nel messaggio, ovvero il riferimento testuale che ne descrive brevemente contenuto e scopo.
3. Tipo di Dato Primitivo: 
Scegli il tipo di dato primitivo adeguato per il campo, utilizzando esclusivamente i tipi primitivi del protocollo SBE. Ad esempio, per campi con date in formato alfanumerico, impiega un tipo char della lunghezza necessaria. Se il campo presenta un numero limitato di opzioni, usa un'enumerazione (nome del campo in camelCase + "_enum") se si puo selezionare solo un valore, o un set (nome del campo in camelCase + "_set") se sono selezionabili piu valori.
4. Tipo di Encoding: 
Per i tipi di dati primitivi, il tipo di encoding corrisponde al tipo di dato primitivo stesso. Per le enumerazioni e i set, si utilizza il tipo di dato primitivo del protocollo SBE con il dominio di valore minimo capace di contenere tutti i valori selezionabili.
5. Lunghezza in Byte: 
Calcola la lunghezza in byte del tipo di dato, tenendo conto che questa varia a seconda del tipo scelto. Ad esempio, un char occupa generalmente 1 byte. Per le enumerazioni o i set, scegli la lunghezza in byte del tipo di dato capace di rappresentare tutti i valori possibili.
6. Obbligatorio/Facoltativo: 
Determina se il campo e obbligatorio o facoltativo, stabilendo se deve essere sempre incluso o se puo essere omesso in alcuni messaggi.
7. Struttura di Enumerazione/Set: 
Per campi di tipo enumerazione o set, associa un oggetto JSON con tutti i valori possibili. Se il tipo di dato e primitivo, usa un JSON vuoto {}.

Assicurati di includere solo ed esclusivamente un array JSON nel codice fornito. Questo array dovrà contenere, per ciascun campo del messaggio, un oggetto JSON con le informazioni richieste. Segui gli esempi che ti sono stati forniti.

### ESEMPIO 1: INPUT ###

[
  {
	"tag": "21005",
	"field name": "ClientMessageSen dingTime",
	"format": "uTCTimestam p",
	"len": "27",
	"possible values": "Timestamp",
	"m/c": "c",
	"short description, compatibility notes and conditions": "indicates the time of message transmission,  the consistency of the time provided is not  checked by the Exchange",
	"value example": "20190214- 15:30:01.4 62743346"
  },
  {
    "Tag": "11",
    "Field Name": "ClOrdID",
    "Format": "String",
    "Len": "20",
    "Possible Values": "From -2^63 to 2^63-1",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Identifier of an Order Modification message assigned by the Client when submitting the order modification message to the Exchange",
    "Value Example": "25"
  },
  {
    "Tag": "21013",
    "Field Name": "AckPhase",
    "Format": "Char",
    "Len": "1",
    "Possible Values": "1 = Continuous Trading Phase 2 = Call Phase 3 = Halt Phase 5 = Trading At Last Phase 6 = Reserved 7 = Suspended 8 = Random Uncrossing Phase",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Indicates the trading phase during which the Matching Engine has received the order Values 5 and 8 apply only for Cash markets",
    "Value Example": "1"
  },
  {
    "Tag": "21014",
    "Field Name": "AckQualifiers",
    "Format": "MultipleCharValue",
    "Len": "15",
    "Possible Values": "0 = Dark Indicator 1 = Queue Indicator 2 = Request with Client Order ID 3 = Use of Cross Partition 4 = Internal1 5 = Internal2 6 = Execution Upon Entry flag Enabled 7 = Executed Upon Entry flag",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Field used to provide additional information on the corresponding order. For Derivatives positions 0 is not applicable and is always set to 0.",
    "Value Example": "0 0 0 0 0 0 0 0"
  }
]

### ESEMPIO 1: OUTPUT ###

[
  {
    "field_id": 21005,
    "field_name": "ClientMessageSendingTime",
    "data_type": "char",
    "encoding_type": "char",
    "length": 27,
    "presence": "optional",
    "structure": {}
  },
  {
    "field_id": 11,
    "field_name": "ClOrdID",
    "data_type": "int64",
    "encoding_type": "int64",
    "length": 8,
    "presence": "mandatory",
    "structure": {}
  },
  {
    "field_id": 21013,
    "field_name": "AckPhase",
    "data_type": "ackPhase_enum",
    "encoding_type": "char",
    "length": 1,
    "presence": "mandatory",
    "structure": {
      "1": "Continuous Trading Phase",
      "2": "Call Phase",
      "3": "Halt Phase",
      "5": "Trading At Last Phase",
      "6": "Reserved",
      "7": "Suspended",
      "8": "Random Uncrossing Phase"
    }
  },
  {
    "field_id": 21014,
    "field_name": "AckQualifiers",
    "data_type": "ackQualifiers_set",
    "encoding_type": "char",
    "length": 15,
    "presence": "mandatory",
    "structure": {
      "0": "Dark Indicator",
      "1": "Queue Indicator",
      "2": "Request with Client Order ID",
      "3": "Use of Cross Partition",
      "4": "Internal1",
      "5": "Internal2",
      "6": "Execution Upon Entry flag Enabled",
      "7": "Executed Upon Entry flag"
    }
  }
]

### ESEMPIO 2: INPUT ###

[
  {
    "Offset": "0",
    "Field": "MsgSize",
    "Format": "Uint16",
    "Len": "2",
    "Description": "Size of the message",
    "Values": "N/A"
  },
  {
    "Offset": "8",
    "Field": "SecurityTradingStatus",
    "Format": "Uint8",
    "Len": "1",
    "Description": "Identifies the trading status of a security.",
    "Values": "2 Trading Halt, 3 Resume"
  },
  {
    "Offset": "12",
    "Field": "TradingPhaseCode",
    "Format": "String",
    "Len": "8",
    "Description": "Identify the trading state of the security",
    "Values": "Please refer to the TradingPhaseCode information in SSE market data of this security for details. N/A for SZSE Instruments"
  }
]

### ESEMPIO 2: OUTPUT ###

[
  {
    "field_id": 0,
    "field_name": "MsgSize",
    "data_type": "uint16",
    "encoding_type": "uint16",
    "length": 2,
    "presence": "mandatory",
    "structure": {}
  },
  {
    "field_id": 8,
    "field_name": "SecurityTradingStatus",
    "data_type": "SecurityTradingStatus_enum",
    "encoding_type": "uint8",
    "length": 1,
    "presence": "mandatory",
    "structure": {
      "2": "Trading Halt",
      "3": "Resume"
    }
  },
  {
    "field_id": 12,
    "field_name": "TradingPhaseCode",
    "data_type": "char",
    "encoding_type": "char",
    "length": 8,
    "presence": "mandatory",
    "structure": {}
  }
]

### ESEMPIO 3: INPUT ###

[
  {
    "Field": "SEDOL",
    "Offset": "31",
    "Length": "8",
    "Type": "Alpha",
    "Description": "SEDOL code of the instrument."
  },
  {
    "Field": "Allowed Book Types",
    "Offset": "39",
    "Length": "1",
    "Type": "Bit Field",
    "Description": "Defines the order-book types that are allowed for the instrument. Each designated bit represents a book type. 0 Means not allowed and 1 means allowed: Bit Name 0 All 1 Firm Quote Book 2 Off-book 3 Electronic Order Book 4 Private RFQ"
  },
  {
    "Field": "Source Venue",
    "Offset": "40",
    "Length": "2",
    "Type": "UInt16",
    "Description": "Please refer the Additional Field Values section of this document for valid values."
  },
  {
    "Field": "Settlement System",
    "Offset": "146",
    "Length": "1",
    "Type": "UInt8",
    "Description": "Settlement system type: Value Meaning 1 RRG 2 Express I 3 Express II 4 Clear stream 5 Undefined value 6 T2S"
  }
]

### ESEMPIO 3: OUTPUT ###

[
  {
    "field_id": 31,
    "field_name": "SEDOL",
    "data_type": "char",
    "encoding_type": "char",
    "length": 8,
    "presence": "mandatory",
    "structure": {}
  },
  {
    "field_id": 39,
    "field_name": "AllowedBookTypes",
    "data_type": "allowedBookTypes_set",
    "encoding_type": "uint8",
    "length": 1,
    "presence": "mandatory",
    "structure": {
      "0": "All",
      "1": "Firm Quote Book",
      "2": "Off-book",
      "3": "Electronic Order Book",
      "4": "Private RFQ"
    }
  },
  {
    "field_id": 40,
    "field_name": "SourceVenue",
    "data_type": "uint16",
    "encoding_type": "uint16",
    "length": 2,
    "presence": "mandatory",
    "structure": {}
  },
  {
    "field_id": 146,
    "field_name": "SettlementSystem",
    "data_type": "settlementSystem_enum",
    "encoding_type": "uint8",
    "length": 1,
    "presence": "mandatory",
    "structure": {
      "1": "RRG",
      "2": "Express I",
      "3": "Express II",
      "4": "Clearstream",
      "5": "Undefined value",
      "6": "T2S"
    }
  }
]

### INPUT ###

[
  {
    "Tag": 21005,
    "Field Name": "ClientMessageSendingTime",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates the time of message transmission, the consistency of the time provided is not checked by the Exchange.",
    "Value Example": "20190214-15:30:01.462743346"
  },
  {
    "Tag": 5979,
    "Field Name": "OEGINFromMember",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Order Entry Gateway IN time from member (in ns), measured when inbound message enters the gateway.",
    "Value Example": "20190214-15:28:52.833883664"
  },
  {
    "Tag": 7764,
    "Field Name": "OEGOUTToME",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Gateway OUT time to ME (in ns), measured when inbound message leaves the gateway.",
    "Value Example": "20190214-15:28:52.834193232"
  },
  {
    "Tag": 21002,
    "Field Name": "BookINTime",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Time of order creation in ME.",
    "Value Example": "20190214-15:28:52.840530924"
  },
  {
    "Tag": 21003,
    "Field Name": "BookOUTTime",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Matching Engine OUT time (in ns), when message leaves the Matching Engine (ME).",
    "Value Example": "20190214-15:28:52.840568733"
  },
  {
    "Tag": 7765,
    "Field Name": "OEGINFromME",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Gateway IN time from ME (in ns), measured when outbound message enters the gateway.",
    "Value Example": "20190214-15:28:52.833883664"
  },
  {
    "Tag": 11,
    "Field Name": "ClOrdID",
    "Format": "String",
    "Len": 20,
    "Possible Values": "From -2^63 to 2^63-1",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Identifier of an Order assigned by the Client when submitting an order to the Exchange.",
    "Value Example": "10"
  },
  {
    "Tag": 48,
    "Field Name": "SecurityID",
    "Format": "String",
    "Len": 10,
    "Possible Values": "From 0 to 2^32-2",
    "M/C": "M",
    "Short Description, Compatibility Notes & Conditions": "Exchange defined ID of an instrument/contract.",
    "Value Example": "1110530"
  },
  {
    "Tag": 22,
    "Field Name": "SecurityIDSource",
    "Format": "String",
    "Len": 1,
    "Possible Values": "8 = Symbol Index",
    "M/C": "M",
    "Short Description, Compatibility Notes & Conditions": "Type of the SecurityID. Always set to 8.",
    "Value Example": "8"
  },
  {
    "Tag": 20020,
    "Field Name": "EMM",
    "Format": "Int",
    "Len": 2,
    "Possible Values": "1 = Cash and Derivative Central Order Book (COB), 7 = Derivative On Exchange Off book, 8 = ETF MTF - NAV Central Order Book",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Exchange Market Mechanism.",
    "Value Example": "1"
  },
  {
    "Tag": 37,
    "Field Name": "OrderID",
    "Format": "String",
   

 "Len": 20,
    "Possible Values": "From 0 to 2^64-2",
    "M/C": "M",
    "Short Description, Compatibility Notes & Conditions": "Numerical order identifier assigned by ME. For acknowledgement of RFQ populated with the same value as in field QuoteReqID (131).",
    "Value Example": "5"
  },
  {
    "Tag": 39,
    "Field Name": "OrdStatus",
    "Format": "Char",
    "Len": 1,
    "Possible Values": "0 = New",
    "M/C": "M",
    "Short Description, Compatibility Notes & Conditions": "Order status.",
    "Value Example": "0"
  }
]

### OUTPUT JSON ###