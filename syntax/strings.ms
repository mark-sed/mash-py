/*
Working with strings in Mash
*/

# Basic string
basic_str = "Text\n"

# Formatted (interpolled) string has prefix `f`
int_str = f"Interpolled {basic_str}"  # "Interpolled Text\n" 

# Raw string
raw_str = r"No escape\tsequences allowed\n"  # "No escape\\tsequences allowed\n"

# All strings support unicode
uni_str = "🍣 Sushi"