# ABC provides the base for abstract classes; abstractmethod marks methods
# that subclasses MUST implement
from abc import ABC, abstractmethod

# Type hints: Any = any type, List = list, Dict = dictionary,
# Union = one of several types, Optional = value or None
from typing import Any, List, Dict, Union, Optional


# Abstract base class - defines the blueprint all processors must follow.
# Any class that inherits from DataProcessor must implement process() and validate()
class DataProcessor(ABC):

    # Subclasses MUST override this - defines how data gets processed
    @abstractmethod
    def process(self, data: Any) -> Union[str, Dict[str, Any]]:
        pass

    # Subclasses MUST override this - defines what counts as valid input
    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    # Shared helper: converts result to a string.
    # If result is a dict, convert it; otherwise return it as-is
    def format_output(self, result: Union[str, Dict[str, Any]]) -> str:
        if isinstance(result, dict):
            return str(result)
        return result

    # Default validation message - subclasses can override with specific messages
    def validation(self) -> str:
        return "data verified"


# Handles lists of numbers (ints or floats)
class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        return (
            # Check if the input is actually a list
            isinstance(data, list)
            # Check if the list is not empty
            and len(data) > 0
            # Check every item in the list is either an int or float
            and all(isinstance(x, (int, float)) for x in data)
        )

    def process(self, data: Any) -> Optional[str]:
        # Store computed stats in a dict for clean organisation
        stats: Dict[str, Any] = {
            "count": len(data),           # how many numbers
            "total": sum(data),           # sum of all numbers
            "avg": sum(data) / len(data)  # average value
        }
        # Format stats into a readable output string (avg rounded to 1 decimal)
        return (f"Processed {stats['count']} numeric values, "
                f"sum={stats['total']}, avg={stats['avg']:.1f}")

    # Override base validation message with a numeric-specific one
    def validation(self) -> str:
        return "Numeric data verified"


# Handles plain text strings
class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        return (
            # Must be a string
            isinstance(data, str)
            # Must not be empty
            and len(data) > 0
        )

    def process(self, data: Any) -> Optional[str]:
        char_len = len(data)          # total number of characters
        count_words = len(data.split())  # split on spaces to count words
        return (f"Processed text: {char_len} characters, "
                f"{count_words} words")

    def validation(self) -> str:
        return "Text data verified"


# Handles log strings formatted as "LEVEL: message" (e.g. "ERROR: disk full")
class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        return (
            # Must be a string
            isinstance(data, str)
            # Must not be empty
            and len(data) > 0
            # Must contain ':' to be a valid log format
            and ":" in data
        )

    def process(self, data: Any) -> Optional[str]:
        # Split on ':' to separate log level from message
        alert = data.split(":")
        # Assign prefix based on severity level
        if alert[0] == "ERROR":
            prefix = "[ALERT]"   # critical issue
        else:
            prefix = "[INFO]"    # informational message
        # strip() removes any leading/trailing whitespace from the message
        return (f"{prefix} {alert[0]} level detected: {alert[1].strip()}")

    def validation(self) -> str:
        return "Log entry verified"


def main() -> None:
    print("=== CODE NEXUS- DATA PROCESSOR FOUNDATION ===")
    print()

    # Create one instance of each processor type
    processors: List[DataProcessor] = [
        NumericProcessor(),
        TextProcessor(),
        LogProcessor(),
    ]

    # Each item matches the processor at the same position above
    data_set: List[Any] = [
        [1, 2, 3, 4, 5],          # for NumericProcessor
        "Hello Nexus World",       # for TextProcessor
        "ERROR: Connection timout" # for LogProcessor
    ]

    # zip() pairs each processor with its matching data item
    for processor, data in zip(processors, data_set):
        try:
            # Get the class name as a string (e.g. "NumericProcessor")
            name = type(processor).__name__
            print(f"Initializing {name}...")

            print(f'Processing "data: {data}"')
            # Only process if the data passes validation
            if processor.validate(data):
                print(f"Validation: {processor.validation()}")
                result = processor.process(data)
            # Guard against None before printing
            if result is not None:
                print(f"Output: {result}")
            print()
        except Exception as e:
            # Catch any unexpected errors and report which processor failed
            print(f"Processing Error in {type(processor).__name__}: {e}")

    # Second demo dataset to show polymorphism
    # (same interface, different data types)
    data_demo: List[Any] = [
        [1, 2, 3],
        "Hello Nexus!s",
        "INFO: System ready"
    ]
    print("=== Polymorphic Processing Demo ===")
    print("Processing multiple data types through same interface...")
    # enumerate(..., 1) gives a counter starting at 1 alongside each item
    for i, (processor, data) in enumerate(zip(processors, data_demo), 1):
        try:
            result = processor.process(data)
            # format_output ensures result is always a string before printing
            formatted = processor.format_output(result)
            print(f"Result {i}: {formatted}")
        except Exception as e:
            print(f"Result: Error - {e}")
    print()
    print("Foundation systems online. Nexus ready for advanced streams.")


# Only run main() when this file is executed directly,
# not when it is imported as a module into another file
if __name__ == "__main__":
    main()
