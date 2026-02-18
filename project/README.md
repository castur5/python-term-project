# Network Inventory & Subnet Planner (Python CLI)

#### Video Demo: <PASTE YOUR UNLISTED YOUTUBE LINK HERE>

## Description

This project is a command-line Python application that helps an IT team manage a small network inventory and perform basic subnet planning. The program was designed for a growing company environment where tracking devices, IP addresses, locations, and lifecycle status is important for troubleshooting, audits, and planning. The application focuses on two practical needs: (1) maintaining an inventory of devices with validated IP addresses and persistent storage, and (2) analyzing network subnets using CIDR notation (for example, `10.0.10.0/24`) to quickly understand usable hosts and sample addresses.

When the program runs, it displays a menu-driven interface. A user can list all devices, list only active devices, add a new device, search and update an existing device, retire a device, generate an inventory report, export the inventory to CSV, or use the subnet planner tool. Device information includes a unique device ID, name, device type, IP address, location, owner, status, and optional notes. The system validates whether a provided IP address is a correctly formatted IPv4 or IPv6 address before saving a device. Inventory data persists between program runs by saving to a local JSON file.

The subnet planner feature uses CIDR input to calculate network details. For IPv4 networks, the program displays the network address, prefix length, netmask, broadcast address, usable host count (when applicable), first/last usable host addresses, and a small sample list of host IPs. For IPv6 networks, it avoids enumerating the entire address space and instead displays a few sample addresses from the start of the subnet.

## Files in this Project

- `TermProject.py`: The main Python source file. It contains the `main()` function and several top-level functions that implement project features such as loading/saving data, adding devices, searching/updating devices, exporting to CSV, generating reports, and subnet planning.
- `inventory.json`: A data file created automatically by the program (if you choose “Save & Exit”). It stores the device inventory as JSON so the information is available the next time the program runs.
- `inventory_export.csv`: A file created when you choose the “Export inventory to CSV” option. This is useful for viewing inventory in spreadsheet software.
- `requirements.txt`: Lists project dependencies. This project uses only Python’s standard library, so no external packages are required.
- `README.md`: This documentation file describing the project and design decisions.

## How to Run

1. Ensure Python 3 is installed.
2. Place `TermProject.py` in your project folder.
3. Run the program:

```bash
python TermProject.py
