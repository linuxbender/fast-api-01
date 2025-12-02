"""
Async/Await examples using standard Python libraries.
Demonstrates various asynchronous operations with time measurements.
"""

import asyncio
import time
from datetime import datetime
from typing import Any


class DemoAsync:
    """
    Class demonstrating various async/await patterns using standard Python libraries.

    This class provides examples of:
    - Parallel task execution
    - Sequential task execution
    - Data fetching simulation
    - Timeout handling
    - Processing tasks as they complete
    """

    @staticmethod
    def print_timestamp(label: str, start_time: float | None = None) -> float:
        """
        Print a timestamp with optional duration calculation.

        Args:
            label: Description of the timestamp.
            start_time: Optional start time for duration calculation.

        Returns:
            Current time as float.
        """
        current_time = time.time()
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        if start_time:
            duration = current_time - start_time
            print(f"[{timestamp}] {label} (Duration: {duration:.3f}s)")
        else:
            print(f"[{timestamp}] {label}")

        return current_time

    async def simple_async_task(self, task_name: str, sleep_duration: float) -> str:
        """
        Simple asynchronous task with sleep.

        Args:
            task_name: Name of the task.
            sleep_duration: Wait time in seconds.

        Returns:
            Task result as string.
        """
        start = self.print_timestamp(f"Start: {task_name}")

        await asyncio.sleep(sleep_duration)

        self.print_timestamp(f"End: {task_name}", start)
        return f"{task_name} completed after {sleep_duration}s"

    async def fetch_data_simulation(self, data_id: int) -> dict[str, Any]:
        """
        Simulate asynchronous data fetching (e.g., from an API).

        Args:
            data_id: ID of the data to fetch.

        Returns:
            Simulated data as dictionary.
        """
        start = self.print_timestamp(f"Fetching data {data_id}")

        # Simulate different loading times
        await asyncio.sleep(0.5 + (data_id % 3) * 0.3)

        self.print_timestamp(f"Data {data_id} fetched", start)

        return {
            "id": data_id,
            "data": f"Content_{data_id}",
            "timestamp": datetime.now().isoformat()
        }

    async def parallel_tasks_example(self) -> list[str]:
        """
        Example of parallel execution of multiple tasks.

        Returns:
            List of results.
        """
        print("\n" + "=" * 60)
        print("EXAMPLE 1: Parallel Tasks")
        print("=" * 60)

        start = self.print_timestamp("Start: Parallel tasks")

        # Create multiple tasks that run in parallel
        tasks = [
            self.simple_async_task("Task-A", 1.0),
            self.simple_async_task("Task-B", 1.5),
            self.simple_async_task("Task-C", 0.8),
        ]

        # Wait for all tasks simultaneously
        results = await asyncio.gather(*tasks)

        self.print_timestamp("End: All parallel tasks", start)
        print(f"Results: {results}")

        return results

    async def sequential_tasks_example(self) -> list[str]:
        """
        Example of sequential execution of tasks.

        Returns:
            List of results.
        """
        print("\n" + "=" * 60)
        print("EXAMPLE 2: Sequential Tasks")
        print("=" * 60)

        start = self.print_timestamp("Start: Sequential tasks")

        results = []
        results.append(await self.simple_async_task("Seq-Task-1", 0.5))
        results.append(await self.simple_async_task("Seq-Task-2", 0.5))
        results.append(await self.simple_async_task("Seq-Task-3", 0.5))

        self.print_timestamp("End: All sequential tasks", start)
        print(f"Results: {results}")

        return results

    async def fetch_multiple_data_example(self) -> list[dict[str, Any]]:
        """
        Example of parallel fetching from multiple data sources.

        Returns:
            List of fetched data.
        """
        print("\n" + "=" * 60)
        print("EXAMPLE 3: Parallel Data Fetching")
        print("=" * 60)

        start = self.print_timestamp("Start: Fetching data")

        # Create tasks for multiple data sources
        data_ids = [1, 2, 3, 4, 5]
        tasks = [self.fetch_data_simulation(data_id) for data_id in data_ids]

        # Fetch all data in parallel
        results = await asyncio.gather(*tasks)

        self.print_timestamp("End: All data fetched", start)
        print(f"Number of fetched records: {len(results)}")

        return results

    async def timeout_example(self) -> str | None:
        """
        Example of timeout handling.

        Returns:
            Result or None on timeout.
        """
        print("\n" + "=" * 60)
        print("EXAMPLE 4: Timeout Handling")
        print("=" * 60)

        start = self.print_timestamp("Start: Task with timeout")

        try:
            # Try task with 2 seconds timeout
            result = await asyncio.wait_for(
                self.simple_async_task("Timeout-Task", 3.0),
                timeout=2.0
            )
            self.print_timestamp("Task successful", start)
            return result
        except asyncio.TimeoutError:
            self.print_timestamp("Task cancelled (Timeout)", start)
            print("⚠️  Task took too long!")
            return None

    async def as_completed_example(self) -> list[dict[str, Any]]:
        """
        Example of as_completed - process results as soon as they are ready.

        Returns:
            List of results in order of completion.
        """
        print("\n" + "=" * 60)
        print("EXAMPLE 5: as_completed - Process tasks as they finish")
        print("=" * 60)

        start = self.print_timestamp("Start: as_completed")

        # Tasks with different durations
        tasks = [
            self.fetch_data_simulation(i)
            for i in [5, 2, 8, 1, 4]
        ]

        results = []
        # Process each result as soon as it's available
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            print(f"  → Result available: ID={result['id']}")

        self.print_timestamp("End: All tasks completed", start)

        return results

    async def task_with_exception_handling(self) -> list[Any]:
        """
        Example of exception handling with gather and return_exceptions.

        Returns:
            List of results and exceptions.
        """
        print("\n" + "=" * 60)
        print("EXAMPLE 6: Exception Handling in Parallel Tasks")
        print("=" * 60)

        start = self.print_timestamp("Start: Tasks with exceptions")

        async def failing_task(task_id: int) -> str:
            """Task that raises an exception."""
            await asyncio.sleep(0.3)
            raise ValueError(f"Task {task_id} failed intentionally")

        async def successful_task(task_id: int) -> str:
            """Task that completes successfully."""
            await asyncio.sleep(0.3)
            return f"Task {task_id} succeeded"

        # Run tasks and capture exceptions
        results = await asyncio.gather(
            successful_task(1),
            failing_task(2),
            successful_task(3),
            return_exceptions=True
        )

        self.print_timestamp("End: All tasks processed", start)

        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"  → Task {i}: Exception - {result}")
            else:
                print(f"  → Task {i}: {result}")

        return results

    async def run_all_examples(self) -> None:
        """
        Run all examples sequentially.
        """
        overall_start = self.print_timestamp("🚀 START: All Async Examples")

        await self.parallel_tasks_example()
        await self.sequential_tasks_example()
        await self.fetch_multiple_data_example()
        await self.timeout_example()
        await self.as_completed_example()
        await self.task_with_exception_handling()

        print("\n" + "=" * 60)
        self.print_timestamp("✅ END: All Async Examples", overall_start)
        print("=" * 60)


async def main_async() -> None:
    """
    Main async function to run the demos.
    """
    demo = DemoAsync()
    await demo.run_all_examples()


def main() -> None:
    """
    Main function that can be called from __main__.py.
    """
    print("\n🔄 Async/Await Demonstration with Standard Python Libraries\n")
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
