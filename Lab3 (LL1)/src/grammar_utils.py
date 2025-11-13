import re
from dataclasses import dataclass


@dataclass
class Production:
    symbols: list[str]
    first_set: list[str]

    def add_first_set(self, first_set: list[str]) -> None:
        self.first_set = first_set


@dataclass
class Rule:
    nonterminal: str
    productions: list[Production]

    def add_production(self, symbols: list[str], first_set: list[str]) -> None:
        self.productions.append(Production(symbols, first_set))


@dataclass
class Grammar:
    rules: dict[str, Rule]

    def add_production(self, nonterminal: str, symbols: list[str], first_set: list[str]) -> None:
        if nonterminal not in self.rules:
            self.rules[nonterminal] = Rule(nonterminal, [])
        self.rules[nonterminal].add_production(symbols, first_set)


def parse_grammar_with_first_set(contents: list[str]) -> Grammar:
    grammar = Grammar(dict())
    pattern = re.compile(r"^\s*(<.+>)\s*->(.*)\|\s*(.*)\s*$")

    for rule in contents:
        match = pattern.match(rule)
        if match:
            nonterminal, symbols, first_set = match.groups()
            grammar.add_production(nonterminal.strip(), symbols.strip().split(), first_set.strip().split())

    return grammar


def parse_grammar(contents: list[str]) -> tuple[Grammar, str]:
    grammar = Grammar(dict())
    pattern = re.compile(r"^\s*(<.+>)\s*->\s*(.*)$")
    axiom = None

    for rule in contents:
        match = pattern.match(rule)
        if match:
            nonterminal, symbols = match.groups()
            if axiom is None:
                axiom = nonterminal
            grammar.add_production(nonterminal.strip(), symbols.strip().split(), [])

    return grammar, axiom


def write_grammar(grammar: Grammar, axiom_nonterminal: str) -> None:
    with open("new-grammar.txt", "w") as f:
        axiom = grammar.rules[axiom_nonterminal]
        for production in axiom.productions:
            f.write(f"{axiom.nonterminal} -> {" ".join(production.symbols)} | {" ".join(sorted(production.first_set))}\n")
        for rule in grammar.rules.values():
            if rule.nonterminal == axiom_nonterminal:
                continue
            for production in rule.productions:
                f.write(
                    f"{rule.nonterminal} -> {" ".join(production.symbols)} | {" ".join(sorted(production.first_set))}\n")
