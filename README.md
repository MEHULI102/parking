# Vehicle Parking Management System

## Description
A multi-user web application for managing vehicle parking lots and reservations. The system allows administrators to manage parking lots, spots, and view bookings, while users can book, release, and manage parking slots. REST APIs are provided for integration purposes.

## Technologies Used
- Python 3.12
- Flask 3.0.3
- Flask-SQLAlchemy
- Jinja2
- SQLite
- Bootstrap 5
- Chart.js

## Folder Structure
- app.py → Application entry point  
- controller.py → All route handlers and logic  
- models.py → Database models (SQLAlchemy)  
- /templates → HTML templates (Jinja2)  
- /static → Static files (CSS, JS)  
- /api_definition.yaml → API specifications  
- /requirements.txt → Python dependencies  

## Database Initialization
The database is created programmatically using SQLAlchemy models when the application is run for the first time. No manual database creation is required.

## Setup Instructions
1. Install Python 3.12.

