import json
import threading
from pathlib import Path

DATABASE_FILE = Path(__file__).with_name("database.txt")
data_lock = threading.RLock()

cars = [
    {
        "id": 1,
        "brand": "Chevrolet",
        "model": "Malibu",
        "year": 2023,
        "daily_price": 500000,
        "available": False
    },
    {
        "id": 2,
        "brand": "Chevrolet",
        "model": "Gentra",
        "year": 2022,
        "daily_price": 400000,
        "available": True
    },
    {
        "id": 3,
        "brand": "BYD",
        "model": "Song Plus",
        "year": 2024,
        "daily_price": 700000,
        "available": True
    },
    {
        "id": 4,
        "brand": "BYD",
        "model": "Chazor",
        "year": 2024,
        "daily_price": 600000,
        "available": True
    }
]

customers = [
    {
        "id": 1,
        "name": "Sanjar",
        "phone": "935592299"
    }
]

rentals = [
    {
        "id": 1,
        "car_id": 1,
        "customer_id": 1,
        "days": 3,
        "total_price": 1500000,
        "status": "ACTIVE"
    },
    {
        "id": 2,
        "car_id": 2,
        "customer_id": 1,
        "days": 2,
        "total_price": 800000,
        "status": "RETURNED"
    }
]


def save_data():
    with data_lock:
        data = {
            "cars": cars,
            "customers": customers,
            "rentals": rentals
        }

        with open(DATABASE_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


def load_data():
    global cars, customers, rentals

    with data_lock:
        if not DATABASE_FILE.exists():
            save_data()
            return

        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            cars = data["cars"]
            customers = data["customers"]
            rentals = data["rentals"]

        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise RuntimeError(
                f"Cannot load database.txt: {error}"
            )


def _next_id(items):
    return max((item["id"] for item in items), default=0) + 1


def _find(items, item_id):
    return next(
        (item for item in items if item["id"] == item_id),
        None
    )


def list_cars():
    with data_lock:
        return [car.copy() for car in cars]


def add_car(brand, model, year, daily_price):
    brand = str(brand).strip()
    model = str(model).strip()
    year = int(year)
    daily_price = float(daily_price)

    if not brand or not model:
        raise ValueError("Brand and model cannot be empty")

    if year < 1886 or year > 2100:
        raise ValueError("Year must be between 1886 and 2100")

    if daily_price <= 0:
        raise ValueError("Daily price must be greater than zero")

    with data_lock:
        car = {
            "id": _next_id(cars),
            "brand": brand,
            "model": model,
            "year": year,
            "daily_price": daily_price,
            "available": True
        }

        cars.append(car)
        save_data()
        return car.copy()


def update_car(car_id, brand, model, year, daily_price):
    car_id = int(car_id)
    year = int(year)
    daily_price = float(daily_price)
    brand = str(brand).strip()
    model = str(model).strip()

    if not brand or not model:
        raise ValueError("Brand and model cannot be empty")

    if year < 1886 or year > 2100 or daily_price <= 0:
        raise ValueError("Invalid year or daily price")

    with data_lock:
        car = _find(cars, car_id)

        if car is None:
            return None

        car.update(
            brand=brand,
            model=model,
            year=year,
            daily_price=daily_price
        )

        save_data()
        return car.copy()


def delete_car(car_id):
    with data_lock:
        car = _find(cars, int(car_id))

        if car is None or not car["available"]:
            return False

        if any(r["car_id"] == car["id"] for r in rentals):
            return False

        cars.remove(car)
        save_data()
        return True


def list_customers():
    with data_lock:
        return [customer.copy() for customer in customers]


def add_customer(name, phone):
    name = str(name).strip()
    phone = str(phone).strip()

    if not name or not phone:
        raise ValueError("Customer name and phone cannot be empty")

    with data_lock:
        if any(c["phone"] == phone for c in customers):
            raise ValueError(
                "A customer with this phone number already exists"
            )

        customer = {
            "id": _next_id(customers),
            "name": name,
            "phone": phone
        }

        customers.append(customer)
        save_data()
        return customer.copy()


def update_customer(customer_id, name, phone):
    customer_id = int(customer_id)
    name = str(name).strip()
    phone = str(phone).strip()

    if not name or not phone:
        raise ValueError("Customer name and phone cannot be empty")

    with data_lock:
        customer = _find(customers, customer_id)

        if customer is None:
            return None

        if any(
            c["phone"] == phone and c["id"] != customer_id
            for c in customers
        ):
            raise ValueError(
                "Another customer already uses this phone number"
            )

        customer.update(name=name, phone=phone)

        save_data()
        return customer.copy()


def delete_customer(customer_id):
    with data_lock:
        customer = _find(customers, int(customer_id))

        if customer is None:
            return False

        if any(
            r["customer_id"] == customer["id"]
            for r in rentals
        ):
            return False

        customers.remove(customer)
        save_data()
        return True


def list_rentals():
    with data_lock:
        return [rental.copy() for rental in rentals]


def rent_car(car_id, customer_id, days):
    car_id = int(car_id)
    customer_id = int(customer_id)
    days = int(days)

    if days <= 0 or days > 365:
        raise ValueError("Rental days must be between 1 and 365")

    with data_lock:
        car = _find(cars, car_id)
        customer = _find(customers, customer_id)

        if car is None:
            return {"error": "Car not found"}

        if customer is None:
            return {"error": "Customer not found"}

        if not car["available"]:
            return {"error": "Car is already rented"}

        rental = {
            "id": _next_id(rentals),
            "car_id": car_id,
            "customer_id": customer_id,
            "days": days,
            "total_price": round(car["daily_price"] * days, 2),
            "status": "ACTIVE"
        }

        rentals.append(rental)
        car["available"] = False

        save_data()
        return rental.copy()


def return_car(rental_id):
    with data_lock:
        rental = _find(rentals, int(rental_id))

        if rental is None or rental["status"] != "ACTIVE":
            return False

        rental["status"] = "RETURNED"

        car = _find(cars, rental["car_id"])

        if car is not None:
            car["available"] = True

        save_data()
        return True


def update_rental(rental_id, new_car_id, new_customer_id, new_days):
    rental_id = int(rental_id)
    new_car_id = int(new_car_id)
    new_customer_id = int(new_customer_id)
    new_days = int(new_days)

    if new_days <= 0 or new_days > 365:
        raise ValueError("Rental days must be between 1 and 365")

    with data_lock:
        rental = _find(rentals, rental_id)
        new_car = _find(cars, new_car_id)
        customer = _find(customers, new_customer_id)

        if rental is None or rental["status"] != "ACTIVE":
            return None

        if new_car is None or customer is None:
            return None

        if new_car_id != rental["car_id"] and not new_car["available"]:
            return None

        old_car = _find(cars, rental["car_id"])

        if old_car is not None and old_car["id"] != new_car_id:
            old_car["available"] = True

        new_car["available"] = False

        rental.update(
            car_id=new_car_id,
            customer_id=new_customer_id,
            days=new_days,
            total_price=round(new_car["daily_price"] * new_days, 2)
        )

        save_data()
        return rental.copy()


def delete_rental(rental_id):
    with data_lock:
        rental = _find(rentals, int(rental_id))

        if rental is None or rental["status"] == "ACTIVE":
            return False

        rentals.remove(rental)

        save_data()
        return True


load_data()
