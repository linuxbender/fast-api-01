# DemoAsync - Async/Await Examples

Umfassende Beispiele für asynchrone Programmierung in Python mit `asyncio`.

## Übersicht

Die `DemoAsync`-Klasse demonstriert verschiedene Async/Await-Patterns mit Standard-Python-Bibliotheken:

- ✅ Parallele Task-Ausführung mit `asyncio.gather()`
- ✅ Sequentielle Task-Ausführung mit `await`
- ✅ Simulation von Daten-Abrufen (z.B. API-Calls)
- ✅ Timeout-Handling mit `asyncio.wait_for()`
- ✅ Processing mit `asyncio.as_completed()`
- ✅ Exception-Handling in parallelen Tasks

## Verwendung

### Alle Beispiele ausführen

```bash
# Direkt ausführen
uv run python src/fastapi_01/DemoAsync.py

# Oder über das Hauptmodul
uv run python -m fastapi_01
```

### Einzelne Beispiele verwenden

```python
import asyncio
from fastapi_01.DemoAsync import DemoAsync

async def main():
    demo = DemoAsync()
    
    # Parallele Tasks
    results = await demo.parallel_tasks_example()
    
    # Sequentielle Tasks
    results = await demo.sequential_tasks_example()
    
    # Daten parallel abrufen
    data = await demo.fetch_multiple_data_example()
    
    # Timeout-Handling
    result = await demo.timeout_example()
    
    # as_completed Pattern
    results = await demo.as_completed_example()
    
    # Exception Handling
    results = await demo.task_with_exception_handling()

# Ausführen
asyncio.run(main())
```

## Beispiele im Detail

### 1. Parallele Tasks

```python
async def parallel_example():
    demo = DemoAsync()
    # Diese Tasks laufen parallel (nicht sequentiell!)
    results = await asyncio.gather(
        demo.simple_async_task("Task-A", 1.0),
        demo.simple_async_task("Task-B", 1.5),
        demo.simple_async_task("Task-C", 0.8),
    )
    # Dauer: ~1.5s (längste Task), nicht 3.3s (Summe)
```

### 2. Sequentielle Tasks

```python
async def sequential_example():
    demo = DemoAsync()
    # Diese Tasks laufen nacheinander
    result1 = await demo.simple_async_task("Task-1", 0.5)
    result2 = await demo.simple_async_task("Task-2", 0.5)
    result3 = await demo.simple_async_task("Task-3", 0.5)
    # Dauer: ~1.5s (0.5 + 0.5 + 0.5)
```

### 3. Timeout-Handling

```python
async def timeout_example():
    try:
        result = await asyncio.wait_for(
            long_running_task(),
            timeout=2.0
        )
    except asyncio.TimeoutError:
        print("Task hat zu lange gedauert!")
```

### 4. as_completed Pattern

```python
async def as_completed_example():
    tasks = [fetch_data(i) for i in range(5)]
    
    # Verarbeite Ergebnisse sobald sie verfügbar sind
    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(f"Ergebnis verfügbar: {result}")
```

### 5. Exception Handling

```python
async def exception_handling_example():
    # Führe Tasks aus und fange Exceptions ab
    results = await asyncio.gather(
        successful_task(),
        failing_task(),
        another_task(),
        return_exceptions=True  # Wichtig!
    )
    
    for result in results:
        if isinstance(result, Exception):
            print(f"Fehler: {result}")
        else:
            print(f"Erfolg: {result}")
```

## Zeit-Messungen

Alle Beispiele zeigen Start- und Endzeiten mit Millisekunden-Präzision:

```
[14:23:45.123] Start: Parallele Tasks
[14:23:45.123] Start: Task-A
[14:23:45.124] Start: Task-B
[14:23:45.124] Start: Task-C
[14:23:45.924] Ende: Task-C (Duration: 0.800s)
[14:23:46.125] Ende: Task-A (Duration: 1.001s)
[14:23:46.625] Ende: Task-B (Duration: 1.501s)
[14:23:46.625] Ende: Parallele Tasks (Duration: 1.502s)
```

## Tests ausführen

```bash
# Alle Tests
uv run pytest tests/test_demo_async.py -v

# Mit Coverage
uv run pytest tests/test_demo_async.py --cov=fastapi_01.DemoAsync --cov-report=term

# Spezifischer Test
uv run pytest tests/test_demo_async.py::TestDemoAsync::test_parallel_tasks_example_runs_tasks_concurrently -v
```

**Test-Coverage: 94%** ✅

## Wichtige Konzepte

### asyncio.gather() vs await

- **`asyncio.gather()`**: Führt Tasks parallel aus
- **`await`**: Wartet auf eine Task bevor die nächste startet (sequentiell)

```python
# Parallel (schnell)
results = await asyncio.gather(task1(), task2(), task3())

# Sequentiell (langsam)
result1 = await task1()
result2 = await task2()
result3 = await task3()
```

### Wann Async verwenden?

✅ **Gut für:**
- I/O-gebundene Operationen (Netzwerk, Dateien, Datenbanken)
- Mehrere externe API-Calls
- Gleichzeitiges Warten auf mehrere Ressourcen

❌ **Nicht gut für:**
- CPU-intensive Berechnungen (verwende `multiprocessing` stattdessen)
- Code der keine async-Operationen hat

## Best Practices

1. **Verwende Type Hints**: Alle Funktionen haben vollständige Type Hints
2. **Docstrings**: Alle öffentlichen Funktionen sind dokumentiert
3. **Error Handling**: Verwende `return_exceptions=True` bei `gather()`
4. **Timeouts**: Setze Timeouts für externe Operationen
5. **Testing**: Teste async Code mit `pytest-anyio` oder `pytest-asyncio`

## Weitere Ressourcen

- [Python asyncio Dokumentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)
- [FastAPI Async Tutorial](https://fastapi.tiangolo.com/async/)

