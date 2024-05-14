# generate_enumerations_set_attributes_from_embeddings_prompt.py

system_message = """
You are an expert in electronic trading systems with a deep understanding of FIX and SBE protocols. 
Your mission is to determine the possible values of an enumeration or set SBE field, specifying all the possible values which the SBE field can contain. 
Your analysis must be based on the SBE field description [SBE FIELD DESCRIPTION] and on the various contexts extracted from market documentation [CONTEXT]. 
If [SBE FIELD DESCRIPTION] and [CONTEXT] do not provide information about the possible values of the enumerations or set SBE field, you must default to the following values:
{
  1: "Yes",
  2: "No"
}

Additionally, you must identify the encoding type of the enumeration or set SBE field. Your goal is to specify the smallest data type capable of containing all selectable values. Only the following data types can be used:
- char (specify the required length to accommodate the values)
- int8
- uint8
- int16
- uint16
- int32
- uint32
- int64
- uint64

In your response, include only a JSON object containing the possible values and the encoding type of the SBE field of type enumeration/set. For instance:
{
    "possible_values": {
      "1": "Buy",
      "2": "Sell"
    },
    "encoding_type": "uint8"
}

Adhere the provided examples closely.
"""

example_1_human_message = """
### SBE FIELD DESCRIPTION ###

{
    "field name": "IndexSendingTime",
    "data_type": "IndexSendingTime_enum",
    "ai_engine_id": 13
}

### CONTEXT 1 ###

User For Cash Index Price Code Field Name Index Price Code Description Type of Price as positioned in Session High/Low or to indicate the trend or at the contrary the reference value from which the price may change. Format Enumerated (unsigned integer 8) Length 1 Possible Values 0 Only Index 1 Index and Session High 2 Index and Session Low 3 Index and Session High and Low (typically first price) 4 Only Session High 5 Only Session Low 6 Previous Day Close Null value: 2^8-1 Used In Real Time Index (1008) User For Cash Instrument Category Field Name Instrument Category Description Indicates to which category the instrument belongs. Format Enumerated (unsigned integer 8) Length 1 Possible Values 1 Equities 2 Fixed Income
"""

example_1_assistant_message = """
{
  "possible_values": {
    "0": "Only Index",
    "1": "Index and Session High",
    "2": "Index and Session Low",
    "3": "Index and Session High and Low (typically first price)",
    "4": "Only Session High",
    "5": "Only Session Low",
    "6": "Previous Day Close"
  },
  "encoding_type": "uint8"
}
"""

example_2_human_message = """
### SBE FIELD DESCRIPTION ###

{
    "field name": "TradeCondition",
    "data_type": "TradeCondition_set",
    "ai_engine_id": 21
}

### CONTEXT 1 ###

Type: Unsigned long (uint64) Value Range 0..>4294967295 Where sent: - Snapshot Message - Delta / Incremental Message 8.32 TradeCondition Description: Together with MDEntryType 2 it defines the type of trade Type: ASCII Character String (MultipleStringValue) Value Status U Exchange last R Opening price AX High price AY Low price AJ Official closing price AW Last auction price V Final price of session AZ BEST price BB Midpoint price BC Price from subscription period (“Handel per Erscheinen”) Deutsche Börse AG Xetra Release 17.0 Xetra Market Data Interface 02.10.2017 Final Version Page 46 of 64
"""

example_2_assistant_message = """
{
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
"""

example_3_human_message = """
### SBE FIELD DESCRIPTION ###

{
  "field_tag_number": 327,
  "field_name": "HaltReason",
  "data_type": "HaltReason_enum",
  "ai_engine_id": 66
}

### CONTEXT 1 ###

1174 SecurityTradingEvent N Indicates the reason a trading session is extended or shortened. Value Meaning 101 Extended by Market Operations 102 Shortened by Market Operations 327 HaltReason N Reason for the trading halt. Required if SecurityTradingStatus (326) is Halt (2). Code Reason 100 Reason Not Available 102 Instrument Status changed to Halt 9998 Matching partition suspended 9999 System suspended 58 Text N Free text. If SecurityTradingEvent(1174) has been populated this will indicate the new time at which the session will end.
"""

example_3_assistant_message = """
{
  "possible_values": {
    "100": "Reason Not Available",
    "102": "Instrument Status changed to Halt",
    "9998": "Matching partition suspended",
    "9999": "System suspended"
  },
  "encoding_type": "uint16"
}
"""

example_4_human_message = ""

example_4_assistant_message = ""
