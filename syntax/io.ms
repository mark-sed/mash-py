/*
Code that showcases IO workflow
*/
# Every IO has its object
# Standard output is stored in global variable `out`
out.println("Message to the user")

# There is also an alias for out.print and out.println that does not contain the out object
print("message to be printed")

# out.print can be accessed by writing a rvalue expression, but it has to be inside of a function or global space
# or code block inside one of these
"message to be printed"

# If one wanted to not print an rvalue, then the silence operator (`~`) can be used
~foo(a, b)  # This won't print

# Variables can be also printed in this way, but the variable has to be defined before the print, otherwise 
# such statment would be taken as a nil assignment
a  # same as writing `a = nil`
a  # same as writing `print(a)`

# Silence operator can be use in this case as well, but in ends up being a pointless expression
~a  # Won't do anything only does semantic check is `a` is define 

# There is also standard error output `err`
err.println("Error to the user")

# And standard input has its file as well - `input`
user_input = input.readln()

# The input can also prompt a message using the first optional argument
user_input = input.readln("> ")

# When writing to a file, the process is almost the same, only the object has to be created first
out_file = File("/path/to/a/file.txt", "w")
out_file.println("Hello file")

# The type of the input file can be specified to even parse the file as well
in_file = File("/path/to/a/file.csv", "r")
csv_content = in_file.read_csv()

# This all can be shorten
json_content = File("/path/to/a/file.csv", "r").read_json()
out.println(json_content["att1"][0])

# The default path from which paths are taken can be set in the File object
File.base_path = "/home/inputs/"
