import os
from collections import deque, defaultdict
from typing import List, Optional, Set, Dict

class RulePartition:
    def __init__(self, name: str, line: int, position: int):
        self.name = name
        self.line = line
        self.position = position
        self.follow: Optional['RulePartition'] = None

class State:
    def __init__(self):
        self.rule_partitions: List[RulePartition] = []
        self.name: str = ""

class GeneratorSLR:
    def __init__(self, input_file_path: str, output_file_path: str):
        self.grammar: Dict[str, List[List[RulePartition]]] = defaultdict(list)
        self.first_sets: Dict[int, Set[str]] = {}
        self.next_sets: Dict[str, Set[str]] = {}
        self.non_terminals: Set[str] = set()
        self.rules: Dict[str, List[int]] = defaultdict(list)
        self.table_title: List[str] = []
        self.table: List[List[State]] = []
        self.state_indices: Dict[str, int] = {}
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    def run(self):
        if os.path.exists(self.input_file_path):
            self.parse_grammar(self.input_file_path)
            self.compute_next_sets()
            self.process_rule_queue()
        else:
            print("Файл не найден.")
            return
        self.print_table(self.output_file_path)

    def parse_grammar(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip()]

        for line_num, line in enumerate(lines, start=1):
            parts = [part.strip() for part in line.split('->', 1)]
            if len(parts) != 2:
                continue

            right_parts = [p.strip() for p in parts[1].split('/', 1)]
            non_terminal = parts[0]
            self.add_symbol(non_terminal)

            rules = [x for x in right_parts[0].split() if x]

            if not rules or (len(rules) == 1 and rules[0] == 'e'):
                self.grammar[non_terminal].append([])
                self.rules[non_terminal].append(line_num)
                continue

            self.first_sets[line_num] = set(map(str.strip, right_parts[1].split(',')))

            rule_parts = []
            prev = None
            for pos, rule_part in enumerate(rules, start=1):
                part = RulePartition(rule_part, line_num, pos)
                if prev:
                    prev.follow = part
                prev = part
                rule_parts.append(part)
                self.add_symbol(rule_part)

            self.grammar[non_terminal].append(rule_parts)
            self.rules[non_terminal].append(line_num)

    def compute_next_sets(self):
        updated = True
        while updated:
            updated = False
            for non_terminal, rules in self.grammar.items():
                for rule in rules:
                    for i, part in enumerate(rule):
                        symbol = part.name
                        if not self.is_non_terminal(symbol):
                            continue
                        if symbol not in self.next_sets:
                            self.next_sets[symbol] = set()
                        if i + 1 < len(rule):
                            next_sym = rule[i + 1].name
                            if next_sym not in self.next_sets[symbol]:
                                self.next_sets[symbol].add(next_sym)
                                updated = True
                            if self.is_non_terminal(next_sym):
                                if rule[i + 1].line in self.first_sets:
                                    before = len(self.next_sets[symbol])
                                    self.next_sets[symbol] |= self.first_sets[rule[i + 1].line]
                                    updated |= len(self.next_sets[symbol]) > before
                        else:
                            if non_terminal != symbol:
                                if non_terminal in self.next_sets:
                                    before = len(self.next_sets[symbol])
                                    self.next_sets[symbol] |= self.next_sets[non_terminal]
                                    updated |= len(self.next_sets[symbol]) > before

            for nt in self.non_terminals:
                if nt not in self.next_sets:
                    continue
                additions = set()
                for sym in self.next_sets[nt]:
                    if self.is_non_terminal(sym):
                        for line in self.rules.get(sym, []):
                            if line in self.first_sets:
                                additions |= self.first_sets[line]
                before = len(self.next_sets[nt])
                self.next_sets[nt] |= additions
                updated |= len(self.next_sets[nt]) > before

    def process_rule_queue(self):
        processed = set()
        queue = deque()

        initial_state = State()
        rp = RulePartition('<Z>', 1, 0)
        rp.follow = self.grammar['<Z>'][0][0] if self.grammar['<Z>'][0] else None
        initial_state.rule_partitions.append(rp)
        initial_state.name = '<Z>'
        queue.append(initial_state)

        while queue:
            current = queue.popleft()
            if current.name in processed:
                continue
            processed.add(current.name)

            row = [State() for _ in range(len(self.table_title) + 1)]
            row[0] = current

            if current.name == '<Z>':
                row[1].name = "OK"
                if len(self.grammar['<Z>']) > 1:
                    if "End" in self.table_title:
                        idx = self.table_title.index("End")
                        reduce_name = f"R{self.grammar['<Z>'][1][0].line}"
                        if reduce_name not in row[idx + 1].name:
                            row[idx + 1].name += reduce_name

            visited = set()
            to_process = deque()
            for rp in current.rule_partitions:
                if rp.follow:
                    if rp.follow.name == "End":
                        if "End" in self.table_title:
                            idx = self.table_title.index("End")
                            reduce_name = f"R{rp.line}"
                            if reduce_name not in row[idx + 1].name:
                                row[idx + 1].name += reduce_name
                    else:
                        if self.is_non_terminal(rp.follow.name):
                            for i, rule in enumerate(self.grammar[rp.follow.name]):
                                if not rule:
                                    epsilon_line = self.rules[rp.follow.name][i]
                                    for sym in self.next_sets.get(rp.follow.name, []):
                                        if sym in self.table_title:
                                            idx = self.table_title.index(sym)
                                            reduce_name = f"R{epsilon_line}"
                                            if reduce_name not in row[idx + 1].name:
                                                row[idx + 1].name += reduce_name
                        to_process.append(rp.follow)
                else:
                    for nt, lines in self.rules.items():
                        if rp.line in lines:
                            for sym in self.next_sets.get(nt, []):
                                if sym in self.table_title:
                                    idx = self.table_title.index(sym)
                                    reduce_name = f"R{rp.line}"
                                    if reduce_name not in row[idx + 1].name:
                                        row[idx + 1].name += reduce_name
                            break

            while to_process:
                part = to_process.popleft()
                key = f"{part.name}_{part.line}_{part.position}"
                if key in visited:
                    continue
                visited.add(key)
                if part.name in self.table_title:
                    idx = self.table_title.index(part.name)
                    if all(r.name != part.name or r.line != part.line or r.position != part.position for r in row[idx + 1].rule_partitions):
                        row[idx + 1].rule_partitions.append(part)
                        row[idx + 1].name += f"{part.name}{part.line}{part.position}"

                if self.is_non_terminal(part.name):
                    for rule in self.grammar[part.name]:
                        if not rule:
                            epsilon_line = self.rules[part.name][self.grammar[part.name].index(rule)]
                            for sym in self.next_sets.get(part.name, []):
                                if sym in self.table_title:
                                    idx = self.table_title.index(sym)
                                    reduce_name = f"R{epsilon_line}"
                                    if reduce_name not in row[idx + 1].name:
                                        row[idx + 1].name += reduce_name
                            continue
                        to_process.append(rule[0])

            for i in range(1, len(row)):
                if row[i].name and row[i].name not in processed:
                    if row[i].name.startswith("R") and row[i].name[1:].isdigit():
                        continue
                    if row[i].name == "OK":
                        continue
                    queue.append(row[i])

                if row[i].name in processed:
                    for trow in self.table:
                        for state in trow:
                            if state.name == row[i].name:
                                row[i] = state
                                break

            self.table.append(row)

    def print_table(self, path: str):
        for i, row in enumerate(self.table):
            state_name = row[0].name
            if state_name not in self.state_indices:
                self.state_indices[state_name] = len(self.state_indices)

        with open(path, 'w', encoding='utf-8') as writer:
            writer.write(';'.join(self.table_title) + '\n')
            for row in self.table:
                names = []
                for cell in row[1:]:
                    name = cell.name
                    if name and not (name.startswith("R") and name[1:].isdigit()) and name != "OK":
                        name = f"S{self.state_indices.get(name, '')}"
                    names.append(name)
                writer.write(';'.join(names) + '\n')

    def add_symbol(self, symbol: str):
        if symbol not in self.table_title:
            self.table_title.append(symbol)
        if self.is_non_terminal(symbol):
            self.non_terminals.add(symbol)

    def is_non_terminal(self, s: str) -> bool:
        return s.startswith('<')