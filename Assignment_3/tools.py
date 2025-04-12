from datetime import datetime
from functools import reduce
import operator
import math


def count_vowels(sentence: str) -> int:
    """
    Count the number of vowels in the given sentence.

    Parameters:
    -----------
    sentence : str
        The sentence in which vowels need to be counted.

    Returns:
    --------
    int
        The total number of vowels (a, e, i, o, u) in the sentence.
    """
    vowels = "aeiouAEIOU"
    count = sum(1 for char in sentence if char in vowels)
    return count

def compute_factorial(n: int) -> int:
    """
    Compute the factorial of a non-negative integer n.

    Parameters:
    -----------
    n : int
        The number for which to compute the factorial. Must be >= 0.

    Returns:
    --------
    int
        The factorial of the input number n.

    Raises:
    -------
    ValueError
        If n is negative.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def get_today_day() -> int:
    """
    Get today's date as the day of the month (1–31).

    Returns:
    --------
    int
        The current day of the month.
    """
    today = datetime.now()
    return today.day

def get_current_hour() -> int:
    """
    Get the current hour of the day in 24-hour format (0–23).

    Returns:
    --------
    int
        The current hour.
    """
    now = datetime.now()
    return now.hour

def compute_a_squared_minus_b_cubed(a: int, b: int) -> int:
    """
    Compute the result of (a^2 - b^3).

     Parameters:
    -----------
    a : int
        Any integer
    b : int
        Any integer

    Returns:
    --------
    int
        The result of the calculation.
    """
    result = (a ** 2) - (b ** 3)
    return result

def split_number_into_digits(number: int) -> list:
    """
    Split a number into its individual digits.

    Parameters:
    -----------
    number : int
        The number to split into digits.

    Returns:
    --------
    list
        A list of individual digits (as integers).
    """
    return [int(digit) for digit in str(abs(number))]

def square_numbers_in_list(numbers: list) -> list:
    """
    Square each number in the given list.

    Parameters:
    -----------
    numbers : list
        A list of integers.

    Returns:
    --------
    list
        A new list containing the square of each number.
    """
    return [num ** 2 for num in numbers]

def sum_numbers_in_list(numbers: list) -> int:
    """
    Calculate the sum of all numbers in the given list.

    Parameters:
    -----------
    numbers : list
        A list of integers or floats.

    Returns:
    --------
    int
        The total sum of the elements in the list.
    """
    return sum(numbers)

def convert_string_to_ascii(text: str) -> list:
    """
    Convert each character in the input string to its ASCII value.

    Parameters:
    -----------
    text : str
        The string whose characters will be converted.

    Returns:
    --------
    list
        A list of ASCII values corresponding to each character in the input string.
    """
    return [ord(char) for char in text]

def multiply_list_elements(numbers: list) -> int:
    """
    Multiply all the elements in the given list.

    Parameters:
    -----------
    numbers : list
        A list of integers or floats.

    Returns:
    --------
    int
        The product of all elements in the list.
    """
    return reduce(operator.mul, numbers, 1)

def compute_log2(number: int) -> float:
    """
    Compute the base-2 logarithm (log₂) of a positive integer.

    Parameters:
    -----------
    number : int
        The number for which to compute log base 2. Must be > 0.

    Returns:
    --------
    float
        The log base 2 of the input number.

    Raises:
    -------
    ValueError
        If the input number is less than or equal to 0.
    """
    if number <= 0:
        raise ValueError("log2 is undefined for non-positive numbers.")
    return math.log2(number)
