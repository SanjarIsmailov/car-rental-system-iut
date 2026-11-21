# Multi-Client Car Rental Management System

## Requirements
- Python 3.8 or newer
- No third-party packages required

## Project structure
car-rental-system/
  server/
    server.py
    data.py
  client/
    client.py

## Run the server
Open a terminal in the project folder:

    cd server
    python server.py

## Run clients
Open another terminal for each client:

    cd client
    python client.py

For a local demonstration, run at least three clients on the same computer.
The client connects to 127.0.0.1, port 5000.

For clients on other computers in the same network, change HOST in
client/client.py to the server computer's local IP address. Allow TCP port
5000 through the server computer's firewall.

## Architecture
- TCP sockets provide reliable, ordered communication.
- ThreadingTCPServer handles each client in a separate thread.
- JSON Lines: each request and response is one JSON object per line.
- Python lists store cars, customers, and rentals in server memory.
- threading.RLock protects shared data from concurrent access.

## Notes
- Data is held in memory and resets when the server stops.
- A car cannot be rented if it is already rented.
- Customers and cars referenced by rental history cannot be deleted.
- Active rentals cannot be deleted; return them first.
- This is an educational demonstration, not a production rental system.
