# generate_presence_from_embeddings_prompt.py

system_message = """
You are an expert in electronic trading systems with a deep understanding of FIX and SBE protocols. 

Your mission is to determine whether a SBE field is mandatory or optional, indicating whether it must always be included or can be omitted in some messages. 
Your analysis must be based on the SBE field description [SBE FIELD DESCRIPTION] and on the various contexts extracted from market documentation [CONTEXT]. 
If [SBE FIELD DESCRIPTION] and [CONTEXT] do not provide information about the presence of the SBE field, you must assume that it is mandatory.

In your response, include only a JSON object containing the presence of the SBE field. For instance:
{
    "presence": "mandatory"
}

Adhere the provided examples closely.
"""

example_1_human_message = """
### SBE FIELD DESCRIPTION ###

{
    "tag": "21005",
    "field name": "ClientMessageSendingTime",
    "ai_engine_id": 5
}

### CONTEXT 1 ###

Sample values provided in this example represent an acknowledgement of a newly entered Limit order with Day validity on instrument with SymbolIndex 1110530 in Central order book. In case of an order in a strategy, the field SecurityID (48) will provide the Symbol Index of that strategy Tag Field Name Format Len Possible Values M/C Short Description, Compatibility Notes & Conditions Value Example Message Header M Optiq Drop Copy Service – Interface Specification Message Structure For Individual Cases © 2022 Euronext N.V. - All rights reserved. Page 24 of 127 5.16.0 Tag Field Name Format Len Possible Values M/C Short Description, Compatibility Notes & Conditions Value Example 21005 ClientMessageSendingTime UTCTimestamp 27 Timestamp M Indicates the time of message transmission, the consistency of the time provided is not checked by the Exchange. 20190214-15:30:01.462743346 5979 OEGINFromMember UTCTimestamp 27 Timestamp C Order Entry Gateway IN time from member (in ns), measured when inbound message enters the gateway 20190214-15:28:52.833883664
"""

example_1_assistant_message = """
{
  "presence": "mandatory"
}
"""

example_2_human_message = """
### SBE FIELD DESCRIPTION ###

{
    "Offset": "8",
    "Field": "SecurityTradingStatus",
    "Description": "Identifies the trading status of a security.",
    "ai_engine_id": 21
}

### CONTEXT 1 ###

Message Fields Offset Field Format Len Description Values 0 MsgSize Uint16 2 Size of the message 2 MsgType Uint16 2 Type of message. 621 Security Status 4 SecurityCode Uint32 4 Uniquely identifies a security available for trading 6 digit security codes with possible values 1 – 999999 8 SecurityTradingStatus Uint8 1 Identifies the trading status of a security. 2 Trading Halt 3 Resume 9 Filler String 3 12 TradingPhaseCode String 8 Identify
"""

example_2_assistant_message = """
{
  "presence": "optional"
}
"""

example_3_human_message = """
### SBE FIELD DESCRIPTION ###

{
  "Field": "Lot Size",
  "Short Description": "For Cash and Derivatives, it defines a multiple of the tradable quantity.",
  "ai_engine_id": 12
}

### CONTEXT 1 ###

Last Adjusted Closing Price Last traded price of the previous trading day after application of the adjustment coefficient (to be calculated with the Price/Index Level Decimals). Price 8 (See field description) Optional Lot Size For Cash and Derivatives, it defines a multiple of the tradable quantity. Quantity 8 0..2^64-2 Optional Maturity Date Maturity Date of the instrument (text formatted as YYYYMMDD). Text 8 (See field description) Optional
"""

example_3_assistant_message = """
{
  "presence": "optional"
}
"""

example_4_human_message = ""

example_4_assistant_message = ""
