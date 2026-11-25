
import json
import socket

HOST = "127.0.0.1"
PORT = 5000


def show_header():
    print("\n" + "=" * 45)
    print("       CAR RENTAL MANAGEMENT SYSTEM")
    print("=" * 45)


def show_menu():
    print("\n--------------- MAIN MENU ---------------")

    print("\nCARS")
    print("1. View all cars")
    print("2. Add a car")
    print("3. Update a car")
    print("4. Delete a car")

    print("\nCUSTOMERS")
    print("5. View customers")
    print("6. Add a customer")
    print("7. Update a customer")
    print("8. Delete a customer")

    print("\nRENTALS")
    print("9. View rental records")
    print("10. Rent a car")
    print("11. Return a car")
    print("12. Update a rental")
    print("13. Delete a rental")

    print("\n0. Exit")
    print("-" * 45)


def send_request(sock, reader, request):
    message = json.dumps(request) + "\n"
    sock.sendall(message.encode("utf-8"))

    response = reader.readline()

    if not response:
        raise ConnectionError("Server disconnected")

    return json.loads(response)


def ask_int(message):
    return int(input(message).strip())


def ask_float(message):
    value = float(input(message).strip())

    if value <= 0:
        raise ValueError("Value must be greater than zero.")

    return value


def build_request(choice):

    if choice == "1":
        return {"action": "list_cars"}

    elif choice == "2":
        return {
            "action": "add_car",
            "brand": input("Brand: ").strip(),
            "model": input("Model: ").strip(),
            "year": ask_int("Year: "),
            "daily_price": ask_float("Daily price ($): ")
        }

    elif choice == "3":
        return {
            "action": "update_car",
            "id": ask_int("Car ID: "),
            "brand": input("New brand: ").strip(),
            "model": input("New model: ").strip(),
            "year": ask_int("New year: "),
            "daily_price": ask_float("New daily price ($): ")
        }

    elif choice == "4":
        return {
            "action": "delete_car",
            "id": ask_int("Car ID: ")
        }

    elif choice == "5":
        return {"action": "list_customers"}

    elif choice == "6":
        return {
            "action": "add_customer",
            "name": input("Customer name: ").strip(),
            "phone": input("Phone: ").strip()
        }

    elif choice == "7":
        return {
            "action": "update_customer",
            "id": ask_int("Customer ID: "),
            "name": input("New name: ").strip(),
            "phone": input("New phone: ").strip()
        }

    elif choice == "8":
        return {
            "action": "delete_customer",
            "id": ask_int("Customer ID: ")
        }

    elif choice == "9":
        return {"action": "list_rentals"}

    elif choice == "10":
        return {
            "action": "rent_car",
            "car_id": ask_int("Car ID: "),
            "customer_id": ask_int("Customer ID: "),
            "days": ask_int("Rental days: ")
        }

    elif choice == "11":
        return {
            "action": "return_car",
            "rental_id": ask_int("Rental ID: ")
        }

    elif choice == "12":
        return {
            "action": "update_rental",
            "id": ask_int("Rental ID: "),
            "car_id": ask_int("New car ID: "),
            "customer_id": ask_int("New customer ID: "),
            "days": ask_int("New rental days: ")
        }

    elif choice == "13":
        return {
            "action": "delete_rental",
            "id": ask_int("Rental ID: ")
        }

    return None


def format_value(key, value):

    if key in ("daily_price", "total_price"):
        return f"${float(value):,.2f}"

    elif key == "available":
        return "Available" if value else "Rented"

    return str(value)


def show_table(title, records, columns):

    print("\n" + "=" * 75)
    print(title.center(75))
    print("=" * 75)

    if not records:
        print("No records found.")
        return

    headers = [column[0] for column in columns]

    rows = []

    for record in records:
        row = []

        for label, key in columns:
            value = record.get(key, "-")
            row.append(format_value(key, value))

        rows.append(row)

    widths = []

    for i, header in enumerate(headers):
        width = len(header)

        for row in rows:
            width = max(width, len(row[i]))

        widths.append(width)

    header_line = " | ".join(
        headers[i].ljust(widths[i])
        for i in range(len(headers))
    )

    print(header_line)
    print("-" * len(header_line))

    for row in rows:
        print(" | ".join(
            row[i].ljust(widths[i])
            for i in range(len(row))
        ))

    print("-" * len(header_line))
    print("Total records:", len(records))


def show_data(data):

    if isinstance(data, list):

        if not data:
            print("\nNo records found.")
            return

        keys = data[0].keys()

        if "brand" in keys:
            show_table("CAR INVENTORY", data, [
                ("ID", "id"),
                ("Brand", "brand"),
                ("Model", "model"),
                ("Year", "year"),
                ("Daily Price ($)", "daily_price"),
                ("Status", "available")
            ])

        elif "name" in keys and "phone" in keys:
            show_table("CUSTOMER LIST", data, [
                ("ID", "id"),
                ("Name", "name"),
                ("Phone", "phone")
            ])

        elif "car_id" in keys:
            show_table("RENTAL RECORDS", data, [
                ("ID", "id"),
                ("Car ID", "car_id"),
                ("Customer ID", "customer_id"),
                ("Days", "days"),
                ("Total Price ($)", "total_price"),
                ("Status", "status")
            ])

    elif isinstance(data, dict):

        print("\nOperation Details")
        print("-" * 40)

        for key, value in data.items():
            label = key.replace("_", " ").title()
            value = format_value(key, value)
            print(f"{label}: {value}")


def show_response(response):

    print("\n" + "-" * 45)

    if response.get("success"):

        print("SUCCESS: Operation completed.")

        if "data" in response:
            show_data(response["data"])

    else:
        print("ERROR:", response.get("error", "Operation failed"))

    print("-" * 45)


def main():

    show_header()

    try:
        with socket.create_connection(
            (HOST, PORT), timeout=10
        ) as sock:

            reader = sock.makefile("r", encoding="utf-8")

            print("\nConnected to server successfully!")

            while True:

                show_menu()

                choice = input("Select option: ").strip()

                if choice == "0":
                    print("\nThank you for using Car Rental System!")
                    break

                try:
                    request = build_request(choice)

                    if request is None:
                        print("\nInvalid option. Try again.")
                        continue

                    response = send_request(
                        sock, reader, request
                    )

                    show_response(response)

                except ValueError as e:
                    print("\nInvalid input:", e)

                except (ConnectionError, OSError, json.JSONDecodeError) as e:
                    print("\nCommunication error:", e)
                    break

    except ConnectionRefusedError:
        print("\nCannot connect to server.")
        print("Please start server.py first.")

    except (TimeoutError, OSError) as e:
        print("\nConnection error:", e)

    except KeyboardInterrupt:
        print("\nClient stopped.")


if __name__ == "__main__":
    main()
