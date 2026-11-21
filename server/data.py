import threading

# Shared in-memory data. All client-handler threads use these same lists.
cars = [
    {"id": 1, "brand": "Toyota", "model": "Camry", "year": 2023,
     "daily_price": 50000.0, "available": True},
    {"id": 2, "brand": "Chevrolet", "model": "Malibu", "year": 2022,
     "daily_price": 40000.0, "available": True},
    {"id": 3, "brand": "BMW", "model": "X5", "year": 2024,
     "daily_price": 100000.0, "available": True},
]
customers = []
rentals = []
data_lock = threading.RLock()


def _next_id(items):
    return max((item["id"] for item in items), default=0) + 1


def _find(items, item_id):
    return next((item for item in items if item["id"] == item_id), None)


def list_cars():
    with data_lock:
        return [car.copy() for car in cars]


def add_car(brand, model, year, daily_price):
    brand, model = str(brand).strip(), str(model).strip()
    year, daily_price = int(year), float(daily_price)
    if not brand or not model:
        raise ValueError("Brand and model cannot be empty")
    if year < 1886 or year > 2100:
        raise ValueError("Year must be between 1886 and 2100")
    if daily_price <= 0:
        raise ValueError("Daily price must be greater than zero")
    with data_lock:
        car = {"id": _next_id(cars), "brand": brand, "model": model,
               "year": year, "daily_price": daily_price, "available": True}
        cars.append(car)
        return car.copy()


def update_car(car_id, brand, model, year, daily_price):
    car_id, year, daily_price = int(car_id), int(year), float(daily_price)
    brand, model = str(brand).strip(), str(model).strip()
    if not brand or not model:
        raise ValueError("Brand and model cannot be empty")
    if year < 1886 or year > 2100 or daily_price <= 0:
        raise ValueError("Invalid year or daily price")
    with data_lock:
        car = _find(cars, car_id)
        if car is None:
            return None
        car.update(brand=brand, model=model, year=year,
                   daily_price=daily_price)
        return car.copy()


def delete_car(car_id):
    with data_lock:
        car = _find(cars, int(car_id))
        if car is None or not car["available"]:
            return False
        # Keep cars referenced by rental history.
        if any(r["car_id"] == car["id"] for r in rentals):
            return False
        cars.remove(car)
        return True


def list_customers():
    with data_lock:
        return [customer.copy() for customer in customers]


def add_customer(name, phone):
    name, phone = str(name).strip(), str(phone).strip()
    if not name or not phone:
        raise ValueError("Customer name and phone cannot be empty")
    with data_lock:
        if any(c["phone"] == phone for c in customers):
            raise ValueError("A customer with this phone number already exists")
        customer = {"id": _next_id(customers), "name": name, "phone": phone}
        customers.append(customer)
        return customer.copy()


def update_customer(customer_id, name, phone):
    customer_id = int(customer_id)
    name, phone = str(name).strip(), str(phone).strip()
    if not name or not phone:
        raise ValueError("Customer name and phone cannot be empty")
    with data_lock:
        customer = _find(customers, customer_id)
        if customer is None:
            return None
        if any(c["phone"] == phone and c["id"] != customer_id
               for c in customers):
            raise ValueError("Another customer already uses this phone number")
        customer.update(name=name, phone=phone)
        return customer.copy()


def delete_customer(customer_id):
    with data_lock:
        customer = _find(customers, int(customer_id))
        if customer is None:
            return False
        if any(r["customer_id"] == customer["id"] for r in rentals):
            return False
        customers.remove(customer)
        return True


def list_rentals():
    with data_lock:
        return [rental.copy() for rental in rentals]


def rent_car(car_id, customer_id, days):
    car_id, customer_id, days = int(car_id), int(customer_id), int(days)
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
            "status": "ACTIVE",
        }
        rentals.append(rental)
        car["available"] = False
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
        return True


def update_rental(rental_id, new_car_id, new_customer_id, new_days):
    rental_id, new_car_id = int(rental_id), int(new_car_id)
    new_customer_id, new_days = int(new_customer_id), int(new_days)
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
            total_price=round(new_car["daily_price"] * new_days, 2),
        )
        return rental.copy()


def delete_rental(rental_id):
    with data_lock:
        rental = _find(rentals, int(rental_id))
        if rental is None or rental["status"] == "ACTIVE":
            return False
        rentals.remove(rental)
        return True
