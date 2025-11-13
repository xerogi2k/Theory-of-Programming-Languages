from src.table import Line


def check_line(line: list[str], table: list[Line]) -> str:
    index = 0
    current_position = 0
    stack = []
    table_dict = {l.number: l for l in table}

    while index < len(line):
        if current_position not in table_dict:
            return f"Error: Invalid position {current_position}"

        current = table_dict[current_position]
        symbol = line[index] # Поставил нижний регистр для считывания

        if symbol not in current.first_set:
            if current.error:
                return f"Error at index {index}: '{symbol}' not in {current.first_set}"
            else:
                current_position += 1
                continue

        if current.end:
            return "Ok" if index == len(line) - 1 else "Error: Unexpected EOL"

        if current.shift:
            index += 1
        if current.stack:
            stack.append(current_position + 1)
        if current.pointer:
            current_position = current.pointer
        elif stack:
            current_position = stack.pop()
        else:
            return f"Error at index {index}: No valid pointer"

    return "Error: Incomplete processing (No EOL)"
