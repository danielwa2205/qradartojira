#Mapping:   Feldname in Jira            Name des Offensefeldes  Feldtyp in Jira
mapping = { "Zusammenfassung"       :   ["description",         "einzeilig"],
            "LHM QRadar Offense - Id"   :   ["id",                  "einzeilig"],
            "LHM QRadar Offense - Source IP"          :   ["offense_source",                 "einzeilig"],
            "LHM QRadar Offense - Source Network"             :   ["source_network",                 "einzeilig"],
            "LHM QRadar Offense - Source Id"          :   ["source_address_ids",                 "einzeilig"],
            "LHM QRadar Offense - Destination Network"          :   ["destination_networks",                 "einzeilig"],
            "LHM QRader Offense - Destination Id"          :   ["local_destination_address_ids",                 "einzeilig"],
            "LHM QRadar Offense - angeschlagene Rules"          :   ["rules",                 "mehrzeilig"],
            "LHM QRadar Offense - Log Sources"          :   ["log_sources",                 "mehrzeilig"],
          }