def main():
    print("Hello World with my uv setup")

    a = 3
    b = 5

    print(f"""

        Hello this time we count: {a} + {b} = {add(a, b)}.

        Nice!

        Have a nice day!
          
          """)


def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    main()
