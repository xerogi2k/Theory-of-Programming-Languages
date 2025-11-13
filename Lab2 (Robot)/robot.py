import sys

class RobotCommandParser:
    def __init__(self, words):
        self.words = words
        self.index = 0

    def current_word(self):
        return self.words[self.index] if self.index < len(self.words) else ""

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        if self.current_word() == "start":
            self.index += 1
            if self.parse_statement_sequence():
                if self.current_word() == "stop":
                    return True
        return False

    def parse_statement_sequence(self):
        if self.parse_action_block():
            if self.parse_looping_steps():
                return True
        return False

    def parse_looping_steps(self):
        if self.parse_step_command():
            if self.parse_action_block():
                if self.parse_looping_steps():
                    return True
            return False
        return True

    def parse_action_block(self):
        if self.parse_action():
            if self.parse_optional_turns():
                return True
        return False

    def parse_optional_turns(self):
        if self.parse_turn_head():
            if self.parse_action():
                if self.parse_optional_turns():
                    return True
            return False
        return True

    def parse_action(self):
        if self.current_word() in ("left", "right"):
            self.index += 1
            return True

        if self.current_word() == "45degrees":
            self.index += 1
            if self.parse_action():
                return True
            return False

        if self.current_word() == "hands_up":
            self.index += 1
            if self.parse_statement_sequence():
                if self.current_word() == "hands_down":
                    self.index += 1
                    return True
        return False

    def parse_step_command(self):
        if self.current_word() == "step_":
            self.index += 1
            if self.current_word() == "(":
                self.index += 1
                if self.parse_number():
                    if self.current_word() == ")":
                        self.index += 1
                        return True
        return False

    def parse_turn_head(self):
        if self.current_word() == "turn_head":
            self.index += 1
            return True
        return False

    def parse_number(self):
        if len(self.current_word()) > 1 and self.current_word()[0] == '0':
            self.index += 1
            return False

        if self.current_word() and self.current_word()[0].isdigit():
            self.index += 1
            if self.parse_digits():
                return True
        return False

    def parse_digits(self):
        word = self.current_word()
        if not word.isdigit():
            return False
        self.index += 1
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python monkey.py <input_file>")
        return

    try:
        with open(sys.argv[1], 'r') as file:
            line = file.readline().strip()
            words = line.split()
            if RobotCommandParser(words).parse():
                print("OK")
            else:
                print("NOT OK")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()