from lab6.lexer import Lexer
from lab6.lexer_token import LexerToken


class Runner:
    def __init__(self, table_file_path: str, chain_file_path: str, rules: list[tuple[str, list[str]]]):
        self._table: dict[tuple[int, str], str] = {}
        self._symbols: list[str] = []
        self._load_table(table_file_path)

        self._file_path = chain_file_path
        self._rules = rules
        self._log_file_path = "output.txt"

    def _log(self, message: str) -> None:
        with open(self._log_file_path, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def _load_table(self, path: str) -> None:
        with open(path, encoding='utf-8') as f:
            lines = f.read().splitlines()

        for i, line in enumerate(lines):
            parts = line.strip().split(';')
            if i == 0:
                self._symbols = parts
            else:
                state = i - 1
                for j, value in enumerate(parts):
                    value = value.strip()
                    if value:
                        self._table[(state, self._symbols[j])] = value

    def run(self) -> bool:
        open(self._log_file_path, "w", encoding="utf-8").close()  # Очистить лог-файл

        state_stack: list[int] = [0]
        symbol_stack: list[str] = []
        position = 0

        lexer = Lexer(self._file_path)

        def next_significant_token():
            while True:
                token = lexer.next_token()
                if token is None:
                    return None
                if token.type not in ('SPACE', 'BLOCK_COMMENT', 'LINE_COMMENT'):
                    return token

        token = next_significant_token()

        if token is None:
            self._log("Input is empty")
            return False
        if token.type == "BAD":
            self._log(f"Error {token.pos[0]} line {token.pos[1]}: Unknown symbol")
            return False

        while True:
            current_state = state_stack[-1]
            current_symbol = token.type
            action = self._table.get((current_state, current_symbol))

            self._log(f"\nPos: {position}")
            self._log(f"Symbol: '{current_symbol}'")
            self._log(f"State: {current_state}")
            self._log(f"Action: {action}")
            self._log("Stacks:")
            self._log(f"  States: {state_stack}")
            self._log(f"  Symbols: {symbol_stack}")

            if action is None:
                self._log(f"Err no action {current_state} {current_symbol}")
                return False

            if action == "OK":
                if current_symbol == "End" and not symbol_stack:
                    self._log("Ok")
                    return True
                self._log("Err")
                return False

            if action.startswith("S"):
                next_state = int(action[1:])
                self._log(f"Shift to {next_state}, symbol {current_symbol}")

                state_stack.append(next_state)
                symbol_stack.append(current_symbol)
                position += 1

                token = next_significant_token()
                if token is None:
                    self._log("Not end")
                    return False
                if token.type == "BAD":
                    self._log(f"Error {token.pos[0]} line {token.pos[1]}: Unknown symbol")
                    return False

            elif action.startswith("R"):
                while action.startswith("R"):
                    rule_index = int(action[1:])
                    rule = self._rules[rule_index - 1]

                    self._log(f"Reduce {rule_index}: {rule.terminal} → {' '.join(rule.parts)}")

                    for _ in rule.parts:
                        popped_symbol = symbol_stack.pop()
                        popped_state = state_stack.pop()
                        self._log(f"  delete {popped_symbol}, state {popped_state}")

                    symbol_stack.append(rule.terminal)
                    self._log(f"  add to stack {rule.terminal}")

                    top_state = state_stack[-1]
                    goto_action = self._table.get((top_state, rule.terminal))

                    if not goto_action:
                        self._log(f"Err state {top_state} symbol {rule.terminal}")
                        return False

                    if goto_action == "OK":
                        self._log("Ok")
                        return True
                    elif goto_action.startswith("S"):
                        state_stack.append(int(goto_action[1:]))
                        self._log(f"Go to {goto_action[1:]} symbol {rule.terminal}")
                        break
                    elif goto_action.startswith("R"):
                        action = goto_action
                    else:
                        self._log(f"Err go to '{goto_action}'")
                        return False
            else:
                self._log("Err")
                return False


class Rule:
    def __init__(self, terminal: str, parts: list[str]):
        self.terminal = terminal
        self.parts = parts