# 🚗 Car Rental Management System

A **multi-client Car Rental Management System** developed using Python TCP Socket Programming as an Operating Systems Term Project at INHA University.

The application allows multiple clients to connect to a central server simultaneously, view available cars, rent cars, return rented cars, and manage rental information.

## 📌 Project Overview

Many car rental businesses face challenges managing cars, customers, and rental bookings. Handling multiple customer requests simultaneously can also lead to conflicts, such as two customers attempting to rent the same car.

Our project addresses these problems through a client-server architecture using TCP socket communication, threading, and thread synchronization.

The server manages shared data, while clients send requests and receive responses.

## ✨ Main Features

- **Multi-client Connection** – Multiple clients can connect to the server simultaneously.
- **Car Management** – Add, view, update, and delete car information.
- **Customer Management** – Add, view, update, and delete customer information.
- **Car Rental** – Rent available cars.
- **Car Return** – Return previously rented cars.
- **Rental Management** – View, update, and delete rental records.
- **Search and Availability** – Check which cars are available for rent.
- **Data Synchronization** – Prevent multiple customers from renting the same car simultaneously.
- **Error Handling** – Handle invalid requests and client disconnections.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| TCP Socket Programming | Client-server communication |
| Threading | Handle multiple clients simultaneously |
| JSON | Exchange data between clients and server |
| Python Lists | Store cars, customers, and rental information |
| Thread Lock | Protect shared data and prevent conflicts |

## 🏗️ System Architecture

The project follows a **Client-Server Architecture**.

```text
          CLIENT 1
              |
          CLIENT 2
              |
          CLIENT 3
              |
              v
      +------------------+
      |   TCP SERVER     |
      |                  |
      |  Socket Server   |
      |  Threading       |
      |  Request Handler |
      +------------------+
              |
              v
      +------------------+
      |   Shared Data    |
      |                  |
      |      Cars        |
      |    Customers     |
      |     Rentals      |
      +------------------+
```

### How It Works

1. The server starts and waits for incoming client connections.
2. Multiple clients connect to the server through TCP sockets.
3. Each client sends requests in JSON format.
4. The server processes requests using separate threads.
5. Thread Lock protects shared data from simultaneous conflicting operations.
6. The server sends responses back to the clients.

## 📂 Project Structure

```text
car-rental-system-iut/
│
├── client/
│
├── server/
│
└── README.md
```

## 🎯 Project Objectives

- Understand TCP socket programming.
- Implement client-server communication.
- Learn how to handle multiple clients using threading.
- Understand synchronization and thread locking.
- Prevent race conditions when accessing shared data.
- Implement CRUD operations.
- Develop a practical application using Operating Systems concepts.

## 👥 Team Members

**Institution:** INHA University

**Course:** Operating Systems

**Semester:** Fall 2026

| No. | Name | Section | Role |
|---|---|---|---|
| 1 | Sanjar Ismailov | UK 2605 | Team Leader |
| 2 | Muhammadaziz Rustamov | UK 2605 | Member |
| 3 | Abdulbosit G'iyosov | Italy 2606 | Member |
| 4 | Muhammadzohid Nurmirzayev | UK 2605 | Member |
| 5 | Jaloliddin Sultonboyev | Italy 2606 | Member |

## 📚 Operating Systems Concepts

This project demonstrates several important Operating Systems concepts:

- **Concurrency:** Multiple clients can interact with the server at the same time.
- **Multithreading:** Separate threads handle client connections.
- **Synchronization:** Thread Lock protects shared resources.
- **Race Condition Prevention:** Synchronization prevents conflicting rental operations.
- **Client-Server Communication:** TCP sockets provide reliable communication between clients and the server.

---

**Developed as an Operating Systems Term Project – Fall 2026.**
