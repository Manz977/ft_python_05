
from abc import ABC, abstractmethod


from typing import Any, List, Dict, Union, Optional


class DataStream(ABC):
    def __init__(self, stream_id: str) -> None:
        self.stream_id = stream_id
        self.processed_count = 0

    @abstractmethod
    def process_batch(self, data_batch: List[Any]) -> str:
        pass

    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def format_input(self, data_batch: List[Any]) -> str:
        pass

    def _format_output(self, messgae: str) -> str:
        return f"[{self.stream_id}] {messgae}"

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None
    ) -> List[Any]:
        if criteria is None:
            return data_batch
        return [
            item for item in data_batch
            if criteria.lower() in str(item).lower()
        ]

    def get_stats(self) -> Dict[str, Union[str, int, float]]:
        return {"id": self.stream_id, "processed": self.processed_count}


class SensorStream(DataStream):
    def __init__(self, stream_id: str) -> None:
        super().__init__(stream_id)
        self.last_avg_temp: float = 0.0

    def type(self) -> str:
        return "Environmental Data"

    def format_input(self, data_batch: List[Any]) -> str:
        try:
            return (f"[temp:{data_batch[0]}, "
                    f"humidity:{data_batch[1]}, "
                    f"pressure:{data_batch[2]}]")
        except IndexError:
            return str(data_batch)

    def process_batch(self, data_batch: List[Any]) -> str:
        try:
            valid_readings = [
                reading for reading in data_batch
                if isinstance(reading, (int, float))
            ]

            self.processed_count += len(valid_readings)

            if not valid_readings:
                return "Sensor analysis: no valid readings"

            self.last_avg_temp = valid_readings[0]

            return (
                f"Sensor analysis: {len(valid_readings)} readings processed, "
                f"avg temp: {self.last_avg_temp}°C"
            )

        except Exception as e:
            return f"Sensor processing error: {str(e)}"

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None
    ) -> List[Any]:
        if criteria == "critical":
            return [
                reading for reading in data_batch
                if isinstance(reading, (int, float))
            ]
        return super().filter_data(data_batch, criteria)

    def get_stats(self) -> Dict[str, Union[str, int, float]]:
        stats = super().get_stats()
        stats["last_avg_temp"] = self.last_avg_temp
        return stats


class TransactionStream(DataStream):
    def __init__(self, stream_id: str) -> None:
        super().__init__(stream_id)
        self.net_flow: float = 0.0

    def type(self) -> str:
        return "Financial Data"

    def format_input(self, data_batch: List[Any]) -> str:
        parts = []
        for x in data_batch:
            label = "buy" if x > 0 else "sell"
            parts.append(f"{label}:{abs(x)}")
        return f"[{', '.join(parts)}]"

    def process_batch(self, data_batch: List[Any]) -> str:
        try:
            valid_transactions = [
                amount for amount in data_batch
                if isinstance(amount, (int, float))
            ]

            self.processed_count += len(valid_transactions)
            self.net_flow = sum(valid_transactions)

            return (
                f"Transaction analysis: {len(valid_transactions)} operations, "
                f"net flow: {self.net_flow:+g} units"
            )
        except Exception as e:
            return f"Transaction processing error: {str(e)}"

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None
    ) -> List[Any]:
        if criteria == "large":
            return [
                tx for tx in data_batch
                if isinstance(tx, (int, float)) and abs(tx) > 100
            ]
        return super().filter_data(data_batch, criteria)


class EventStream(DataStream):
    def __init__(self, stream_id: str) -> None:
        super().__init__(stream_id)
        self.error_count = 0

    def type(self) -> str:
        return "System Events"

    def format_input(self, data_batch: List[Any]) -> str:
        items = ", ".join(str(x) for x in data_batch)
        return f"[{items}]"

    def process_batch(self, data_batch: List[Any]) -> str:
        try:
            valid_events = [
                event for event in data_batch
                if isinstance(event, str)
            ]
            self.processed_count += len(valid_events)

            self.error_count = sum(
                1 for event in valid_events
                if "error" in event.lower()
            )
            return (
                f"Event analysis: {len(valid_events)} events, "
                f"{self.error_count} error detected"
            )
        except Exception as e:
            return f"Event processing error {str(e)}"

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None
    ) -> List[Any]:
        if criteria == "critical":
            return [
                event for event in data_batch
                if isinstance(event, str) and
                ("error" in event.lower() or "fail" in event.lower())
            ]
        return super().filter_data(data_batch, criteria)


class StreamProcessor:
    def __init__(self) -> None:
        self.streams: List[DataStream] = []

    def add_stream(self, stream: DataStream) -> None:
        if isinstance(stream, DataStream):
            self.streams.append(stream)

    def process_all(self, all_data: List[list[Any]]) -> None:
        print("\nBatch 1 Results:")
        for stream, batch in zip(self.streams, all_data):
            try:
                valid_items = [
                    item for item in batch
                    if isinstance(item, (int, float, str))
                ]
                count = len(valid_items)

                if isinstance(stream, SensorStream):
                    print(f"- Sensor data: {count} readings processed")
                elif isinstance(stream, TransactionStream):
                    print(f"- Transaction data: {count} operations processed")
                elif isinstance(stream, EventStream):
                    print(f"- Event data: {count} events processed")
            except Exception as e:
                print(f"Stream Failure ({stream.stream_id}): {str(e)}")

    def filter_all(
        self,
        all_data: List[List[Any]],
        criteria: Optional[str] = None
    ) -> List[List[Any]]:
        filtered_results = []

        for stream, batch in zip(self.streams, all_data):
            filtered = stream.filter_data(batch, criteria)
            filtered_results.append(filtered)

        return filtered_results


def main() -> None:
    print("=== CODE NEXUS- POLYMORPHIC STREAM SYSTEM ===")
    processor = StreamProcessor()

    scenarios = [
        (SensorStream, "SENSOR_001", [22.5, 65, 1013]),
        (TransactionStream, "TRANS_001", [100, -150, 75]),
        (EventStream, "EVENT_001", ["login", "error", "logout"])
    ]

    for stream_class, s_id, initial_batch in scenarios:
        stream = stream_class(s_id)
        processor.add_stream(stream)
        stream_name = stream_class.__name__.replace('Stream', '')

        print(
            f"\nInitializing {stream_name} Stream... "
            f"\nStream ID: {stream.stream_id}, Type: {stream.type()}"
        )

        print(
            f"Processing {stream_name.lower()} batch: "
            f"{stream.format_input(initial_batch)}"
        )

        result = stream.process_batch(initial_batch)
        print(result)

    mixed_batch = [
        [23.5, 60],
        [50, -20, 150, -10],
        ["login", "logout", "error"]
    ]

    print("\n=== Polymorphic Stream Processing ===")
    print("Processing mixed stream types through unified interface...")

    processor.process_all(mixed_batch)

    print("\nStream filtering active: High-priority data only")
    filtered = processor.filter_all(mixed_batch, "critical")

    sensor_critical = len(filtered[0])
    transaction_large = len(
        processor.streams[1].filter_data(mixed_batch[1], "large")
    )

    print(
        f"Filtered results: {sensor_critical} critical sensor alerts, "
        f"{transaction_large} large transaction"
    )
    print("\nAll streams processed successfully. Nexus throughput optimal.")


if __name__ == "__main__":
    main()
