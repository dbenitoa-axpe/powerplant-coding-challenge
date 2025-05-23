from pydantic import BaseModel, Field, field_validator
from typing import List, Literal

# Pydantic models to validate JSON
class Fuels(BaseModel):
    gas_euro_mwh: float = Field(..., alias="gas(euro/MWh)", ge=0)
    kerosine_euro_mwh: float = Field(..., alias="kerosine(euro/MWh)", ge=0)
    co2_euro_ton: float = Field(..., alias="co2(euro/ton)", ge=0)
    wind_per: float = Field(..., alias="wind(%)", ge=0, le=100)

    class Config:
        allow_population_by_field_name = True

class PowerPlant(BaseModel):
    name: str = Field(...)
    type: Literal["gasfired", "turbojet", "windturbine"] = Field(...)
    efficiency: float = Field(..., ge=0, le=1)
    pmin: int = Field(..., ge=0)
    pmax: int = Field(...)

    # Pmax should be higher or equal than pmin
    @field_validator("pmax", mode="after")
    @classmethod
    def check_pmax_ge_pmin(cls, v, values):
        if "pmin" in values.data and v < values.data["pmin"]:
            raise ValueError("pmax must be greater than or equal to pmin")
        return v

class ProductionPlanRequest(BaseModel):
    load: int = Field(..., ge=0)
    fuels: Fuels = Field(...)
    powerplants: List[PowerPlant] = Field(...)

    # Powerplants needs at least one powerplant
    @field_validator("powerplants", mode="after")
    @classmethod
    def check_powerplants_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError("The 'powerplants' list must contain at least one element")
        return v