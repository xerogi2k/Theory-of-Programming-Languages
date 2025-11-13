import os
from collections import defaultdict, deque
from itertools import chain

class FirstSetFormation:
    def __init__(self, input_file_path, output_file_path):
        self.grammar = defaultdict(list)
        self.first_sets = defaultdict(list)
        self.next_sets = defaultdict(set)
        self._new_non_terminal_index = 1
        self._input_file_path = input_file_path
        self._output_file_path = output_file_path

    def run(self):
        try:
            self.parse_grammar(self._input_file_path)
            self.remove_unproductive_symbols()
            self.remove_unreachable_symbols()
            self.eliminate_epsilon_productions()
            self.initialize_next_sets()
            self.compute_next_sets()
            self.compute_first_sets()
            self.transitive_closure()
            self.print_results(self._output_file_path)
        except Exception as e:
            print(f"Ошибка: {e}")

    def parse_grammar(self, file_path):
        if not os.path.exists(file_path):
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return

        start_symbol = lines[0].split("->")[0].strip()
        self.grammar["<Z>"].append([start_symbol, "End"])

        for line in lines:
            if '->' not in line:
                continue
            non_terminal, rhs = map(str.strip, line.split('->', 1))
            rules = [r.strip().split() for r in rhs.split('|') if r.strip()]
            self.grammar[non_terminal].extend(rules)

    def remove_unreachable_symbols(self):
        start_symbol = next(iter(self.grammar))
        reachable = set([start_symbol])
        queue = deque([start_symbol])

        while queue:
            current = queue.popleft()
            for rule in self.grammar.get(current, []):
                for symbol in rule:
                    if symbol in self.grammar and symbol not in reachable:
                        reachable.add(symbol)
                        queue.append(symbol)

        unreachable = set(self.grammar) - reachable
        if unreachable:
            raise Exception(f"Обнаружены недостижимые правила: {', '.join(unreachable)}")

    def remove_unproductive_symbols(self):
        productive = set()
        updated = True

        while updated:
            updated = False
            for non_terminal, rules in self.grammar.items():
                if non_terminal in productive:
                    continue
                for rule in rules:
                    if all(s not in self.grammar or s in productive for s in rule):
                        productive.add(non_terminal)
                        updated = True
                        break

        unproductive = set(self.grammar) - productive
        if unproductive:
            raise Exception(f"Обнаружены непродуктивные правила: {', '.join(unproductive)}")

    def initialize_next_sets(self):
        for non_terminal in self.grammar:
            self.next_sets[non_terminal] = set()

    def compute_next_sets(self):
        updated = True
        while updated:
            updated = False
            for non_terminal, rules in self.grammar.items():
                for rule in rules:
                    for i, symbol in enumerate(rule):
                        if symbol not in self.grammar:
                            continue
                        if i + 1 < len(rule):
                            before = len(self.next_sets[symbol])
                            self.next_sets[symbol].add(rule[i + 1])
                            updated |= len(self.next_sets[symbol]) > before
                        elif non_terminal != symbol:
                            before = len(self.next_sets[symbol])
                            self.next_sets[symbol].update(self.next_sets[non_terminal])
                            updated |= len(self.next_sets[symbol]) > before

    def compute_first_sets(self):
        for non_terminal, rules in self.grammar.items():
            sets_for_rules = []
            for rule in rules:
                first = set()
                if rule[0] == 'e':
                    for next_symbol in self.next_sets[non_terminal]:
                        if next_symbol in self.grammar and next_symbol in self.first_sets:
                            first.update(chain.from_iterable(self.first_sets[next_symbol]))
                        else:
                            first.add(next_symbol)
                else:
                    first.add(rule[0])
                sets_for_rules.append(first)
            self.first_sets[non_terminal] = sets_for_rules

    def transitive_closure(self):
        updated = True
        while updated:
            updated = False
            for non_terminal, rule_sets in self.first_sets.items():
                for i in range(len(rule_sets)):
                    current_set = rule_sets[i]
                    expanded = set(current_set)
                    for symbol in current_set:
                        if symbol in self.grammar and symbol in self.first_sets:
                            for fs in self.first_sets[symbol]:
                                expanded.update(fs)
                    if expanded != current_set:
                        rule_sets[i] = expanded
                        updated = True

    def get_first_set(self, symbol, visited=None):
        if visited is None:
            visited = set()
        if symbol in visited:
            return set()
        visited.add(symbol)
        if symbol not in self.grammar:
            return {symbol}

        result = set()
        for production in self.grammar[symbol]:
            for i, sym in enumerate(production):
                first = self.get_first_set(sym, visited)
                result.update(first)
                if 'e' not in first:
                    break
        return result

    def get_common_prefix(self, rules):
        if not rules:
            return []
        prefix = list(rules[0])
        for rule in rules[1:]:
            j = 0
            while j < len(prefix) and j < len(rule) and prefix[j] == rule[j]:
                j += 1
            prefix = prefix[:j]
            if not prefix:
                break
        return prefix

    def print_results(self, file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            for non_terminal, rules in self.grammar.items():
                for i, rule in enumerate(rules):
                    self.first_sets[non_terminal][i].discard('e')
                    rule_str = ' '.join(rule)
                    first_str = ','.join(self.first_sets[non_terminal][i])
                    f.write(f"{non_terminal} -> {rule_str} / {first_str}\n")

    def eliminate_epsilon_productions(self):
        nullable = set()
        changed = True
        while changed:
            changed = False
            for non_terminal, rules in self.grammar.items():
                if non_terminal in nullable:
                    continue
                for rule in rules:
                    if rule == ['e'] or all(s in nullable for s in rule):
                        nullable.add(non_terminal)
                        changed = True
                        break

        start_symbol = next(iter(self.grammar))
        new_grammar = defaultdict(list)

        for non_terminal, rules in self.grammar.items():
            had_epsilon = any(rule == ['e'] for rule in rules)
            for rule in rules:
                if rule == ['e']:
                    continue
                positions = [i for i, sym in enumerate(rule) if sym in nullable]
                for mask in range(1 << len(positions)):
                    new_rule = []
                    for i, sym in enumerate(rule):
                        if i in positions and (mask >> positions.index(i)) & 1:
                            continue
                        new_rule.append(sym)
                    if not new_rule:
                        if non_terminal == start_symbol:
                            new_grammar[non_terminal].append(['e'])
                    elif new_rule not in new_grammar[non_terminal]:
                        new_grammar[non_terminal].append(new_rule)
            if had_epsilon and non_terminal == start_symbol and ['e'] not in new_grammar[non_terminal]:
                new_grammar[non_terminal].append(['e'])

        self.grammar = new_grammar