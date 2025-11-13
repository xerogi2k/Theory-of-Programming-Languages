from itertools import chain

from src.grammar_utils import Grammar, Production
from src.table import Line
from src.util import is_nonterminal


def build_parsing_table(grammar: Grammar, first_symbol: str) -> list[Line]:
    rule_indices = compute_rule_indices(grammar)
    table = []
    index = 0
    end_set = False

    ordered_rules = []
    if first_symbol in grammar.rules:
        ordered_rules.append(grammar.rules[first_symbol])
    
    for nt, rule in grammar.rules.items():
        if nt != first_symbol:
            ordered_rules.append(rule)

    for rule in ordered_rules:
        production_symbols = [prod.symbols for prod in rule.productions]

        for prod_idx, production in enumerate(rule.productions):
            error = (prod_idx == len(rule.productions) - 1)
            pointer = index + len(rule.productions) - prod_idx + sum(
                len(p.symbols) for p in rule.productions[:prod_idx])

            table.append(Line(index, rule.nonterminal, production.first_set, shift=False, error=error, pointer=pointer,
                              stack=False, end=False))
            index += 1

        for sym_idx, symbols in enumerate(production_symbols):
            for sub_idx, symbol in enumerate(symbols):
                first_set = get_first_set(symbol, grammar, rule.productions[sym_idx])
                pointer = get_pointer(symbol, symbols, sub_idx, index, rule_indices)
                end, end_set = check_end(symbol, symbols, sub_idx, end_set)
                stack = (sub_idx != len(symbols) - 1) if is_nonterminal(symbol) else False

                table.append(
                    Line(index, symbol, first_set, shift=is_terminal(symbol), error=True, pointer=pointer, stack=stack,
                         end=end))
                index += 1

    return table


def compute_rule_indices(grammar: Grammar) -> dict[str, int]:
    rule_indices = {}
    index = 0
    for rule in grammar.rules.values():
        rule_indices[rule.nonterminal] = index
        index += sum(len(production.symbols) + 1 for production in rule.productions)
    return rule_indices


def get_first_set(symbol: str, grammar: Grammar, production: Production) -> list[str]:
    if is_nonterminal(symbol):
        return list(set(chain.from_iterable(prod.first_set for prod in grammar.rules[symbol].productions)))
    return production.first_set if symbol == "ε" else [symbol]


def get_pointer(symbol: str, symbols: list[str], index: int, current_index: int,
                rule_indices: dict[str, int]) -> int | None:
    if is_nonterminal(symbol):
        return rule_indices[symbol]
    return None if index == len(symbols) - 1 else current_index + 1


def check_end(symbol: str, symbols: list[str], index: int, end_set: bool) -> (bool, bool):
    end = not end_set and index == len(symbols) - 1 and is_terminal(symbol)
    return end, end_set or end



def is_terminal(symbol: str) -> bool:
    return not (symbol.startswith("<") and symbol.endswith(">")) and symbol != "ε"
