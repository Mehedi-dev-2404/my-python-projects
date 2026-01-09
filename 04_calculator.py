### There will be 2 inputs 
# a user inputs the numbers first and then it will ask them what operator they want and the calculation will be performed
# each operation will have its own function to perform the action

print("WELCOME TO YOUR CALCULATOR APP")
num1 = 0
num2 = 0

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
def power(num1, num2):
    result = num1 ** num2
    return result
def modulo(num1, num2):
    result = num1 % num2
    return result

while True:
    try:
        num1 = float(input("Enter your number 1: "))
        num2 = float(input("Enter your number 2: "))
    except ValueError:
        print("Input must be a number")
        continue

    print("Enter the number of the operation you want:")
    print("1. Addition") 
    print("2. Subtraction")
    print("3. Division" )
    print("4. Multiplication")
    print("5. Power")
    print("6. Modulo")
    print("0. Exit Application")

    try:
        operation = int(input("Enter the number of the operation you want to perform: "))
    except ValueError:
        print("Input must be from 1-4 ")
        continue

    if operation == 1:
        result = add(num1, num2)
        print(result)
    elif operation == 2:
        result = subtract(num1, num2)
        print(result)
    elif operation == 3:
        if num2 != 0:
            result = divide(num1, num2)
            print(result)
        else:
            print("Cannot divide by zero")
            continue
    elif operation == 4:
        result = multiply(num1, num2)
        print(result)
    elif operation == 5:
        result = power(num1, num2)
        print(result)
    elif operation == 6:
        result = modulo(num1, num2)
        print(result)
    elif operation == 0:
        break
    else: 
        print("Invalid operation")
        continue
    selection = input("Do you want to continue (Y/N): ").upper
    if selection == "Y":
        continue
    else:
        print("Thank you for using the application")
        break
print("Thank you for using the application")