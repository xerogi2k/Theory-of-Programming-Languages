from src.build_parsing_table import is_terminal
from src.grammar_utils import Grammar


def check_reachability(grammar: Grammar, start_symbol: str) -> str | None:
    reachable = set()
    queue = [start_symbol]

    while queue:
        current = queue.pop()
        if current in reachable:
            continue
        reachable.add(current)

        if current in grammar.rules:
            for production in grammar.rules[current].productions:
                for symbol in production.symbols:
                    if symbol in grammar.rules and symbol not in reachable:
                        queue.append(symbol)

    all_nonterminals = set(grammar.rules.keys())
    unreachable = all_nonterminals - reachable

    return None if len(unreachable) == 0 else "Grammar is not reachable from start symbol. Symbols" + ",".join(
        unreachable)


def check_productivity(grammar: Grammar) -> str | None:
    productive = set()
    changed = True

    for nonterminal, rule in grammar.rules.items():
        for production in rule.productions:
            if all(is_terminal(symbol) or symbol == "ε" for symbol in production.symbols):
                productive.add(nonterminal)
                break

    while changed:
        changed = False
        for nonterminal, rule in grammar.rules.items():
            if nonterminal in productive:
                continue

            for production in rule.productions:
                if all(is_terminal(symbol) or symbol == "ε" or symbol in productive for symbol in production.symbols):
                    productive.add(nonterminal)
                    changed = True
                    break

    all_nonterminals = set(grammar.rules.keys())
    unproductive = all_nonterminals - productive

    if unproductive:
        dependency_graph = {nt: set() for nt in all_nonterminals}

        for nonterminal, rule in grammar.rules.items():
            for production in rule.productions:
                for symbol in production.symbols:
                    if symbol in grammar.rules:
                        dependency_graph[nonterminal].add(symbol)

        new_unproductive = set()
        for nt in unproductive:
            if all(dep in unproductive for dep in dependency_graph[nt]):
                new_unproductive.add(nt)

        if new_unproductive:
            return "Grammar is not productive. This nonterminals create a cycle: " + ",".join(sorted(new_unproductive))

    return None if len(unproductive) == 0 else "Grammar is not productive."


def check_ll1_uniqueness(grammar: Grammar) -> str | None:
    conflicts = []

    for nonterminal, rule in grammar.rules.items():
        if len(rule.productions) <= 1:
            continue

        directing_sets = []
        for i, production in enumerate(rule.productions):
            directing_set = set(production.first_set)
            directing_sets.append((i, directing_set))

        for i in range(len(directing_sets)):
            for j in range(i + 1, len(directing_sets)):
                set1 = directing_sets[i][1]
                set2 = directing_sets[j][1]
                intersection = set1 & set2

                if intersection:
                    prod1_symbols = ' '.join(rule.productions[directing_sets[i][0]].symbols)
                    prod2_symbols = ' '.join(rule.productions[directing_sets[j][0]].symbols)
                    conflicts.append(
                        f"{nonterminal}: '{prod1_symbols}' and '{prod2_symbols}' have common symbols {sorted(intersection)}")

    if conflicts:
        return "Grammar is not LL(1). Directing set conflicts:\n" + "\n".join(conflicts)

    return None


def validate_grammar(grammar: Grammar, start_symbol: str) -> str | None:
    reachability_error = check_reachability(grammar, start_symbol)
    if reachability_error:
        return reachability_error

    productivity_error = check_productivity(grammar)
    if productivity_error:
        return productivity_error

    return None
