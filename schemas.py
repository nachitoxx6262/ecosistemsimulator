from pydantic import BaseModel

class OrganismCreate(BaseModel):
    name: str
    organism_type: str
    birth_rate: float  # Tasa de reproducción por individuo/año
    death_rate: float  # Tasa de mortalidad por individuo/año
    initial_energy: float  # Energía inicial por individuo
    quantity: int  # Cantidad de individuos en la población inicial
    environment_id: int  # ID del entorno asociado
    growth_rate: float  # Tasa de crecimiento en función de los recursos disponibles
    energy_consumption_rate: float  # Energía consumida por día por cada individuo
    reproduction_season: str  # Temporada de reproducción (Ej: primavera, todo el año)
    lifespan: float  # Esperanza de vida promedio de un organismo en años
    reproduction_energy_threshold: float  # Umbral de energía necesario para la reproducción
    min_energy_for_health: float  # Umbral de energía para mantenerse sano



class InteractionCreate(BaseModel):
    predator_id: int
    prey_id: int


class EnvironimentoCreate(BaseModel):
    name : str
    temperature: float
    humidity: float
    resources:float
    surface_area: float  # Superficie en km²
