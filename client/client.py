import socket
import json

HOST = "127.0.0.1"
PORT = 5000


class CancelOperation(Exception):
    pass


def ask_text(prompt):
    value = input(prompt).strip()
    if not value:
        raise CancelOperation
    return value


def ask_int(prompt):
    try:
        return int(ask_text(prompt))
    except ValueError:
        raise ValueError("Please enter a valid number.")


def ask_float(prompt):
    try:
        value = float(ask_text(prompt))
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        raise ValueError("Please enter a valid positive price.")


def send_request(request):
    try:
        with socket.create_connection((HOST, PORT), timeout=10) as client:
            client.sendall((json.dumps(request) + "\n").encode("utf-8"))
            response_data = b""

            while b"\n" not in response_data:
                chunk = client.recv(4096)
                if not chunk:
                    break
                response_data += chunk

            if not response_data:
                return {
                    "success": False,
                    "error": "No response from server."
                }

            return json.loads(
                response_data.split(b"\n", 1)[0].decode("utf-8")
            )

    except ConnectionRefusedError:
        return {
            "success": False,
            "error": "Cannot connect to server."
        }
    except socket.timeout:
        return {
            "success": False,
            "error": "Connection timed out."
        }
    except (OSError, json.JSONDecodeError) as error:
        return {
            "success": False,
            "error": str(error)
        }


def format_value(key, value):
    if key in ("daily_price", "total_price"):
        return f"{float(value):,.0f} UZS"

    if key == "available":
        return "Available" if value else "Rented"

    return str(value)


def show_table(data):
    if not data:
        print("\nNo records found.")
        return

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        print(data)
        return

    keys = list(data[0].keys())

    rows = [
        [format_value(key, item.get(key, "")) for key in keys]
        for item in data
    ]

    widths = [
        max(len(key), *(len(row[i]) for row in rows))
        for i, key in enumerate(keys)
    ]

    header = " | ".join(
        key.upper().ljust(widths[i])
        for i, key in enumerate(keys)
    )

    print("\n" + header)
    print("-" * len(header))

    for row in rows:
        print(" | ".join(
            value.ljust(widths[i])
            for i, value in enumerate(row)
        ))


def handle_response(response):
    if not isinstance(response, dict):
        print(response)
        return

    if response.get("success"):
        print("\nSuccess!")

        if response.get("data") is not None:
            show_table(response["data"])
    else:
        print("\nError:", response.get("error", "Unknown error."))


def build_request(action):
    if action == 1:
        return {"action": "list_cars"}

    elif action == 2:
        print("\nADD A CAR")
        return {
            "action": "add_car",
            "brand": ask_text("Brand: "),
            "model": ask_text("Model: "),
            "year": ask_int("Year: "),
            "daily_price": ask_float("Daily price (UZS): ")
        }

    elif action == 3:
        print("\nUPDATE A CAR")
        return {
            "action": "update_car",
            "id": ask_int("Car ID: "),
            "brand": ask_text("New brand: "),
            "model": ask_text("New model: "),
            "year": ask_int("New year: "),
            "daily_price": ask_float("New daily price (UZS): ")
        }

    elif action == 4:
        print("\nDELETE A CAR")
        return {
            "action": "delete_car",
            "id": ask_int("Car ID: ")
        }

    elif action == 5:
        return {"action": "list_customers"}

    elif action == 6:
        print("\nADD A CUSTOMER")
        return {
            "action": "add_customer",
            "name": ask_text("Customer name: "),
            "phone": ask_text("Phone number: ")
        }

    elif action == 7:
        print("\nUPDATE A CUSTOMER")
        return {
            "action": "update_customer",
            "id": ask_int("Customer ID: "),
            "name": ask_text("New name: "),
            "phone": ask_text("New phone number: ")
        }

    elif action == 8:
        print("\nDELETE A CUSTOMER")
        return {
            "action": "delete_customer",
            "id": ask_int("Customer ID: ")
        }

    elif action == 9:
        return {"action": "list_rentals"}

    elif action == 10:
        print("\nRENT A CAR")
        return {
            "action": "rent_car",
            "car_id": ask_int("Car ID: "),
            "customer_id": ask_int("Customer ID: "),
            "days": ask_int("Number of days: ")
        }

    elif action == 11:
        print("\nRETURN A CAR")
        return {
            "action": "return_car",
            "rental_id": ask_int("Rental ID: ")
        }

    elif action == 12:
        print("\nUPDATE A RENTAL")
        return {
            "action": "update_rental",
            "id": ask_int("Rental ID: "),
            "car_id": ask_int("New car ID: "),
            "customer_id": ask_int("New customer ID: "),
            "days": ask_int("New number of days: ")
        }

    elif action == 13:
        print("\nDELETE A RENTAL")
        return {
            "action": "delete_rental",
            "id": ask_int("Rental ID: ")
        }

    return None


def open_submenu(title, options):
    while True:
        print(f"\n{title}")

        for number, (action, description) in options.items():
            print(f"{number}. {description}")

        print("\n0. Back")
        print("-" * 45)

        choice = input("Select option: ").strip()

        if choice == "0":
            break

        if choice not in options:
            print("Invalid option.")
            continue

        try:
            action = options[choice][0]
            request = build_request(action)

            if request:
                response = send_request(request)
                handle_response(response)

        except CancelOperation:
            print("Operation cancelled.")

        except ValueError as error:
            print("Invalid input:", error)


def main():
    while True:
        print("\nMAIN MENU")
        print("1. Cars")
        print("2. Customers")
        print("3. Rentals")
        print("\n0. Exit")
        print("-" * 45)

        choice = input("Select option: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        elif choice == "1":
            open_submenu("CARS", {
                "1": (1, "View all cars"),
                "2": (2, "Add a car"),
                "3": (3, "Update a car"),
                "4": (4, "Delete a car")
            })

        elif choice == "2":
            open_submenu("CUSTOMERS", {
                "1": (5, "View customers"),
                "2": (6, "Add a customer"),
                "3": (7, "Update a customer"),
                "4": (8, "Delete a customer")
            })

        elif choice == "3":
            open_submenu("RENTALS", {
                "1": (9, "View rental records"),
                "2": (10, "Rent a car"),
                "3": (11, "Return a car"),
                "4": (12, "Update a rental"),
                "5": (13, "Delete a rental")
            })

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
