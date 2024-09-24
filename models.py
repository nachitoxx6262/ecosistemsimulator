from sqlalchemy import Column, Integer, String, ForeignKey, Float,DateTime
from sqlalchemy.orm import relationship
from .database import Base  # Asegúrate de que esta ruta es correcta
from datetime import datetime
# Tabla de Entornos (Environment)
class Environment(Base):
    __tablename__ = "environments"  # Nombre de la tabla en plural

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # Nombre del entorno
    temperature = Column(Float, nullable=False)  # Temperatura del entorno
    humidity = Column(Float, nullable=False)     # Humedad
    resources = Column(Float, nullable=False)    # Recursos disponibles en el entorno
    surface_area = Column(Float, nullable=True)  # Campo opcional de superficie, nullable=True

    # Relación con PopulationHistory
    population_history = relationship("PopulationHistory", back_populates="environment")

    # Relación con Organisms
    organisms = relationship("Organisms", back_populates="environment")

class Lifecycle(Base):
    __tablename__ = "lifecycle"
    
    id = Column(Integer, primary_key=True, index=True)
    organism_id = Column(Integer, ForeignKey("organisms.id"), nullable=False)  # Referencia a la tabla "organisms"
    event_type = Column(String, nullable=False)  # Ej: "consume", "death", "growth"
    description = Column(String)
    energy=Column(Float, nullable=False)
    quantity=Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)  # Tiempo del evento en la simulación

    # Relación con la tabla Organisms
    organism = relationship("Organisms", back_populates="lifecycle_events")


class Organisms(Base):
    __tablename__ = "organisms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    organism_type = Column(String, index=True, nullable=False)  # Ej: Planta, Herbívoro, Carnívoro
    birth_rate = Column(Float, nullable=False)  # Tasa de reproducción por individuo/año
    death_rate = Column(Float, nullable=False)  # Tasa de mortalidad por individuo/año
    initial_energy = Column(Float, nullable=False)  # Energía inicial por individuo
    quantity = Column(Integer, nullable=False)  # Cantidad de individuos en la población inicial
    environment_id = Column(Integer, ForeignKey('environments.id'), nullable=True)  # Relación con el entorno
    growth_rate = Column(Float, nullable=True)  # Tasa de crecimiento en función de los recursos disponibles
    energy_consumption_rate = Column(Float, nullable=True)  # Energía consumida por día por cada individuo
    reproduction_season = Column(String, nullable=True)  # Temporada de reproducción (Ej: primavera, todo el año)
    lifespan = Column(Float, nullable=True)  # Esperanza de vida promedio de un organismo en años
    reproduction_energy_threshold = Column(Float, nullable=False)  # Umbral de energía necesario para la reproducción
    min_energy_for_health = Column(Float, nullable=False)  # Umbral de energía para mantenerse sano
    
    # Relación con Environment (entorno)
    environment = relationship("Environment", back_populates="organisms")
    
    # Relaciones con Interactions (depredación y presas)
    interactions_as_prey = relationship("Interactions", foreign_keys='Interactions.prey_id', back_populates="prey")
    interactions_as_predator = relationship("Interactions", foreign_keys='Interactions.predator_id', back_populates="predator")
    
    # Relación con Lifecycle (historia de vida del organismo)
    lifecycle_events = relationship("Lifecycle", back_populates="organism")
    
    
    def reduce_energy(self, amount):
        """Reduce la energía del organismo y verifica su estado de salud."""
        self.initial_energy -= amount
        if self.initial_energy < self.min_energy_for_health:
            self.is_sick = True
            print(f"{self.name} se ha enfermado por falta de energía.")
        if self.initial_energy <= 0:
            return True  # El organismo ha muerto
        return False

class PopulationHistory(Base):
    __tablename__ = "population_history"  
    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey('environments.id'), nullable=False)  # Relación con Environment
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)  # Momento en que se guarda el estado
    plant_population = Column(Integer, nullable=False)  # Cantidad de plantas
    herbivore_population = Column(Integer, nullable=False)  # Cantidad de herbívoros
    predator_population = Column(Integer, nullable=False)  # Cantidad de depredadores
    
    # Relación con el entorno
    environment = relationship("Environment", back_populates="population_history")




class Interactions(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    prey_id = Column(Integer, ForeignKey('organisms.id'), nullable=False)     # Presa
    predator_id = Column(Integer, ForeignKey('organisms.id'), nullable=False) # Depredador
    interaction_type = Column(String, index=True, nullable=False)  # Ej: Depredación, Competencia, Simbiosis
    interaction_rate = Column(Float, nullable=False)               # Tasa de interacción

    # Relaciones con Organisms
    prey = relationship("Organisms", foreign_keys=[prey_id], back_populates="interactions_as_prey")
    predator = relationship("Organisms", foreign_keys=[predator_id], back_populates="interactions_as_predator")
