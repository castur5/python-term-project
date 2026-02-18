"""
Term Project: Network Inventory & Subnet Planner (CLI)

What it does:
- Maintain a small IT/network inventory (devices, IPs, locations, owners, notes)
- Validate IP addresses
- Plan subnets using CIDR notation (e.g., 10.0.10.0/24)
- Export inventory to CSV
- Persist data to a JSON file between runs

No external libraries required (standard library only).
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from ipaddress import ip_address, ip_network
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DATA_FILE = Path("inventory.json")
EXPORT_FILE = Path("inventory_export.csv")


# -----------------------------
# Data Model
# -----------------------------
@dataclass
class Device:
    device_id: str
    name: str
    device_type: str
    ip: str
    location: str
    owner: str
    status: str
    notes: str
    created_at: str  # ISO timestamp


# -----------------------------
# Persistence Functions (Top-Level)
# -----------------------------
def load_data(file_path: Path = DATA_FILE) -> List[Device]:
    """Load inventory data from JSON; return an empty list if file doesn't exist."""
    if not file_path.exists():
        return []
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
        return [Device(**item) for item in raw]
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"\n[ERROR] Could not read {file_path.name}: {exc}")
        print("Starting with an empty inventory.\n")
        return []


def save_data(devices: List[Device], file_path: Path = DATA_FILE) -> None:
    """Save inventory data to JSON."""
    payload = [asdict(d) for d in devices]
    file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def export_to_csv(devices: List[Device], file_path: Path = EXPORT_FILE) -> None:
    """Export inventory to CSV."""
    if not devices:
        print("\nNothing to export (inventory is empty).\n")
        return

    fieldnames = list(asdict(devices[0]).keys())
    with file_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for d in devices:
            writer.writerow(asdict(d))

    print(f"\nExported {len(devices)} device(s) to {file_path.name}\n")


# -----------------------------
# Utility / Validation (Top-Level)
# -----------------------------
def validate_ip(ip_text: str) -> bool:
    """Return True if ip_text is a valid IPv4 or IPv6 address."""
    try:
        ip_address(ip_text)
        return True
    except ValueError:
        return False


def generate_device_id(devices: List[Device]) -> str:
    """Generate a simple unique ID like DEV-0007."""
    existing_nums = []
    for d in devices:
        if d.device_id.startswith("DEV-"):
            try:
                existing_nums.append(int(d.device_id.split("-")[1]))
            except (IndexError, ValueError):
                pass
    next_num = (max(existing_nums) + 1) if existing_nums else 1
    return f"DEV-{next_num:04d}"


def prompt_nonempty(label: str) -> str:
    """Prompt until user enters a non-empty value."""
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("  Please enter a value.")


def prompt_choice(label: str, choices: List[str]) -> str:
    """Prompt until input matches one of choices (case-insensitive)."""
    normalized = {c.lower(): c for c in choices}
    while True:
        value = input(f"{label} {choices}: ").strip().lower()
        if value in normalized:
            return normalized[value]
        print(f"  Please choose one of: {', '.join(choices)}")


# -----------------------------
# Feature Functions (Top-Level)
# -----------------------------
def add_device(devices: List[Device]) -> None:
    """Add a device record to inventory."""
    print("\nAdd New Device")
    name = prompt_nonempty("Device name")
    device_type = prompt_choice("Device type", ["Laptop", "Desktop", "Server", "Router", "Switch", "AP", "Printer", "Other"])

    while True:
        ip = prompt_nonempty("IP address (IPv4/IPv6)")
        if validate_ip(ip):
            break
        print("  Invalid IP address. Example: 192.168.1.10 or 2001:db8::1")

    location = prompt_nonempty("Location (e.g., Minneapolis HQ, Seattle Branch)")
    owner = prompt_nonempty("Owner / primary user")
    status = prompt_choice("Status", ["Active", "Spare", "Repair", "Retired"])
    notes = input("Notes (optional): ").strip()

    device_id = generate_device_id(devices)
    created_at = datetime.now().isoformat(timespec="seconds")

    devices.append(
        Device(
            device_id=device_id,
            name=name,
            device_type=device_type,
            ip=ip,
            location=location,
            owner=owner,
            status=status,
            notes=notes,
            created_at=created_at,
        )
    )
    print(f"\nAdded device {device_id}.\n")


def list_devices(devices: List[Device], *, only_active: bool = False) -> None:
    """Display devices in a simple table-like output."""
    filtered = [d for d in devices if (d.status == "Active" or not only_active)]

    if not filtered:
        print("\nNo devices found.\n")
        return

    print("\nInventory")
    print("-" * 95)
    print(f"{'ID':<10} {'Name':<18} {'Type':<10} {'IP':<18} {'Location':<18} {'Status':<8}")
    print("-" * 95)
    for d in filtered:
        print(f"{d.device_id:<10} {d.name[:18]:<18} {d.device_type:<10} {d.ip[:18]:<18} {d.location[:18]:<18} {d.status:<8}")
    print("-" * 95)
    print(f"Total shown: {len(filtered)} (Total in inventory: {len(devices)})\n")


def find_device(devices: List[Device]) -> Optional[Device]:
    """Search by device ID or keyword; return a single selected device if found."""
    if not devices:
        print("\nInventory is empty.\n")
        return None

    query = input("\nSearch (device ID like DEV-0001 or keyword): ").strip().lower()
    matches = []
    for d in devices:
        haystack = f"{d.device_id} {d.name} {d.device_type} {d.ip} {d.location} {d.owner} {d.status} {d.notes}".lower()
        if query in haystack:
            matches.append(d)

    if not matches:
        print("No matches.\n")
        return None

    if len(matches) == 1:
        return matches[0]

    print("\nMatches:")
    for i, d in enumerate(matches, start=1):
        print(f"  {i}) {d.device_id} | {d.name} | {d.device_type} | {d.ip} | {d.location} | {d.status}")

    while True:
        choice = input("Select a number (or press Enter to cancel): ").strip()
        if choice == "":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            return matches[int(choice) - 1]
        print("  Invalid selection.")


def update_or_retire_device(devices: List[Device]) -> None:
    """Update a device's status/notes, or retire it."""
    target = find_device(devices)
    if not target:
        return

    print("\nSelected:")
    print_device_details(target)

    action = prompt_choice("Action", ["Update", "Retire", "Cancel"])
    if action == "Cancel":
        print()
        return

    if action == "Retire":
        target.status = "Retired"
        print(f"\n{target.device_id} marked as Retired.\n")
        return

    # Update
    print("\nLeave any field blank to keep current value.\n")

    new_owner = input(f"Owner [{target.owner}]: ").strip()
    if new_owner:
        target.owner = new_owner

    new_location = input(f"Location [{target.location}]: ").strip()
    if new_location:
        target.location = new_location

    new_status = input(f"Status [{target.status}] (Active/Spare/Repair/Retired): ").strip()
    if new_status:
        allowed = {"Active", "Spare", "Repair", "Retired"}
        if new_status in allowed:
            target.status = new_status
        else:
            print("  Invalid status entered; keeping previous status.")

    new_notes = input(f"Notes [{target.notes if target.notes else '(none)'}]: ").strip()
    if new_notes:
        target.notes = new_notes

    print("\nDevice updated.\n")


def print_device_details(d: Device) -> None:
    """Pretty-print a device record."""
    print("-" * 60)
    print(f"Device ID : {d.device_id}")
    print(f"Name      : {d.name}")
    print(f"Type      : {d.device_type}")
    print(f"IP        : {d.ip}")
    print(f"Location  : {d.location}")
    print(f"Owner     : {d.owner}")
    print(f"Status    : {d.status}")
    print(f"Notes     : {d.notes if d.notes else '(none)'}")
    print(f"Created   : {d.created_at}")
    print("-" * 60)


def subnet_planner() -> None:
    """
    Plan a subnet and show:
    - network address, broadcast (IPv4), usable host count, first/last usable
    - a few sample host IPs
    """
    print("\nSubnet Planner")
    print("Enter a network in CIDR format, e.g., 10.0.10.0/24 or 2001:db8::/64")

    while True:
        cidr = input("CIDR network: ").strip()
        try:
            net = ip_network(cidr, strict=False)
            break
        except ValueError:
            print("  Invalid CIDR. Try again (example: 192.168.1.0/24).")

    print("\nResults")
    print("-" * 60)
    print(f"Network      : {net.network_address}")
    print(f"Prefix length: /{net.prefixlen}")
    print(f"Netmask      : {net.netmask if hasattr(net, 'netmask') else 'N/A'}")
    print(f"Total addrs  : {net.num_addresses}")

    # IPv4 extras
    if net.version == 4:
        print(f"Broadcast    : {net.broadcast_address}")
        # usable hosts for typical subnets
        usable = max(net.num_addresses - 2, 0) if net.prefixlen <= 30 else (2 if net.prefixlen == 31 else 1)
        print(f"Usable hosts : {usable}")

        hosts = list(net.hosts())
        if hosts:
            print(f"First host   : {hosts[0]}")
            print(f"Last host    : {hosts[-1]}")
            sample = hosts[:5]
            print("Sample hosts : " + ", ".join(str(h) for h in sample))
    else:
        # IPv6 doesn't have broadcast; "hosts()" is huge, so just sample first few
        print("Broadcast    : N/A (IPv6)")
        sample = []
        addr = int(net.network_address)
        for i in range(min(5, net.num_addresses)):
            sample.append(str(ip_address(addr + i)))
        print("Sample addrs : " + ", ".join(sample))

    print("-" * 60)
    print()


def generate_report(devices: List[Device]) -> None:
    """Generate a simple summary report grouped by status and location."""
    if not devices:
        print("\nInventory is empty.\n")
        return

    by_status: Dict[str, int] = {}
    by_location: Dict[str, int] = {}
    by_type: Dict[str, int] = {}

    for d in devices:
        by_status[d.status] = by_status.get(d.status, 0) + 1
        by_location[d.location] = by_location.get(d.location, 0) + 1
        by_type[d.device_type] = by_type.get(d.device_type, 0) + 1

    print("\nInventory Report")
    print("-" * 60)
    print("By Status:")
    for k in sorted(by_status):
        print(f"  {k:<10} : {by_status[k]}")

    print("\nBy Location:")
    for k in sorted(by_location):
        print(f"  {k:<20} : {by_location[k]}")

    print("\nBy Device Type:")
    for k in sorted(by_type):
        print(f"  {k:<10} : {by_type[k]}")
    print("-" * 60)
    print()


# -----------------------------
# Main Program (Top-Level)
# -----------------------------
def main() -> None:
    devices = load_data()

    MENU = """
Network Inventory & Subnet Planner
---------------------------------
1) List all devices
2) List ACTIVE devices only
3) Add a device
4) Search / Update / Retire a device
5) Subnet planner
6) Inventory report
7) Export inventory to CSV
8) Save & Exit
9) Exit without saving
"""

    while True:
        print(MENU)
        choice = input("Choose an option (1-9): ").strip()

        if choice == "1":
            list_devices(devices)
        elif choice == "2":
            list_devices(devices, only_active=True)
        elif choice == "3":
            add_device(devices)
        elif choice == "4":
            update_or_retire_device(devices)
        elif choice == "5":
            subnet_planner()
        elif choice == "6":
            generate_report(devices)
        elif choice == "7":
            export_to_csv(devices)
        elif choice == "8":
            save_data(devices)
            print("\nSaved. Goodbye!\n")
            break
        elif choice == "9":
            print("\nGoodbye (changes not saved).\n")
            break
        else:
            print("\nInvalid choice. Please select 1-9.\n")


if __name__ == "__main__":
    main()
