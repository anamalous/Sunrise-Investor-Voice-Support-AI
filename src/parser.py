mapping = { # keyword based category matching
    "KYC": ["kyc", "onboarding", "documents", "minor", "identity", "pan", "aadhaar"],
    "SIP": ["sip", "invest", "installment", "pause", "stop", "frequency", "insufficient"],
    "Redemption": ["redeem", "withdrawal", "units", "money back", "payout", "duration"],
    "Taxation": ["tax", "stcg", "ltcg", "tds", "gains", "equity"]
}
def advanced_query_parser(query):
    query = query.lower()
    
    found_categories = [cat for cat, keywords in mapping.items() if any(k in query for k in keywords)]
    return found_categories