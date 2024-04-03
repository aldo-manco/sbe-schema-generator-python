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

20175 TriggeredStopTim
eInForce
Char 1 0 = Day
1 = Good Till Cancel
6 = Good till Date
C CASH ONLY
Specifies the maximum validity of an
triggered stop order. On triggering of a Stop
order the value in this field is populated in
the field TimeInForce (59).
131 QuoteReqID String 20 From 0 to 2^64-2 C Numerical RFQ identifier assigned by the
matching engine, unique per instrument
and EMM.
21037 RFQAnswerIndicat
or
Int 1 0 = No
1 = Yes
C CASH ONLY
Indicates whether the message is, or not, a
quote sent as an answer to a QuoteRequest
(R) message.
21038 RFQConfirmationI
ndicator
Int 1 0 = No
1 = Yes
C CASH ONLY
Indicates whether the message is, or not, an
order sent as a confirmation of a
QuoteRequest (R) message.
21800 ConditionalOrderF
lag
Int 1 0 = Firm (default)
1 = Conditional
C CASH ONLY
Indicates if the order is a conditional or a
firm order
453 NoPartyIDs NumInGroup 1 Always set to 1 A Number of PartyID entries 1
448 PartyID String 11 Alphanumeric A In this case provides the
ExecutionWithinFirmShortCode
59786
447 PartyIDSource Char 1 P = Short code identifier A Source of PartyID value P
452 PartyRole Int 3 3 = Client ID
12 = Executing Trader
999 = Not Applicable
A Identifies the type or role of the PartyID
(448) specified.
For Execution with Firm short code in Drop
Copy where the values in the original
trading OEG message:
• were received in SBE protocol the
value will be set to 999 (Not
Applicable);
• were received in FIX protocol, the
value will be set to 3 (Client ID) or
12 (Executing Trader)
Tag Field Name Format Len Possible Values M/C Short Description, Compatibility Notes
& Conditions
Value
Example
2376 PartyRoleQualifier Int 2 22 = Algorithm
23 = Firm or legal entity
24 = Natural person
99 = Not Applicable
C Used to further qualify the value of
PartyRole (452)
For ExecutionWithinFirmShortCode in Drop
Copy where the values in the original
trading OEG message:
• were received in SBE protocol the
value will be set to 99 (Not
Applicable);
• were received in FIX protocol, the
value will be set to 22 (Algorithm)
or 23 (Firm or Legal Entity) or 24
(Natural Person);
23
1724 OrderOrigination Int 1 5 = Order received from a direct access or
sponsored access customer
C Identifies the origin of the order
2593 NoOrderAttribute
s
NumInGroup 1 If provided, from 1 to 2 C Number of order attribute entries
2594 OrderAttributeTyp
e
Int 1 0 = Aggregated order
1 = Pending allocation
3 = Risk reduction order
C Used in case client needs to indicate values
of AGGR or PNAL, OR in Risk Reduction
order
2595 OrderAttributeVal
ue
String 1 Y = Yes C Always set to Yes if OrderAttributeType
(2594) if provided
29 LastCapacity Char 1 7 = Dealing on own account (DEAL)
8 = Matched principal (MTCH)
9 = Any other capacity (AOTC)
A Indicates whether the order submission
results from trading as matched principal,
on own account or as any other capacity.
7
110 MinQty Qty 20 Value '0' by default and depending to a minimum
value for the given instrument and/or market type
C Minimum quantity to be executed upon
order entry (else the order is rejected).
Only provided when submitted in the
original order entry message
21013 AckPhase Char 1 1 = Continuous Trading Phase
2 = Call Phase
3 = Halt Phase
5 = Trading At Last Phase
6 = Reserved
7 = Suspended
8 = Random Uncrossing Phase
A Indicates the trading phase during which
the Matching Engine has received the order
Values 5 and 8 apply only for Cash markets
1

### OUTPUT JSON ###