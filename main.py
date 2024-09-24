from .ecosystem_simulation import EcosystemSimulation
from fastapi import FastAPI,Depends,HTTPException
from .models import Environment,Interactions,Lifecycle,Organisms,PopulationHistory
from .schemas import OrganismCreate,InteractionCreate,EnvironimentoCreate
from .database import get_db
from sqlalchemy.orm import Session
app = FastAPI()

## ENTORNOS
@app.post("/environments/")
def create_environment(enviroments: EnvironimentoCreate, db: Session = Depends(get_db)):
   new_environments = Environment(
        name = enviroments.name,
        temperature= enviroments.temperature,
        humidity= enviroments.humidity,
        resources=enviroments.resources,
        surface_area=enviroments.surface_area  # Superficie en km²  # Superficie en km²  # Superficie en km²  # Superficie en km²  # Superficie en km²  # Superficie en km²  # Superficie en km²  # Superficie en km²  # Superficie en km²  # Superficie en km²  # Superficie en km²
    )
   db.add(new_environments)
   db.commit()
   db.refresh(new_environments)
   return new_environments
## Obtener todos los entornos
@app.get("/environments/")
def get_all_environments(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    environments = db.query(Environment).offset(skip).limit(limit).all()
    return environments
##  Obtener un entorno por ID
@app.get("/environments/{environment_id}")
def get_environment_by_id(environment_id: int, db: Session = Depends(get_db)):
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    if environment is None:
        raise HTTPException(status_code=404, detail="Environment not found")
    return environment
## Actualizar entorno
@app.put("/environments/{environment_id}")
def update_environment(enviroments:EnvironimentoCreate,environment_id: int, db: Session = Depends(get_db)):
   db_environments = db.query(Environment).filter(Environment.id == environment_id).first()
   if db_environments is None:
        raise HTTPException(status_code=404, detail="Environment id not found")
   db_environments.name = enviroments.name,
   db_environments.temperature= enviroments.temperature,
   db_environments.humidity= enviroments.humidity,
   db_environments.resources=enviroments.resources,
   db_environments.surface_area=enviroments.surface_area
   db.add(db_environments)
   db.commit()
   db.refresh(db_environments)
   return db_environments
# Eliminar entorno
@app.delete("/environments/{environment_id}")
def delete_environment(environment_id: int, db: Session = Depends(get_db)):
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    if environment is None:
        raise HTTPException(status_code=404, detail="Environment not found")
 
    db.delete(environment)
    db.commit()
    return {"detail": "Environment deleted"}
## Asignar organismo a entorno
@app.post("/environments/{environment_id}/organisms/")
def assign_organism_to_environment(environment_id: int, organism_id: int, db: Session = Depends(get_db)):
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    if environment is None:
        raise HTTPException(status_code=404, detail="Environment not found")
 
    organism = db.query(Organisms).filter(Organisms.id == organism_id).first()
    if organism is None:
        raise HTTPException(status_code=404, detail="Organism not found")
 
    organism.environment_id = environment_id
    db.commit()
    db.refresh(organism)
    return {"detail": "Organism assigned to environment"}
# Obetener todos los organismos de un entorno
@app.get("/environments/{environment_id}/organisms/")
def get_organisms_in_environment(environment_id: int, db: Session = Depends(get_db)):
    organisms = db.query(Organisms).filter(Organisms.environment_id == environment_id).all()
    if not organisms:
        raise HTTPException(status_code=404, detail="No organisms found in this environment")
    return organisms
from sqlalchemy.exc import DBAPIError
@app.post("/environments/{environment_id}/simulate/")
async def simulate_environment(environment_id: int, simulation_time: int, db: Session = Depends(get_db)):
    try:
        simulation = EcosystemSimulation(db, environment_id)
        simulation.env.process(simulation.run(simulation_time))
        simulation.env.run()
        return {"message": "Simulation completed successfully", "environment_id": environment_id}
    except Exception as e:
        return {"error": str(e), "message": "An error occurred during the simulation."}
    


#################### INTERACTIONS

@app.get("/interactions/")
def get_all_interactions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    interactions = db.query(Interactions).offset(skip).limit(limit).all()
    return interactions
@app.post("/interactions/")
def create_interactions(interaction: InteractionCreate, db: Session = Depends(get_db)):
    predator = db.query(Organisms).filter(Organisms.id == interaction.predator_id).first()
    prey = db.query(Organisms).filter(Organisms.id == interaction.prey_id).first()
    if predator is None:
        raise HTTPException(status_code=404, detail="Predator not found")
    if prey is None:
        raise HTTPException(status_code=404, detail="Prey not found")
    new_interaction = Interactions(
        predator_id=interaction.predator_id,
        prey_id=interaction.prey_id,
        interaction_type="Depredacion",
        interaction_rate=0.5
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    return {
        "id": new_interaction.id,
        "predator_id": new_interaction.predator_id,
        "prey_id": new_interaction.prey_id,
        "message": "Interaction successfully created"
    }


########## ORGANISMS

@app.get("/organisms/")
def read_organisms(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    organisms = db.query(Organisms).offset(skip).limit(limit).all()
    return organisms

@app.get("/organisms/{organism_id}")
def read_organisms_by_id(organism_id: int, db: Session = Depends(get_db)):
    organism = db.query(Organisms).filter(Organisms.id == organism_id).first()
    if organism is None:
        raise HTTPException(status_code=404, detail="Organism id not found")
    return organism

@app.post("/organisms/")
def create_organisms(organism: OrganismCreate, db: Session = Depends(get_db)):
    new_organism = Organisms(
        name = organism.name,
        organism_type = organism.organism_type,
        birth_rate = organism.birth_rate,
        death_rate = organism.death_rate,
        initial_energy = organism.initial_energy,
        quantity = organism.quantity,
        environment_id = organism.environment_id,
        growth_rate = organism.growth_rate,
        energy_consumption_rate = organism.energy_consumption_rate,
        reproduction_season = organism.reproduction_season,
        lifespan = organism.lifespan,
        reproduction_energy_threshold = organism.reproduction_energy_threshold,
        min_energy_for_health = organism.min_energy_for_health
    )
    db.add(new_organism)
    db.commit()
    db.refresh(new_organism)
    return new_organism

@app.put("/organisms/{organism_id}")
def modify_organism(organism_id: int, organism: OrganismCreate, db: Session = Depends(get_db)):
    db_organism = db.query(Organisms).filter(Organisms.id == organism_id).first()
    if db_organism is None:
        raise HTTPException(status_code=404, detail="Organism id not found")

    db_organism.name = organism.name,
    db_organism.organism_type = organism.organism_type,
    db_organism.birth_rate = organism.birth_rate,
    db_organism.death_rate = organism.death_rate,
    db_organism.initial_energy = organism.initial_energy,
    db_organism.quantity = organism.quantity,
    db_organism.environment_id = organism.environment_id,
    db_organism.growth_rate = organism.growth_rate,
    db_organism.energy_consumption_rate = organism.energy_consumption_rate,
    db_organism.reproduction_season = organism.reproduction_season,
    db_organism.lifespan = organism.lifespan,
    db_organism.reproduction_energy_threshold = organism.reproduction_energy_threshold,
    db_organism.min_energy_for_health= organism.min_energy_for_health
    db.commit()
    db.refresh(db_organism)
    return db_organism


@app.delete("/organisms/{organism_id}")
def delete_organism(organism_id: int, db: Session = Depends(get_db)):
    organism = db.query(Organisms).filter(Organisms.id == organism_id).first()
    if organism is None:
        raise HTTPException(status_code=404, detail="Organism id not found")

    db.delete(organism)
    db.commit()
    return {"detail": "Organism deleted"}





@app.post("/ecosystem/simulate/{environment_id}")
def simulate_ecosystem(environment_id: int,time:int, db: Session = Depends(get_db)):
    print("Inicia la simulación del ecosistema para un entorno específico.")
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    simulation = EcosystemSimulation(db_session=db, environment_id=environment_id)
    
    try:
        # Ejecutar la simulación de manera síncrona (sin await)
        simulation.run(simulation_time=time)  # Por ejemplo, 100 días
        return {"message": "Simulation completed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
