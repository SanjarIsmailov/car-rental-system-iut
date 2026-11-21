import json
import socketserver
import data


class ClientHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print(f"[CONNECTED] {self.client_address}")
        try:
            # Each line is one complete JSON request.
            for raw_line in self.rfile:
                try:
                    request = json.loads(raw_line.decode("utf-8"))
                    if not isinstance(request, dict):
                        raise ValueError("Request must be a JSON object")
                    response = self.process_request(request)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    response = {"success": False, "error": "Invalid JSON"}
                except (KeyError, TypeError, ValueError) as exc:
                    response = {"success": False, "error": str(exc)}
                except Exception:
                    # Keep an unexpected request error from killing the server.
                    response = {"success": False, "error": "Internal server error"}

                encoded = (json.dumps(response) + "\n").encode("utf-8")
                self.wfile.write(encoded)
                self.wfile.flush()
        except (ConnectionError, OSError):
            pass
        finally:
            print(f"[DISCONNECTED] {self.client_address}")

    def process_request(self, req):
        action = req.get("action")

        if action == "list_cars":
            return {"success": True, "data": data.list_cars()}
        if action == "add_car":
            result = data.add_car(req["brand"], req["model"],
                                  req["year"], req["daily_price"])
            return {"success": True, "data": result}
        if action == "update_car":
            result = data.update_car(req["id"], req["brand"], req["model"],
                                     req["year"], req["daily_price"])
            return {"success": result is not None, "data": result}
        if action == "delete_car":
            result = data.delete_car(req["id"])
            return {"success": result, "error": None if result else
                    "Car not found, rented, or referenced by rental history"}

        if action == "list_customers":
            return {"success": True, "data": data.list_customers()}
        if action == "add_customer":
            result = data.add_customer(req["name"], req["phone"])
            return {"success": True, "data": result}
        if action == "update_customer":
            result = data.update_customer(req["id"], req["name"], req["phone"])
            return {"success": result is not None, "data": result}
        if action == "delete_customer":
            result = data.delete_customer(req["id"])
            return {"success": result, "error": None if result else
                    "Customer not found or referenced by rental history"}

        if action == "list_rentals":
            return {"success": True, "data": data.list_rentals()}
        if action == "rent_car":
            result = data.rent_car(req["car_id"], req["customer_id"], req["days"])
            if "error" in result:
                return {"success": False, "error": result["error"]}
            return {"success": True, "data": result}
        if action == "return_car":
            result = data.return_car(req["rental_id"])
            return {"success": result, "error": None if result else
                    "Active rental not found"}
        if action == "update_rental":
            result = data.update_rental(req["id"], req["car_id"],
                                        req["customer_id"], req["days"])
            return {"success": result is not None, "data": result,
                    "error": None if result else "Rental update failed"}
        if action == "delete_rental":
            result = data.delete_rental(req["id"])
            return {"success": result, "error": None if result else
                    "Rental not found or still active"}

        return {"success": False, "error": "Unknown action"}


class CarRentalServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 5000

    with CarRentalServer((HOST, PORT), ClientHandler) as server:
        print(f"Car Rental TCP Server listening on port {PORT}")
        print("Waiting for clients...")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
