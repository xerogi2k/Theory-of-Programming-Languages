import os

from FSR import FirstSetFormation
from ParseSLR import GeneratorSLR
from Parser import Runner, Rule


class SLRAnalyzer:
    def __init__(self, grammar_path: str, chain_path: str):
        self.grammar_path = grammar_path
        self.chain_path = chain_path

    def parse_grammar_to_rules(self, grammar_path: str) -> list[Rule]:
        if not os.path.exists(grammar_path):
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}")

        rules = []

        with open(grammar_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip()]

        for line in lines:
            rule_part = line.split('/')[0]
            parts = rule_part.split("->")
            if len(parts) != 2:
                raise ValueError(f"Invalid grammar rule: {rule_part}")

            left = parts[0].strip()
            right = parts[1].strip().split()

            rules.append(Rule(left, right))

        # Remove 'End' symbol from the first rule's right-hand side
        if "End" in rules[0].parts:
            rules[0].parts.remove("End")

        return rules

    def run(self):
        try:
            first_set_formation = FirstSetFormation(self.grammar_path, "fs.txt")
            first_set_formation.run()
        except Exception as ex:
            print(f"FirstSetFormation error: {ex}")

        rules = self.parse_grammar_to_rules("fs.txt")

        try:
            generator_slr = GeneratorSLR("fs.txt", "table.csv")
            generator_slr.run()
        except Exception as ex:
            print(f"GeneratorSLR error: {ex}")

        try:
            print("Chain path (as passed):", self.chain_path)
            abs_chain_path = os.path.abspath(self.chain_path)
            print("Chain path (absolute):", abs_chain_path)

            # И передаем абсолютный путь
            runner = Runner("table.csv", abs_chain_path, rules)
            print(runner.run())
        except Exception as ex:
            print(f"Runner error: {ex}")