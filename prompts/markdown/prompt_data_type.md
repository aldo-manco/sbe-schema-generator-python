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
    "Tag": 20175,
    "Field Name": "TriggeredStopTimeInForce",
    "Format": "Char",
    "Len": 1,
    "Possible Values": "0 = Day, 1 = Good Till Cancel, 6 = Good till Date",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Specifies the maximum validity of a triggered stop order. On triggering of a Stop order the value in this field is populated in the field TimeInForce (59).",
    "ai_engine_id": 1 
  },
  {
    "Tag": 131,
    "Field Name": "QuoteReqID",
    "Format": "String",
    "Len": 20,
    "Possible Values": "From 0 to 2^64-2",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Numerical RFQ identifier assigned by the matching engine, unique per instrument and EMM.",
    "ai_engine_id": 2
  },
  {
    "Tag": 21037,
    "Field Name": "RFQAnswerIndicator",
    "Format": "Int",
    "Len": 1,
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Indicates whether the message is, or not, a quote sent as an answer to a QuoteRequest (R) message.",
    "ai_engine_id": 3
  },
  {
    "Tag": 21038,
    "Field Name": "RFQConfirmationIndicator",
    "Format": "Int",
    "Len": 1,
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Indicates whether the message is, or not, an order sent as a confirmation of a QuoteRequest (R) message.",
    "ai_engine_id": 4
  },
  {
    "Tag": 21800,
    "Field Name": "ConditionalOrderFlag",
    "Format": "Int",
    "Len": 1,
    "Possible Values": "0 = Firm (default), 1 = Conditional",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Indicates if the order is a conditional or a firm order.",
    "ai_engine_id": 5
  },
  {
    "Tag": 453,
    "Field Name": "NoPartyIDs",
    "Format": "NumInGroup",
    "Len": 1,
    "Possible Values": "Always set to 1",
    "M/C": "A",
    "Short Description, Compatibility Notes, & Conditions": "Number of PartyID entries.",
    "ai_engine_id": 6
  },
  {
    "Tag": 448,
    "Field Name": "PartyID",
    "Format": "String",
    "Len": 11,
    "Possible Values": "Alphanumeric",
    "M/C": "A",
    "Short Description, Compatibility Notes, & Conditions": "In this case provides the ExecutionWithinFirmShortCode.",
    "ai_engine_id": 7
  },
  {
    "Tag": 447,
    "Field Name": "PartyIDSource",
    "Format": "Char",
    "Len": 1,
    "Possible Values": "P = Short code identifier",
    "M/C": "A",
    "Short Description, Compatibility Notes, & Conditions": "Source of PartyID value.",
    "ai_engine_id": 8
  },
  {
    "Tag": 452,
    "Field Name": "PartyRole",
    "Format": "Int",
    "Len": 3,
    "Possible Values": "3 = Client ID, 12 = Executing Trader, 999 = Not Applicable",
    "M/C": "A",
    "Short Description, Compatibility Notes, & Conditions": "Identifies the type or role of the PartyID (448) specified. For Execution with Firm short code in Drop Copy where the values in the original trading OEG message were received in SBE protocol the value will be set to 999 (Not Applicable); were received in FIX protocol, the value will be set to 3 (Client ID) or 12 (Executing Trader)",
    "ai_engine_id": 9
  },
  {
    "Tag": 2376,
    "Field Name": "PartyRoleQualifier",
    "Format": "Int",
    "Len": 2,
    "Possible Values": "22 = Algorithm, 23 = Firm or legal entity, 24 = Natural person, 99 = Not Applicable",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Used to further qualify the value of PartyRole (452). For ExecutionWithinFirmShortCode in Drop Copy where the values in the original trading OEG message were received in SBE protocol the value will be set to 99 (Not Applicable); were received in FIX protocol, the value will be set to 22 (Algorithm) or 23 (Firm or Legal Entity) or 24 (Natural Person);",
    "ai_engine_id": 10
  },
  {
    "Tag": 1724,
    "Field Name": "OrderOrigination",
    "Format": "Int",
    "Len": 1,
    "Possible Values": "5 = Order received from a direct access or sponsored access customer",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Identifies the origin of the order.",
    "ai_engine_id": 11
  },
  {
    "Tag": 2593,
    "Field Name": "NoOrderAttributes",
    "Format": "NumInGroup",
    "Len": 1,
    "Possible Values": "If provided, from 1 to 2",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Number of order attribute entries.",
    "ai_engine_id": 12
  },
  {
    "Tag": 2594,
    "Field Name": "OrderAttributeType",
    "Format": "Int",
    "Len": 1,
    "Possible Values": "0 = Aggregated order, 1 = Pending allocation, 3 = Risk reduction order",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Used in case client needs to indicate values of AGGR or PNAL, or in Risk Reduction order.",
    "ai_engine_id": 13
  },
  {
    "Tag": 2595,
    "Field Name": "OrderAttributeValue",
    "Format": "String",
    "Len": 1,
    "Possible Values": "Y = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Always set to Yes if OrderAttributeType (2594) if provided.",
    "ai_engine_id": 14
  },
  {
    "Tag": 29,
    "Field Name": "LastCapacity",
    "Format": "Char",
    "Len": 1,
    "Possible Values": "7 = Dealing on own account (DEAL), 8 = Matched principal (MTCH), 9 = Any other capacity (AOTC)",
    "M/C": "A",
    "Short Description, Compatibility Notes, & Conditions": "Indicates whether the order submission results from trading as matched principal, on own account or as any other capacity.",
    "ai_engine_id": 15
  },
  {
    "Tag": 110,
    "Field Name": "MinQty",
    "Format": "Qty",
    "Len": 20,
    "Possible Values": "Value '0' by default and depending to a minimum value for the given instrument and/or market type",
    "M/C": "C",
    "Short Description, Compatibility Notes, & Conditions": "Minimum quantity to be executed upon order entry (else the order is rejected). Only provided when submitted in the original order entry message.",
    "ai_engine_id": 16
  },
  {
    "Tag": 21013,
    "Field Name": "AckPhase",
    "Format": "Char",
    "Len": 1,
    "Possible Values": "1 = Continuous Trading Phase, 2 = Call Phase, 3 = Halt Phase, 5 = Trading At Last Phase, 6 = Reserved, 7 = Suspended, 8 = Random Uncrossing Phase",
    "M/C": "A",
    "Short Description, Compatibility Notes, & Conditions": "Indicates the trading phase during which the Matching Engine has received the order. Values 5 and 8 apply only for Cash markets.",
    "ai_engine_id": 17
  }
]

### OUTPUT JSON ###