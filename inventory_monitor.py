
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class Availability(Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    UNKNOWN = "unknown"


@dataclass
class Product:
    tcin: str
    name: str
    url: str


@dataclass
class InventoryResult:
    product: Product
    availability: Availability
    checked_at: datetime
    source: str


PRODUCT = Product(
    tcin="95271190",
    name="NeeDoh Ginger Glowman",
    url="https://www.target.com/p/needoh-ginger-glowman-fidget-toy/-/A-95271190"
)


def detect_restock(previous, current):

    if previous is None:
        return False

    return (
        previous == Availability.OUT_OF_STOCK
        and current == Availability.IN_STOCK
    )


def process_inventory(result, previous):

    print(f"\nProduct: {result.product.name}")
    print(f"TCIN: {result.product.tcin}")
    print(f"Source: {result.source}")
    print(f"Availability: {result.availability.value}")
    print(f"Checked: {result.checked_at.isoformat()}")

    if detect_restock(previous, result.availability):
        print("\n*** RESTOCK DETECTED ***")
        print(result.product.url)

    return result.availability


if __name__ == "__main__":

    print("GingerGlowmanBot inventory engine initialized.")

    print(f"Monitoring product: {PRODUCT.name}")
    print(f"TCIN: {PRODUCT.tcin}")
    print("Waiting for an authorized inventory provider.")
