from fastapi import FastAPI, HTTPException
import uvicorn
import logging
from production_plan_request import ProductionPlanRequest
from production_plan_calculator import calculate_production_plan

# Logger configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ProductionPlanLogger')

app = FastAPI(title="Production Plan API")
app.CALCULATE_CO2 = True
app.CO2_GENERATION_TONS_PER_MWH = 0.3

# Endpoint POST /productionplan
@app.post("/productionplan")
async def production_plan(request: ProductionPlanRequest):
    try:
        logger.info(f'Received payload: {request.model_dump_json(indent=2)}')
        calculated_production_plan = calculate_production_plan(request, app.CALCULATE_CO2, app.CO2_GENERATION_TONS_PER_MWH)

        response = []
        for powerplant in calculated_production_plan.keys():
            response.append({"name": powerplant, "p": float(calculated_production_plan[powerplant])})

        logger.info(f'Production plan calculated: {response}')

        return response

    except Exception as e:
        # Generic error handler
        logger.exception(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="debug")