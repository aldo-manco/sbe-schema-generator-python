# generate_repeating_groups_prompt.py

system_message = """
Sei esperto in sistemi di trading elettronico e conosci approfonditamente i protocolli FIX e SBE. Devi analizzare un array JSON contenente informazioni sui campi di un messaggio SBE per identificare se alcuni di essi formano un repeating group, basandoti su criteri specifici:
- Pattern nei Nomi: Campi con nomi simili, come PartyID, PartyIDSource, PartyRole, PartyRoleQualifier, indicano un insieme comune.
- Sequenza Numerica: I campi di un repeating group sono tipicamente in sequenza numerica continua o raggruppati senza interruzioni.
- Descrizione dei Campi: Termini come "party" o "group" nelle descrizioni possono suggerire l'appartenenza a un repeating group.
- Consistenza nei Tipi di Dato e Lunghezza: I campi in un repeating group solitamente hanno tipi di dato simili e un campo che indica la lunghezza o il numero di elementi spesso precede il gruppo.
- Correlazione Semantica: Una logica relazione tra i campi può indicare che rappresentano attributi di un medesimo oggetto o concetto.
- Indicatori di Inizio/Fine: In alcuni casi, i repeating groups sono delimitati da campi speciali che segnano l'inizio e la fine o presentano un campo composito come intestazione.

Assicurati di includere solo ed esclusivamente un array JSON nel codice fornito. Questo array dovrà contenere, per ciascun gruppo ripetuto, un oggetto JSON che lo descrive con i rispettivi campi. Ogni oggetto JSON deve contenere:
- group_id: l'identificativo del campo che indica il numero di elementi nel gruppo (NumInGroup),
- group_name: un nome proposto per il gruppo, derivato dai nomi dei campi,
- items: un array JSON contenente un oggetto per ogni campo all'interno del gruppo ripetuto, includendo tutte le informazioni disponibili.

Qualora non siano presenti gruppi ripetuti, l'output sarà un array JSON vuoto.

Segui gli esempi che ti sono stati forniti.
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
    "Value Example": "CASH ONLY"
  },
  {
    "Tag": "21800",
    "Field Name": "ConditionalOrderFlag",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = Firm (default), 1 = Conditional",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates if the order is a conditional or a firm order",
    "Value Example": "CASH ONLY"
  },
  {
    "Tag": "453",
    "Field Name": "NoPartyIDs",
    "Format": "NumInGroup",
    "Len": "1",
    "Possible Values": "Always set to 1",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Number of PartyID entries",
    "Value Example": "1"
  },
  {
    "Tag": "448",
    "Field Name": "PartyID",
    "Format": "String",
    "Len": "11",
    "Possible Values": "Alphanumeric",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "In this case provides the ExecutionWithinFirmShortCode",
    "Value Example": "59786"
  },
  {
    "Tag": "447",
    "Field Name": "PartyIDSource",
    "Format": "Char",
    "Len": "1",
    "Possible Values": "P = Short code identifier",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Source of PartyID value",
    "Value Example": "P"
  },
  {
    "Tag": "452",
    "Field Name": "PartyRole",
    "Format": "Int",
    "Len": "3",
    "Possible Values": "3 = Client ID, 12 = Executing Trader, 999 = Not Applicable",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Identifies the type or role of the PartyID specified.",
    "Value Example": "3"
  },
  {
    "Tag": "2376",
    "Field Name": "PartyRoleQualifier",
    "Format": "Int",
    "Len": "2",
    "Possible Values": "22 = Algorithm, 23 = Firm or legal entity, 24 = Natural person, 99 = Not Applicable",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Used to further qualify the value of PartyRole",
    "Value Example": "23"
  },
  {
    "Tag": "1724",
    "Field Name": "OrderOrigination",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "5 = Order received from a direct access or sponsored access customer",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Identifies the origin of the order",
    "Value Example": ""
  },
  {
    "Tag": "2593",
    "Field Name": "NoOrderAttributes",
    "Format": "NumInGroup",
    "Len": "1",
    "Possible Values": "If provided, from 1 to 2",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Number of order attribute entries",
    "Value Example": ""
  },
  {
    "Tag": "2594",
    "Field Name": "OrderAttributeType",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = Aggregated order, 1 = Pending allocation, 3 = Risk reduction order",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Used in case client needs to indicate values of AGGR or PNAL, OR in Risk Reduction order",
    "Value Example": ""
  },
  {
    "Tag": "2595",
    "Field Name": "OrderAttributeValue",
    "Format": "String",
    "Len": "1",
    "Possible Values": "Y = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Always set to Yes if OrderAttributeType if provided",
    "Value Example": ""
  }
]
    """

example_1_assistant_message = """
[
  {
    "group_id": "453",
    "group_name": "PartyIDGroup",
    "items": [
      {
        "Tag": "448",
        "Field Name": "PartyID",
        "Format": "String",
        "Len": "11",
        "Possible Values": "Alphanumeric",
        "M/C": "A",
        "Short Description, Compatibility Notes & Conditions": "In this case provides the ExecutionWithinFirmShortCode",
        "Value Example": "59786"
      },
      {
        "Tag": "447",
        "Field Name": "PartyIDSource",
        "Format": "Char",
        "Len": "1",
        "Possible Values": "P = Short code identifier",
        "M/C": "A",
        "Short Description, Compatibility Notes & Conditions": "Source of PartyID value",
        "Value Example": "P"
      },
      {
        "Tag": "452",
        "Field Name": "PartyRole",
        "Format": "Int",
        "Len": "3",
        "Possible Values": "3 = Client ID, 12 = Executing Trader, 999 = Not Applicable",
        "M/C": "A",
        "Short Description, Compatibility Notes & Conditions": "Identifies the type or role of the PartyID specified.",
        "Value Example": "3"
      },
      {
        "Tag": "2376",
        "Field Name": "PartyRoleQualifier",
        "Format": "Int",
        "Len": "2",
        "Possible Values": "22 = Algorithm, 23 = Firm or legal entity, 24 = Natural person, 99 = Not Applicable",
        "M/C": "C",
        "Short Description, Compatibility Notes & Conditions": "Used to further qualify the value of PartyRole",
        "Value Example": "23"
      }
    ]
  },
  {
    "group_id": "2593",
    "group_name": "OrderAttributesGroup",
    "items": [
      {
        "Tag": "2594",
        "Field Name": "OrderAttributeType",
        "Format": "Int",
        "Len": "1",
        "Possible Values": "0 = Aggregated order, 1 = Pending allocation, 3 = Risk reduction order",
        "M/C": "C",
        "Short Description, Compatibility Notes & Conditions": "Used in case client needs to indicate values of AGGR or PNAL, OR in Risk Reduction order",
        "Value Example": ""
      },
      {
        "Tag": "2595",
        "Field Name": "OrderAttributeValue",
        "Format": "String",
        "Len": "1",
        "Possible Values": "Y = Yes",
        "M/C": "C",
        "Short Description, Compatibility Notes & Conditions": "Always set to Yes if OrderAttributeType if provided",
        "Value Example": ""
      }
    ]
  }
]
    """

example_2_human_message = """
[
  {
    "Tag": "454",
    "FieldName": "NoSecurityAltID",
    "Req": "N",
    "Description": "Number of alternate Security Identifiers"
  },
  {
    "Tag": "455",
    "FieldName": "SecurityAltID",
    "Req": "N",
    "Description": "Security Alternate identifier for this security"
  },
  {
    "Tag": "456",
    "FieldName": "SecurityAltIDSource",
    "Req": "N",
    "Description": "Source of SecurityAltID <455>. Required if SecurityAltID <455> is specified.",
    "Value Meaning": {
      "1": "CUSIP"
    }
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
    }
  },
  {
    "Tag": "1174",
    "FieldName": "SecurityTradingEvent",
    "Req": "N",
    "Description": "Indicates the reason a trading session is extended or shortened.",
    "Value Meaning": {
      "101": "Extended by Market Operations",
      "102": "Shortened by Market Operations"
    }
  }
]
    """

example_2_assistant_message = """
[
  {
    "group_id": "454",
    "group_name": "SecurityAltIDGroup",
    "items": [
      {
        "Tag": "455",
        "FieldName": "SecurityAltID",
        "Req": "N",
        "Description": "Security Alternate identifier for this security"
      },
      {
        "Tag": "456",
        "FieldName": "SecurityAltIDSource",
        "Req": "N",
        "Description": "Source of SecurityAltID <455>. Required if SecurityAltID <455> is specified.",
        "Value Meaning": {
          "1": "CUSIP"
        }
      }
    ]
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
    "Description": "X = MarketDataIncrementalRefresh"
  },
  {
    "FIX tag": "34",
    "Field Name": "MsgSeqNum",
    "Req’d": "Y",
    "Field Format": "See 8.15",
    "Description": "The sequence number of the message is incremented per ticker message."
  },
  {
    "FIX tag": "49",
    "Field Name": "SenderCompID",
    "Req’d": "Y",
    "Field Format": "See 8.28",
    "Description": "Source ID of sender"
  },
  {
    "FIX tag": "268",
    "Field Name": "NoMDEntries",
    "Req’d": "Y",
    "Field Format": "See 8.17",
    "Description": "Defines the size of the repeating group"
  },
  {
    "FIX tag": "279",
    "Field Name": "MDUpdateAction",
    "Req’d": "Y",
    "Field Format": "See 8.14",
    "Description": "0= New ; always “new”"
  },
  {
    "FIX tag": "48",
    "Field Name": "SecurityID",
    "Req’d": "Y",
    "Field Format": "See 8.23",
    "Description": "ISIN of instrument"
  },
  {
    "FIX tag": "270",
    "Field Name": "MDEntryPx",
    "Req’d": "Y",
    "Field Format": "See 8.8",
    "Description": "Price or index value"
  },
  {
    "FIX tag": "271",
    "Field Name": "MDEntrySize",
    "Req’d": "N",
    "Field Format": "See 8.9",
    "Description": "Quantity, not set for indices"
  },
  {
    "FIX tag": "273",
    "Field Name": "MDEntryTime",
    "Req’d": "N",
    "Field Format": "See 8.10",
    "Description": "Time of market data entry"
  },
  {
    "FIX tag": "15",
    "Field Name": "Currency",
    "Req’d": "N",
    "Field Format": "See 8.1",
    "Description": "Price currency"
  },
  {
    "FIX tag": "1500",
    "Field Name": "MDStreamID",
    "Req’d": "Y",
    "Field Format": "See 8.13",
    "Description": "Name of the price source"
  }
]
    """

example_3_assistant_message = """
[
  {
    "group_id": "268",
    "group_name": "MDEntriesGroup",
    "items": [
      {
        "FIX tag": "279",
        "Field Name": "MDUpdateAction",
        "Req’d": "Y",
        "Field Format": "See 8.14",
        "Description": "0= New ; always “new”"
      },
      {
        "FIX tag": "48",
        "Field Name": "SecurityID",
        "Req’d": "Y",
        "Field Format": "See 8.23",
        "Description": "ISIN of instrument"
      },
      {
        "FIX tag": "270",
        "Field Name": "MDEntryPx",
        "Req’d": "Y",
        "Field Format": "See 8.8",
        "Description": "Price or index value"
      },
      {
        "FIX tag": "271",
        "Field Name": "MDEntrySize",
        "Req’d": "N",
        "Field Format": "See 8.9",
        "Description": "Quantity, not set for indices"
      },
      {
        "FIX tag": "273",
        "Field Name": "MDEntryTime",
        "Req’d": "N",
        "Field Format": "See 8.10",
        "Description": "Time of market data entry"
      },
      {
        "FIX tag": "15",
        "Field Name": "Currency",
        "Req’d": "N",
        "Field Format": "See 8.1",
        "Description": "Price currency"
      },
      {
        "FIX tag": "1500",
        "Field Name": "MDStreamID",
        "Req’d": "Y",
        "Field Format": "See 8.13",
        "Description": "Name of the price source"
      }
    ]
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
    "Value Example": "CASH ONLY - Specifies the maximum validity of an triggered stop order. On triggering of a Stop order the value in this field is populated in the field TimeInForce (59)."
  },
  {
    "Tag": "131",
    "Field Name": "QuoteReqID",
    "Format": "String",
    "Len": "20",
    "Possible Values": "From 0 to 2^64-2",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Numerical RFQ identifier assigned by the matching engine, unique per instrument and EMM.",
    "Value Example": "CASH ONLY - Numerical RFQ identifier assigned by the matching engine, unique per instrument and EMM."
  },
  {
    "Tag": "21037",
    "Field Name": "RFQAnswerIndicator",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates whether the message is, or not, a quote sent as an answer to a QuoteRequest (R) message.",
    "Value Example": "CASH ONLY - Indicates whether the message is, or not, a quote sent as an answer to a QuoteRequest (R) message."
  },
  {
    "Tag": "21038",
    "Field Name": "RFQConfirmationIndicator",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates whether the message is, or not, an order sent as a confirmation of a QuoteRequest (R) message.",
    "Value Example": "CASH ONLY - Indicates whether the message is, or not, an order sent as a confirmation of a QuoteRequest (R) message."
  },
  {
    "Tag": "21800",
    "Field Name": "ConditionalOrderFlag",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = Firm (default), 1 = Conditional",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates if the order is a conditional or a firm order",
    "Value Example": "CASH ONLY - Indicates if the order is a conditional or a firm order"
  }
]
    """

example_4_assistant_message = """
[]
    """