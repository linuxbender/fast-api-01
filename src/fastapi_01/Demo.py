Vector = list[int | float]


def main():
    """
    Main function to demonstrate basic addition operation.
    """

    a = 3
    b = 5
    c = 2.8

    print(f"""Hello this time we count: {a} + {b} = {add(a, b)}. 
          Nice!
          Have a nice day!
          """)

    print(f""" a+b = {add_with_default(a, b)} """)
    print(f""" a+b+c = {add_with_default(a, b, c)} """)
    print(f""" 1.5 * [2, 3, 4] = {scale(1.5, [2, 3, 4])} """)


def scale(scaler: float, vector: Vector) -> Vector:
    return [num * scaler for num in vector]


def add_with_default(a: int | float, b: int | float, c: int | float | None = None) -> int | float:
    """
    Add two or three numbers together and return the result.

    Args:
        a (Union[int, float]): The first number to add.
        b (Union[int, float]): The second number to add.
        c (Optional[Union[int, float]], optional): The third number to add. Defaults to None.

    Returns:
        Union[int, float]: The sum of the provided numbers.

    Example:
        >>> add_with_default(2, 3)
        5
        >>> add_with_default(2.5, 3.5, 1.0)
        7.0
    """

    if not c:
        return a + b
    return a + b + c


def add(a: int, b: int) -> int:
    """
    Add two integers together and return the result.
    Args:
        a (int): The first integer to add.
        b (int): The second integer to add.
    Returns:
        int: The sum of a and b.
    Example:
        >>> add(2, 3)
        5
    """
    return a + b


if __name__ == "__main__":
    main()
