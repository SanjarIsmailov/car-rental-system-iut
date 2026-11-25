
import socket
import json


HOST = "127.0.0.1"
PORT = 5000


class CancelOperation(Exception):
    pass


# -------------------- INPUT FUNCTIONS --------------------

def ask_text(prompt):
    value = input(prompt).strip()

    if not value:
        raise CancelOperation

    return value


def ask_int(prompt):
    value = ask_text(prompt)

    try:
        return int(value)
    except ValueError:
        raise ValueError("Please enter a valid number.")


def ask_float(prompt):
    value = ask_text(prompt)

    try:
        number = float(value)

        if number <= 0:
            raise ValueError

        return number

    except ValueError:
        raise ValueError("Please enter a valid positive price.")


# -------------------- SERVER CONNECTION --------------------

def send_request(request):
    try:
        with socket.create_connection((HOST, PORT), timeout=10) as client:
            message = json.dumps(request) + "\n"
            client.sendall(message.encode("utf-8"))

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

            response_line = response_data.split(b"\n", 1)[0]
            return json.loads(response_line.decode("utf-8"))

    except ConnectionRefusedError:
        return {
            "success": False,
            "error": "Cannot connect to server. Start server.py first."
        }

    except socket.timeout:
        return {
            "success": False,
            "error": "Server connection timed out."
        }

    except (OSError, json.JSONDecodeError) as error:
        return {
            "success": False,
            "error": str(error)
        }


# -------------------- DISPLAY FUNCTIONS --------------------

def format_value(key, value):
    if key in ("daily_price", "total_price"):
        return f"${float(value):,.2f}"

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

    if not data:
        print("\nNo records found.")
        return

    keys = list(data[0].keys())

    formatted_rows = []

    for item in data:
        row = []

        for key in keys:
            row.append(format_value(key, item.get(key, "")))

        formatted_rows.append(row)

    widths = []

    for index, key in enumerate(keys):
        max_width = len(key)

        for row in formatted_rows:
            max_width = max(max_width, len(row[index]))

        widths.append(max_width)

    print()

    header = " | ".join(
        key.upper().ljust(widths[index])
        for index, key in enumerate(keys)
    )

    print(header)
    print("-" * len(header))

    for row in formatted_rows:
        print(
            " | ".join(
                value.ljust(widths[index])
                for index, value in enumerate(row)
            )
        )


def handle_response(response):
    if not isinstance(response, dict):
        print(response)
        return

    if response.get("success"):
        print("\nSuccess!")

        data = response.get("data")

        if data is not None:
            show_table(data)

    else:
        print("\nError:", response.get("error", "Unknown error."))


# -------------------- REQUEST BUILDER --------------------

def build_request(action_number):

    # CARS

    if action_number == 1:
        return {"action": "list_cars"}

    elif action_number == 2:
        print("\nADD A CAR")

        brand = ask_text("Brand: ")
        model = ask_text("Model: ")
        year = ask_int("Year: ")
        daily_price = ask_float("Daily price (USD): ")

        return {
            "action": "add_car",
            "brand": brand,
            "model": model,
            "year": year,
            "daily_price": daily_price
        }

    elif action_number == 3:
        print("\nUPDATE A CAR")

        car_id = ask_int("Car ID: ")
        brand = ask_text("New brand: ")
        model = ask_text("New model: ")
        year = ask_int("New year: ")
        daily_price = ask_float("New daily price (USD): ")

        return {
            "action": "update_car",
            "id": car_id,
            "brand": brand,
            "model": model,
            "year": year,
            "daily_price": daily_price
        }

    elif action_number == 4:
        print("\nDELETE A CAR")

        car_id = ask_int("Car ID: ")

        return {
            "action": "delete_car",
            "id": car_id
        }

    # CUSTOMERS

    elif action_number == 5:
        return {"action": "list_customers"}

    elif action_number == 6:
        print("\nADD A CUSTOMER")

        name = ask_text("Customer name: ")
        phone = ask_text("Phone number: ")

        return {
            "action": "add_customer",
            "name": name,
            "phone": phone
        }

    elif action_number == 7:
        print("\nUPDATE A CUSTOMER")

        customer_id = ask_int("Customer ID: ")
        name = ask_text("New name: ")
        phone = ask_text("New phone number: ")

        return {
            "action": "update_customer",
            "id": customer_id,
            "name": name,
            "phone": phone
        }

    elif action_number == 8:
        print("\nDELETE A CUSTOMER")

        customer_id = ask_int("Customer ID: ")

        return {
            "action": "delete_customer",
            "id": customer_id
        }

    # RENTALS

    elif action_number == 9:
        return {"action": "list_rentals"}

    elif action_number == 10:
        print("\nRENT A CAR")

        car_id = ask_int("Car ID: ")
        customer_id = ask_int("Customer ID: ")
        days = ask_int("Number of days: ")

        return {
            "action": "rent_car",
            "car_id": car_id,
            "customer_id": customer_id,
            "days": days
        }

    elif action_number == 11:
        print("\nRETURN A CAR")

        rental_id = ask_int("Rental ID: ")

        return {
            "action": "return_car",
            "rental_id": rental_id
        }

    elif action_number == 12:
        print("\nUPDATE A RENTAL")

        rental_id = ask_int("Rental ID: ")
        car_id = ask_int("New car ID: ")
        customer_id = ask_int("New customer ID: ")
        days = ask_int("New number of days: ")

        return {
            "action": "update_rental",
            "id": rental_id,
            "car_id": car_id,
            "customer_id": customer_id,
            "days": days
        }

    elif action_number == 13:
        print("\nDELETE A RENTAL")

        rental_id = ask_int("Rental ID: ")

        return {
            "action": "delete_rental",
            "id": rental_id
        }

    return None


# -------------------- SUBMENUS --------------------

def cars_menu():
    return {
        "title": "CARS",
        "options": {
            "1": (1, "View all cars"),
            "2": (2, "Add a car"),
            "3": (3, "Update a car"),
            "4": (4, "Delete a car")
        }
    }


def customers_menu():
    return {
        "title": "CUSTOMERS",
        "options": {
            "1": (5, "View customers"),
            "2": (6, "Add a customer"),
            "3": (7, "Update a customer"),
            "4": (8, "Delete a customer")
        }
    }


def rentals_menu():
    return {
        "title": "RENTALS",
        "options": {
            "1": (9, "View rental records"),
            "2": (10, "Rent a car"),
            "3": (11, "Return a car"),
            "4": (12, "Update a rental"),
            "5": (13, "Delete a rental")
        }
    }


# -------------------- MENU HANDLING --------------------

def open_submenu(menu):
    while True:
        print("\n" + menu["title"])

        for number, (_, description) in menu["options"].items():
            print(f"{number}. {description}")

        print("\n0. Back")
        print("-" * 45)

        choice = input("Select option: ").strip()

        if choice == "0":
            return

        if choice not in menu["options"]:
            print("\nInvalid option. Try again.")
            continue

        action_number = menu["options"][choice][0]

        try:
            request = build_request(action_number)

            if request:
                response = send_request(request)
                handle_response(response)

        except CancelOperation:
            print("\nOperation cancelled. No data was sent to the server.")

        except ValueError as error:
            print("\nInvalid input:", error)

        except Exception as error:
            print("\nError:", error)


# -------------------- MAIN MENU --------------------

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
            print("\nGoodbye!")
            break

        elif choice == "1":
            open_submenu(cars_menu())

        elif choice == "2":
            open_submenu(customers_menu())

        elif choice == "3":
            open_submenu(rentals_menu())

        else:
            print("\nInvalid option. Try again.")


if __name__ == "__main__":
    main()
