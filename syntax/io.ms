/*
Code that showcases IO workflow
*/
# Every IO has its object
# Standard output is stored in global variable `out`
out.println("Message to the user")

# out.print can be accessed by writing a rvalue expression
"message to be printed"

# If one wanted to not print an rvalue, then the silence operator (`~`) can be used
~foo(a, b)  # This won't print

# There is also an alias for out.print and out.println that does not contain the out object
print("message to be printed")

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
