import json
import socket

HOST = "127.0.0.1"
PORT = 5000


def send_request(sock, reader, request):
    payload = (json.dumps(request) + "\n").encode("utf-8")
    sock.sendall(payload)
    line = reader.readline()
    if not line:
        raise ConnectionError("Server closed the connection")
    return json.loads(line)


def show_response(response):
    print("\n--- SERVER RESPONSE ---")
    if response.get("success"):
        print("SUCCESS")
        if "data" in response:
            print(json.dumps(response["data"], indent=2))
    else:
        print("FAILED:", response.get("error", "Operation failed"))
        if response.get("data") is not None:
            print(json.dumps(response["data"], indent=2))
    print("-----------------------")


def ask_int(prompt):
    return int(input(prompt).strip())


def ask_float(prompt):
    return float(input(prompt).strip())


def build_request(choice):
    if choice == "1":
        return {"action": "list_cars"}
    if choice == "2":
        return {
            "action": "add_car",
            "brand": input("Brand: "),
            "model": input("Model: "),
            "year": ask_int("Year: "),
            "daily_price": ask_float("Daily price: "),
        }
    if choice == "3":
        return {
            "action": "update_car",
            "id": ask_int("Car ID: "),
            "brand": input("New brand: "),
            "model": input("New model: "),
            "year": ask_int("New year: "),
            "daily_price": ask_float("New daily price: "),
        }
    if choice == "4":
        return {"action": "delete_car", "id": ask_int("Car ID: ")}
    if choice == "5":
        return {"action": "list_customers"}
    if choice == "6":
        return {
            "action": "add_customer",
            "name": input("Customer name: "),
            "phone": input("Phone: "),
        }
    if choice == "7":
        return {
            "action": "update_customer",
            "id": ask_int("Customer ID: "),
            "name": input("New name: "),
            "phone": input("New phone: "),
        }
    if choice == "8":
        return {"action": "delete_customer",
                "id": ask_int("Customer ID: ")}
    if choice == "9":
        return {"action": "list_rentals"}
    if choice == "10":
        return {
            "action": "rent_car",
            "car_id": ask_int("Car ID: "),
            "customer_id": ask_int("Customer ID: "),
            "days": ask_int("Number of rental days: "),
        }
    if choice == "11":
        return {"action": "return_car",
                "rental_id": ask_int("Rental ID: ")}
    if choice == "12":
        return {
            "action": "update_rental",
            "id": ask_int("Rental ID: "),
            "car_id": ask_int("New car ID: "),
            "customer_id": ask_int("New customer ID: "),
            "days": ask_int("New number of days: "),
        }
    if choice == "13":
        return {"action": "delete_rental",
                "id": ask_int("Rental ID: ")}
    return None


MENU = """
========== CAR RENTAL SYSTEM ==========
 1. View cars
 2. Add car
 3. Update car
 4. Delete car
 5. View customers
 6. Add customer
 7. Update customer
 8. Delete customer
 9. View rentals
10. Rent a car
11. Return a car
12. Update rental
13. Delete rental
 0. Exit
=======================================
"""


def main():
    try:
        with socket.create_connection((HOST, PORT), timeout=10) as sock:
            # Use a file wrapper for line-by-line JSON responses.
            reader = sock.makefile("r", encoding="utf-8")
            print(f"Connected to server {HOST}:{PORT}")

            while True:
                print(MENU)
                choice = input("Choose an option: ").strip()
                if choice == "0":
                    print("Goodbye!")
                    break

                try:
                    request = build_request(choice)
                    if request is None:
                        print("Invalid menu choice.")
                        continue
                    response = send_request(sock, reader, request)
                    show_response(response)
                except ValueError:
                    print("Invalid number. Please enter a valid number.")
                except (ConnectionError, OSError, json.JSONDecodeError) as exc:
                    print("Communication error:", exc)
                    break
    except ConnectionRefusedError:
        print("Cannot connect. Start the server first.")
    except (TimeoutError, OSError) as exc:
        print("Connection problem:", exc)


if __name__ == "__main__":
    main()
