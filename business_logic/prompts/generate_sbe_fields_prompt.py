# generate_sbe_fields_prompt.py

system_message = """
You are an expert in electronic trading systems with a deep understanding of FIX and SBE protocols. 
Your mission is to identify various features regarding each message field of the given list of message fields, provided by a market documentation.
For each field in the message, determine the following attributes step by step:
1. ai_engine_id:
Unique identifier assigned to each field within the message, specified under "ai_engine_id".
2. field_name: 
Textual reference briefly describing the content and purpose of the field.
3. field_tag_number: 
Only applicable if the field corresponds to a FIX protocol tag number, either standard or custom. 
Assign the appropriate tag number to this attribute. 
If no FIX tag number is applicable, this attribute must be -1.
4. data_type:
Select a suitable data type from the list provided:
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
- null (if the data type is not defined)
5. presence: 
Indicate whether the field is mandatory or optional. 
The "mandatory" designation means the field must always be present, while "optional" allows for the field to be omitted under certain conditions. 
Use "null" if the presence status is not specified.

Define only for alphanumeric fields the following attribute:
- length: 
Byte length of the alphanumeric string.
If length is not specified, this attribute must be -1.

Define only for enumeration or set fields the following attributes:
- possible_values: 
JSON object with all possible values.
If possible values are not specified, this attribute must be an empty JSON object.
- encoding_type: 
Smallest data type capable of containing all selectable values.
If possible values are not specified, this attribute must be "null".

Define only for enumeration or set fields whose encoding type is char the following attribute:
- length: 
Smallest byte length capable of containing all selectable values.

In your response, include only a JSON array. This array must contain a JSON object with the requested features for each message field. 

The JSON array must be incorporated into the following JSON object:
{
    "json_array": [
        ...
    ]
}

Adhere the provided examples closely.
"""

example_1_human_message = """
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
    "Tag": "21010",
    "Field Name": "TotalNumOfTrades",
    "Short Description, Compatibility Notes & Conditions": "The cumulative total of the number of Trades for the current day in a given instrument.",
    "Value Example": "1",
    "ai_engine_id": 3
  }
  {
    "Tag": "21013",
    "Field Name": "AckPhase",
    "Format": "Char",
    "Len": "1",
    "Possible Values": "1 = Continuous Trading Phase 2 = Call Phase 3 = Halt Phase 5 = Trading At Last Phase 6 = Reserved 7 = Suspended 8 = Random Uncrossing Phase",
    "M/C": "m",
    "Short Description, Compatibility Notes & Conditions": "Indicates the trading phase during which the Matching Engine has received the order Values 5 and 8 apply only for Cash markets",
    "Value Example": "1",
    "ai_engine_id": 4
  },
  {
    "Tag": "21014",
    "Field Name": "AckQualifiers",
    "Format": "MultipleCharValue",
    "Len": "15",
    "Possible Values": "0 = Dark Indicator 1 = Queue Indicator 2 = Request with Client Order ID 3 = Use of Cross Partition 4 = Internal1 5 = Internal2 6 = Execution Upon Entry flag Enabled 7 = Executed Upon Entry flag",
    "Short Description, Compatibility Notes & Conditions": "Field used to provide additional information on the corresponding order. For Derivatives positions 0 is not applicable and is always set to 0.",
    "Value Example": "0 0 0 0 0 0 0 0",
    "ai_engine_id": 5
  },
  {
    "tag": "21016",
    "field name": "RFQIndicator",
    "len": "1",
    "short description, compatibility notes and conditions": "indicates the time of message transmission,  the consistency of the time provided is not  checked by the Exchange",
    "value example": "20190214- 15:30:01.4 62743346",
    "ai_engine_id": 6
  }
]
"""

example_1_assistant_message = """
{
    "json_array": [
      {
        "ai_engine_id": 1,
        "field_name": "ClientMessageSendingTime",
        "field_tag_number": 21005,
        "data_type": "char",
        "presence": "optional",
        "length": 27
      },
      {
        "ai_engine_id": 2,
        "field_name": "ClOrdID",
        "field_tag_number": 11,
        "data_type": "int64",
        "presence": "optional"
      },
      {
        "ai_engine_id": 3,
        "field_name": "TotalNumOfTrades",
        "field_tag_number": 21010,
        "data_type": "null",
        "presence": "null"
      }
      {
        "ai_engine_id": 4,
        "field_name": "AckPhase",
        "field_tag_number": 21013,
        "data_type": "AckPhase_enum",
        "presence": "mandatory",
        "possible_values": {
          "1": "Continuous Trading Phase",
          "2": "Call Phase",
          "3": "Halt Phase",
          "5": "Trading At Last Phase",
          "6": "Reserved",
          "7": "Suspended",
          "8": "Random Uncrossing Phase"
        },
        "encoding_type": "uint8"
      },
      {
        "ai_engine_id": 5,
        "field_name": "AckQualifiers",
        "field_tag_number": 21014,
        "data_type": "AckQualifiers_set",
        "presence": "null",
        "possible_values": {
          "0": "Dark Indicator",
          "1": "Queue Indicator",
          "2": "Request with Client Order ID",
          "3": "Use of Cross Partition",
          "4": "Internal1",
          "5": "Internal2",
          "6": "Execution Upon Entry flag Enabled",
          "7": "Executed Upon Entry flag"
        },
        "encoding_type": "uint8"
      },
      {
        "ai_engine_id": 6,
        "field_name": "RFQIndicator",
        "field_tag_number": 21016,
        "data_type": "null",
        "presence": "null"
      }
    ]
}
"""

example_2_human_message = """
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
  },
  {
    "Offset": "32",
    "Field": "TradingSessionSubID",
    "Description": "The cumulative total of the number of Trades for the current day in a given instrument.",
    "ai_engine_id": 8
  }
]
"""

example_2_assistant_message = """
{
    "json_array": [
      {
        "ai_engine_id": 5,
        "field_name": "MsgSize",
        "field_tag_number": -1,
        "data_type": "uint16",
        "presence": "null"
      },
      {
        "ai_engine_id": 6,
        "field_name": "SecurityTradingStatus",
        "field_tag_number": -1,
        "data_type": "SecurityTradingStatus_enum",
        "presence": "null",
        "possible_values": {
          "2": "Trading Halt",
          "3": "Resume"
        },
        "encoding_type": "uint8"
      },
      {
        "ai_engine_id": 7,
        "field_name": "TradingPhaseCode",
        "field_tag_number": -1,
        "data_type": "char",
        "presence": "null",
        "length": 8
      },
      {
        "ai_engine_id": 8,
        "field_name": "TradingSessionSubID",
        "field_tag_number": -1,
        "data_type": "null",
        "presence": "null"
      }
    ]
}
"""

example_3_human_message = """
[
  {
    "Field": "SEDOL",
    "Offset": "31",
    "Length": "8",
    "Type": "Alpha",
    "Presence": "M",
    "Description": "SEDOL code of the instrument.",
    "ai_engine_id": 12
  },
  {
    "Field": "Allowed Book Types",
    "Offset": "39",
    "Length": "1",
    "Type": "Bit Field",
    "Presence": "A",
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
    "Presence": "c",
    "Description": "Settlement system type: Value Meaning 1 RRG 2 Express I 3 Express II 4 Clear stream 5 Undefined value 6 T2S",
    "ai_engine_id": 15
  },
  {
    "Field": "Tradec ondition",
    "Offset": "149",
    "Length": "2",
    "Type": "CHAR",
    "Presence": "m",
    "Description": "Together with MDEntryType 2 it defines the type of trade U Exchange last R Opening price AX High price AY Low price AJ Official closing price AW Last auction price V Final price of session AZ BEST price BB Midpoint price BC Price from subscription period (Handel per Erscheinen)",
    "ai_engine_id": 16
  }
]
"""

example_3_assistant_message = """
{
    "json_array": [
      {
        "ai_engine_id": 12,
        "field_name": "SEDOL",
        "field_tag_number": -1,
        "data_type": "char",
        "presence": "mandatory",
        "length": 8
      },
      {
        "ai_engine_id": 13,
        "field_name": "AllowedBookTypes",
        "field_tag_number": -1,
        "data_type": "AllowedBookTypes_set",
        "presence": "optional",
        "possible_values": {
          "0": "All",
          "1": "Firm Quote Book",
          "2": "Off-book",
          "3": "Electronic Order Book",
          "4": "Private RFQ"
        },
        "encoding_type": "uint8"
      },
      {
        "ai_engine_id": 14,
        "field_name": "SourceVenue",
        "field_tag_number": -1,
        "data_type": "uint16",
        "presence": "null"
      },
      {
        "ai_engine_id": 15,
        "field_name": "SettlementSystem",
        "field_tag_number": -1,
        "data_type": "SettlementSystem_enum",
        "presence": "optional",
        "possible_values": {
          "1": "RRG",
          "2": "Express I",
          "3": "Express II",
          "4": "Clearstream",
          "5": "Undefined value",
          "6": "T2S"
        },
        "encoding_type": "uint8"
      },
      {
        "ai_engine_id": 16,
        "field_name": "TradeCondition",
        "field_tag_number": -1,
        "data_type": "TradeCondition_set",
        "presence": "mandatory",
        "possible_values": {
          "U": "Exchange last",
          "R": "Opening price",
          "AX": "High price",
          "AY": "Low price",
          "AJ": "Official closing price",
          "AW": "Last auction price",
          "V": "Final price of session",
          "AZ": "BEST price",
          "BB": "Midpoint price",
          "BC": "Price from subscription period (Handel per Erscheinen)"
        },
        "encoding_type": "char",
        "length": 2
      }
    ]
}
"""

example_4_human_message = ""

example_4_assistant_message = ""
