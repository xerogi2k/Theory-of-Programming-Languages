def is_nonterminal(symbol: str) -> bool:
    return symbol.startswith('<') and symbol.endswith('>') and len(symbol) > 2
