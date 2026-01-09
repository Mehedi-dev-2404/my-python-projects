with open('text.txt', 'r') as file:
    data = file.read()
    words = data.split()

    num_of_char = len(data)
    total_words = len(words)


print(f"The total number of characters is: {num_of_char}")
print(f"Total words: {total_words}")
