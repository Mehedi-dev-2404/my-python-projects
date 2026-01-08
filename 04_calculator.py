### There will be 2 inputs 
# a user inputs the numbers first and then it will ask them what operator they want and the calculation will be performed
# each operation will have its own function to perform the action

print("WELCOME TO YOUR CALCULATOR APP")
num1 = float(input("Enter your number 1: "))
num2 = float(input("Enter your number 2: "))

print("Enter the number of the oparation you want:")
print("1. Addition") 
print("2. Subtraction")
print("3. Division" )
print("4. Multiplication")

def add(num1, num2):
    result = num1 + num2
    return result

def subtract(num1, num2):
    result = num1 - num2
    return result

def divide(num1, num2):
    result = num1 / num2
    return result

def multiply(num1, num2):
    result = num1 * num2
    return result

while True:
    try:
        operation = int(input("Enter the number of the operation you want to perform: "))
    except ValueError:
        print("Input must be from 1-4 ")
        continue

    if operation == 1:
        result = add(num1, num2)
        print(result)
        break
    elif operation == 2:
        result = subtract(num1, num2)
        print(result)
        break
    elif operation == 3:
        if num2 != 0:
            result = divide(num1, num2)
            print(result)
            break
        else:
            print("Infinite")
            break

    elif operation == 4:
        result = multiply(num1, num2)
        print(result)
        break
    else: 
        print("Invalid operation")
        continue