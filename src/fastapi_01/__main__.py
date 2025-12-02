"""Main entry point for the application"""

from fastapi_01.Demo import main as demo_main
from fastapi_01.DemoAsync import main as demo_async_main


def main() -> None:
    """Run the demo"""
    # Choose which demo to run:

    # Synchronous demo
    # demo_main()

    # Asynchronous demo
    demo_async_main()


if __name__ == "__main__":
    main()
