import string
filename = 'text.txt'
try:
    with open(filename, 'r') as file:
        data = file.read().lower()

        data = data.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))

        if not data:
            print(f"Warning: The file {filename} is empty.")
        else:
            words = data.split()
            lines = data.splitlines()
            num_of_char = len(data)
            total_words = len(words)
            total_lines = len(lines)

            print(f"The total number of characters is: {num_of_char}")
            print(f"Total words: {total_words}")
            print(f"Total lines: {total_lines}")

except FileNotFoundError:
    print(f"Error: The file {filename} was not found. Please check the spelling.")

except Exception as e:
    print(f"An unexpected error occurred: {e}")