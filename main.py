from Regex import Regex
from Yalex import Yalex
from syntax_tree import SyntaxTree

yal = Yalex("examples/slr-4.yal")
postfix = Regex(yal.final_regex).shunting_yard()
SyntaxTree(postfix).render()

print("Parsed regex:", yal.final_regex)
print("Generated tree is saved in result/tree.png file.")
