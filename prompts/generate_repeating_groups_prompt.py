# generate_repeating_groups_prompt.py

system_message = """
You are an expert in electronic trading systems with a deep understanding of FIX and SBE protocols. Your mission is to identify repeating groups within a provided JSON array of message field information from market documentation. Identify repeating groups using the following criteria:
- Start/End Indicators: 
Typically, a field that indicates the length or number of elements (NumInGroup) often precedes the repeating group fields. In some cases, repeating groups are delimited by special fields that mark the beginning and end, or they may include a composite field that serves as a header.
- Pattern in Names: 
Groups of fields with similar names, such as PartyID, PartyIDSource, PartyRole, and PartyRoleQualifier, suggest a common grouping.
- Fields Grouped Together: 
Repeating groups are often consecutive in the JSON array and may follow a numerical sequence.
- Field Descriptions: 
Descriptions containing words like "party" or "group" can indicate a field's association with a repeating group.
- Semantic Correlation: 
A logical relationship between fields can indicate that they represent attributes of the same repeating group.

In your response, include only a JSON array. This array must contain a JSON object for each repeating group, described as follows:
- ai_engine_id: AI Engine Identifier of the NumInGroup field.
- group_id: Identifier of the NumInGroup field.
- group_name: A name derived from the repeating group field names.
- items: A JSON array of AI Engine Identifiers of fields within the repeating group.

In your response, include only an empty JSON array if no repeating groups are identified. 

Adhere the provided examples closely.
    """

example_1_human_message = """
[
  {
    "Tag": "21038",
    "Field Name": "RFQConfirmationIndicator",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates whether the message is, or not, an order sent as a confirmation of a QuoteRequest (R) message.",
    "Value Example": "CASH ONLY",
    "ai_engine_id": 1
  },
  {
    "Tag": "21800",
    "Field Name": "ConditionalOrderFlag",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = Firm (default), 1 = Conditional",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates if the order is a conditional or a firm order",
    "Value Example": "CASH ONLY",
    "ai_engine_id": 2
  },
  {
    "Tag": "453",
    "Field Name": "NoPartyIDs",
    "Format": "NumInGroup",
    "Len": "1",
    "Possible Values": "Always set to 1",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Number of PartyID entries",
    "Value Example": "1",
    "ai_engine_id": 3
  },
  {
    "Tag": "448",
    "Field Name": "PartyID",
    "Format": "String",
    "Len": "11",
    "Possible Values": "Alphanumeric",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "In this case provides the ExecutionWithinFirmShortCode",
    "Value Example": "59786",
    "ai_engine_id": 4
  },
  {
    "Tag": "447",
    "Field Name": "PartyIDSource",
    "Format": "Char",
    "Len": "1",
    "Possible Values": "P = Short code identifier",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Source of PartyID value",
    "Value Example": "P",
    "ai_engine_id": 5
  },
  {
    "Tag": "452",
    "Field Name": "PartyRole",
    "Format": "Int",
    "Len": "3",
    "Possible Values": "3 = Client ID, 12 = Executing Trader, 999 = Not Applicable",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Identifies the type or role of the PartyID specified.",
    "Value Example": "3",
    "ai_engine_id": 6
  },
  {
    "Tag": "2376",
    "Field Name": "PartyRoleQualifier",
    "Format": "Int",
    "Len": "2",
    "Possible Values": "22 = Algorithm, 23 = Firm or legal entity, 24 = Natural person, 99 = Not Applicable",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Used to further qualify the value of PartyRole",
    "Value Example": "23",
    "ai_engine_id": 7
  },
  {
    "Tag": "1724",
    "Field Name": "OrderOrigination",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "5 = Order received from a direct access or sponsored access customer",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Identifies the origin of the order",
    "Value Example": "",
    "ai_engine_id": 8
  },
  {
    "Tag": "2593",
    "Field Name": "NoOrderAttributes",
    "Format": "NumInGroup",
    "Len": "1",
    "Possible Values": "If provided, from 1 to 2",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Number of order attribute entries",
    "Value Example": "",
    "ai_engine_id": 9
  },
  {
    "Tag": "2594",
    "Field Name": "OrderAttributeType",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = Aggregated order, 1 = Pending allocation, 3 = Risk reduction order",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Used in case client needs to indicate values of AGGR or PNAL, OR in Risk Reduction order",
    "Value Example": "",
    "ai_engine_id": 10
  },
  {
    "Tag": "2595",
    "Field Name": "OrderAttributeValue",
    "Format": "String",
    "Len": "1",
    "Possible Values": "Y = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Always set to Yes if OrderAttributeType if provided",
    "Value Example": "",
    "ai_engine_id": 11
  }
]
    """

example_1_assistant_message = """
[
  {
    "ai_engine_id": 3,
    "group_id": "453",
    "group_name": "PartyIDGroup",
    "items": [4, 5, 6, 7]
  },
  {
    "ai_engine_id": 9,
    "group_id": "2593",
    "group_name": "OrderAttributesGroup",
    "items": [10, 11]
  }
]
    """

example_2_human_message = """
[
  {
    "Tag": "454",
    "FieldName": "NoSecurityAltID",
    "Req": "N",
    "Description": "Number of alternate Security Identifiers",
    "ai_engine_id": 5
  },
  {
    "Tag": "455",
    "FieldName": "SecurityAltID",
    "Req": "N",
    "Description": "Security Alternate identifier for this security",
    "ai_engine_id": 6
  },
  {
    "Tag": "456",
    "FieldName": "SecurityAltIDSource",
    "Req": "N",
    "Description": "Source of SecurityAltID <455>. Required if SecurityAltID <455> is specified.",
    "Value Meaning": {
      "1": "CUSIP"
    },
    "ai_engine_id": 7
  },
  {
    "Tag": "326",
    "FieldName": "SecurityTradingStatus",
    "Req": "Y",
    "Description": "Indicates the current trading session for the instrument.",
    "Value Meaning": {
      "2": "Halt",
      "3": "Resume",
      "111": "Pause",
      "112": "End of Pause"
    },
    "ai_engine_id": 8
  },
  {
    "Tag": "1174",
    "FieldName": "SecurityTradingEvent",
    "Req": "N",
    "Description": "Indicates the reason a trading session is extended or shortened.",
    "Value Meaning": {
      "101": "Extended by Market Operations",
      "102": "Shortened by Market Operations"
    },
    "ai_engine_id": 9
  }
]
    """

example_2_assistant_message = """
[
  {
    "ai_engine_id": 5,
    "group_id": "454",
    "group_name": "SecurityAltIDGroup",
    "items": [6, 7]
  }
]
    """

example_3_human_message = """
[
  {
    "FIX tag": "35",
    "Field Name": "MsgType",
    "Req’d": "Y",
    "Field Format": "See 8.16",
    "Description": "X = MarketDataIncrementalRefresh",
    "ai_engine_id": 13
  },
  {
    "FIX tag": "34",
    "Field Name": "MsgSeqNum",
    "Req’d": "Y",
    "Field Format": "See 8.15",
    "Description": "The sequence number of the message is incremented per ticker message.",
    "ai_engine_id": 14
  },
  {
    "FIX tag": "49",
    "Field Name": "SenderCompID",
    "Req’d": "Y",
    "Field Format": "See 8.28",
    "Description": "Source ID of sender",
    "ai_engine_id": 15
  },
  {
    "FIX tag": "268",
    "Field Name": "NoMDEntries",
    "Req’d": "Y",
    "Field Format": "See 8.17",
    "Description": "Defines the size of the repeating group",
    "ai_engine_id": 16
  },
  {
    "FIX tag": "279",
    "Field Name": "MDUpdateAction",
    "Req’d": "Y",
    "Field Format": "See 8.14",
    "Description": "0= New ; always “new”",
    "ai_engine_id": 17
  },
  {
    "FIX tag": "48",
    "Field Name": "SecurityID",
    "Req’d": "Y",
    "Field Format": "See 8.23",
    "Description": "ISIN of instrument",
    "ai_engine_id": 18
  },
  {
    "FIX tag": "270",
    "Field Name": "MDEntryPx",
    "Req’d": "Y",
    "Field Format": "See 8.8",
    "Description": "Price or index value",
    "ai_engine_id": 19
  },
  {
    "FIX tag": "271",
    "Field Name": "MDEntrySize",
    "Req’d": "N",
    "Field Format": "See 8.9",
    "Description": "Quantity, not set for indices",
    "ai_engine_id": 20
  },
  {
    "FIX tag": "273",
    "Field Name": "MDEntryTime",
    "Req’d": "N",
    "Field Format": "See 8.10",
    "Description": "Time of market data entry",
    "ai_engine_id": 21
  },
  {
    "FIX tag": "15",
    "Field Name": "Currency",
    "Req’d": "N",
    "Field Format": "See 8.1",
    "Description": "Price currency",
    "ai_engine_id": 22
  },
  {
    "FIX tag": "1500",
    "Field Name": "MDStreamID",
    "Req’d": "Y",
    "Field Format": "See 8.13",
    "Description": "Name of the price source",
    "ai_engine_id": 23
  }
]
    """

example_3_assistant_message = """
[
  {
    "ai_engine_id": 16,
    "group_id": "268",
    "group_name": "MDEntriesGroup",
    "items": [17, 18, 19, 20, 21, 22, 23]
  }
]
    """

example_4_human_message = """
[
  {
    "Tag": "20175",
    "Field Name": "TriggeredStopTimeInForce",
    "Format": "Char",
    "Len": "1",
    "Possible Values": "0 = Day, 1 = Good Till Cancel, 6 = Good till Date",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Specifies the maximum validity of an triggered stop order. On triggering of a Stop order the value in this field is populated in the field TimeInForce (59).",
    "Value Example": "CASH ONLY - Specifies the maximum validity of an triggered stop order. On triggering of a Stop order the value in this field is populated in the field TimeInForce (59).",
    "ai_engine_id": 34
  },
  {
    "Tag": "131",
    "Field Name": "QuoteReqID",
    "Format": "String",
    "Len": "20",
    "Possible Values": "From 0 to 2^64-2",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Numerical RFQ identifier assigned by the matching engine, unique per instrument and EMM.",
    "Value Example": "CASH ONLY - Numerical RFQ identifier assigned by the matching engine, unique per instrument and EMM.",
    "ai_engine_id": 35
  },
  {
    "Tag": "21037",
    "Field Name": "RFQAnswerIndicator",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates whether the message is, or not, a quote sent as an answer to a QuoteRequest (R) message.",
    "Value Example": "CASH ONLY - Indicates whether the message is, or not, a quote sent as an answer to a QuoteRequest (R) message.",
    "ai_engine_id": 36
  },
  {
    "Tag": "21038",
    "Field Name": "RFQConfirmationIndicator",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates whether the message is, or not, an order sent as a confirmation of a QuoteRequest (R) message.",
    "Value Example": "CASH ONLY - Indicates whether the message is, or not, an order sent as a confirmation of a QuoteRequest (R) message.",
    "ai_engine_id": 37
  },
  {
    "Tag": "21800",
    "Field Name": "ConditionalOrderFlag",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = Firm (default), 1 = Conditional",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates if the order is a conditional or a firm order",
    "Value Example": "CASH ONLY - Indicates if the order is a conditional or a firm order",
    "ai_engine_id": 38
  }
]
    """

example_4_assistant_message = """
[]
    """