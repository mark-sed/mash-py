# Generates standalone LALR(1) parser for mash
python3 -m lark.tools.standalone mash.lark > ../mash_parser.py
