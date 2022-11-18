
import random

numbers = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100)

def rand_number(n=6):
    return random.choices(numbers, k=n)

def rand_target():
    return random.randrange(100, 1000)

if __name__ == "__main__":
    print(rand_number())

    print(rand_target())
