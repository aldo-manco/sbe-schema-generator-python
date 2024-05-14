# generate_char_attributes_from_embeddings_prompt.py

system_message = """
You are an expert in electronic trading systems with a deep understanding of FIX and SBE protocols. 
Your mission is to determine the byte length of an alphanumeric SBE field, specifying the maximum number of characters the string can contain. 
Your analysis must be based on the SBE field description [SBE FIELD DESCRIPTION] and on the various contexts extracted from market documentation [CONTEXT]. 
If [SBE FIELD DESCRIPTION] and [CONTEXT] do not provide the length of the alphanumeric SBE field, you must assume that the length is 30.

In your response, include only a JSON object containing the byte length of the alphanumeric SBE field. For instance:
{
    "length": 15
}

Adhere the provided examples closely.
"""

example_1_human_message = """
### SBE FIELD DESCRIPTION ###

{
    "field_tag_number": "21005",
    "field_name": "ClientMessageSendingTime",
    "data_type": "char",
    "ai_engine_id": 13
}

### CONTEXT 1 ###

Sample values provided in this example represent an acknowledgement of a newly entered Limit order with Day validity on instrument with SymbolIndex 1110530 in Central order book. In case of an order in a strategy, the field SecurityID (48) will provide the Symbol Index of that strategy Tag Field Name Format Len Possible Values M/C Short Description, Compatibility Notes & Conditions Value Example Message Header M Optiq Drop Copy Service – Interface Specification Message Structure For Individual Cases © 2022 Euronext N.V. - All rights reserved. Page 24 of 127 5.16.0 Tag Field Name Format Len Possible Values M/C Short Description, Compatibility Notes & Conditions Value Example 21005 ClientMessageSendingTime UTCTimestamp 27 Timestamp C Indicates the time of message transmission, the consistency of the time provided is not checked by the Exchange. 20190214-15:30:01.462743346 5979 OEGINFromMember UTCTimestamp 27 Timestamp C Order Entry Gateway IN time from member (in ns), measured when inbound message enters the gateway 20190214-15:28:52.833883664
"""

example_1_assistant_message = """
{
  "length": 27
}
"""

example_2_human_message = """
### SBE FIELD DESCRIPTION ###

{
    "field_name": "ISINCode",
    "data_type": "char",
    "ai_engine_id": 21
}

### CONTEXT 1 ###

String 4 Market code ASHR SSE A-Share ASZR SZSE A-Share 11 ISINCode String 12 ISIN code of the security. 24 InstrumentType String 4 Instrument type of the security. BOND Bonds EQTY Equities TRST Trusts 28 Filler String 2 30 SecurityShortName String 40 Security short name
"""

example_2_assistant_message = """
{
  "length": 12
}
"""

example_3_human_message = """
### SBE FIELD DESCRIPTION ###

{
  "field_tag_number": 1020,
  "field_name": "TradeVolume",
  "data_type": "char"
  "ai_engine_id": 66
}

### CONTEXT 1 ###

Where sent: - Snapshot Message - Delta / Incremental Message - All Trade Price Message - Price Without Turnover Message 8.33 TradeVolume Description: Cumulative volume of units traded in the day Type: Decimal Value Example exponent = -2 mantissa = 2555 resulting value = 25.55 Where sent: - Snapshot Message - Delta / Incremental Message
"""

example_3_assistant_message = """
{
  "length": 30
}
"""

example_4_human_message = ""

example_4_assistant_message = ""
