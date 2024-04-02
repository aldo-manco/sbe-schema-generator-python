# generate_document_fields_prompt.py

system_message = """
Sei un esperto in sistemi di trading elettronico con una conoscenza approfondita dei protocolli FIX e SBE. Ti verra fornita in input una trascrizione grezza ottenuta tramite OCR di una tabella che rappresenta i campi di un messaggio FIX o SBE. La tua missione e ricostruire la tabella step by step seguendo i seguenti passaggi:
1. Definire quali sono le colonne della tabella.
2. Definire per ogni campo della tabella quali sono i valori delle colonne.
3. Creare un JSON array contenente un JSON object per ogni campo della tabella. Ogni JSON object conterra delle coppie chiave/valore in cui la chiave corrisponde al nome della colonna e il valore corrisponde al valore della colonna per il campo specifico che il JSON object rappresenta.

Assicurati di includere solo ed esclusivamente un array JSON nel codice fornito. Questo array dovrà contenere, per ciascun campo del messaggio, un oggetto JSON con le informazioni fornite. Segui gli esempi che ti sono stati forniti.
        """

example_1_human_message = """
Tag Field Name Format Len Possible Values M/C | Short Description, Compatibility Notes Value
& Conditions Example
21005 | ClientMessageSen | UTCTimestam 27 | Timestamp Cc Indicates the time of message transmission, | 20190214-
dingTime p the consistency of the time provided is not 15:30:01.4
checked by the Exchange. 62743346
5979 | OEGINFromMemb | UTCTimestam 27 | Timestamp Cc Order Entry Gateway IN time from member | 29190214-
er p (in ns), measured when inbound message 15:28:52.8
enters the gateway 33883664
7764 | OEGOUTTOME UTCTimestam 27 | Timestamp Cc Gateway OUT time to ME (inns), measured | 29190214-
p when inbound message leaves the gateway | 15-28-52.8
34193232
21002 | BookINTime UTCTimestam 27 | Timestamp A Time of order creation in ME 20190214-
p 15:28:52.8
40530924
21003 | BookOUTTime UTCTimestam | 27 | Timestamp c Matching Engine OUT time (in ns), when 20190214-
p message leaves the Matching Engine (ME) 15:28:52.8
40568733
7765 | OEGINFromME UTCTimestam | 27 | Timestamp c Gateway IN time from ME (in ns), measured | 29190214-
p when outbound message enters the 15:28:52.8
gateway 33883664
11 CclOrdiD String 20 | From -2463 to 2463-1 A Identifier of an Order assigned by the Client | 39
when submitting an order to the Exchange
48 SecuritylD String 10 | From 0 to 2432-2 M Exchange defined ID of an 1110530
instrument/contract
22 SecurityIDSource String 1 8 = Symbol Index M Type of the SecurityID. Always set to 8 8
20020 | EMM Int 2 1 = Cash and Derivative Central Order Book (COB) A Exchange Market Mechanism a
7 = Derivative On Exchange Off book
8 = ETF MTF - NAV Central Order Book
37 OrderID String 20 | From 0 to 2464-2 M Numerical order identifier assigned by ME. 5
For acknowledgement of RFQ populated
with the same value as in field QuoteReqID
(131)
39 OrdStatus Char 1 0=New M Order status 0
        """

example_1_assistant_message = """
[
  {
    "Tag": 21005,
    "Field Name": "ClientMessageSendingTime",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Indicates the time of message transmission, the consistency of the time provided is not checked by the Exchange.",
    "Value Example": "20190214-15:30:01.462743346"
  },
  {
    "Tag": 5979,
    "Field Name": "OEGINFromMember",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Order Entry Gateway IN time from member (in ns), measured when inbound message enters the gateway.",
    "Value Example": "29190214-15:28:52.833883664"
  },
  {
    "Tag": 7764,
    "Field Name": "OEGOUTTOME",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Gateway OUT time to ME (in ns), measured when inbound message leaves the gateway.",
    "Value Example": "29190214-15-28-52.834193232"
  },
  {
    "Tag": 21002,
    "Field Name": "BookINTime",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "A",
    "Short Description, Compatibility Notes, Value & Conditions": "Time of order creation in ME.",
    "Value Example": "20190214-15:28:52.840530924"
  },
  {
    "Tag": 21003,
    "Field Name": "BookOUTTime",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Matching Engine OUT time (in ns), when message leaves the Matching Engine (ME).",
    "Value Example": "20190214-15:28:52.840568733"
  },
  {
    "Tag": 7765,
    "Field Name": "OEGINFromME",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Gateway IN time from ME (in ns), measured when outbound message enters the gateway.",
    "Value Example": "29190214-15:28:52.833883664"
  },
  {
    "Tag": 11,
    "Field Name": "ClOrdID",
    "Format": "String",
    "Len": 20,
    "Possible Values": "From -2463 to 2463-1",
    "M/C": "A",
    "Short Description, Compatibility Notes, Value & Conditions": "Identifier of an Order assigned by the Client when submitting an order to the Exchange.",
    "Value Example": "39"
  },
  {
    "Tag": 48,
    "Field Name": "SecurityID",
    "Format": "String",
    "Len": 10,
    "Possible Values": "From 0 to 2432-2",
    "M/C": "M",
    "Short Description, Compatibility Notes, Value & Conditions": "Exchange defined ID of an instrument/contract.",
    "Value Example": "1110530"
  },
  {
    "Tag": 22,
    "Field Name": "SecurityIDSource",
    "Format": "String",
    "Len": 1,
    "Possible Values": "8 = Symbol Index",
    "M/C": "M",
    "Short Description, Compatibility Notes, Value & Conditions": "Type of the SecurityID. Always set to 8.",
    "Value Example": "8"
  },
  {
    "Tag": 20020,
    "Field Name": "EMM",
    "Format": "Int",
    "Len": 2,
    "Possible Values": "1 = Cash and Derivative Central Order Book (COB), 7 = Derivative On Exchange Off book, 8 = ETF MTF - NAV Central Order Book",
    "M/C": "A",
    "Short Description, Compatibility Notes, Value & Conditions": "Exchange Market Mechanism.",
    "Value Example": ""
  },
  {
    "Tag": 37,
    "Field Name": "OrderID",
    "Format": "String",
    "Len": 20,
    "Possible Values": "From 0 to 2464-2",
    "M/C": "M",
    "Short Description, Compatibility Notes, Value & Conditions": "Numerical order identifier assigned by ME. For acknowledgement of RFQ populated with the same value as in field QuoteReqID (131).",
    "Value Example": "5"
  },
  {
    "Tag": 39,
    "Field Name": "OrdStatus",
    "Format": "Char",
    "Len": 1,
    "Possible Values": "0=New",
    "M/C": "M",
    "Short Description, Compatibility Notes, Value & Conditions": "Order status.",
    "Value Example": "0"
  }
]
        """

example_2_human_message = """
Tag Field Name
Standard Header
35 MsgType
Message Body
268 NoMDEntries
>
>
279
269
278
48
22
454
MDUpdateAction
MDEntryType
MDEntryID
Securityld
SecurityIDsource
NoSecurityAltID
Req Description
X = Market Data Incremental Refresh
Number of entries following.
Type of Market Data update action.
Value Meaning
0 New
1 Update
2 Delete
Types of Market Data Entries that the firm requesting
the Market Data is interested in receiving.
Value Meaning
0 Bid
1 Offer
Unique entry identifier.
Will be same as the OrderlD value for a firm order or
an indicative quote side.
The CUSIP or the ISIN of the symbol.
Source database of the Security Id for a given
symbol.
By default this field will be populated with the ISIN.
If ISIN is NOT present this will contain the CUSIP of
the instrument.
Value Meaning
1 CUSIP
4 ISIN
Number of alternate Security Identifiers

=> 455 SecurityAltID N
=> 456 SecurityAltIDSource N
+ 270 MDEntryPx N
+ 271 MDEntrySize N
+ 1023 MDPriceLevel Y
+ 290 MDEntryPositionNo Y
+ 6373 FirmnessIndicator N
> 110 MinQty N
+ 6372 Mine N
MMI BondsPro — FIX 4.4 Market Data Feed
Security Alternate identifier for this security
Source of SecurityAItID <455>. Required if
SecurityAltID <455> is specified.
Value Meaning
1 CUSIP
Used if the entry has price related data. Unmarked
flat price will be populated always.
Required only if the MDUpdateAction(279) is 'New(0)'
or 'Update(1)’.
Quantity or volume represented by the Market Data
Entry.
Required only if the MDUpdateAction(279) is 'New(0)'
or 'Update(1)’.
Integer to convey the level of a bid or offer at a given
price level.
This is in contrast to MDEntryPositionNo which is
used to convey the position of an order within a Price
level.
Display position of a bid or offer within a price level,
numbered from most competitive to least
competitive, beginning with 1.
Indicates the quality of market data for indicative
quotes (>0).
A Firmness Indicator value of 0 is reserved to
represent firm orders.
Value Meaning
0 Firm Order
>0 Subject quote and quality of market data
Permission
1. Population of the tag is dependent on
the required permissions being
present for the user who is receiving
market data
Minimum quantity of the order in Buy or Sell side. By
default the value for this field will be set to 0.
Indicates whether the interest was submitted by the
same firm or an external firm.
        """

example_2_assistant_message = """
[
  {
    "Tag": 35,
    "Field Name": "MsgType",
    "Req Description": "X = Market Data Incremental Refresh"
  },
  {
    "Tag": 268,
    "Field Name": "NoMDEntries",
    "Req Description": "Number of entries following."
  },
  {
    "Tag": 279,
    "Field Name": "MDUpdateAction",
    "Req Description": "Type of Market Data update action.",
    "Value Meaning": {
      "0": "New",
      "1": "Update",
      "2": "Delete"
    }
  },
  {
    "Tag": 269,
    "Field Name": "MDEntryType",
    "Req Description": "Types of Market Data Entries that the firm requesting the Market Data is interested in receiving.",
    "Value Meaning": {
      "0": "Bid",
      "1": "Offer"
    }
  },
  {
    "Tag": 278,
    "Field Name": "MDEntryID",
    "Req Description": "Unique entry identifier. Will be same as the OrderID value for a firm order or an indicative quote side."
  },
  {
    "Tag": 48,
    "Field Name": "SecurityID",
    "Req Description": "The CUSIP or the ISIN of the symbol."
  },
  {
    "Tag": 22,
    "Field Name": "SecurityIDSource",
    "Req Description": "Source database of the Security Id for a given symbol. By default this field will be populated with the ISIN. If ISIN is NOT present this will contain the CUSIP of the instrument.",
    "Value Meaning": {
      "1": "CUSIP",
      "4": "ISIN"
    }
  },
  {
    "Tag": 454,
    "Field Name": "NoSecurityAltID",
    "Req Description": "Number of alternate Security Identifiers"
  },
  {
    "Tag": 455,
    "Field Name": "SecurityAltID",
    "Req Description": "Security Alternate identifier for this security"
  },
  {
    "Tag": 456,
    "Field Name": "SecurityAltIDSource",
    "Req Description": "Source of SecurityAltID <455>. Required if SecurityAltID <455> is specified.",
    "Value Meaning": {
      "1": "CUSIP"
    }
  },
  {
    "Tag": 270,
    "Field Name": "MDEntryPx",
    "Req Description": "Used if the entry has price related data. Unmarked flat price will be populated always. Required only if the MDUpdateAction(279) is \'New(0)\'
or \'Update(1)\'."
  },
  {
    "Tag": 271,
    "Field Name": "MDEntrySize",
    "Req Description": "Quantity or volume represented by the Market Data Entry. Required only if the MDUpdateAction(279) is \'New(0)\' or \'Update(1)\'."
  },
  {
    "Tag": 1023,
    "Field Name": "MDPriceLevel",
    "Req Description": "Integer to convey the level of a bid or offer at a given price level. This is in contrast to MDEntryPositionNo which is used to convey the position of an order within a Price level."
  },
  {
    "Tag": 290,
    "Field Name": "MDEntryPositionNo",
    "Req Description": "Display position of a bid or offer within a price level, numbered from most competitive to least competitive, beginning with 1."
  },
  {
    "Tag": 6373,
    "Field Name": "FirmnessIndicator",
    "Req Description": "Indicates the quality of market data for indicative quotes (>0). A Firmness Indicator value of 0 is reserved to represent firm orders.",
    "Value Meaning": {
      "0": "Firm Order",
      ">0": "Subject quote and quality of market data"
    },
    "Permission": "1. Population of the tag is dependent on the required permissions being present for the user who is receiving market data"
  },
  {
    "Tag": 110,
    "Field Name": "MinQty",
    "Req Description": "Minimum quantity of the order in Buy or Sell side. By default the value for this field will be set to 0."
  },
  {
    "Tag": 6372,
    "Field Name": "Mine",
    "Req Description": "Indicates whether the interest was submitted by the same firm or an external firm."
  }
]
        """

example_3_human_message = """
FIX tag | Field Name R| Field | Description
e | Form
q| at
d
35 MsgType Y | See Message Type.
8.16 CO = SecurityMassStatus
34 See an
MsgSeqNum x 815 The sequence number of the message is incremented p
, maintenance feed message.
See
49 SenderCompld ¥ 8.28 Source ID of sender
1679 SecurityMassTradingStatus Y| See 2: Trading Halt
8.25 17: Ready to Trade
18: Not available for trading
23: Fast Market
1680 SecurityMassTradingEvent Y| See 2: Market Reset, Trading resumes.
8.24 5: Change of Trading Subsession; Exchange segment
state change.
6: Change of SecurityTradingStatus; Fast Market chang
1544 InstrumentScopeProductComplex | N| See This tag is restricted to instruments in trading model
8.2 “Continuous Auction” only. The target state is always
delivered with TradingSessionSubID (625). Mutually
exclusive with (1616, 1547) and 1545.
        """

example_3_assistant_message = """
[
  {
    "FIX tag": 35,
    "Field Name": "MsgType",
    "Required": "Y",
    "Field Format": "See Message Type.",
    "Field Description": "CO = SecurityMassStatus"
  },
  {
    "FIX tag": 34,
    "Field Name": "MsgSeqNum",
    "Required": "Y",
    "Field Format": "See",
    "Field Description": "The sequence number of the message is incremented, maintenance feed message."
  },
  {
    "FIX tag": 49,
    "Field Name": "SenderCompID",
    "Required": "Y",
    "Field Format": "See",
    "Field Description": "Source ID of sender"
  },
  {
    "FIX tag": 1679,
    "Field Name": "SecurityMassTradingStatus",
    "Required": "Y",
    "Field Format": "See",
    "Field Description": "2: Trading Halt, 17: Ready to Trade, 18: Not available for trading, 23: Fast Market"
  },
  {
    "FIX tag": 1680,
    "Field Name": "SecurityMassTradingEvent",
    "Required": "Y",
    "Field Format": "See",
    "Field Description": "2: Market Reset, Trading resumes, 5: Change of Trading Subsession; Exchange segment state change, 6: Change of SecurityTradingStatus; Fast Market change"
  },
  {
    "FIX tag": 1544,
    "Field Name": "InstrumentScopeProductComplex",
    "Required": "N",
    "Field Format": "See",
    "Field Description": "This tag is restricted to instruments in trading model “Continuous Auction” only. The target state is always delivered with TradingSessionSubID (625). Mutually exclusive with (1616, 1547) and 1545."
  }
]
        """

example_4_human_message = ""

example_4_assistant_message = ""