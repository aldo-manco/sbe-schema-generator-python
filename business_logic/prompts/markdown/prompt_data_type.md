You are an expert in electronic trading systems with a deep understanding of FIX and SBE protocols. Your mission is to identify various features regarding each message field of the given list of message fields, provided by a market documentation. For each message field, determine each of the following features step by step:
1. field_tag_number: 
If a field in message fields represents a FIX protocol tag number, either standard or custom, assign the appropriate tag number to the Field Tag Number. If no such tag number is defined, do not define the Field Tag Number.
2. field_name: 
Textual reference briefly describing the content and purpose of the field.
3. data_type:
Choose the appropriate data type for the field, using only the types defined in the SBE protocol. Here is a guide on the different available data types:
- char
- int8
- uint8
- int16
- uint16
- int32
- uint32
- int64
- uint64
- Field Name in camelCase + "_enum" (For fields with a limited number of options where only one value can be selected)
- Field Name in camelCase + "_set" (For fields with a limited number of options where multiple values can be selected)
4. encoding_type: 
For primitive data types, encoding type corresponds to the primitive data type itself. For enumerations and sets, use the smallest data type capable of containing all selectable values.
5. length: 
Calculate the byte length of the chosen data type. For enumerations or sets, calculate the byte length of the chosen encoding type capable of representing all possible values.
6. presence: 
Determine if the field is mandatory or optional, indicating whether it must always be included or can be omitted in some messages.
7. structure: 
For enumeration or set fields, associate a JSON object with all possible values. For primitive data types, associate an empty JSON {}.
8. ai_engine_id:
Unique identifier for the field in the message, defined in "ai_engine_id".

In your response, include only a JSON array. This array must contain a JSON object with the requested features for each message field. 

Adhere the provided examples closely.

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
    "value example": "20190214- 15:30:01.4 62743346",
    "ai_engine_id": 1
  },
  {
    "Tag": "11",
    "Field Name": "ClOrdID",
    "Format": "String",
    "Len": "20",
    "Possible Values": "From -2^63 to 2^63-1",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Identifier of an Order Modification message assigned by the Client when submitting the order modification message to the Exchange",
    "Value Example": "25",
    "ai_engine_id": 2
  },
  {
    "Tag": "21013",
    "Field Name": "AckPhase",
    "Format": "Char",
    "Len": "1",
    "Possible Values": "1 = Continuous Trading Phase 2 = Call Phase 3 = Halt Phase 5 = Trading At Last Phase 6 = Reserved 7 = Suspended 8 = Random Uncrossing Phase",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Indicates the trading phase during which the Matching Engine has received the order Values 5 and 8 apply only for Cash markets",
    "Value Example": "1",
    "ai_engine_id": 3
  },
  {
    "Tag": "21014",
    "Field Name": "AckQualifiers",
    "Format": "MultipleCharValue",
    "Len": "15",
    "Possible Values": "0 = Dark Indicator 1 = Queue Indicator 2 = Request with Client Order ID 3 = Use of Cross Partition 4 = Internal1 5 = Internal2 6 = Execution Upon Entry flag Enabled 7 = Executed Upon Entry flag",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Field used to provide additional information on the corresponding order. For Derivatives positions 0 is not applicable and is always set to 0.",
    "Value Example": "0 0 0 0 0 0 0 0",
    "ai_engine_id": 4
  }
]

### ESEMPIO 1: OUTPUT ###

[
  {
    "field_tag_number": 21005,
    "field_name": "ClientMessageSendingTime",
    "data_type": "char",
    "encoding_type": "char",
    "length": 27,
    "presence": "optional",
    "structure": {},
    "ai_engine_id": 1
  },
  {
    "field_tag_number": 11,
    "field_name": "ClOrdID",
    "data_type": "int64",
    
    "encoding_type": "int64",
    "length": 8,
    "presence": "mandatory",
    "structure": {},
    "ai_engine_id": 2
  },
  {
    "field_tag_number": 21013,
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
    },
    "ai_engine_id": 3
  },
  {
    "field_tag_number": 21014,
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
    },
    "ai_engine_id": 4
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
    "Values": "N/A",
    "ai_engine_id": 5
  },
  {
    "Offset": "8",
    "Field": "SecurityTradingStatus",
    "Format": "Uint8",
    "Len": "1",
    "Description": "Identifies the trading status of a security.",
    "Values": "2 Trading Halt, 3 Resume",
    "ai_engine_id": 6
  },
  {
    "Offset": "12",
    "Field": "TradingPhaseCode",
    "Format": "String",
    "Len": "8",
    "Description": "Identify the trading state of the security",
    "Values": "Please refer to the TradingPhaseCode information in SSE market data of this security for details. N/A for SZSE Instruments",
    "ai_engine_id": 7
  }
]

### ESEMPIO 2: OUTPUT ###

[
  {
    "field_name": "MsgSize",
    "data_type": "uint16",
    "encoding_type": "uint16",
    "length": 2,
    "presence": "mandatory",
    "structure": {},
    "ai_engine_id": 5
  },
  {
    "field_name": "SecurityTradingStatus",
    "data_type": "SecurityTradingStatus_enum",
    "encoding_type": "uint8",
    "length": 1,
    "presence": "mandatory",
    "structure": {
      "2": "Trading Halt",
      "3": "Resume"
    },
    "ai_engine_id": 6
  },
  {
    "field_name": "TradingPhaseCode",
    "data_type": "char",
    "encoding_type": "char",
    "length": 8,
    "presence": "mandatory",
    "structure": {},
    "ai_engine_id": 7
  }
]

### ESEMPIO 3: INPUT ###

[
  {
    "Field": "SEDOL",
    "Offset": "31",
    "Length": "8",
    "Type": "Alpha",
    "Description": "SEDOL code of the instrument.",
    "ai_engine_id": 12
  },
  {
    "Field": "Allowed Book Types",
    "Offset": "39",
    "Length": "1",
    "Type": "Bit Field",
    "Description": "Defines the order-book types that are allowed for the instrument. Each designated bit represents a book type. 0 Means not allowed and 1 means allowed: Bit Name 0 All 1 Firm Quote Book 2 Off-book 3 Electronic Order Book 4 Private RFQ",
    "ai_engine_id": 13
  },
  {
    "Field": "Source Venue",
    "Offset": "40",
    "Length": "2",
    "Type": "UInt16",
    "Description": "Please refer the Additional Field Values section of this document for valid values.",
    "ai_engine_id": 14
  },
  {
    "Field": "Settlement System",
    "Offset": "146",
    "Length": "1",
    "Type": "UInt8",
    "Description": "Settlement system type: Value Meaning 1 RRG 2 Express I 3 Express II 4 Clear stream 5 Undefined value 6 T2S",
    "ai_engine_id": 15
  }
]

### ESEMPIO 3: OUTPUT ###

[
  {
    "field_name": "SEDOL",
    "data_type": "char",
    "encoding_type": "char",
    "length": 8,
    "presence": "mandatory",
    "structure": {},
    "ai_engine_id": 12
  },
  {
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
    },
    "ai_engine_id": 13
  },
  {
    "field_name": "SourceVenue",
    "data_type": "uint16",
    "encoding_type": "uint16",
    "length": 2,
    "presence": "mandatory",
    "structure": {},
    "ai_engine_id": 14
  },
  {
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
    },
    "ai_engine_id": 15
  }
]

### INPUT ###

[
  {
    "Field": "Market Data Sequence Number",
    "Short Description": "Assigned by MDG for each message. Each channel has its own Market Data Sequence Number sequence.",
    "Format": "Sequence",
    "Len": 8,
    "Values": "0..2^64-2",
    "Presence": "Mandatory",
    "ai_engine_id": 1
  },
  {
    "Field": "Rebroadcast Indicator",
    "Short Description": "Indicates if this message is resent or new (1 if resent, 0 otherwise). For a snapshot, this field will always be set to '1'.",
    "Format": "Numerical ID",
    "Len": 1,
    "Values": "0..2^8-2",
    "Presence": "Mandatory",
    "ai_engine_id": 2
  },
  {
    "Field": "EMM",
    "Short Description": "Defines the Exchange Market Mechanism applied on each platform.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "(See field description)",
    "Presence": "Optional",
    "ai_engine_id": 3
  },
  {
    "Field": "Pattern ID",
    "Short Description": "Pattern identifier available as a characteristic of an instrument in Standing Data file and message, and used in the MDG timetable message. Cash Markets only.",
    "Format": "Numerical ID",
    "Len": 2,
    "Values": "0..2^16-2",
    "Presence": "Optional",
    "ai_engine_id": 4
  },
  {
    "Field": "Symbol Index",
    "Short Description": "Exchange identification code of the instrument/contract.",
    "Format": "Numerical ID",
    "Len": 4,
    "Values": "0..2^32-2",
    "Presence": "Optional",
    "ai_engine_id": 5
  },
  {
    "Field": "Timetables length",
    "Short Description": "Repeating section header",
    "Format": "Numerical",
    "Len": 1,
    "Values": "0..2^16-2",
    "Presence": "Mandatory",
    "ai_engine_id": 6
  },
  {
    "Field": "Timetables occurrences",
    "Short Description": "Repeating section header",
    "Format": "Numerical",
    "Len": 1,
    "Values": "1..254",
    "Presence": "Mandatory",
    "ai_engine_id": 7
  },
  {
    "Field": "Phase Time",
    "Short Description": "Time of Phase start",
    "Format": "Integer Time in hhmmss",
    "Len": 8,
    "Values": "0..2^64-2",
    "Presence": "Mandatory",
    "ai_engine_id": 8
  },
  {
    "Field": "Phase Id",
    "Short Description": "Indicates the phase of the instrument.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "(See field description)",
    "Presence": "Mandatory",
    "ai_engine_id": 9
  },
  {
    "Field": "Phase Qualifier",
    "Short Description": "Indicates the Phase Qualifier.",
    "Format": "Bitmap",
    "Len": 2,
    "Values": "(See field description)",
    "Presence": "Mandatory",
    "ai_engine_id": 10
  },
  {
    "Field": "Trading Period",
    "Short Description": "Provides the current trading period.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "1 Opening (Cash and Derivatives), 2 Standard (Cash and Derivatives), 3 Closing (Cash and Derivatives)",
    "Presence": "Mandatory"
    "ai_engine_id": 11
  },
  {
    "Field": "Order Entry Qualifier",
    "Short Description": "Field indicating the state of the Order Entry for the current market state.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "0 Order Entry/Cancel/Modify Disabled, 1 Order Entry/Cancel/Modify Enabled, 2 Cancel and Modify Only (Derivatives Only), 3 Cancel Only",
    "Presence": "Optional",
    "ai_engine_id": 12
  },
  {
    "Field": "Session",
    "Short Description": "Current market session.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "(See field description)",
    "Presence": "Mandatory",
    "ai_engine_id": 13
  },
  {
    "Field": "Scheduled Event",
    "Short Description": "Type of Scheduled Event.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "(See field description)",
    "Presence": "Optional",
    "ai_engine_id": 14
  }
]

### OUTPUT JSON ###