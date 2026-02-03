"""Pytest configuration and fixtures."""

import pytest
import asyncio
from pathlib import Path
from typing import AsyncGenerator

# Configure pytest-asyncio
pytest_plugins = ['pytest_asyncio']


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_flowchart_code() -> str:
    """Sample flowchart Mermaid code."""
    return """graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B
    C --> E[End]"""


@pytest.fixture
def sample_sequence_code() -> str:
    """Sample sequence diagram Mermaid code."""
    return """sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I'm good thanks!"""


@pytest.fixture
def sample_class_code() -> str:
    """Sample class diagram Mermaid code."""
    return """classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()"""


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """Temporary output directory for tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temp_diagrams_dir(tmp_path) -> Path:
    """Temporary diagrams directory for tests."""
    diagrams_dir = tmp_path / "diagrams"
    diagrams_dir.mkdir()
    return diagrams_dir
