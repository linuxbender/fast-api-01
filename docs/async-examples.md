# DemoAsync - Async/Await Examples

Comprehensive examples for asynchronous programming in Python with `asyncio`.

## Overview

The `DemoAsync` class demonstrates various async/await patterns using standard Python libraries:

- ✅ Parallel task execution with `asyncio.gather()`
- ✅ Sequential task execution with `await`
- ✅ Simulating data fetching (e.g., API calls)
- ✅ Timeout handling with `asyncio.wait_for()`
- ✅ Processing with `asyncio.as_completed()`
- ✅ Exception handling in parallel tasks

## Usage

### Run All Examples

```bash
# Run directly
uv run python src/fastapi_01/DemoAsync.py

# Or via main module
uv run python -m fastapi_01
```

### Use Individual Examples

```python
import asyncio
from fastapi_01.DemoAsync import DemoAsync

async def main():
    demo = DemoAsync()
    
    # Parallel tasks
    results = await demo.parallel_tasks_example()
    
    # Sequential tasks
    results = await demo.sequential_tasks_example()
    
    # Fetch data in parallel
    data = await demo.fetch_multiple_data_example()
    
    # Timeout handling
    result = await demo.timeout_example()
    
    # as_completed pattern
    results = await demo.as_completed_example()
    
    # Exception handling
    results = await demo.task_with_exception_handling()

# Execute
asyncio.run(main())
```

## Examples in Detail

### 1. Parallel Tasks

```python
async def parallel_example():
    demo = DemoAsync()
    # These tasks run in parallel (not sequentially!)
    results = await asyncio.gather(
        demo.simple_async_task("Task-A", 1.0),
        demo.simple_async_task("Task-B", 1.5),
        demo.simple_async_task("Task-C", 0.8),
    )
    # Duration: ~1.5s (longest task), not 3.3s (sum)
```

### 2. Sequential Tasks

```python
async def sequential_example():
    demo = DemoAsync()
    # These tasks run one after another
    result1 = await demo.simple_async_task("Task-1", 0.5)
    result2 = await demo.simple_async_task("Task-2", 0.5)
    result3 = await demo.simple_async_task("Task-3", 0.5)
    # Duration: ~1.5s (0.5 + 0.5 + 0.5)
```

### 3. Timeout Handling

```python
async def timeout_example():
    try:
        result = await asyncio.wait_for(
            long_running_task(),
            timeout=2.0
        )
    except asyncio.TimeoutError:
        print("Task took too long!")
```

### 4. as_completed Pattern

```python
async def as_completed_example():
    tasks = [fetch_data(i) for i in range(5)]
    
    # Process results as soon as they're available
    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(f"Result available: {result}")
```

### 5. Exception Handling

```python
async def exception_handling_example():
    # Execute tasks and catch exceptions
    results = await asyncio.gather(
        successful_task(),
        failing_task(),
        another_task(),
        return_exceptions=True  # Important!
    )
    
    for result in results:
        if isinstance(result, Exception):
            print(f"Error: {result}")
        else:
            print(f"Success: {result}")
```

## Time Measurements

All examples show start and end times with millisecond precision:

```
[14:23:45.123] Start: Parallel Tasks
[14:23:45.123] Start: Task-A
[14:23:45.124] Start: Task-B
[14:23:45.124] Start: Task-C
[14:23:45.924] End: Task-C (Duration: 0.800s)
[14:23:46.125] End: Task-A (Duration: 1.001s)
[14:23:46.625] End: Task-B (Duration: 1.501s)
[14:23:46.625] End: Parallel Tasks (Duration: 1.502s)
```

## Run Tests

```bash
# All tests
uv run pytest tests/test_demo_async.py -v

# With coverage
uv run pytest tests/test_demo_async.py --cov=fastapi_01.DemoAsync --cov-report=term

# Specific test
uv run pytest tests/test_demo_async.py::TestDemoAsync::test_parallel_tasks_example_runs_tasks_concurrently -v
```

**Test Coverage: 94%** ✅

## Important Concepts

### asyncio.gather() vs await

- **`asyncio.gather()`**: Executes tasks in parallel
- **`await`**: Waits for one task to complete before starting the next (sequential)

```python
# Parallel (fast)
results = await asyncio.gather(task1(), task2(), task3())

# Sequential (slow)
result1 = await task1()
result2 = await task2()
result3 = await task3()
```

### When to Use Async?

✅ **Good for:**
- I/O-bound operations (network, files, databases)
- Multiple external API calls
- Waiting for multiple resources concurrently

❌ **Not good for:**
- CPU-intensive computations (use `multiprocessing` instead)
- Code without any async operations

## Best Practices

1. **Use Type Hints**: All functions have complete type hints
2. **Docstrings**: All public functions are documented
3. **Error Handling**: Use `return_exceptions=True` with `gather()`
4. **Timeouts**: Set timeouts for external operations
5. **Testing**: Test async code with `pytest-anyio` or `pytest-asyncio`

## Further Resources

- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)
- [FastAPI Async Tutorial](https://fastapi.tiangolo.com/async/)

