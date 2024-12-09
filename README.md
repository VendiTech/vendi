# Vendi 🚀

**MSPY-Vendi** is a Python-based service that leverages RESTAPI communication (via FastAPI) to manage the vending machine settings and conduct real-time transactions among customers.

## 🚀 Features

- **RestAPI-Powered**: Built with FastAPI for fast and reliable asynchronous communication.
- **Real-Time Data Processing**: Supports real-time transaction handling for vending machine operations.
- **Inventory Management**: Facilitates the management of vending machine inventory and transactions in real-time.
- **Scheduled Maintenance**: Supports scheduled tasks for vending machine exports functionality.
## 🛠️ Development Setup

### Prerequisites

- Docker
- Docker Compose
- Poetry

### Getting Started

1. **Clone the Repository**

    ```bash
    git clone https://github.com/VendiTech/vendi.git
    cd mspy-vendi
    ```

2. **Set Up Environment**

    Ensure you have a `.env` file with the required environment variables.

   ```bash
   cp .env.example .env
   ```

3. **Build & Run the Service**

    ```bash
    make up
    ```

### Makefile Commands

Here's a summary of available commands in the `Makefile`:

| Command                    | Description                                                 |
|----------------------------|-------------------------------------------------------------|
| `make help`                | Show this help message.                                     |
| `make build`               | Build the Docker image.                                     |
| `make up`                  | Build and start the vendi service && scheduler && consumers |
| `make down`                | Stop the vendi services.                                    |
| `make ruff-fix`            | Run `ruff` to fix issues.                                   |
| `make lint`                | Run linters on the codebase.                                |
| `make up-test`             | Run tests.                                                  |
| `make up-datajam-consumer` | Start the standalone DataJam consumer.                      |
| `make up-najax-consumer`   | Start the standalone Nayax consumer.                        |
### Docker Compose Services

The project includes Docker Compose configurations for managing services. Below is a summary of the services and their exposed ports:

| Service            | Container Name     | Exposed Ports | Description              |
|--------------------|--------------------|---------------|--------------------------|
| `vendi-service`    | `vendi-service`    | `8040:8080`   | FastAPI service          |
| `vendi-db`         | `vendi-db`         | `5464:5432`   | PostgreSQL database.     |
| `vendi-redis`      | `vendi-redis`      | `6364:6379`   | Redis database.          |
| `vendi-worker`     | `vendi-worker`     | N/A           | Scheduler service        |
| `nayax-consumer`   | `nayax-consumer`   | N/A           | Nayax Consumer service   |
| `datajam-consumer` | `datajam-consumer` | N/A           | Datajam Consumer service |


#### Service Details

- **vendi-service**:
  - **Ports**:
    - `8080` (internal) → `8040` (external)

- **vendi-worker**:
  - **Command**:
    - `vendi_worker` (runs the TaskIQ scheduler)

- **nayax-consumer**:
  - **Command**:
    - `nayax_consumer` (runs the Nayax consumer)

- **datajam-consumer**:
  - **Command**:
    - `vendi_consumer` (runs the DataJam consumer)
