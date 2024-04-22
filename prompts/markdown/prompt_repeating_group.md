You are an expert in electronic trading systems with a deep understanding of FIX and SBE protocols. Your mission is to identify repeating groups within a provided JSON array of message field information from market documentation. Identify repeating groups using the following criteria:
- Start/End Indicators: 
Typically, one or more fields that indicates the length or number of elements of the repeating group (ex. NumInGroup) often precedes the repeating group fields. In some cases, repeating groups are delimited by special fields that mark the beginning and end, or they may include a composite field that serves as a header.
- Pattern in Names: 
Groups of fields with similar names, such as PartyID, PartyIDSource, PartyRole, and PartyRoleQualifier, suggest a common grouping.
- Fields Grouped Together: 
Repeating groups are often consecutive in the JSON array and may follow a numerical sequence.
- Field Descriptions: 
Descriptions containing words like "party" or "group" can indicate a field's association with a repeating group.
- Semantic Correlation: 
A logical relationship between fields can indicate that they represent attributes of the same repeating group.

In your response, include only a JSON array. This array must contain a JSON object for each repeating group, described as follows:
- group_tag_number: If a field in message fields represents a FIX protocol tag number, either standard or custom, assign the appropriate of the NumInGroup field. If no such tag number is defined, do not define the group_tag_number.
- group_name: A name derived from the repeating group field names.
- items: A JSON array of AI Engine Identifiers of fields within the repeating group.
- indicators_items: A JSON array of AI Engine Identifiers of Start/End Indicators of the repeating group. Typically, one or more fields that indicates the length or number of elements of the repeating group (ex. NumInGroup).

In your response, include only an empty JSON array if no repeating groups are identified. 

Adhere the provided examples closely.

### ESEMPIO 1: INPUT ###

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

### ESEMPIO 1: OUTPUT ###

[
  {
    "group_tag_number": 453,
    "group_name": "PartyIDGroup",
    "items": [4, 5, 6, 7]
    "indicators_items": [3]
  },
  {
    "group_tag_number": 2593,
    "group_name": "OrderAttributesGroup",
    "items": [10, 11]
    "indicators_items": [9]
  }
]

### ESEMPIO 2: INPUT ###

[
  {
    "Field": "Market Data Sequence Number",
    "Short Description": "Assigned by MDG for each message. Each channel has its own Market Data Sequence Number sequence.",
    "Format": "Sequence",
    "Len": 8,
    "Values": "From 0 to 2^64-2",
    "Presence": "Mandatory",
    "ai_engine_id": 9
  },
  {
    "Field": "Rebroadcast Indicator",
    "Short Description": "Indicates if this message is resent or new (1 if resent, 0 otherwise). For a snapshot, this field will always be set to '1'.",
    "Format": "Numerical ID",
    "Len": 1,
    "Values": "From 0 to 2^8-2",
    "Presence": "Mandatory",
    "ai_engine_id": 10 
  },
  {
    "Field": "EMM",
    "Short Description": "Defines the Exchange Market Mechanism applied on each platform.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "(See field description)",
    "Presence": "Mandatory",
    "ai_engine_id": 11
  },
  {
    "Field": "Event Time",
    "Short Description": "Time when an event has been processed",
    "Format": "Epoch Time in Nanoseconds",
    "Len": 8,
    "Values": "From 0 to 2^64-2",
    "Presence": "Mandatory",
    "ai_engine_id": 12
  },
  {
    "Field": "Orders length",
    "Short Description": "Repeating Section Header",
    "Format": "Numerical",
    "Len": 1,
    "Values": "0...2^16-2",
    "Presence": "Mandatory",
    "ai_engine_id": 13
  },
  {
    "Field": "Orders occurrences",
    "Short Description": "Repeating Section Header",
    "Format": "Numerical",
    "Len": 1,
    "Values": "1..254",
    "Presence": "Mandatory",
    "ai_engine_id": 14
  },
  {
    "Field": "Symbol Index",
    "Short Description": "Exchange identification code of the instrument/contract.",
    "Format": "Numerical ID",
    "Len": 4,
    "Values": "From 0 to 2^32-2",
    "Presence": "Mandatory",
    "ai_engine_id": 15
  },
  {
    "Field": "Market Data Action Type",
    "Short Description": "Identifies if the order is a New Order, a Deletion, a Modification or a Retransmission.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "(See field description)",
    "Presence": "Mandatory",
    "ai_engine_id": 16
  },
  {
    "Field": "Order Priority",
    "Short Description": "Rank giving the priority of the order. The order with the lowest value of Order Priority has the highest priority.",
    "Format": "Numerical ID",
    "Len": 8,
    "Values": "From 0 to 2^64-2",
    "Presence": "Optional",
    "ai_engine_id": 17
  },
  {
    "Field": "Previous Priority",
    "Short Description": "Previous Priority is populated only when there is a 'Modification of existing order With Loss Of Priority' or order deletions. Then clients have to remove from their market sheet the order identified with the field 'Previous Priority' and add a new order with the field 'Order Priority' newly provided.",
    "Format": "Numerical ID",
    "Len": 8,
    "Values": "From 0 to 2^64-2",
    "Presence": "Optional",
    "ai_engine_id": 18
  },
  {
    "Field": "Order Type",
    "Short Description": "Type of Order.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "(See field description)",
    "Presence": "Optional",
    "ai_engine_id": 19
  },
  {
    "Field": "Order Price",
    "Short Description": "Instrument price per quantity unit (To be calculated with Price/Index Level Decimals).",
    "Format": "Price",
    "Len": 8,
    "Values": "From -2^63+1 to 2^63-1",
    "Presence": "Optional",
    "ai_engine_id": 20
  },
  {
    "Field": "Order Side",
    "Short Description": "Indicates the side of the order.",
    "Format": "Enumerated",
    "Len": 1,
    "Values": "1 Buy, 2 Sell, 3 Cross",
    "Presence": "Optional",
    "ai_engine_id": 21
  },
  {
    "Field": "Order Quantity",
    "Short Description": "Total order quantity, per quantity unit.(To be calculated with Quantity Decimals).",
    "Format": "Quantity",
    "Len": 8,
    "Values": "From 0 to 2^64-2",
    "Presence": "Optional",
    "ai_engine_id": 22
  },
  {
    "Field": "Peg Offset",
    "Short Description": "(Future Use) Tick offset for a pegged order.",
    "Format": "Numerical ID",
    "Len": 1,
    "Values": "From -127 to 127",
    "Presence": "Optional",
    "ai_engine_id": 23
  }
]

### ESEMPIO 2: OUTPUT ###

[
  {
    "group_name": "OrdersGroup",
    "items": [15, 16, 17, 18, 19, 20, 21, 22, 23]
    "indicators_items": [13, 14]
  }
]

### ESEMPIO 3: INPUT ###

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

### ESEMPIO 3: OUTPUT ###

[
  {
    "group_tag_number": 268,
    "group_name": "MDEntriesGroup",
    "items": [17, 18, 19, 20, 21, 22, 23]
    "indicators_items": [16]
  }
]

### ESEMPIO 4: INPUT ###

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

### ESEMPIO 4: OUTPUT ###

[]

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