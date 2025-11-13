from src.grammar_utils import Grammar, Rule, Production
from src.util import is_nonterminal


def factorize_grammar(grammar: Grammar) -> Grammar:
    new_grammar = Grammar({})

    for nonterminal, rule in grammar.rules.items():
        productions_by_prefix = find_common_prefixes(rule.productions)

        if len(productions_by_prefix) == len(rule.productions):
            new_grammar.rules[nonterminal] = rule
            continue

        new_rule = Rule(nonterminal, [])

        for prefix, productions in productions_by_prefix.items():
            if len(productions) == 1:
                new_rule.productions.append(productions[0])
                continue

            new_nonterminal = f"<{nonterminal.strip('<>')}'>"

            prefix_symbols = list(prefix)
            new_rule.productions.append(Production(prefix_symbols + [new_nonterminal], []))

            suffix_productions = []
            for production in productions:
                suffix = production.symbols[len(prefix_symbols):]
                suffix_productions.append(Production(suffix or ["ε"], []))

            new_grammar.rules[new_nonterminal] = Rule(new_nonterminal, suffix_productions)

        new_grammar.rules[nonterminal] = new_rule

    if any(len(find_common_prefixes(rule.productions)) < len(rule.productions) for rule in new_grammar.rules.values()):
        return factorize_grammar(new_grammar)

    return new_grammar


def find_common_prefixes(productions: list[Production]) -> dict[tuple, list[Production]]:
    if not productions:
        return {}

    result = {}
    processed = set()

    for i, prod1 in enumerate(productions):
        if i in processed:
            continue

        common_prefix = []
        common_productions = [prod1]
        processed.add(i)

        for j, prod2 in enumerate(productions[i + 1:], i + 1):
            if j in processed:
                continue

            common_length = 0
            min_length = min(len(prod1.symbols), len(prod2.symbols))

            for k in range(min_length):
                if prod1.symbols[k] == prod2.symbols[k]:
                    common_length = k + 1
                else:
                    break

            if common_length > 0:
                if not common_prefix or common_length >= len(common_prefix):
                    if common_length > len(common_prefix):
                        common_prefix = prod1.symbols[:common_length]
                        common_productions = [prod1, prod2]
                    else:
                        common_productions.append(prod2)
                    processed.add(j)

        if len(common_productions) > 1:
            prefix_key = tuple(common_prefix)
            result[prefix_key] = common_productions
        else:
            first_symbol = prod1.symbols[0] if prod1.symbols else "ε"
            prefix_key = (f"{first_symbol}_unique_{i}",)
            result[prefix_key] = [prod1]

    return result


def remove_direct_recursion(grammar: Grammar) -> Grammar:
    new_grammar = Grammar({})

    for nonterminal, rule in grammar.rules.items():
        recursive = []
        non_recursive = []

        for production in rule.productions:
            if production.symbols and production.symbols[0] == nonterminal:
                recursive.append(production.symbols[1:])
            else:
                non_recursive.append(production.symbols)

        if recursive:
            new_nonterminal = f"<{nonterminal.strip('<>')}r>"
            new_grammar.rules[new_nonterminal] = Rule(new_nonterminal, [])

            new_grammar.rules[nonterminal] = Rule(nonterminal, [])
            for body in non_recursive:
                clean_body = [] if body == ["ε"] else body
                new_body = clean_body + [new_nonterminal]
                new_grammar.rules[nonterminal].productions.append(Production(new_body, []))

            new_grammar.rules[new_nonterminal].productions = [Production(body + [new_nonterminal], []) for body in
                                                              recursive] + [Production(["ε"], [])]
        else:
            new_grammar.rules[nonterminal] = rule

    return new_grammar


def build_dependency_graph(grammar: Grammar) -> dict[str, set[str]]:
    graph = dict()
    for nonterminal, rule in grammar.rules.items():
        for production in rule.productions:
            graph.setdefault(nonterminal, set())
            if production.symbols and production.symbols[0] in grammar.rules:
                graph[nonterminal].add(production.symbols[0])
    return graph


def topological_sort(graph: dict[str, set[str]], nonterminal: str) -> tuple[list[str], bool]:
    visited = []
    order = []

    def dfs(node: str) -> None:
        if node in visited:
            visited.append(node)
            return
        visited.append(node)
        for neighbor in graph[node]:
            if neighbor != node:
                dfs(neighbor)
        order.append(node)

    dfs(nonterminal)

    return order, len(visited) != len(order)


def remove_indirect_recursion(grammar: Grammar) -> Grammar:
    graph = build_dependency_graph(grammar)

    for node in graph:
        order, is_indirect = topological_sort(graph, node)
        order = order[:-1]
        if not is_indirect:
            continue

        for i, a_i in enumerate(order):
            for j in range(i):
                a_j = order[j]
                new_productions = []

                for production in grammar.rules[a_i].productions:
                    if production.symbols and production.symbols[0] == a_j:
                        for a_j_prod in grammar.rules[a_j].productions:
                            new_productions.append(Production(a_j_prod.symbols + production.symbols[1:], []))
                    else:
                        new_productions.append(production)

                grammar.rules[a_i].productions = new_productions

    return grammar


def remove_unreachable_rules(grammar: Grammar, start_symbol: str) -> Grammar:
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

    new_rules = {nt: rule for nt, rule in grammar.rules.items() if nt in reachable}
    return Grammar(new_rules)


def calculate_directing_sets(grammar: Grammar, start_symbol: str) -> Grammar:
    first_sets = {}

    for rule in grammar.rules.values():
        for production in rule.productions:
            for symbol in production.symbols:
                if not (is_nonterminal(symbol)):
                    first_sets[symbol] = {symbol}

    for nonterminal in grammar.rules:
        first_sets[nonterminal] = set()

    changed = True
    while changed:
        changed = False
        for nonterminal, rule in grammar.rules.items():
            for production in rule.productions:
                all_can_derive_empty = True
                for symbol in production.symbols:
                    if symbol == "ε":
                        continue

                    if not (is_nonterminal(symbol)):
                        if symbol not in first_sets[nonterminal]:
                            first_sets[nonterminal].add(symbol)
                            changed = True
                        all_can_derive_empty = False
                        break

                    for sym in first_sets.get(symbol, set()):
                        if sym != "ε" and sym not in first_sets[nonterminal]:
                            first_sets[nonterminal].add(sym)
                            changed = True

                    if "ε" not in first_sets.get(symbol, set()):
                        all_can_derive_empty = False
                        break

                if all_can_derive_empty and "ε" not in first_sets[nonterminal]:
                    first_sets[nonterminal].add("ε")
                    changed = True

    follow_sets = {nonterminal: set() for nonterminal in grammar.rules}

    follow_sets[start_symbol].add(grammar.rules[start_symbol].productions[0].symbols[-1])

    changed = True
    while changed:
        changed = False
        for nonterminal, rule in grammar.rules.items():
            for production in rule.productions:
                for i, symbol in enumerate(production.symbols):
                    if not (is_nonterminal(symbol)) or symbol == "ε":
                        continue

                    trailing_first = set()
                    all_can_derive_empty = True

                    for j in range(i + 1, len(production.symbols)):
                        next_symbol = production.symbols[j]
                        if next_symbol == "ε":
                            continue

                        symbol_first = first_sets.get(next_symbol, {next_symbol})
                        for sym in symbol_first:
                            if sym != "ε":
                                trailing_first.add(sym)

                        if "ε" not in symbol_first:
                            all_can_derive_empty = False
                            break

                    if all_can_derive_empty or i == len(production.symbols) - 1:
                        for follow_sym in follow_sets[nonterminal]:
                            if follow_sym not in follow_sets[symbol]:
                                follow_sets[symbol].add(follow_sym)
                                changed = True

                    for sym in trailing_first:
                        if sym not in follow_sets[symbol]:
                            follow_sets[symbol].add(sym)
                            changed = True

    new_grammar = Grammar({})
    for nonterminal, rule in grammar.rules.items():
        new_rule = Rule(nonterminal, [])
        for production in rule.productions:
            prod_first = calculate_production_first(production.symbols, first_sets)

            can_derive_empty = True
            for symbol in production.symbols:
                if symbol == "ε":
                    continue
                symbol_first = first_sets.get(symbol, {symbol})
                if "ε" not in symbol_first:
                    can_derive_empty = False
                    break

            directing_set = set()
            for sym in prod_first:
                if sym != "ε":
                    directing_set.add(sym)

            if can_derive_empty or "ε" in prod_first:
                directing_set.update(follow_sets[nonterminal])

            new_production = Production(symbols=production.symbols,
                                        first_set=[sym for sym in directing_set if sym != "ε"])
            new_rule.productions.append(new_production)

        new_grammar.rules[nonterminal] = new_rule

    return new_grammar


def calculate_production_first(symbols: list[str], first_sets: dict[str, set[str]]) -> set[str]:
    if not symbols or symbols[0] == "ε":
        return {"ε"}

    result = set()
    all_can_derive_empty = True

    for symbol in symbols:
        if symbol == "ε":
            continue

        if not (is_nonterminal(symbol)):
            result.add(symbol)
            all_can_derive_empty = False
            break

        symbol_first = first_sets.get(symbol, set())
        for sym in symbol_first:
            if sym != "ε":
                result.add(sym)

        if "ε" not in symbol_first:
            all_can_derive_empty = False
            break

    if all_can_derive_empty:
        result.add("ε")

    return result
