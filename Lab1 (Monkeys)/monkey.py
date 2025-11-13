import sys

class Pattern1:
    def __init__(self, words):
        self.words = words
        self.index = 0

    def current_word(self):
        return self.words[self.index] if self.index < len(self.words) else ""

    def start(self):
        return self.parse_sequence()

    def parse_sequence(self):
        saved = self.index
        if self.parse_phrase():
            if self.parse_sequence_tail():
                return True
        self.index = saved
        return False

    def parse_sequence_tail(self):
        if self.current_word() == "ау":
            self.index += 1
            if self.parse_phrase():
                if self.parse_sequence_tail():
                    return True
            return False
        return True

    def parse_phrase(self):
        saved = self.index
        if self.parse_base():
            if self.parse_phrase_tail():
                return True
        self.index = saved
        return False

    def parse_phrase_tail(self):
        if self.current_word() == "ку":
            self.index += 1
            if self.parse_base():
                if self.parse_phrase_tail():
                    return True
            return False
        return True

    def parse_base(self):
        if self.current_word() == "ух-ты":
            self.index += 1
            return True

        if self.current_word() == "хо":
            self.index += 1
            if self.parse_base():
                return True
            return False

        if self.current_word() == "ну":
            self.index += 1
            if self.parse_sequence():
                if self.current_word() == "и_ну":
                    self.index += 1
                    return True
        return False


class Pattern2:
    def __init__(self, words):
        self.words = words
        self.index = 0

    def current_word(self):
        return self.words[self.index] if self.index < len(self.words) else ""

    def start(self):
        return self.parse_expression()

    def parse_expression(self):
        if self.current_word() == "ой":
            self.index += 1
            if self.parse_prefix():
                if self.current_word() == "ай":
                    self.index += 1
                    if self.parse_suffix():
                        return True
        return False

    def parse_prefix(self):
        if self.current_word() == "ну":
            self.index += 1
            if self.parse_repeated_nu():
                return True
        return False

    def parse_repeated_nu(self):
        if self.current_word() == "ну":
            self.index += 1
            if self.parse_repeated_nu():
                return True
            return False
        return True

    def parse_suffix(self):
        if self.current_word() == "ух-ты":
            self.index += 1
            return True

        if self.current_word() == "хо":
            self.index += 1
            if self.parse_suffix():
                if self.current_word() == "хо":
                    self.index += 1
                    return True
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python monkey.py <input_file>")
        return

    with open(sys.argv[1], 'r') as f:
        line = f.readline().strip().replace("  ", " ")
        words = line.split(' ')

    if Pattern1(words).start():
        print("Первый паттерн")
    elif Pattern2(words).start():
        print("Второй паттерн")
    else:
        print("Не соответствует паттернам")


if __name__ == "__main__":
    main()