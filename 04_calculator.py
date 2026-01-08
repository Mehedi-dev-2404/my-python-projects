### There will be 2 inputs 
# a user inputs the numbers first and then it will ask them what operator they want and the calculation will be performed
# each operation will have its own function to perform the action

print("WELCOME TO YOUR CALCULATOR APP")
num1 = float(input("Enter your number 1: "))
num2 = float(input("Enter your number 2: "))

print("Enter the number of the oparation you want:"
"1. Addition" \
"2. Subtraction" \
"3. Division" \
"4. Multiplication")
while True:
    operation = int(input("Enter the number of the operation you want to perform: "))

    if operation == 1:
        cal = num1 + num2
        print(cal)
        break
    elif operation == 2:
        cal = num1 - num2
        print(cal)
        break
    elif operation == 3:
        cal = num1 / num2
        print(cal)
        break
    elif operation == 4:
        cal = num1 * num2
        print(cal)
        break
    else: 
        print("Invalid operation")
        continue