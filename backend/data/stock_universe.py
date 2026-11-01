"""
NSE/BSE Stock Universe — curated list of major stocks with sector/industry info.
Cleaned and verified against live NSE and Yahoo Finance data.
"""

# Format: (symbol, name, sector, industry, sub_industry, exchange, yf_symbol)
# If yf_symbol is not provided, defaults to f"{symbol}.NS" for NSE or f"{symbol}.BO" for BSE.

RAW_UNIVERSE = [
    # ---- Information Technology ----
    ("TCS", "Tata Consultancy Services", "Information Technology", "IT", "IT Consulting & Services", "NSE", "TCS.NS"),
    ("INFY", "Infosys", "Information Technology", "IT", "IT Consulting & Services", "NSE", "INFY.NS"),
    ("WIPRO", "Wipro", "Information Technology", "IT", "IT Consulting & Services", "NSE", "WIPRO.NS"),
    ("HCLTECH", "HCL Technologies", "Information Technology", "IT", "IT Consulting & Services", "NSE", "HCLTECH.NS"),
    ("TECHM", "Tech Mahindra", "Information Technology", "IT", "IT Consulting & Services", "NSE", "TECHM.NS"),
    ("LTIM", "LTIMindtree", "Information Technology", "IT", "IT Consulting & Services", "NSE", "LTM.NS"),
    ("MPHASIS", "Mphasis", "Information Technology", "IT", "IT Consulting & Services", "NSE", "MPHASIS.NS"),
    ("PERSISTENT", "Persistent Systems", "Information Technology", "IT", "IT Consulting & Services", "NSE", "PERSISTENT.NS"),
    ("COFORGE", "Coforge", "Information Technology", "IT", "IT Consulting & Services", "NSE", "COFORGE.NS"),
    ("KPITTECH", "KPIT Technologies", "Information Technology", "IT", "IT Services - Auto", "NSE", "KPITTECH.NS"),
    ("TATAELXSI", "Tata Elxsi", "Information Technology", "IT", "IT Design", "NSE", "TATAELXSI.NS"),
    ("NEWGEN", "Newgen Software", "Information Technology", "IT", "Software Products", "NSE", "NEWGEN.NS"),
    ("MASTEK", "Mastek", "Information Technology", "IT", "IT Services", "NSE", "MASTEK.NS"),
    ("BSOFT", "Birlasoft", "Information Technology", "IT", "IT Services", "NSE", "BSOFT.NS"),
    ("CYIENT", "Cyient", "Information Technology", "IT", "IT Engineering Services", "NSE", "CYIENT.NS"),
    ("NIITLTD", "NIIT Limited", "Information Technology", "IT", "IT Training", "NSE", "NIITLTD.NS"),
    ("ROUTE", "Route Mobile", "Information Technology", "IT", "Communications Platform", "NSE", "ROUTE.NS"),
    ("FSL", "Firstsource Solutions", "Information Technology", "IT", "BPO", "NSE", "FSL.NS"),
    ("INTELLECT", "Intellect Design Arena", "Information Technology", "IT", "FinTech Software", "NSE", "INTELLECT.NS"),
    ("RAMCOSYS", "Ramco Systems", "Information Technology", "IT", "ERP Software", "NSE", "RAMCOSYS.NS"),
    ("ZENSARTECH", "Zensar Technologies", "Information Technology", "IT", "IT Services", "NSE", "ZENSARTECH.NS"),

    # ---- Banking ----
    ("HDFCBANK", "HDFC Bank", "Banks", "Banks", "Private Banks", "NSE", "HDFCBANK.NS"),
    ("ICICIBANK", "ICICI Bank", "Banks", "Banks", "Private Banks", "NSE", "ICICIBANK.NS"),
    ("KOTAKBANK", "Kotak Mahindra Bank", "Banks", "Banks", "Private Banks", "NSE", "KOTAKBANK.NS"),
    ("AXISBANK", "Axis Bank", "Banks", "Banks", "Private Banks", "NSE", "AXISBANK.NS"),
    ("INDUSINDBK", "IndusInd Bank", "Banks", "Banks", "Private Banks", "NSE", "INDUSINDBK.NS"),
    ("FEDERALBNK", "Federal Bank", "Banks", "Banks", "Private Banks", "NSE", "FEDERALBNK.NS"),
    ("IDFCFIRSTB", "IDFC First Bank", "Banks", "Banks", "Private Banks", "NSE", "IDFCFIRSTB.NS"),
    ("YESBANK", "Yes Bank", "Banks", "Banks", "Private Banks", "NSE", "YESBANK.NS"),
    ("BANDHANBNK", "Bandhan Bank", "Banks", "Banks", "Private Banks", "NSE", "BANDHANBNK.NS"),
    ("RBLBANK", "RBL Bank", "Banks", "Banks", "Private Banks", "NSE", "RBLBANK.NS"),
    ("SBIN", "State Bank of India", "Banks", "Banks", "PSU Banks", "NSE", "SBIN.NS"),
    ("BANKBARODA", "Bank of Baroda", "Banks", "Banks", "PSU Banks", "NSE", "BANKBARODA.NS"),
    ("PNB", "Punjab National Bank", "Banks", "Banks", "PSU Banks", "NSE", "PNB.NS"),
    ("CANBK", "Canara Bank", "Banks", "Banks", "PSU Banks", "NSE", "CANBK.NS"),
    ("UNIONBANK", "Union Bank of India", "Banks", "Banks", "PSU Banks", "NSE", "UNIONBANK.NS"),
    ("KARURVYSYA", "Karur Vysya Bank", "Banks", "Banks", "Private Banks", "NSE", "KARURVYSYA.NS"),
    ("CUB", "City Union Bank", "Banks", "Banks", "Private Banks", "NSE", "CUB.NS"),
    ("DCBBANK", "DCB Bank", "Banks", "Banks", "Private Banks", "NSE", "DCBBANK.NS"),

    # ---- Financial Services ----
    ("BAJFINANCE", "Bajaj Finance", "Financial Services", "NBFC", "Consumer Finance", "NSE", "BAJFINANCE.NS"),
    ("BAJAJFINSV", "Bajaj Finserv", "Financial Services", "Financial Holding", "Diversified Financial", "NSE", "BAJAJFINSV.NS"),
    ("CHOLAFIN", "Cholamandalam Investment", "Financial Services", "NBFC", "Vehicle Finance", "NSE", "CHOLAFIN.NS"),
    ("MUTHOOTFIN", "Muthoot Finance", "Financial Services", "NBFC", "Gold Loans", "NSE", "MUTHOOTFIN.NS"),
    ("MANAPPURAM", "Manappuram Finance", "Financial Services", "NBFC", "Gold Loans", "NSE", "MANAPPURAM.NS"),
    ("SHRIRAMFIN", "Shriram Finance", "Financial Services", "NBFC", "Vehicle Finance", "NSE", "SHRIRAMFIN.NS"),
    ("M&MFIN", "M&M Financial Services", "Financial Services", "NBFC", "Rural Finance", "NSE", "M&MFIN.NS"),
    ("LICHSGFIN", "LIC Housing Finance", "Financial Services", "HFC", "Housing Finance", "NSE", "LICHSGFIN.NS"),
    ("PNBHOUSING", "PNB Housing Finance", "Financial Services", "HFC", "Housing Finance", "NSE", "PNBHOUSING.NS"),
    ("CANFINHOME", "Can Fin Homes", "Financial Services", "HFC", "Housing Finance", "NSE", "CANFINHOME.NS"),
    ("HOMEFIRST", "Home First Finance", "Financial Services", "HFC", "Housing Finance", "NSE", "HOMEFIRST.NS"),
    ("AAVAS", "Aavas Financiers", "Financial Services", "HFC", "Affordable Housing", "NSE", "AAVAS.NS"),
    ("APTUS", "Aptus Value Housing", "Financial Services", "HFC", "Affordable Housing", "NSE", "APTUS.NS"),
    ("IRFC", "Indian Railway Finance Corp", "Financial Services", "NBFC", "Railway Finance", "NSE", "IRFC.NS"),
    ("RECLTD", "REC", "Financial Services", "NBFC", "Power Sector Finance", "NSE", "RECLTD.NS"),
    ("PFC", "Power Finance Corporation", "Financial Services", "NBFC", "Power Sector Finance", "NSE", "PFC.NS"),
    ("HUDCO", "HUDCO", "Financial Services", "HFC", "Urban Infrastructure Finance", "NSE", "HUDCO.NS"),

    # ---- Capital Markets ----
    ("ANGELONE", "Angel One", "Capital Markets", "Broking", "Retail Broking", "NSE", "ANGELONE.NS"),
    ("ICICIPRULI", "ICICI Prudential Life", "Capital Markets", "Insurance", "Life Insurance", "NSE", "ICICIPRULI.NS"),
    ("SBILIFE", "SBI Life Insurance", "Capital Markets", "Insurance", "Life Insurance", "NSE", "SBILIFE.NS"),
    ("HDFCLIFE", "HDFC Life Insurance", "Capital Markets", "Insurance", "Life Insurance", "NSE", "HDFCLIFE.NS"),
    ("LICI", "Life Insurance Corporation", "Capital Markets", "Insurance", "Life Insurance", "NSE", "LICI.NS"),
    ("NIACL", "New India Assurance", "Capital Markets", "Insurance", "General Insurance", "NSE", "NIACL.NS"),
    ("ICICIGI", "ICICI Lombard General Insurance", "Capital Markets", "Insurance", "General Insurance", "NSE", "ICICIGI.NS"),
    ("STARHEALTH", "Star Health Insurance", "Capital Markets", "Insurance", "Health Insurance", "NSE", "STARHEALTH.NS"),
    ("BSE", "BSE", "Capital Markets", "Exchange", "Stock Exchange", "NSE", "BSE.NS"),
    ("CDSL", "Central Depository Services", "Capital Markets", "Depository", "Financial Infrastructure", "NSE", "CDSL.NS"),
    ("MCX", "MCX India", "Capital Markets", "Exchange", "Commodity Exchange", "NSE", "MCX.NS"),
    ("CAMS", "CAMS", "Capital Markets", "Asset Management", "Financial Infrastructure", "NSE", "CAMS.NS"),
    ("360ONE", "360 One WAM", "Capital Markets", "Wealth Management", "HNI Wealth", "NSE", "360ONE.NS"),
    ("NUVAMA", "Nuvama Wealth", "Capital Markets", "Wealth Management", "HNI Wealth", "NSE", "NUVAMA.NS"),
    ("IIFL", "IIFL Finance", "Capital Markets", "NBFC", "Diversified Finance", "NSE", "IIFL.NS"),
    ("MOTILALOFS", "Motilal Oswal Financial", "Capital Markets", "Broking", "Full-Service Broking", "NSE", "MOTILALOFS.NS"),
    ("5PAISA", "5Paisa Capital", "Capital Markets", "Broking", "Discount Broking", "NSE", "5PAISA.NS"),
    ("FINCABLES", "Finolex Cables", "Capital Markets", "Electrical", "Cables", "NSE", "FINCABLES.NS"),
    ("SMCGLOBAL", "SMC Global Securities", "Capital Markets", "Broking", "Diversified Broking", "NSE", "SMCGLOBAL.NS"),

    # ---- Auto ----
    ("MARUTI", "Maruti Suzuki", "Auto", "Auto", "Passenger Vehicles", "NSE", "MARUTI.NS"),
    ("M&M", "Mahindra & Mahindra", "Auto", "Auto", "Passenger & Commercial Vehicles", "NSE", "M&M.NS"),
    ("TMPV", "Tata Motors (PV)", "Auto", "Auto", "Passenger Vehicles", "NSE", "TMPV.NS"),
    ("TMCV", "Tata Motors (CV)", "Auto", "Auto", "Commercial Vehicles", "NSE", "TMCV.NS"),
    ("BAJAJ-AUTO", "Bajaj Auto", "Auto", "Auto", "Two-Wheelers", "NSE", "BAJAJ-AUTO.NS"),
    ("HEROMOTOCO", "Hero MotoCorp", "Auto", "Auto", "Two-Wheelers", "NSE", "HEROMOTOCO.NS"),
    ("EICHERMOT", "Eicher Motors", "Auto", "Auto", "Premium Motorcycles", "NSE", "EICHERMOT.NS"),
    ("TVSMOTOR", "TVS Motor Company", "Auto", "Auto", "Two-Wheelers", "NSE", "TVSMOTOR.NS"),
    ("ASHOKLEY", "Ashok Leyland", "Auto", "Auto", "Commercial Vehicles", "NSE", "ASHOKLEY.NS"),
    ("MOTHERSON", "Samvardhana Motherson", "Auto", "Auto Ancillaries", "Auto Components", "NSE", "MOTHERSON.NS"),
    ("BOSCHLTD", "Bosch", "Auto", "Auto Ancillaries", "Auto Components", "NSE", "BOSCHLTD.NS"),
    ("BHARATFORG", "Bharat Forge", "Auto", "Auto Ancillaries", "Forgings", "NSE", "BHARATFORG.NS"),
    ("TIINDIA", "Tube Investments", "Auto", "Auto Ancillaries", "Auto Components", "NSE", "TIINDIA.NS"),
    ("SUPRAJIT", "Suprajit Engineering", "Auto", "Auto Ancillaries", "Auto Cables", "NSE", "SUPRAJIT.NS"),
    ("ENDURANCE", "Endurance Technologies", "Auto", "Auto Ancillaries", "Auto Components", "NSE", "ENDURANCE.NS"),
    ("SUNDRMFAST", "Sundaram Fasteners", "Auto", "Auto Ancillaries", "Fasteners", "NSE", "SUNDRMFAST.NS"),
    ("APOLLOTYRE", "Apollo Tyres", "Auto", "Tyres", "Tyres", "NSE", "APOLLOTYRE.NS"),
    ("MRF", "MRF", "Auto", "Tyres", "Tyres", "NSE", "MRF.NS"),
    ("CEATLTD", "CEAT", "Auto", "Tyres", "Tyres", "NSE", "CEATLTD.NS"),
    ("BALKRISIND", "Balkrishna Industries", "Auto", "Tyres", "Off-Highway Tyres", "NSE", "BALKRISIND.NS"),

    # ---- Pharma & Healthcare ----
    ("SUNPHARMA", "Sun Pharmaceutical", "Pharma & Healthcare", "Pharma", "Pharma - Diversified", "NSE", "SUNPHARMA.NS"),
    ("DRREDDY", "Dr. Reddy's Laboratories", "Pharma & Healthcare", "Pharma", "Pharma - Global", "NSE", "DRREDDY.NS"),
    ("CIPLA", "Cipla", "Pharma & Healthcare", "Pharma", "Pharma - Branded", "NSE", "CIPLA.NS"),
    ("DIVISLAB", "Divi's Laboratories", "Pharma & Healthcare", "Pharma", "API Manufacturing", "NSE", "DIVISLAB.NS"),
    ("BIOCON", "Biocon", "Pharma & Healthcare", "Pharma", "Biologics", "NSE", "BIOCON.NS"),
    ("LUPIN", "Lupin", "Pharma & Healthcare", "Pharma", "Pharma - Global", "NSE", "LUPIN.NS"),
    ("AUROPHARMA", "Aurobindo Pharma", "Pharma & Healthcare", "Pharma", "Pharma - Global", "NSE", "AUROPHARMA.NS"),
    ("ALKEM", "Alkem Laboratories", "Pharma & Healthcare", "Pharma", "Pharma - Branded", "NSE", "ALKEM.NS"),
    ("TORNTPHARM", "Torrent Pharmaceuticals", "Pharma & Healthcare", "Pharma", "Pharma - Branded", "NSE", "TORNTPHARM.NS"),
    ("ZYDUSLIFE", "Zydus Lifesciences", "Pharma & Healthcare", "Pharma", "Pharma - Diversified", "NSE", "ZYDUSLIFE.NS"),
    ("ABBOTINDIA", "Abbott India", "Pharma & Healthcare", "Pharma", "Pharma - Branded", "NSE", "ABBOTINDIA.NS"),
    ("SANOFI", "Sanofi India", "Pharma & Healthcare", "Pharma", "Pharma - MNC", "NSE", "SANOFI.NS"),
    ("PFIZER", "Pfizer", "Pharma & Healthcare", "Pharma", "Pharma - MNC", "NSE", "PFIZER.NS"),
    ("IPCALAB", "IPCA Laboratories", "Pharma & Healthcare", "Pharma", "Pharma - API", "NSE", "IPCALAB.NS"),
    ("LAURUSLABS", "Laurus Labs", "Pharma & Healthcare", "Pharma", "API Manufacturing", "NSE", "LAURUSLABS.NS"),
    ("GRANULES", "Granules India", "Pharma & Healthcare", "Pharma", "API Manufacturing", "NSE", "GRANULES.NS"),
    ("SUVEN", "Suven Pharmaceuticals", "Pharma & Healthcare", "Pharma", "CRAMS", "NSE", "SUVEN.NS"),
    ("AJANTPHARM", "Ajanta Pharma", "Pharma & Healthcare", "Pharma", "Pharma - Branded", "NSE", "AJANTPHARM.NS"),
    ("MAXHEALTH", "Max Healthcare", "Pharma & Healthcare", "Healthcare", "Hospitals", "NSE", "MAXHEALTH.NS"),
    ("APOLLOHOSP", "Apollo Hospitals", "Pharma & Healthcare", "Healthcare", "Hospitals", "NSE", "APOLLOHOSP.NS"),
    ("FORTIS", "Fortis Healthcare", "Pharma & Healthcare", "Healthcare", "Hospitals", "NSE", "FORTIS.NS"),
    ("KIMS", "Krishna Institute of Medical Sciences", "Pharma & Healthcare", "Healthcare", "Hospitals", "NSE", "KIMS.NS"),
    ("MEDANTA", "Global Health (Medanta)", "Pharma & Healthcare", "Healthcare", "Hospitals", "NSE", "MEDANTA.NS"),
    ("METROPOLIS", "Metropolis Healthcare", "Pharma & Healthcare", "Healthcare", "Diagnostics", "NSE", "METROPOLIS.NS"),
    ("THYROCARE", "Thyrocare Technologies", "Pharma & Healthcare", "Healthcare", "Diagnostics", "NSE", "THYROCARE.NS"),
    ("LALPATHLAB", "Dr. Lal Path Labs", "Pharma & Healthcare", "Healthcare", "Diagnostics", "NSE", "LALPATHLAB.NS"),

    # ---- FMCG ----
    ("HINDUNILVR", "Hindustan Unilever", "FMCG", "FMCG", "Personal & Home Care", "NSE", "HINDUNILVR.NS"),
    ("ITC", "ITC", "FMCG", "FMCG", "Diversified FMCG", "NSE", "ITC.NS"),
    ("NESTLEIND", "Nestle India", "FMCG", "FMCG", "Food Products", "NSE", "NESTLEIND.NS"),
    ("BRITANNIA", "Britannia Industries", "FMCG", "FMCG", "Biscuits & Bakery", "NSE", "BRITANNIA.NS"),
    ("DABUR", "Dabur India", "FMCG", "FMCG", "Ayurvedic & Healthcare", "NSE", "DABUR.NS"),
    ("MARICO", "Marico", "FMCG", "FMCG", "Hair & Edible Oils", "NSE", "MARICO.NS"),
    ("GODREJCP", "Godrej Consumer Products", "FMCG", "FMCG", "Personal Care", "NSE", "GODREJCP.NS"),
    ("EMAMILTD", "Emami", "FMCG", "FMCG", "Ayurvedic & Healthcare", "NSE", "EMAMILTD.NS"),
    ("COLPAL", "Colgate-Palmolive India", "FMCG", "FMCG", "Oral Care", "NSE", "COLPAL.NS"),
    ("VBL", "Varun Beverages", "FMCG", "FMCG", "Beverages", "NSE", "VBL.NS"),
    ("RADICO", "Radico Khaitan", "FMCG", "FMCG", "Spirits", "NSE", "RADICO.NS"),
    ("UBL", "United Breweries", "FMCG", "FMCG", "Beer", "NSE", "UBL.NS"),
    ("TATACONSUM", "Tata Consumer Products", "FMCG", "FMCG", "Tea & Foods", "NSE", "TATACONSUM.NS"),
    ("UNITDSPR", "United Spirits", "FMCG", "FMCG", "Spirits", "NSE", "UNITDSPR.NS"),
    ("PGHH", "Procter & Gamble Hygiene", "FMCG", "FMCG", "Personal Care - MNC", "NSE", "PGHH.NS"),
    ("GILLETTE", "Gillette India", "FMCG", "FMCG", "Grooming Products", "NSE", "GILLETTE.NS"),

    # ---- Oil & Gas ----
    ("RELIANCE", "Reliance Industries", "Oil & Gas", "Oil & Gas", "Integrated Energy", "NSE", "RELIANCE.NS"),
    ("ONGC", "Oil & Natural Gas Corp", "Oil & Gas", "Oil & Gas", "Exploration & Production", "NSE", "ONGC.NS"),
    ("BPCL", "Bharat Petroleum", "Oil & Gas", "Oil & Gas", "Refining & Marketing", "NSE", "BPCL.NS"),
    ("IOC", "Indian Oil Corporation", "Oil & Gas", "Oil & Gas", "Refining & Marketing", "NSE", "IOC.NS"),
    ("HINDPETRO", "Hindustan Petroleum", "Oil & Gas", "Oil & Gas", "Refining & Marketing", "NSE", "HINDPETRO.NS"),
    ("GAIL", "GAIL India", "Oil & Gas", "Oil & Gas", "Natural Gas Transmission", "NSE", "GAIL.NS"),
    ("PETRONET", "Petronet LNG", "Oil & Gas", "Oil & Gas", "LNG Terminal", "NSE", "PETRONET.NS"),
    ("OIL", "Oil India", "Oil & Gas", "Oil & Gas", "Exploration & Production", "NSE", "OIL.NS"),
    ("CASTROLIND", "Castrol India", "Oil & Gas", "Lubricants", "Lubricants", "NSE", "CASTROLIND.NS"),
    ("MRPL", "Mangalore Refinery", "Oil & Gas", "Oil & Gas", "Refining", "NSE", "MRPL.NS"),

    # ---- Power ----
    ("POWERGRID", "Power Grid Corporation", "Power", "Power", "Power Transmission", "NSE", "POWERGRID.NS"),
    ("NTPC", "NTPC", "Power", "Power", "Power Generation", "NSE", "NTPC.NS"),
    ("ADANIGREEN", "Adani Green Energy", "Power", "Power", "Renewable Energy", "NSE", "ADANIGREEN.NS"),
    ("TATAPOWER", "Tata Power", "Power", "Power", "Integrated Power", "NSE", "TATAPOWER.NS"),
    ("TORNTPOWER", "Torrent Power", "Power", "Power", "Integrated Power", "NSE", "TORNTPOWER.NS"),
    ("CESC", "CESC", "Power", "Power", "Integrated Power", "NSE", "CESC.NS"),
    ("JSWENERGY", "JSW Energy", "Power", "Power", "Power Generation", "NSE", "JSWENERGY.NS"),
    ("ADANIPOWER", "Adani Power", "Power", "Power", "Thermal Power", "NSE", "ADANIPOWER.NS"),
    ("NHPC", "NHPC", "Power", "Power", "Hydro Power", "NSE", "NHPC.NS"),
    ("SJVN", "SJVN", "Power", "Power", "Hydro Power", "NSE", "SJVN.NS"),
    ("INOXWIND", "Inox Wind", "Power", "Power", "Wind Energy", "NSE", "INOXWIND.NS"),
    ("SUZLON", "Suzlon Energy", "Power", "Power", "Wind Energy", "NSE", "SUZLON.NS"),
    ("RPOWER", "Reliance Power", "Power", "Power", "Power Generation", "NSE", "RPOWER.NS"),

    # ---- Infrastructure ----
    ("LT", "Larsen & Toubro", "Infrastructure", "Engineering", "EPC - Diversified", "NSE", "LT.NS"),
    ("ADANIPORTS", "Adani Ports & SEZ", "Infrastructure", "Ports & Logistics", "Ports", "NSE", "ADANIPORTS.NS"),
    ("IRB", "IRB Infrastructure", "Infrastructure", "Roads", "BOT Roads", "NSE", "IRB.NS"),
    ("ASHOKA", "Ashoka Buildcon", "Infrastructure", "Roads", "BOT Roads", "NSE", "ASHOKA.NS"),
    ("KNRCON", "KNR Constructions", "Infrastructure", "Roads", "Road Construction", "NSE", "KNRCON.NS"),
    ("PNCINFRA", "PNC Infratech", "Infrastructure", "Roads", "Road Construction", "NSE", "PNCINFRA.NS"),
    ("HGINFRA", "H.G. Infra Engineering", "Infrastructure", "Roads", "Road Construction", "NSE", "HGINFRA.NS"),
    ("GRINFRA", "G R Infraprojects", "Infrastructure", "Roads", "Road Construction", "NSE", "GRINFRA.NS"),
    ("AHLUCONT", "Ahluwalia Contracts", "Infrastructure", "Construction", "Building Construction", "NSE", "AHLUCONT.NS"),
    ("GMRAIRPORT", "GMR Airports", "Infrastructure", "Airports", "Airport Operations", "NSE", "GMRAIRPORT.NS"),
    ("RVNL", "Rail Vikas Nigam", "Infrastructure", "Railways", "Railway Construction", "NSE", "RVNL.NS"),
    ("IRCTC", "Indian Railway Catering", "Infrastructure", "Railways", "Railway Services", "NSE", "IRCTC.NS"),
    ("RITES", "RITES", "Infrastructure", "Railways", "Railway Consultancy", "NSE", "RITES.NS"),
    ("NBCC", "NBCC India", "Infrastructure", "Construction", "Govt Construction", "NSE", "NBCC.NS"),
    ("KPIL", "Kalpataru Projects International", "Infrastructure", "Engineering", "Power Transmission EPC", "NSE", "KPIL.NS"),

    # ---- Metals & Mining ----
    ("TATASTEEL", "Tata Steel", "Metals", "Metals", "Steel - Integrated", "NSE", "TATASTEEL.NS"),
    ("JSWSTEEL", "JSW Steel", "Metals", "Metals", "Steel - Integrated", "NSE", "JSWSTEEL.NS"),
    ("HINDALCO", "Hindalco Industries", "Metals", "Metals", "Aluminium", "NSE", "HINDALCO.NS"),
    ("VEDL", "Vedanta", "Metals", "Metals", "Diversified Metals", "NSE", "VEDL.NS"),
    ("COALINDIA", "Coal India", "Metals", "Mining", "Coal Mining", "NSE", "COALINDIA.NS"),
    ("NMDC", "NMDC", "Metals", "Mining", "Iron Ore Mining", "NSE", "NMDC.NS"),
    ("NATIONALUM", "National Aluminium", "Metals", "Metals", "Aluminium - PSU", "NSE", "NATIONALUM.NS"),
    ("SAIL", "Steel Authority of India", "Metals", "Metals", "Steel - PSU", "NSE", "SAIL.NS"),
    ("JINDALSTEL", "Jindal Steel & Power", "Metals", "Metals", "Steel - Integrated", "NSE", "JINDALSTEL.NS"),
    ("JINDALPOLY", "Jindal Poly Films", "Metals", "Metals", "Packaging Films", "NSE", "JINDALPOLY.NS"),
    ("RATNAMANI", "Ratnamani Metals & Tubes", "Metals", "Metals", "Steel Tubes", "NSE", "RATNAMANI.NS"),
    ("APLAPOLLO", "APL Apollo Tubes", "Metals", "Metals", "Steel Tubes", "NSE", "APLAPOLLO.NS"),

    # ---- Chemicals ----
    ("PCBL", "PCBL", "Chemicals", "Chemicals", "Carbon Black", "NSE", "PCBL.NS"),
    ("PIDILITIND", "Pidilite Industries", "Chemicals", "Chemicals", "Adhesives & Sealants", "NSE", "PIDILITIND.NS"),
    ("ASIANPAINT", "Asian Paints", "Chemicals", "Chemicals", "Paints", "NSE", "ASIANPAINT.NS"),
    ("BERGEPAINT", "Berger Paints", "Chemicals", "Chemicals", "Paints", "NSE", "BERGEPAINT.NS"),
    ("KANSAINER", "Kansai Nerolac Paints", "Chemicals", "Chemicals", "Paints", "NSE", "KANSAINER.NS"),
    ("JSWDULUX", "JSW Dulux (Akzo Nobel)", "Chemicals", "Chemicals", "Specialty Paints", "NSE", "JSWDULUX.NS"),
    ("SRF", "SRF", "Chemicals", "Chemicals", "Specialty Chemicals - Fluorine", "NSE", "SRF.NS"),
    ("NAVINFLUOR", "Navin Fluorine", "Chemicals", "Chemicals", "Fluorine Specialty", "NSE", "NAVINFLUOR.NS"),
    ("DEEPAKNTR", "Deepak Nitrite", "Chemicals", "Chemicals", "Basic & Specialty Chemicals", "NSE", "DEEPAKNTR.NS"),
    ("FINEORG", "Fine Organics", "Chemicals", "Chemicals", "Oleo Chemicals", "NSE", "FINEORG.NS"),
    ("ANURAS", "Anupam Rasayan", "Chemicals", "Chemicals", "Custom Synthesis", "NSE", "ANURAS.NS"),
    ("CLEAN", "Clean Science", "Chemicals", "Chemicals", "Performance Chemicals", "NSE", "CLEAN.NS"),
    ("SUDARSCHEM", "Sudarshan Chemical", "Chemicals", "Chemicals", "Pigments", "NSE", "SUDARSCHEM.NS"),
    ("GALAXYSURF", "Galaxy Surfactants", "Chemicals", "Chemicals", "Surfactants", "NSE", "GALAXYSURF.NS"),
    ("VINATIORGA", "Vinati Organics", "Chemicals", "Chemicals", "Specialty Chemicals", "NSE", "VINATIORGA.NS"),
    ("ATUL", "Atul", "Chemicals", "Chemicals", "Agrochemicals & Specialty", "NSE", "ATUL.NS"),
    ("TATACHEM", "Tata Chemicals", "Chemicals", "Chemicals", "Basic Chemicals", "NSE", "TATACHEM.NS"),
    ("CHAMBLFERT", "Chambal Fertilizers", "Chemicals", "Fertilizers", "Fertilizers", "NSE", "CHAMBLFERT.NS"),
    ("COROMANDEL", "Coromandel International", "Chemicals", "Fertilizers", "Fertilizers & Agri", "NSE", "COROMANDEL.NS"),
    ("GNFC", "Gujarat Narmada Valley Fertilizer", "Chemicals", "Fertilizers", "Fertilizers", "NSE", "GNFC.NS"),
    ("MOLDTKPAC", "Mold-Tek Packaging", "Chemicals", "Packaging", "Rigid Packaging", "NSE", "MOLDTKPAC.NS"),

    # ---- Consumer Durables ----
    ("HAVELLS", "Havells India", "Consumer Durables", "Consumer Durables", "Electrical Products", "NSE", "HAVELLS.NS"),
    ("VOLTAS", "Voltas", "Consumer Durables", "Consumer Durables", "Air Conditioning", "NSE", "VOLTAS.NS"),
    ("CROMPTON", "Crompton Greaves Consumer", "Consumer Durables", "Consumer Durables", "Fans & Pumps", "NSE", "CROMPTON.NS"),
    ("BLUESTARCO", "Blue Star", "Consumer Durables", "Consumer Durables", "Air Conditioning", "NSE", "BLUESTARCO.NS"),
    ("WHIRLPOOL", "Whirlpool of India", "Consumer Durables", "Consumer Durables", "Home Appliances", "NSE", "WHIRLPOOL.NS"),
    ("TITAN", "Titan Company", "Consumer Durables", "Retail", "Jewellery & Watches", "NSE", "TITAN.NS"),
    ("KALYANKJIL", "Kalyan Jewellers", "Consumer Durables", "Retail", "Jewellery", "NSE", "KALYANKJIL.NS"),
    ("SENCO", "Senco Gold", "Consumer Durables", "Retail", "Jewellery", "NSE", "SENCO.NS"),
    ("POLYCAB", "Polycab India", "Consumer Durables", "Consumer Durables", "Wires & Cables", "NSE", "POLYCAB.NS"),
    ("KEI", "KEI Industries", "Consumer Durables", "Consumer Durables", "Wires & Cables", "NSE", "KEI.NS"),
    ("BAJAJELEC", "Bajaj Electricals", "Consumer Durables", "Consumer Durables", "Electrical Products", "NSE", "BAJAJELEC.NS"),
    ("VIPIND", "VIP Industries", "Consumer Durables", "Retail", "Luggage", "NSE", "VIPIND.NS"),
    ("SAFARI", "Safari Industries", "Consumer Durables", "Retail", "Luggage", "NSE", "SAFARI.NS"),
    ("DIXON", "Dixon Technologies", "Consumer Durables", "Electronics", "EMS - Consumer Electronics", "NSE", "DIXON.NS"),
    ("AMBER", "Amber Enterprises", "Consumer Durables", "Electronics", "EMS - AC", "NSE", "AMBER.NS"),
    ("SYRMA", "Syrma SGS Technology", "Consumer Durables", "Electronics", "EMS", "NSE", "SYRMA.NS"),
    ("AVALON", "Avalon Technologies", "Consumer Durables", "Electronics", "EMS", "NSE", "AVALON.NS"),

    # ---- Telecom ----
    ("BHARTIARTL", "Bharti Airtel", "Telecom", "Telecom", "Telecom Services", "NSE", "BHARTIARTL.NS"),
    ("INDUSTOWER", "Indus Towers", "Telecom", "Telecom", "Tower Infrastructure", "NSE", "INDUSTOWER.NS"),
    ("TATACOMM", "Tata Communications", "Telecom", "Telecom", "Enterprise Connectivity", "NSE", "TATACOMM.NS"),
    ("IDEA", "Vodafone Idea", "Telecom", "Telecom", "Telecom Services", "NSE", "IDEA.NS"),
    ("RAILTEL", "RailTel Corporation", "Telecom", "Telecom", "Railway Telecom", "NSE", "RAILTEL.NS"),
    ("STLTECH", "Sterlite Technologies", "Telecom", "Telecom", "Telecom Equipment", "NSE", "STLTECH.NS"),
    ("VINDHYATEL", "Vindhya Telelinks", "Telecom", "Telecom", "Cables", "NSE", "VINDHYATEL.NS"),
    ("HFCL", "HFCL", "Telecom", "Telecom", "Telecom Infrastructure", "NSE", "HFCL.NS"),

    # ---- Realty ----
    ("DLF", "DLF", "Realty", "Realty", "Residential & Commercial", "NSE", "DLF.NS"),
    ("GODREJPROP", "Godrej Properties", "Realty", "Realty", "Residential", "NSE", "GODREJPROP.NS"),
    ("OBEROIRLTY", "Oberoi Realty", "Realty", "Realty", "Premium Residential", "NSE", "OBEROIRLTY.NS"),
    ("PHOENIXLTD", "Phoenix Mills", "Realty", "Realty", "Retail Malls", "NSE", "PHOENIXLTD.NS"),
    ("PRESTIGE", "Prestige Estates", "Realty", "Realty", "Residential & Commercial", "NSE", "PRESTIGE.NS"),
    ("BRIGADE", "Brigade Enterprises", "Realty", "Realty", "Residential", "NSE", "BRIGADE.NS"),
    ("SUNTECK", "Sunteck Realty", "Realty", "Realty", "Luxury Residential", "NSE", "SUNTECK.NS"),
    ("SOBHA", "Sobha", "Realty", "Realty", "Residential", "NSE", "SOBHA.NS"),
    ("MAHLIFE", "Mahindra Lifespace", "Realty", "Realty", "Residential", "NSE", "MAHLIFE.NS"),
    ("LODHA", "Macrotech Developers", "Realty", "Realty", "Affordable & Mid Residential", "NSE", "LODHA.NS"),
    ("KOLTEPATIL", "Kolte-Patil Developers", "Realty", "Realty", "Residential", "NSE", "KOLTEPATIL.NS"),

    # ---- Data Centres & Cloud ----
    ("BBOX", "Black Box", "Data Centres & Cloud", "IT Infrastructure", "IT Enabled Services", "NSE", "BBOX.NS"),
    ("E2E", "E2E Networks", "Data Centres & Cloud", "IT Infrastructure", "Cloud Computing & GPU", "NSE", "E2E.NS"),
    ("NETWEB", "Netweb Technologies", "Data Centres & Cloud", "IT Infrastructure", "High Performance Computing", "NSE", "NETWEB.NS"),
    ("ANANTRAJ", "Anant Raj", "Data Centres & Cloud", "IT Infrastructure", "Data Centers", "NSE", "ANANTRAJ.NS"),

    # ---- Defence ----
    ("HAL", "Hindustan Aeronautics", "Defence", "Defence", "Aerospace & Defence", "NSE", "HAL.NS"),
    ("BEL", "Bharat Electronics", "Defence", "Defence", "Defence Electronics", "NSE", "BEL.NS"),
    ("BEML", "BEML", "Defence", "Defence", "Defence Vehicles", "NSE", "BEML.NS"),
    ("MIDHANI", "Mishra Dhatu Nigam", "Defence", "Defence", "Specialty Alloys", "NSE", "MIDHANI.NS"),
    ("COCHINSHIP", "Cochin Shipyard", "Defence", "Defence", "Shipbuilding", "NSE", "COCHINSHIP.NS"),
    ("MAZDOCK", "Mazagon Dock Shipbuilders", "Defence", "Defence", "Shipbuilding", "NSE", "MAZDOCK.NS"),
    ("GRSE", "Garden Reach Shipbuilders", "Defence", "Defence", "Shipbuilding", "NSE", "GRSE.NS"),
    ("IDEAFORGE", "ideaForge Technology", "Defence", "Defence", "Drones & UAVs", "NSE", "IDEAFORGE.NS"),
    ("DCXINDIA", "DCX Systems", "Defence", "Defence", "Defence Electronics", "NSE", "DCXINDIA.NS"),
    ("DATAPATTNS", "Data Patterns", "Defence", "Defence", "Defence Electronics", "NSE", "DATAPATTNS.NS"),
    ("MTARTECH", "MTAR Technologies", "Defence", "Defence", "Aerospace & Precision", "NSE", "MTARTECH.NS"),
    ("PARAS", "Paras Defence", "Defence", "Defence", "Optics & Electronics", "NSE", "PARAS.NS"),
    ("SOLARINDS", "Solar Industries", "Defence", "Defence", "Explosives", "NSE", "SOLARINDS.NS"),

    # ---- Cement ----
    ("ULTRACEMCO", "UltraTech Cement", "Cement", "Cement", "Large Cap Cement", "NSE", "ULTRACEMCO.NS"),
    ("SHREECEM", "Shree Cement", "Cement", "Cement", "Large Cap Cement", "NSE", "SHREECEM.NS"),
    ("AMBUJACEM", "Ambuja Cements", "Cement", "Cement", "Large Cap Cement", "NSE", "AMBUJACEM.NS"),
    ("ACC", "ACC", "Cement", "Cement", "Large Cap Cement", "NSE", "ACC.NS"),
    ("DALBHARAT", "Dalmia Bharat", "Cement", "Cement", "Mid Cap Cement", "NSE", "DALBHARAT.NS"),
    ("JKCEMENT", "JK Cement", "Cement", "Cement", "Mid Cap Cement", "NSE", "JKCEMENT.NS"),
    ("RAMCOCEM", "The Ramco Cements", "Cement", "Cement", "South India Cement", "NSE", "RAMCOCEM.NS"),
    ("HEIDELBERG", "HeidelbergCement India", "Cement", "Cement", "Cement", "NSE", "HEIDELBERG.NS"),
    ("PRSMJOHNSN", "Prism Johnson", "Cement", "Cement", "Tiles & Building Materials", "NSE", "PRSMJOHNSN.NS"),

    # ---- Retail ----
    ("DMART", "Avenue Supermarts", "Retail", "Retail", "Grocery Retail", "NSE", "DMART.NS"),
    ("TRENT", "Trent", "Retail", "Retail", "Fashion Retail", "NSE", "TRENT.NS"),
    ("ABFRL", "Aditya Birla Fashion", "Retail", "Retail", "Fashion Retail", "NSE", "ABFRL.NS"),
    ("SHOPERSTOP", "Shoppers Stop", "Retail", "Retail", "Department Stores", "NSE", "SHOPERSTOP.NS"),
    ("VSTIND", "VST Industries", "Retail", "FMCG", "Cigarettes", "NSE", "VSTIND.NS"),
    ("NYKAA", "FSN E-Commerce (Nykaa)", "Retail", "Retail", "Beauty E-commerce", "NSE", "NYKAA.NS"),
    ("CARTRADE", "CarTrade Tech", "Retail", "Retail", "Auto Classifieds", "NSE", "CARTRADE.NS"),
    ("GOCOLORS", "Go Fashion", "Retail", "Retail", "Women's Bottomwear", "NSE", "GOCOLORS.NS"),

    # ---- Media ----
    ("ZEEL", "Zee Entertainment", "Media", "Media", "TV Broadcasting", "NSE", "ZEEL.NS"),
    ("PVRINOX", "PVR INOX", "Media", "Media", "Exhibition", "NSE", "PVRINOX.NS"),
    ("NETWORK18", "Network18 Media", "Media", "Media", "News & Entertainment", "NSE", "NETWORK18.NS"),
    ("SAREGAMA", "Saregama India", "Media", "Media", "Music & Content", "NSE", "SAREGAMA.NS"),

    # ---- Gems, Jewellery And Watches ----
    ("GOLDIAM", "Goldiam International", "Gems, Jewellery And Watches", "Jewellery", "Gems & Jewellery", "NSE", "GOLDIAM.NS"),
    ("TBZ", "Tribhovandas Bhimji Zaveri", "Gems, Jewellery And Watches", "Jewellery", "Gems & Jewellery", "NSE", "TBZ.NS"),
    ("PCJEWELLER", "PC Jeweller", "Gems, Jewellery And Watches", "Jewellery", "Gems & Jewellery", "NSE", "PCJEWELLER.NS"),
    ("RAJESHEXPO", "Rajesh Exports", "Gems, Jewellery And Watches", "Jewellery", "Gold Refining", "NSE", "RAJESHEXPO.NS"),
    ("SHANTIGOLD", "Shanti Gold International", "Gems, Jewellery And Watches", "Jewellery", "Gems & Jewellery", "NSE", "SHANTIGOLD.NS"),

    # ---- Capital Goods ----
    ("SIEMENS", "Siemens", "Capital Goods", "Capital Goods", "Electrical Equipment", "NSE", "SIEMENS.NS"),
    ("ABB", "ABB India", "Capital Goods", "Capital Goods", "Electrical Equipment", "NSE", "ABB.NS"),
    ("CUMMINSIND", "Cummins India", "Capital Goods", "Capital Goods", "Diesel Engines", "NSE", "CUMMINSIND.NS"),
    ("THERMAX", "Thermax", "Capital Goods", "Capital Goods", "Energy & Environment", "NSE", "THERMAX.NS"),
    ("BHEL", "Bharat Heavy Electricals", "Capital Goods", "Capital Goods", "Power Equipment - PSU", "NSE", "BHEL.NS"),
    ("TITAGARH", "Titagarh Rail Systems", "Capital Goods", "Capital Goods", "Rail Wagons", "NSE", "TITAGARH.NS"),
    ("POWERMECH", "Power Mech Projects", "Capital Goods", "Capital Goods", "Power Equipment Services", "NSE", "POWERMECH.NS"),
    ("CRAFTSMAN", "Craftsman Automation", "Capital Goods", "Capital Goods", "Precision Engineering", "NSE", "CRAFTSMAN.NS"),
    ("ELGIRUBCO", "Elgi Equipments", "Capital Goods", "Capital Goods", "Air Compressors", "NSE", "ELGIRUBCO.NS"),
    ("CGPOWER", "CG Power", "Capital Goods", "Capital Goods", "Electrical Transformers", "NSE", "CGPOWER.NS"),
    ("KAYNES", "Kaynes Technology", "Capital Goods", "Capital Goods", "EMS & IoT", "NSE", "KAYNES.NS"),
    ("KEC", "KEC International", "Capital Goods", "Power Equipment", "Transmission Towers", "NSE", "KEC.NS"),

    # ---- Shipbuilding & Maritime ----
    ("SCI", "Shipping Corporation of India", "Shipbuilding & Maritime", "Logistics", "Shipping", "NSE", "SCI.NS"),
    ("ESSARSHPNG", "Essar Shipping", "Shipbuilding & Maritime", "Logistics", "Shipping", "NSE", "ESSARSHPNG.NS"),
    ("GESHIP", "Great Eastern Shipping", "Shipbuilding & Maritime", "Logistics", "Shipping", "NSE", "GESHIP.NS"),
    ("SEAMECLTD", "Seamec", "Shipbuilding & Maritime", "Logistics", "Offshore Services", "NSE", "SEAMECLTD.NS"),
    ("DREDGECORP", "Dredging Corporation of India", "Shipbuilding & Maritime", "Logistics", "Dredging", "NSE", "DREDGECORP.NS"),

    # ---- Textiles ----
    ("PAGEIND", "Page Industries", "Textiles", "Textiles", "Premium Innerwear", "NSE", "PAGEIND.NS"),
    ("RAYMOND", "Raymond", "Textiles", "Textiles", "Branded Apparel", "NSE", "RAYMOND.NS"),
    ("VTL", "Vardhman Textiles", "Textiles", "Textiles", "Yarn & Fabric", "NSE", "VTL.NS"),
    ("WELCORP", "Welspun Corp", "Textiles", "Textiles", "Line Pipes", "NSE", "WELCORP.NS"),
    ("WELSPUNLIV", "Welspun Living", "Textiles", "Textiles", "Home Textiles", "NSE", "WELSPUNLIV.NS"),
    ("RUPA", "Rupa & Company", "Textiles", "Textiles", "Innerwear", "NSE", "RUPA.NS"),
    ("GOKEX", "Gokaldas Exports", "Textiles", "Textiles", "Garment Exports", "NSE", "GOKEX.NS"),
    ("KPRMILL", "KPR Mill", "Textiles", "Textiles", "Integrated Textiles", "NSE", "KPRMILL.NS"),
    ("FILATEX", "Filatex India", "Textiles", "Textiles", "Polyester Yarn", "NSE", "FILATEX.NS"),

    # ---- Internet & New-Age Tech ----
    ("ETERNAL", "Eternal (Zomato)", "Internet & New-Age Tech", "Internet", "Food Delivery & Quick Commerce", "NSE", "ETERNAL.NS"),
    ("NAUKRI", "Info Edge (India)", "Internet & New-Age Tech", "Internet", "Online Classifieds", "NSE", "NAUKRI.NS"),
    ("POLICYBZR", "PB Fintech (Policy Bazaar)", "Internet & New-Age Tech", "FinTech", "Insurance Aggregator", "NSE", "POLICYBZR.NS"),
    ("PAYTM", "One97 Communications (Paytm)", "Internet & New-Age Tech", "FinTech", "Digital Payments", "NSE", "PAYTM.NS"),
    ("DELHIVERY", "Delhivery", "Internet & New-Age Tech", "Logistics", "Logistics Tech", "NSE", "DELHIVERY.NS"),
    ("MAPMYINDIA", "CE Info Systems (MapmyIndia)", "Internet & New-Age Tech", "Internet", "Mapping & Location", "NSE", "MAPMYINDIA.NS"),
    ("RATEGAIN", "RateGain Travel Technologies", "Internet & New-Age Tech", "Internet", "Travel Tech", "NSE", "RATEGAIN.NS"),
    ("EASEMYTRIP", "Easy Trip Planners", "Internet & New-Age Tech", "Internet", "Travel Tech", "NSE", "EASEMYTRIP.NS"),
    ("IXIGO", "Le Travenues Technology (ixigo)", "Internet & New-Age Tech", "Internet", "Travel Tech", "NSE", "IXIGO.NS"),

    # ---- Sugar & Ethanol ----
    ("RENUKA", "Shree Renuka Sugars", "Sugar & Ethanol", "Sugar", "Sugar & Ethanol", "NSE", "RENUKA.NS"),
    ("BALRAMCHIN", "Balrampur Chini Mills", "Sugar & Ethanol", "Sugar", "Sugar & Ethanol", "NSE", "BALRAMCHIN.NS"),
    ("TRIVENI", "Triveni Engineering", "Sugar & Ethanol", "Sugar", "Sugar & Ethanol", "NSE", "TRIVENI.NS"),
    ("DWARKESH", "Dwarikesh Sugar", "Sugar & Ethanol", "Sugar", "Sugar & Ethanol", "NSE", "DWARKESH.NS"),
    ("UTTAMSUGAR", "Uttam Sugar Mills", "Sugar & Ethanol", "Sugar", "Sugar", "NSE", "UTTAMSUGAR.NS"),

    # ---- Building Materials ----
    ("ORIENTBELL", "Orient Bell", "Building Materials", "Building Materials", "Tiles", "NSE", "ORIENTBELL.NS"),
    ("KAJARIACER", "Kajaria Ceramics", "Building Materials", "Building Materials", "Tiles", "NSE", "KAJARIACER.NS"),
    ("CERA", "Cera Sanitaryware", "Building Materials", "Building Materials", "Sanitaryware", "NSE", "CERA.NS"),
    ("ASTRAL", "Astral", "Building Materials", "Building Materials", "PVC Pipes", "NSE", "ASTRAL.NS"),
    ("PRINCEPIPE", "Prince Pipes", "Building Materials", "Building Materials", "PVC Pipes", "NSE", "PRINCEPIPE.NS"),
    ("FINPIPE", "Finolex Industries", "Building Materials", "Building Materials", "PVC Pipes", "NSE", "FINPIPE.NS"),
    ("SUPREMEIND", "Supreme Industries", "Building Materials", "Plastics", "Plastic Products", "NSE", "SUPREMEIND.NS"),
    ("GREENPLY", "Greenply Industries", "Building Materials", "Building Materials", "Plywood & Laminates", "NSE", "GREENPLY.NS"),
    ("CENTURYPLY", "Century Plyboards", "Building Materials", "Building Materials", "Plywood & Laminates", "NSE", "CENTURYPLY.NS"),
    ("SOMANYCERA", "Somany Ceramics", "Building Materials", "Building Materials", "Tiles", "NSE", "SOMANYCERA.NS"),
    ("SHANKARA", "Shankara Building Products", "Building Materials", "Retail", "Building Materials Retail", "NSE", "SHANKARA.NS"),

    # ---- High-Momentum Market Leaders (Railways, Defence, Renewables, EMS) ----
    ("SUZLON", "Suzlon Energy", "Power", "Renewable Energy", "Wind Energy Equipment", "BOTH", "SUZLON.NS"),
    ("IREDA", "Indian Renewable Energy Dev Agency", "Financial Services", "NBFC", "Green Energy Financing", "BOTH", "IREDA.NS"),
    ("HUDCO", "Housing & Urban Dev Corp", "Financial Services", "Housing Finance", "Urban Infrastructure", "BOTH", "HUDCO.NS"),
    ("NBCC", "NBCC India", "Infrastructure", "Construction", "Project Management", "BOTH", "NBCC.NS"),
    ("IRFC", "Indian Railway Finance Corp", "Financial Services", "NBFC", "Rail Infrastructure Financing", "BOTH", "IRFC.NS"),
    ("RAILTEL", "RailTel Corp of India", "Telecom", "Telecom Infrastructure", "Telecom & Optical Fibre", "BOTH", "RAILTEL.NS"),
    ("TITAGARH", "Titagarh Rail Systems", "Capital Goods", "Railways", "Passenger Coaches & Freight Wagons", "BOTH", "TITAGARH.NS"),
    ("JWL", "Jupiter Wagons", "Capital Goods", "Railways", "Wagons & Castings", "BOTH", "JWL.NS"),
    ("TEXRAIL", "Texmaco Rail & Engineering", "Capital Goods", "Railways", "Freight Wagons & Track Works", "BOTH", "TEXRAIL.NS"),
    ("COCHINSHIP", "Cochin Shipyard", "Shipbuilding & Maritime", "Shipbuilding", "Defence & Commercial Vessels", "BOTH", "COCHINSHIP.NS"),
    ("GRSE", "Garden Reach Shipbuilders", "Shipbuilding & Maritime", "Defence Shipbuilding", "Warships & Corvettes", "BOTH", "GRSE.NS"),
    ("BDL", "Bharat Dynamics", "Defence", "Defence Equipment", "Guided Missiles & Torpedoes", "BOTH", "BDL.NS"),
    ("KAYNES", "Kaynes Technology", "Capital Goods", "EMS", "Electronic Manufacturing Services", "BOTH", "KAYNES.NS"),
    ("CYIENTDLM", "Cyient DLM", "Capital Goods", "EMS", "Electronic Manufacturing Services", "BOTH", "CYIENTDLM.NS"),
    ("SYRMA", "Syrma SGS Technology", "Capital Goods", "EMS", "Electronic Manufacturing Services", "BOTH", "SYRMA.NS"),
    ("AVALON", "Avalon Technologies", "Capital Goods", "EMS", "Electronic Manufacturing Services", "BOTH", "AVALON.NS"),
    ("EPACK", "EPACK Durable", "Consumer Durables", "EMS", "RAC & Small Appliances", "BOTH", "EPACK.NS"),
    ("PCJEWELLER", "PC Jeweller", "Gems, Jewellery And Watches", "Jewellery", "Gold & Diamond Jewellery", "BOTH", "PCJEWELLER.NS"),
    ("SENCO", "Senco Gold", "Gems, Jewellery And Watches", "Jewellery", "Retail Jewellery", "BOTH", "SENCO.NS"),
    ("THANGAMAYL", "Thangamayil Jewellery", "Gems, Jewellery And Watches", "Jewellery", "Retail Jewellery", "BOTH", "THANGAMAYL.NS"),
    ("MOTISONS", "Motisons Jewellers", "Gems, Jewellery And Watches", "Jewellery", "Retail Jewellery", "BOTH", "MOTISONS.NS"),

    # ---- BSE Exclusive & Prominent Stocks ----
    ("BSE", "BSE Limited", "Capital Markets", "Stock Exchanges", "Securities Exchange", "BOTH", "BSE.NS"),
    ("ALOKINDS", "Alok Industries", "Textiles", "Textiles", "Integrated Textiles", "BOTH", "ALOKINDS.NS"),
    ("GTLINFRA", "GTL Infrastructure", "Telecom", "Telecom Infrastructure", "Telecom Towers", "BOTH", "GTLINFRA.NS"),
    ("SULA", "Sula Vineyards", "FMCG", "Beverages", "Wine & Beverages", "BOTH", "SULA.NS"),
    ("LLOYDSENGG", "Lloyds Engineering Works", "Capital Goods", "Engineering", "Heavy Engineering", "BOTH", "LLOYDSENGG.NS"),
    ("500002", "ABB India (BSE)", "Capital Goods", "Electrical Equipment", "Automation & Power", "BSE", "500002.BO"),

    # ---- NSE SME & Emerging Platform ----
    ("PARTH", "Parth Electricals & Engineering (SME)", "Capital Goods", "Electrical Equipment", "Transformers & Switchgears", "NSE", "PARTH-SM.NS"),
    ("K2INFRA", "K2 Infragen (SME)", "NSE SME & Emerging", "SME Infrastructure", "Engineering & EPC", "NSE", "K2INFRA.NS"),
    ("KOTYARK", "Kotyark Industries (SME)", "NSE SME & Emerging", "SME Biofuels", "Biofuel & Energy", "NSE", "KOTYARK.NS"),
    ("VITAL", "Vital Chemtech (SME)", "NSE SME & Emerging", "SME Chemicals", "Specialty Chemicals", "NSE", "VITAL.NS"),
    ("SHREEOSWAL", "ShreeOswal Seeds (SME)", "NSE SME & Emerging", "SME Agro", "Seeds & Agrochemicals", "NSE", "SHREEOSWAL.NS"),
    ("BEWLTD", "BEW Engineering (SME)", "NSE SME & Emerging", "SME Engineering", "Pharma Machinery", "NSE", "BEWLTD.NS"),
    ("DYNAMIC", "Dynamic Services (SME)", "NSE SME & Emerging", "SME Services", "Facility Management", "NSE", "DYNAMIC.NS"),
    ("CWD", "CWD Limited (SME)", "NSE SME & Emerging", "SME Electronics", "IoT Products", "NSE", "CWD.NS"),
    ("MACFOS", "Macfos Limited (SME)", "NSE SME & Emerging", "SME E-Commerce", "Electronics & Robotics", "NSE", "MACFOS.NS"),
    ("INDOCOSMO", "Indo Cotspin (SME)", "NSE SME & Emerging", "SME Textiles", "Yarn & Textiles", "NSE", "INDOCOSMO.NS"),
    ("SARTELE", "SAR Televenture (SME)", "NSE SME & Emerging", "SME Telecom", "Telecom Infrastructure", "NSE", "SARTELE.NS"),
    ("BASILIC", "Basilic Fly Studio (SME)", "NSE SME & Emerging", "SME Media", "VFX & Animation", "NSE", "BASILIC.NS"),
    ("NEXUS", "Nexus Surgical (SME)", "NSE SME & Emerging", "SME Healthcare", "Surgical Devices", "NSE", "NEXUS.NS"),
    ("CUBEXTUB", "Cubex Tubings (SME)", "NSE SME & Emerging", "SME Metals", "Copper Tubes", "NSE", "CUBEXTUB.NS"),
]

# Deduplicate by symbol
_seen = set()
STOCK_UNIVERSE = []
for row in RAW_UNIVERSE:
    sym = row[0].upper()
    if sym not in _seen:
        _seen.add(sym)
        yf_sym = row[6] if len(row) > 6 and row[6] else f"{sym}.NS"
        exch = row[5] if len(row) > 5 and row[5] else "BOTH"
        STOCK_UNIVERSE.append({
            "symbol": sym,
            "name": row[1],
            "sector": row[2],
            "industry": row[3],
            "sub_industry": row[4],
            "exchange": exch,
            "yf_symbol": yf_sym,
        })

# Fast lookups
SYMBOL_META = {s["symbol"]: s for s in STOCK_UNIVERSE}
# Also allow looking up by yf_symbol or previous tickers
YF_TO_SYMBOL = {s["yf_symbol"]: s["symbol"] for s in STOCK_UNIVERSE}
# Aliases for backwards compatibility / common ticker queries
ALIASES = {
    "LTIM": "LTIM",
    "ZOMATO": "ETERNAL",
    "TATAMOTORS": "TMPV",
    "NIIT": "NIITLTD",
    "BIRLASOFT": "BSOFT",
    "BALARAMCHIN": "BALRAMCHIN",
    "KAJARIA": "KAJARIACER",
    "DWARIKESH": "DWARKESH",
    "RAILVIKAS": "RVNL",
    "GMRINFRA": "GMRAIRPORT",
    "VARDHMAN": "VTL",
    "KPR": "KPRMILL",
    "MEDI": "MEDANTA",
    "BERGERPAINTS": "BERGEPAINT",
    "AKZOINDIA": "JSWDULUX",
    "WELSPUNIND": "WELSPUNLIV",
    "APL": "APLAPOLLO",
    "KNR": "KNRCON",
    "BLUESTAR": "BLUESTARCO",
    "FINOLEX": "FINPIPE",
    "VIP": "VIPIND",
    "VODAFONE": "IDEA",
    "MAZAGON": "MAZDOCK",
    "ZENSAR": "ZENSARTECH",
    "DCX": "DCXINDIA",
    "MTAR": "MTARTECH",
    "PARTH": "PARTH",
    "DALMIACEME": "DALBHARAT",
    "PRISMCEM": "PRSMJOHNSN",
    "AAPL": "ANURAS",
    "VINATIORG": "VINATIORGA",
    "JSW ENERGY": "JSWENERGY",
    "KALPATPOWR": "KPIL",
    "HG INFRA": "HGINFRA",
    "MCDOWELL-N": "UNITDSPR",
}

for alias, target in ALIASES.items():
    if target in SYMBOL_META and alias not in SYMBOL_META:
        SYMBOL_META[alias] = SYMBOL_META[target]


def get_all_symbols(exchange="NSE"):
    if exchange == "NSE":
        return [s for s in STOCK_UNIVERSE if s["exchange"] in ("NSE", "BOTH")]
    elif exchange == "BSE":
        return [s for s in STOCK_UNIVERSE if s["exchange"] in ("BSE", "BOTH")]
    return STOCK_UNIVERSE


def get_meta(symbol: str):
    sym = symbol.upper().replace(".NS", "").replace(".BO", "")
    return SYMBOL_META.get(sym, {
        "symbol": sym,
        "name": sym,
        "exchange": "BOTH",
        "sector": "Other",
        "industry": "Other",
        "sub_industry": "Other",
        "yf_symbol": f"{sym}.NS"
    })


def get_yf_symbol(symbol: str) -> str:
    meta = get_meta(symbol)
    return meta.get("yf_symbol", f"{symbol}.NS")


def get_sectors():
    return sorted(set(s["sector"] for s in STOCK_UNIVERSE if s.get("sector")))


def get_industries_list():
    return sorted(set(s["industry"] for s in STOCK_UNIVERSE if s.get("industry")))


def get_sub_industries_list():
    return sorted(set(s["sub_industry"] for s in STOCK_UNIVERSE if s.get("sub_industry")))


def get_stocks_in_sector(sector: str):
    sec = sector.lower().strip()
    return [
        s for s in STOCK_UNIVERSE
        if sec in s.get("sector", "").lower() or sec in s.get("industry", "").lower() or sec in s.get("sub_industry", "").lower()
    ]
