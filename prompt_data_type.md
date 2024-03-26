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
    "Field Name": "HeartBtInt",
    "FIX Tag": "108",
    "Use in Drop Copy": "While FIX allows clients to set a value for Heartbeat interval, in Optiq this value will be restricted to the maximum allowed by the exchange and made available in configuration of the segment."
  },
  {
    "Field Name": "EncryptMethod",
    "FIX Tag": "98",
    "Use in Drop Copy": "Always set to zero (0)"
  },
  {
    "Field Name": "OEPartitionID",
    "FIX Tag": "21019",
    "Use in Drop Copy": "Field used, and must be specified with OE Partition ID setup for the Drop Copy gateway ID. If not provided or provided with an incorrect Drop Copy gateway ID, then the Logon will not be accepted."
  },
  {
    "Field Name": "LogicalAccessID",
    "FIX Tag": "21021",
    "Use in Drop Copy": "Field used, and must be specified with the Logical Access ID setup for the Drop Copy connection."
  },
  {
    "Field Name": "NextExpectedMsgSeqNum",
    "FIX Tag": "789",
    "Use in Drop Copy": "Mandatory to be provided. The field always indicates the sequence number of the next message the client is expecting to receive from the Drop Copy gateway. For the first logon of the day the field must be set to one (1)."
  },
  {
    "Field Name": "Queueing Indicator",
    "FIX Tag": "21020",
    "Use in Drop Copy": "Mandatory to be provided and while it won’t be functionally used for Drop Copy the value provided in the field must be set to one of the possible values for this field as described in the FIX specifications."
  },
  {
    "Field Name": "DefaultApplVerID",
    "FIX Tag": "1137",
    "Use in Drop Copy": "Mandatory to be provided and should be set by default to 9 = FIX50SP2"
  },
  {
    "Field Name": "Software Provider",
    "FIX Tag": "21050",
    "Use in Drop Copy": "Optional field in which clients may provide details of the software provider used for their solution. This field may be used by the Exchange for improved troubleshooting and service purposes."
  }
]

### OUTPUT JSON ###