"""
Tests for the DemoAsync class.

Test suite covering all async/await examples including:
- Simple async tasks
- Parallel and sequential execution
- Data fetching simulation
- Timeout handling
- as_completed pattern
- Exception handling
"""

import asyncio
import time
from datetime import datetime

import pytest

from fastapi_01.DemoAsync import DemoAsync

# Configure pytest to use anyio for async tests
pytestmark = pytest.mark.anyio


@pytest.fixture
def demo_async() -> DemoAsync:
    """
    Fixture that provides a DemoAsync instance.

    Returns:
        DemoAsync: Instance of the DemoAsync class.
    """
    return DemoAsync()


class TestDemoAsync:
    """Test suite for DemoAsync class."""

    def test_print_timestamp_without_start_time_returns_float(self, demo_async: DemoAsync) -> None:
        """Test that print_timestamp returns a time without start time."""
        result = demo_async.print_timestamp("Test Label")
        assert isinstance(result, float)
        assert result > 0

    def test_print_timestamp_with_start_time_calculates_duration(self, demo_async: DemoAsync) -> None:
        """Test that print_timestamp calculates duration with start time."""
        start_time = time.time()
        time.sleep(0.1)
        result = demo_async.print_timestamp("Test Label", start_time)
        assert isinstance(result, float)
        assert result > start_time

    async def test_simple_async_task_completes_successfully(self, demo_async: DemoAsync) -> None:
        """Test that simple_async_task completes successfully."""
        task_name = "TestTask"
        sleep_duration = 0.1

        result = await demo_async.simple_async_task(task_name, sleep_duration)

        assert isinstance(result, str)
        assert task_name in result
        assert str(sleep_duration) in result

    async def test_simple_async_task_respects_sleep_duration(self, demo_async: DemoAsync) -> None:
        """Test that simple_async_task respects the given wait time."""
        sleep_duration = 0.2
        start = time.time()

        await demo_async.simple_async_task("TestTask", sleep_duration)

        elapsed = time.time() - start
        assert elapsed >= sleep_duration
        assert elapsed < sleep_duration + 0.1  # With some tolerance

    async def test_fetch_data_simulation_returns_dict(self, demo_async: DemoAsync) -> None:
        """Test that fetch_data_simulation returns a dictionary."""
        data_id = 42

        result = await demo_async.fetch_data_simulation(data_id)

        assert isinstance(result, dict)
        assert "id" in result
        assert "data" in result
        assert "timestamp" in result
        assert result["id"] == data_id

    async def test_fetch_data_simulation_has_valid_timestamp(self, demo_async: DemoAsync) -> None:
        """Test that fetch_data_simulation contains a valid timestamp."""
        result = await demo_async.fetch_data_simulation(1)

        # Try to parse the timestamp
        timestamp = datetime.fromisoformat(result["timestamp"])
        assert isinstance(timestamp, datetime)

    async def test_parallel_tasks_example_runs_tasks_concurrently(self, demo_async: DemoAsync) -> None:
        """Test that parallel_tasks_example executes tasks in parallel."""
        start = time.time()

        results = await demo_async.parallel_tasks_example()

        elapsed = time.time() - start
        # Parallel should take ~1.5s (longest task), not 3.3s (sum)
        assert elapsed < 2.0
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)

    async def test_sequential_tasks_example_runs_tasks_sequentially(self, demo_async: DemoAsync) -> None:
        """Test that sequential_tasks_example executes tasks one after another."""
        start = time.time()

        results = await demo_async.sequential_tasks_example()

        elapsed = time.time() - start
        # Sequential should take ~1.5s (3 * 0.5s)
        assert elapsed >= 1.4
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)

    async def test_fetch_multiple_data_example_returns_list_of_dicts(self, demo_async: DemoAsync) -> None:
        """Test that fetch_multiple_data_example returns a list of dicts."""
        results = await demo_async.fetch_multiple_data_example()

        assert isinstance(results, list)
        assert len(results) == 5
        assert all(isinstance(item, dict) for item in results)
        assert all("id" in item for item in results)

    async def test_fetch_multiple_data_example_runs_in_parallel(self, demo_async: DemoAsync) -> None:
        """Test that fetch_multiple_data_example runs in parallel."""
        start = time.time()

        results = await demo_async.fetch_multiple_data_example()

        elapsed = time.time() - start
        # Parallel should be faster than sequential
        assert elapsed < 2.0  # For 5 tasks in parallel
        assert len(results) == 5

    async def test_timeout_example_catches_timeout(self, demo_async: DemoAsync) -> None:
        """Test that timeout_example catches timeouts."""
        result = await demo_async.timeout_example()

        # Task should timeout and return None
        assert result is None

    async def test_timeout_example_completes_within_timeout(self, demo_async: DemoAsync) -> None:
        """Test that a task completes successfully if it's fast enough."""
        start = time.time()

        # Create a task that completes within the timeout
        try:
            result = await asyncio.wait_for(
                demo_async.simple_async_task("FastTask", 0.5),
                timeout=1.0
            )
            elapsed = time.time() - start

            assert result is not None
            assert elapsed < 1.0
        except asyncio.TimeoutError:
            pytest.fail("Task should not timeout with sufficient time")

    async def test_as_completed_example_returns_results(self, demo_async: DemoAsync) -> None:
        """Test that as_completed_example returns results."""
        results = await demo_async.as_completed_example()

        assert isinstance(results, list)
        assert len(results) == 5
        assert all(isinstance(item, dict) for item in results)

    async def test_as_completed_example_processes_as_completed(self, demo_async: DemoAsync) -> None:
        """Test that as_completed_example processes tasks in completion order."""
        results = await demo_async.as_completed_example()

        # Check that we have all expected IDs
        ids = [r["id"] for r in results]
        expected_ids = {1, 2, 4, 5, 8}
        assert set(ids) == expected_ids

    async def test_task_with_exception_handling_returns_results_and_exceptions(
        self, demo_async: DemoAsync
    ) -> None:
        """Test that task_with_exception_handling captures both results and exceptions."""
        results = await demo_async.task_with_exception_handling()

        assert isinstance(results, list)
        assert len(results) == 3

        # Check that first and third are strings (successful tasks)
        assert isinstance(results[0], str)
        assert isinstance(results[2], str)

        # Check that second is an exception (failing task)
        assert isinstance(results[1], Exception)

    async def test_task_with_exception_handling_has_correct_messages(
        self, demo_async: DemoAsync
    ) -> None:
        """Test that task_with_exception_handling has correct success and error messages."""
        results = await demo_async.task_with_exception_handling()

        assert "Task 1 succeeded" in results[0]
        assert "Task 2 failed intentionally" in str(results[1])
        assert "Task 3 succeeded" in results[2]

    async def test_run_all_examples_completes_successfully(self, demo_async: DemoAsync) -> None:
        """Test that run_all_examples executes all examples successfully."""
        start = time.time()

        # Should run without exception
        await demo_async.run_all_examples()

        elapsed = time.time() - start
        # All examples should take several seconds total
        assert elapsed > 5.0  # At least a few seconds
        assert elapsed < 15.0  # But not too long


async def test_multiple_tasks_can_run_concurrently() -> None:
    """Test that multiple tasks really run in parallel."""

    async def task(duration: float) -> float:
        """Simple task with sleep."""
        await asyncio.sleep(duration)
        return duration

    start = time.time()
    results = await asyncio.gather(
        task(0.1),
        task(0.1),
        task(0.1)
    )
    elapsed = time.time() - start

    # If parallel: ~0.1s, if sequential: ~0.3s
    assert elapsed < 0.2
    assert len(results) == 3


async def test_asyncio_gather_with_exception_handling() -> None:
    """Test that asyncio.gather works with return_exceptions."""

    async def failing_task() -> str:
        """Task that raises an exception."""
        await asyncio.sleep(0.1)
        raise ValueError("Test Error")

    async def successful_task() -> str:
        """Task that completes successfully."""
        await asyncio.sleep(0.1)
        return "Success"

    results = await asyncio.gather(
        successful_task(),
        failing_task(),
        return_exceptions=True
    )

    assert len(results) == 2
    assert results[0] == "Success"
    assert isinstance(results[1], ValueError)


async def test_asyncio_wait_for_timeout() -> None:
    """Test that asyncio.wait_for raises TimeoutError correctly."""

    async def slow_task() -> str:
        """Task that takes longer than timeout."""
        await asyncio.sleep(2.0)
        return "Done"

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_task(), timeout=0.5)


async def test_asyncio_as_completed_processes_in_order() -> None:
    """Test that as_completed yields results as they complete."""

    async def task_with_delay(task_id: int, delay: float) -> tuple[int, float]:
        """Task with specified delay."""
        await asyncio.sleep(delay)
        return task_id, delay

    tasks = [
        task_with_delay(1, 0.3),
        task_with_delay(2, 0.1),
        task_with_delay(3, 0.2),
    ]

    results = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)

    # Task 2 should finish first (0.1s), then 3 (0.2s), then 1 (0.3s)
    assert len(results) == 3
    assert results[0][0] == 2  # First to complete
    assert results[1][0] == 3  # Second to complete
    assert results[2][0] == 1  # Last to complete

