from BuildSLR import SLRAnalyzer
import os
print("Current dir:", os.getcwd())
print("Files here:", os.listdir())

def main():
    analyzer = SLRAnalyzer("grammar.txt", "chain.txt")
    analyzer.run()

if __name__ == "__main__":
    main()