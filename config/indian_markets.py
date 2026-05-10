"""
config/indian_markets.py
─────────────────────────
Complete registry of Indian market indices:
  • Nifty 50  — NSE's benchmark index (50 large-cap stocks)
  • Sensex 30 — BSE's benchmark index (30 large-cap stocks)

Ticker format used: Yahoo Finance NSE format → SYMBOL.NS
BSE format: SYMBOL.BO (also supported)

Each entry contains:
  ticker_ns  : yfinance NSE ticker  (e.g., "RELIANCE.NS")
  ticker_bs  : yfinance BSE ticker  (e.g., "RELIANCE.BO")
  symbol     : NSE trading symbol   (e.g., "RELIANCE")
  name       : Full company name
  sector     : GICS sector
  nifty50    : True if part of Nifty 50
  sensex30   : True if part of Sensex 30
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class IndianStock:
    symbol:    str
    name:      str
    sector:    str
    nifty50:   bool = False
    sensex30:  bool = False

    @property
    def ticker_ns(self) -> str:
        """Yahoo Finance NSE ticker symbol."""
        return f"{self.symbol}.NS"

    @property
    def ticker_bo(self) -> str:
        """Yahoo Finance BSE ticker symbol."""
        return f"{self.symbol}.BO"


# ─────────────────────────────────────────────────────────────────
# MASTER STOCK REGISTRY
# ─────────────────────────────────────────────────────────────────

INDIAN_STOCKS: list[IndianStock] = [

    # ── NIFTY 50 + SENSEX 30 overlap ─────────────────────────────
    IndianStock("RELIANCE",    "Reliance Industries Ltd",           "Energy",                nifty50=True, sensex30=True),
    IndianStock("TCS",         "Tata Consultancy Services Ltd",     "Information Technology", nifty50=True, sensex30=True),
    IndianStock("HDFCBANK",    "HDFC Bank Ltd",                     "Financials",            nifty50=True, sensex30=True),
    IndianStock("INFY",        "Infosys Ltd",                       "Information Technology", nifty50=True, sensex30=True),
    IndianStock("ICICIBANK",   "ICICI Bank Ltd",                    "Financials",            nifty50=True, sensex30=True),
    IndianStock("HINDUNILVR",  "Hindustan Unilever Ltd",            "Consumer Staples",      nifty50=True, sensex30=True),
    IndianStock("SBIN",        "State Bank of India",               "Financials",            nifty50=True, sensex30=True),
    IndianStock("BHARTIARTL",  "Bharti Airtel Ltd",                 "Communication Services",nifty50=True, sensex30=True),
    IndianStock("KOTAKBANK",   "Kotak Mahindra Bank Ltd",           "Financials",            nifty50=True, sensex30=True),
    IndianStock("LT",          "Larsen & Toubro Ltd",               "Industrials",           nifty50=True, sensex30=True),
    IndianStock("HCLTECH",     "HCL Technologies Ltd",              "Information Technology", nifty50=True, sensex30=True),
    IndianStock("BAJFINANCE",  "Bajaj Finance Ltd",                 "Financials",            nifty50=True, sensex30=True),
    IndianStock("ASIANPAINT",  "Asian Paints Ltd",                  "Materials",             nifty50=True, sensex30=True),
    IndianStock("AXISBANK",    "Axis Bank Ltd",                     "Financials",            nifty50=True, sensex30=True),
    IndianStock("TITAN",       "Titan Company Ltd",                 "Consumer Discretionary", nifty50=True, sensex30=True),
    IndianStock("MARUTI",      "Maruti Suzuki India Ltd",           "Consumer Discretionary", nifty50=True, sensex30=True),
    IndianStock("SUNPHARMA",   "Sun Pharmaceutical Industries Ltd", "Health Care",           nifty50=True, sensex30=True),
    IndianStock("WIPRO",       "Wipro Ltd",                         "Information Technology", nifty50=True, sensex30=True),
    IndianStock("ULTRACEMCO",  "UltraTech Cement Ltd",              "Materials",             nifty50=True, sensex30=True),
    IndianStock("NESTLEIND",   "Nestle India Ltd",                  "Consumer Staples",      nifty50=True, sensex30=True),
    IndianStock("POWERGRID",   "Power Grid Corporation of India",   "Utilities",             nifty50=True, sensex30=True),
    IndianStock("NTPC",        "NTPC Ltd",                          "Utilities",             nifty50=True, sensex30=True),
    IndianStock("TECHM",       "Tech Mahindra Ltd",                 "Information Technology", nifty50=True, sensex30=True),
    IndianStock("M&M",         "Mahindra & Mahindra Ltd",           "Consumer Discretionary", nifty50=True, sensex30=True),
    IndianStock("INDUSINDBK",  "IndusInd Bank Ltd",                 "Financials",            nifty50=True, sensex30=True),
    IndianStock("TATAMOTORS",  "Tata Motors Ltd",                   "Consumer Discretionary", nifty50=True, sensex30=True),
    IndianStock("JSWSTEEL",    "JSW Steel Ltd",                     "Materials",             nifty50=True, sensex30=True),
    IndianStock("TATASTEEL",   "Tata Steel Ltd",                    "Materials",             nifty50=True, sensex30=True),
    IndianStock("BAJAJFINSV",  "Bajaj Finserv Ltd",                 "Financials",            nifty50=True, sensex30=True),
    IndianStock("ITC",         "ITC Ltd",                           "Consumer Staples",      nifty50=True, sensex30=True),

    # ── Nifty 50 ONLY ─────────────────────────────────────────────
    IndianStock("ONGC",        "Oil and Natural Gas Corporation",   "Energy",                nifty50=True),
    IndianStock("HEROMOTOCO",  "Hero MotoCorp Ltd",                 "Consumer Discretionary", nifty50=True),
    IndianStock("ADANIENT",    "Adani Enterprises Ltd",             "Industrials",           nifty50=True),
    IndianStock("ADANIPORTS",  "Adani Ports & SEZ Ltd",             "Industrials",           nifty50=True),
    IndianStock("DIVISLAB",    "Divi's Laboratories Ltd",           "Health Care",           nifty50=True),
    IndianStock("BRITANNIA",   "Britannia Industries Ltd",          "Consumer Staples",      nifty50=True),
    IndianStock("COALINDIA",   "Coal India Ltd",                    "Energy",                nifty50=True),
    IndianStock("GRASIM",      "Grasim Industries Ltd",             "Materials",             nifty50=True),
    IndianStock("HINDALCO",    "Hindalco Industries Ltd",           "Materials",             nifty50=True),
    IndianStock("BPCL",        "Bharat Petroleum Corporation Ltd",  "Energy",                nifty50=True),
    IndianStock("DRREDDY",     "Dr. Reddy's Laboratories Ltd",      "Health Care",           nifty50=True),
    IndianStock("CIPLA",       "Cipla Ltd",                         "Health Care",           nifty50=True),
    IndianStock("EICHERMOT",   "Eicher Motors Ltd",                 "Consumer Discretionary", nifty50=True),
    IndianStock("TATACONSUM",  "Tata Consumer Products Ltd",        "Consumer Staples",      nifty50=True),
    IndianStock("APOLLOHOSP",  "Apollo Hospitals Enterprise Ltd",   "Health Care",           nifty50=True),
    IndianStock("SBILIFE",     "SBI Life Insurance Company Ltd",    "Financials",            nifty50=True),
    IndianStock("HDFCLIFE",    "HDFC Life Insurance Company Ltd",   "Financials",            nifty50=True),
    IndianStock("BAJAJ-AUTO",  "Bajaj Auto Ltd",                    "Consumer Discretionary", nifty50=True),
    IndianStock("SHREECEM",    "Shree Cement Ltd",                  "Materials",             nifty50=True),
    IndianStock("UPL",         "UPL Ltd",                           "Materials",             nifty50=True),

    # ── Popular Nifty Next 50 / Nifty 500 stocks (NOT in Nifty 50) ──
    IndianStock("MOTHERSON",   "Samvardhana Motherson International Ltd", "Consumer Discretionary"),
    IndianStock("ZOMATO",      "Zomato Ltd",                        "Consumer Discretionary"),
    IndianStock("PAYTM",       "One97 Communications Ltd",          "Financials"),
    IndianStock("NYKAA",       "FSN E-Commerce Ventures Ltd",       "Consumer Discretionary"),
    IndianStock("POLICYBZR",   "PB Fintech Ltd",                    "Financials"),
    IndianStock("IRCTC",       "Indian Railway Catering & Tourism", "Consumer Discretionary"),
    IndianStock("HAL",         "Hindustan Aeronautics Ltd",         "Industrials"),
    IndianStock("BEL",         "Bharat Electronics Ltd",            "Industrials"),
    IndianStock("NHPC",        "NHPC Ltd",                          "Utilities"),
    IndianStock("RVNL",        "Rail Vikas Nigam Ltd",              "Industrials"),
    IndianStock("IRFC",        "Indian Railway Finance Corporation","Financials"),
    IndianStock("PFC",         "Power Finance Corporation Ltd",     "Financials"),
    IndianStock("RECLTD",      "REC Ltd",                           "Financials"),
    IndianStock("TATAPOWER",   "Tata Power Company Ltd",            "Utilities"),
    IndianStock("ADANIPOWER",  "Adani Power Ltd",                   "Utilities"),
    IndianStock("ADANIGREEN",  "Adani Green Energy Ltd",            "Utilities"),
    IndianStock("CANBK",       "Canara Bank",                       "Financials"),
    IndianStock("BANKBARODA",  "Bank of Baroda",                    "Financials"),
    IndianStock("PNB",         "Punjab National Bank",              "Financials"),
    IndianStock("UNIONBANK",   "Union Bank of India",               "Financials"),
    IndianStock("IOB",         "Indian Overseas Bank",              "Financials"),
    IndianStock("FEDERALBNK",  "Federal Bank Ltd",                  "Financials"),
    IndianStock("BANDHANBNK",  "Bandhan Bank Ltd",                  "Financials"),
    IndianStock("IDFCFIRSTB",  "IDFC First Bank Ltd",               "Financials"),
    IndianStock("YESBANK",     "Yes Bank Ltd",                      "Financials"),
    IndianStock("IDEA",        "Vodafone Idea Ltd",                 "Communication Services"),
    IndianStock("MTNL",        "Mahanagar Telephone Nigam Ltd",     "Communication Services"),
    IndianStock("SUZLON",      "Suzlon Energy Ltd",                 "Utilities"),
    IndianStock("RPOWER",      "Reliance Power Ltd",                "Utilities"),
    IndianStock("TATACHEM",    "Tata Chemicals Ltd",                "Materials"),
    IndianStock("PIIND",       "PI Industries Ltd",                 "Materials"),
    IndianStock("UBL",         "United Breweries Ltd",              "Consumer Staples"),
    IndianStock("MCDOWELL-N",  "United Spirits Ltd",                "Consumer Staples"),
    IndianStock("JUBLFOOD",    "Jubilant FoodWorks Ltd",            "Consumer Discretionary"),
    IndianStock("DMART",       "Avenue Supermarts Ltd",             "Consumer Staples"),
    IndianStock("ABFRL",       "Aditya Birla Fashion & Retail Ltd", "Consumer Discretionary"),
    IndianStock("PAGEIND",     "Page Industries Ltd",               "Consumer Discretionary"),
    IndianStock("MUTHOOTFIN",  "Muthoot Finance Ltd",               "Financials"),
    IndianStock("CHOLAFIN",    "Cholamandalam Investment & Finance","Financials"),
    IndianStock("SBICARD",     "SBI Cards & Payment Services Ltd",  "Financials"),
    IndianStock("MARICO",      "Marico Ltd",                        "Consumer Staples"),
    IndianStock("GODREJCP",    "Godrej Consumer Products Ltd",      "Consumer Staples"),
    IndianStock("DABUR",       "Dabur India Ltd",                   "Consumer Staples"),
    IndianStock("EMAMILTD",    "Emami Ltd",                         "Consumer Staples"),
    IndianStock("COLPAL",      "Colgate-Palmolive India Ltd",       "Consumer Staples"),
    IndianStock("PGHH",        "Procter & Gamble Hygiene & Health", "Consumer Staples"),
    IndianStock("TORNTPHARM",  "Torrent Pharmaceuticals Ltd",       "Health Care"),
    IndianStock("AUROPHARMA",  "Aurobindo Pharma Ltd",              "Health Care"),
    IndianStock("ALKEM",       "Alkem Laboratories Ltd",            "Health Care"),
    IndianStock("LUPIN",       "Lupin Ltd",                         "Health Care"),
    IndianStock("BIOCON",      "Biocon Ltd",                        "Health Care"),
    IndianStock("MAXHEALTH",   "Max Healthcare Institute Ltd",      "Health Care"),
    IndianStock("FORTIS",      "Fortis Healthcare Ltd",             "Health Care"),
    IndianStock("LALPATHLAB",  "Dr Lal PathLabs Ltd",               "Health Care"),
    IndianStock("PERSISTENT",  "Persistent Systems Ltd",            "Information Technology"),
    IndianStock("LTIM",        "LTIMindtree Ltd",                   "Information Technology"),
    IndianStock("COFORGE",     "Coforge Ltd",                       "Information Technology"),
    IndianStock("MPHASIS",     "Mphasis Ltd",                       "Information Technology"),
    IndianStock("OFSS",        "Oracle Financial Services Software","Information Technology"),
    IndianStock("KPIT",        "KPIT Technologies Ltd",             "Information Technology"),
    IndianStock("TATAELXSI",   "Tata Elxsi Ltd",                    "Information Technology"),
    IndianStock("NAUKRI",      "Info Edge India Ltd",               "Information Technology"),
    IndianStock("INDIGO",      "InterGlobe Aviation Ltd",           "Industrials"),
    IndianStock("SPICEJET",    "SpiceJet Ltd",                      "Industrials"),
    IndianStock("CONCOR",      "Container Corporation of India",    "Industrials"),
    IndianStock("VBL",         "Varun Beverages Ltd",               "Consumer Staples"),
    IndianStock("TRENT",       "Trent Ltd",                         "Consumer Discretionary"),
    IndianStock("VEDL",        "Vedanta Ltd",                       "Materials"),
    IndianStock("NMDC",        "NMDC Ltd",                          "Materials"),
    IndianStock("SAIL",        "Steel Authority of India Ltd",      "Materials"),
    IndianStock("JINDALSAW",   "Jindal Saw Ltd",                    "Materials"),
    IndianStock("ASTRAL",      "Astral Ltd",                        "Materials"),
    IndianStock("SUPREMEIND",  "Supreme Industries Ltd",            "Materials"),
    IndianStock("CUMMINSIND",  "Cummins India Ltd",                 "Industrials"),
    IndianStock("ABB",         "ABB India Ltd",                     "Industrials"),
    IndianStock("SIEMENS",     "Siemens Ltd",                       "Industrials"),
    IndianStock("HONAUT",      "Honeywell Automation India Ltd",    "Industrials"),
    IndianStock("SCHAEFFLER",  "Schaeffler India Ltd",              "Industrials"),
    IndianStock("BOSCHLTD",    "Bosch Ltd",                         "Consumer Discretionary"),
    IndianStock("MRF",         "MRF Ltd",                           "Consumer Discretionary"),
    IndianStock("APOLLOTYRE",  "Apollo Tyres Ltd",                  "Consumer Discretionary"),
    IndianStock("CEATLTD",     "CEAT Ltd",                          "Consumer Discretionary"),
    IndianStock("BALKRISIND",  "Balkrishna Industries Ltd",         "Consumer Discretionary"),
    IndianStock("DIXON",       "Dixon Technologies Ltd",            "Consumer Discretionary"),
    IndianStock("AMBER",       "Amber Enterprises India Ltd",       "Consumer Discretionary"),
    IndianStock("VOLTAS",      "Voltas Ltd",                        "Consumer Discretionary"),
    IndianStock("BLUESTARCO",  "Blue Star Ltd",                     "Consumer Discretionary"),
    IndianStock("HAVELLS",     "Havells India Ltd",                 "Industrials"),
    IndianStock("POLYCAB",     "Polycab India Ltd",                 "Industrials"),
    IndianStock("KEI",         "KEI Industries Ltd",                "Industrials"),
    IndianStock("APLAPOLLO",   "APL Apollo Tubes Ltd",              "Materials"),
    IndianStock("DEEPAKNI",    "Deepak Nitrite Ltd",                "Materials"),
    IndianStock("SRF",         "SRF Ltd",                           "Materials"),
    IndianStock("AARTIIND",    "Aarti Industries Ltd",              "Materials"),
    IndianStock("PIDILITIND",  "Pidilite Industries Ltd",           "Materials"),
    IndianStock("BERGEPAINT",  "Berger Paints India Ltd",           "Materials"),
    IndianStock("KANSAINER",   "Kansai Nerolac Paints Ltd",         "Materials"),
    IndianStock("SUNDARMFIN",  "Sundaram Finance Ltd",              "Financials"),
    IndianStock("MANAPPURAM",  "Manappuram Finance Ltd",            "Financials"),
    IndianStock("LICHSGFIN",   "LIC Housing Finance Ltd",           "Financials"),
    IndianStock("HDFCAMC",     "HDFC Asset Management Company",     "Financials"),
    IndianStock("NAM-INDIA",   "Nippon India Mutual Fund",          "Financials"),
    IndianStock("360ONE",      "360 ONE WAM Ltd",                   "Financials"),
    IndianStock("ANGELONE",    "Angel One Ltd",                     "Financials"),
    IndianStock("BSE",         "BSE Ltd",                           "Financials"),
    IndianStock("MCX",         "Multi Commodity Exchange",          "Financials"),
    IndianStock("CAMS",        "Computer Age Management Services",  "Financials"),
    IndianStock("CDSL",        "Central Depository Services Ltd",   "Financials"),
    IndianStock("NSDL",        "National Securities Depository Ltd","Financials"),

    # ── Recently rebranded / popular stocks ───────────────────────
    IndianStock("ETERNAL",     "Eternal Ltd (formerly Zomato)",      "Consumer Discretionary", nifty50=True),
]


# ─────────────────────────────────────────────────────────────────
# Convenience lookup structures
# ─────────────────────────────────────────────────────────────────

# All stocks as dict: symbol → IndianStock
STOCKS_BY_SYMBOL: dict[str, IndianStock] = {s.symbol: s for s in INDIAN_STOCKS}

# Nifty 50 only
NIFTY_50: list[IndianStock] = [s for s in INDIAN_STOCKS if s.nifty50]

# Sensex 30 only
SENSEX_30: list[IndianStock] = [s for s in INDIAN_STOCKS if s.sensex30]

# All NSE tickers (for yfinance): ["RELIANCE.NS", "TCS.NS", ...]
NIFTY_50_TICKERS: list[str] = [s.ticker_ns for s in NIFTY_50]
SENSEX_30_TICKERS: list[str] = [s.ticker_ns for s in SENSEX_30]

# Sectors represented
SECTORS: set[str] = {s.sector for s in INDIAN_STOCKS}

# Sector → list of stocks
STOCKS_BY_SECTOR: dict[str, list[IndianStock]] = {}
for stock in INDIAN_STOCKS:
    STOCKS_BY_SECTOR.setdefault(stock.sector, []).append(stock)


def get_stock(symbol: str) -> IndianStock | None:
    """Look up a stock by symbol (case-insensitive)."""
    return STOCKS_BY_SYMBOL.get(symbol.upper().replace(".NS", "").replace(".BO", ""))


# ─────────────────────────────────────────────────────────────────
# Common aliases — users might type these instead of NSE symbols
# ─────────────────────────────────────────────────────────────────
ALIASES: dict[str, str] = {
    "INFOSYS":              "INFY",
    "HDFC":                 "HDFCBANK",
    "HDFC BANK":            "HDFCBANK",
    "RELIANCE INDUSTRIES":  "RELIANCE",
    "SBI":                  "SBIN",
    "STATE BANK":           "SBIN",
    "AIRTEL":               "BHARTIARTL",
    "BHARTI AIRTEL":        "BHARTIARTL",
    "TATA MOTORS":          "TATAMOTORS",
    "TATA STEEL":           "TATASTEEL",
    "TATA CONSULTANCY":     "TCS",
    "BAJAJ FINANCE":        "BAJFINANCE",
    "BAJAJ FINSERV":        "BAJAJFINSV",
    "ASIAN PAINTS":         "ASIANPAINT",
    "ULTRA CEMENT":         "ULTRACEMCO",
    "ULTRATECH":            "ULTRACEMCO",
    "KOTAK":                "KOTAKBANK",
    "KOTAK BANK":           "KOTAKBANK",
    "HUL":                  "HINDUNILVR",
    "HINDUSTAN UNILEVER":   "HINDUNILVR",
    "NESTLE":               "NESTLEIND",
    "MAHINDRA":             "M&M",
    "M AND M":              "M&M",
    "INDUSIND":             "INDUSINDBK",
    "AXIS":                 "AXISBANK",
    "ICICI":                "ICICIBANK",
    "HCL":                  "HCLTECH",
    "TECH MAHINDRA":        "TECHM",
    "WIPRO":                "WIPRO",
    "SUN PHARMA":           "SUNPHARMA",
    "DR REDDY":             "DRREDDY",
    "DR. REDDY":            "DRREDDY",
    "APOLLO":               "APOLLOHOSP",
    "ADANI":                "ADANIENT",
    "JSW":                  "JSWSTEEL",
    "POWER GRID":           "POWERGRID",
    "COAL INDIA":           "COALINDIA",
    "BRITANNIA":            "BRITANNIA",
    "CIPLA":                "CIPLA",
    "BPCL":                 "BPCL",
    "ONGC":                 "ONGC",
    "BAJAJ AUTO":           "BAJAJ-AUTO",
    "HERO":                 "HEROMOTOCO",
    "EICHER":               "EICHERMOT",
    "ROYAL ENFIELD":        "EICHERMOT",
    "SHREE CEMENT":         "SHREECEM",
    "DIVI":                 "DIVISLAB",
    "DIVIS":                "DIVISLAB",
    "TITAN":                "TITAN",
    "ITC":                  "ITC",
    "GRASIM":               "GRASIM",
    "HINDALCO":             "HINDALCO",
    "TATA CONSUMER":        "TATACONSUM",
    "SBI LIFE":             "SBILIFE",
    "HDFC LIFE":            "HDFCLIFE",
    "MARUTI":               "MARUTI",
    "MARUTI SUZUKI":        "MARUTI",
    "L&T":                  "LT",
    "LARSEN":               "LT",
    "MOTHERSON":            "MOTHERSON",
    "SAMVARDHANA":          "MOTHERSON",
    "ZOMATO":               "ZOMATO",
    "PAYTM":                "PAYTM",
    "NYKAA":                "NYKAA",
    "POLICYBAZAAR":         "POLICYBZR",
    "POLICY BAZAAR":        "POLICYBZR",
    "IRCTC":                "IRCTC",
    "HAL":                  "HAL",
    "HINDUSTAN AERONAUTICS":"HAL",
    "BEL":                  "BEL",
    "BHARAT ELECTRONICS":   "BEL",
    "TATA POWER":           "TATAPOWER",
    "ADANI POWER":          "ADANIPOWER",
    "ADANI GREEN":          "ADANIGREEN",
    "CANARA BANK":          "CANBK",
    "BANK OF BARODA":       "BANKBARODA",
    "BOB":                  "BANKBARODA",
    "PNB":                  "PNB",
    "PUNJAB NATIONAL":      "PNB",
    "YES BANK":             "YESBANK",
    "FEDERAL BANK":         "FEDERALBNK",
    "BANDHAN":              "BANDHANBNK",
    "IDFC":                 "IDFCFIRSTB",
    "VODAFONE":             "IDEA",
    "VODAFONE IDEA":        "IDEA",
    "VI":                   "IDEA",
    "SUZLON":               "SUZLON",
    "DMART":                "DMART",
    "AVENUE SUPERMARTS":    "DMART",
    "INDIGO":               "INDIGO",
    "INTERGLOBE":           "INDIGO",
    "SPICEJET":             "SPICEJET",
    "LUPIN":                "LUPIN",
    "BIOCON":               "BIOCON",
    "AUROBINDO":            "AUROPHARMA",
    "TORRENT":              "TORNTPHARM",
    "PERSISTENT":           "PERSISTENT",
    "LTIMINDTREE":          "LTIM",
    "LTI":                  "LTIM",
    "MPHASIS":              "MPHASIS",
    "NAUKRI":               "NAUKRI",
    "INFO EDGE":            "NAUKRI",
    "TATA ELXSI":           "TATAELXSI",
    "VEDANTA":              "VEDL",
    "NMDC":                 "NMDC",
    "SAIL":                 "SAIL",
    "MRF":                  "MRF",
    "HAVELLS":              "HAVELLS",
    "POLYCAB":              "POLYCAB",
    "VOLTAS":               "VOLTAS",
    "BLUE STAR":            "BLUESTARCO",
    "PIDILITE":             "PIDILITIND",
    "MARICO":               "MARICO",
    "DABUR":                "DABUR",
    "GODREJ":               "GODREJCP",
    "COLGATE":              "COLPAL",
    "MUTHOOT":              "MUTHOOTFIN",
    "CHOLA":                "CHOLAFIN",
    "SBI CARD":             "SBICARD",
    "TRENT":                "TRENT",
    "ZARA INDIA":           "TRENT",
    "DIXON":                "DIXON",
    "BOSCH":                "BOSCHLTD",
    "APOLLO TYRES":         "APOLLOTYRE",
    "ABB":                  "ABB",
    "SIEMENS":              "SIEMENS",
    "BSE":                  "BSE",
    "MCX":                  "MCX",
    "ANGEL ONE":            "ANGELONE",
    "CDSL":                 "CDSL",
    "360 ONE":              "360ONE",
    "FORTIS":               "FORTIS",
    "MAX HEALTH":           "MAXHEALTH",
    "VBL":                  "VBL",
    "VARUN BEVERAGES":      "VBL",
    "JUBILANT":             "JUBLFOOD",
    "EMAMI":                "EMAMILTD",
    "BERGER":               "BERGEPAINT",
    "KANSAI":               "KANSAINER",
    "NEROLAC":              "KANSAINER",
    "LIC HOUSING":          "LICHSGFIN",
    "MANAPPURAM":           "MANAPPURAM",
    "RVNL":                 "RVNL",
    "IRFC":                 "IRFC",
    "PFC":                  "PFC",
    "REC":                  "RECLTD",
    "HAL":                  "HAL",
    "CONCOR":               "CONCOR",
    "NSDL":                 "NSDL",
    "CAMS":                 "CAMS",
    "ZOMATO":               "ETERNAL",
    "ZOMATO LTD":           "ETERNAL",
    "ETERNAL LTD":          "ETERNAL",
}


def resolve_ticker(user_input: str) -> tuple[str, IndianStock | None]:
    """
    Resolve a user input (symbol, alias, or company name) to a
    Yahoo Finance NSE ticker.

    Examples:
      "INFOSYS"         -> "INFY.NS"    (alias match)
      "Reliance"        -> "RELIANCE.NS" (direct match)
      "Tata Motors"     -> "TATAMOTORS.NS" (name match)
      "HDFC"            -> "HDFCBANK.NS" (alias match)
      "RELIANCE.NS"     -> "RELIANCE.NS"  (passthrough)
    """
    clean = user_input.strip().upper().replace(".NS", "").replace(".BO", "")

    # 1. Direct symbol match (fastest)
    if clean in STOCKS_BY_SYMBOL:
        stock = STOCKS_BY_SYMBOL[clean]
        return stock.ticker_ns, stock

    # 2. Alias match (e.g. INFOSYS -> INFY, HDFC -> HDFCBANK)
    if clean in ALIASES:
        resolved = ALIASES[clean]
        stock = STOCKS_BY_SYMBOL.get(resolved)
        if stock:
            return stock.ticker_ns, stock

    # 3. Fuzzy name match (partial, case-insensitive)
    for stock in INDIAN_STOCKS:
        if clean in stock.name.upper():
            return stock.ticker_ns, stock

    # 4. Unknown — append .NS and let yfinance try
    return f"{clean}.NS", None


def is_indian_ticker(ticker: str) -> bool:
    """Return True if ticker belongs to the Indian market registry."""
    clean = ticker.upper().replace(".NS", "").replace(".BO", "")
    return clean in STOCKS_BY_SYMBOL


# ─────────────────────────────────────────────────────────────────
# Quick summary print (run directly to verify)
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Total stocks loaded : {len(INDIAN_STOCKS)}")
    print(f"Nifty 50 stocks     : {len(NIFTY_50)}")
    print(f"Sensex 30 stocks    : {len(SENSEX_30)}")
    print(f"Sectors covered     : {len(SECTORS)}")
    print("\nNifty 50 tickers:")
    print(", ".join(NIFTY_50_TICKERS))
    print("\nSensex 30 tickers:")
    print(", ".join(SENSEX_30_TICKERS))
