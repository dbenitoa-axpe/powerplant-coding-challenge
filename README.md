# powerplant-coding-challenge

## Prerequisites
- [Docker](https://www.docker.com/get-started) installed on your system.

## Project Structure
The project includes:
- `main.py`: The main FastAPI application file.
- `production_plan_calculator.py`: The main logic for the production plan.
- `production_plan_request.py`: A pydantic model for validation purposes.
- `requirements.txt`: Lists dependencies (e.g., `fastapi`, `uvicorn`).
- `Dockerfile`: Defines the Docker image.
- `.dockerignore`: Excludes unnecessary files from the Docker image.

## Instructions to Build and Run

### 1. Clone or Download the Project
Ensure you have the project files in a local directory.

### 2. CO2 emission allowance
This is an optional step. You can activate o deactivate the calculation of the CO2 emission allowance cost by changing the values of the CALCULATE_CO2 and CO2_GENERATION_PER_MHW variables inside the main.py file. These are the values by default:
```python
app.CALCULATE_CO2 = True
app.CO2_GENERATION_TONS_PER_MWH = 0.3
```

- CALCULATE_CO2, if True, will add the cost of the CO2 emissions to the calculation of the production plan.
- CO2_GENERATION_TONS_PER_MWH is the CO2 generated in tons per MWH.


### 2. Build and Run the Docker Image
Open a terminal in the project directory (where the `Dockerfile` is located) and run:

```bash
docker build -t powerplant-coding-challenge .
docker run -d -p 8888:8888 powerplant-coding-challenge
```

### 3. Test the app
You can check the app using curl:

```bash
curl -X POST "http://localhost:8888/productionplan" -H "Content-Type: application/json" -d @example_payloads/payload1.json
```

