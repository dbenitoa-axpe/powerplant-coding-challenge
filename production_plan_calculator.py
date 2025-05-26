import math
import logging
from production_plan_request import ProductionPlanRequest

def calculate_merit_order(request: ProductionPlanRequest, calculate_co2, co2_generation_tons_per_mwh):
    """
    Returns the powerplants in merit order
    """
    powerplants_with_merit = []
    for powerplant in request.powerplants:
        if powerplant.type == "windturbine":
            powerplants_with_merit.append({"name": powerplant.name,
                                           "merit": 0,  # Assigning the lowest cost possible
                                           "pmin": math.ceil(powerplant.pmin * request.fuels.wind_per/100 * 10) / 10,
                                           "pmax": math.floor(powerplant.pmax * request.fuels.wind_per/100 * 10) / 10
                                           })
            continue

        if powerplant.type == "turbojet":
            powerplants_with_merit.append({"name": powerplant.name,
                                           "merit": request.fuels.kerosine_euro_mwh / powerplant.efficiency,
                                           "pmin": powerplant.pmin,
                                           "pmax": powerplant.pmax
                                           })
            continue

        # gasfired
        powerplants_with_merit.append({"name": powerplant.name,
                                       "merit": request.fuels.gas_euro_mwh / powerplant.efficiency,
                                       "pmin": powerplant.pmin,
                                       "pmax": powerplant.pmax
                                       })

        # Add the cost of the co2 emissions
        if calculate_co2:
            powerplants_with_merit[-1]["merit"] += request.fuels.co2_euro_ton * co2_generation_tons_per_mwh

    return sorted(powerplants_with_merit, key=lambda x: (x["merit"], x["pmin"], -x["pmax"]))

def calculate_production_plan(request: ProductionPlanRequest, calculate_co2, co2_generation_tons_per_mwh):
    logger = logging.getLogger('ProductionPlanLogger')
    powerplants_by_merit_list = calculate_merit_order(request, calculate_co2, co2_generation_tons_per_mwh)

    logger.info(f'Merit order: {powerplants_by_merit_list}')

    production_plan = {}
    for powerplant in powerplants_by_merit_list:
        production_plan[powerplant["name"]] = 0

    remaining_load = request.load
    overproduction = 0
    for powerplant in powerplants_by_merit_list:
        # pmax <= remaining load, just add the powerplant at max potency and go next
        if remaining_load > powerplant["pmax"]:
            production_plan[powerplant["name"]] = powerplant["pmax"]
            remaining_load = remaining_load - powerplant["pmax"]
            continue

        # pmin <= remaining load <= pmax, add this powerplant with
        # the potency equal the remaining load and this finishes the power plan
        if powerplant["pmin"] <= remaining_load:
            production_plan[powerplant["name"]] = remaining_load
            break

        # at this time, remaining load < pmin, add the powerplant at pmin production and annotate the overproduction
        production_plan[powerplant["name"]] = powerplant["pmin"]
        overproduction = powerplant["pmin"] - remaining_load
        break

    # Deal with overproduction by reducing output in other powerplants, in reverse merit order
    if overproduction > 0:
        for powerplant in reversed(powerplants_by_merit_list):
            # If the plant is off or is at its minimum, continue
            if production_plan[powerplant["name"]] == 0 \
                or production_plan[powerplant["name"]] == powerplant["pmin"]:
                continue

            # The overproduction >= the production of the powerplant,
            # switch off this entire powerplant and go next
            if production_plan[powerplant["name"]] < overproduction:
                overproduction = overproduction - production_plan[powerplant["name"]]
                production_plan[powerplant["name"]] = 0
                continue

            # at this time overproduction <= production_plan[powerplant["name"]]
            production_plan[powerplant["name"]] = production_plan[powerplant["name"]] - overproduction

            # if the production needed is >= pmin, then this finishes the power plan.
            if production_plan[powerplant["name"]] >= powerplant["pmin"]:
                break

            # Otherwise, we need to put pmin and go next powerplant with the overproduction
            overproduction = powerplant["pmin"] - production_plan[powerplant["name"]]
            production_plan[powerplant["name"]] = powerplant["pmin"]

    return production_plan