from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import Environment, Organisms, PopulationHistory, Lifecycle
from . import database
import simpy
import random
from datetime import datetime
import asyncio

class EcosystemSimulation:
    def __init__(self, db_session, environment_id):
        self.db_session = db_session
        self.environment_id = environment_id
        self.env = simpy.Environment()
        self.organisms = self.load_organisms()
        self.environment = self.load_environment()

    def load_organisms(self):
        """Cargar organismos de la base de datos."""
        organisms_data = self.db_session.query(Organisms).filter(
            Organisms.environment_id == self.environment_id
        ).all()
        return organisms_data

    def load_environment(self):
        """Cargar el entorno desde la base de datos."""
        print("Cargando entorno...")
        return self.db_session.query(Environment).filter(Environment.id == self.environment_id).first()

    def organism_lifecycle(self, organism):
        """Ciclo de vida individual de un organismo."""
        print(f"Iniciando ciclo de vida de {organism.name} ({organism.organism_type})")
        while organism.quantity > 0:
            # Simula el paso de días
            yield self.env.timeout(random.randint(1, 5))

            if organism.organism_type == "Plant":
                # Crecimiento basado en recursos disponibles
                growth = self.environment.resources * 0.1 * organism.growth_rate
                organism.initial_energy += growth
                self.log_lifecycle_event(organism, "growth", f"{organism.name} ha crecido en {growth:.2f} energía.")

            elif organism.organism_type == "Herbivore":
                plants = [org for org in self.organisms if org.organism_type == "Plant" and org.initial_energy > 0]
                if plants:
                    consumed_energy = min(self.environment.resources, random.uniform(0.5, 2.0))
                    organism.initial_energy += consumed_energy
                    self.environment.resources -= consumed_energy
                    self.log_lifecycle_event(organism, "consume", f"{organism.name} consumió {consumed_energy:.2f} de energía.")
                else:
                    self.log_lifecycle_event(organism, "energy_loss", f"{organism.name} no encontró plantas y perdió energía.")
                    organism.reduce_energy(0.5)  # Pérdida de energía por falta de alimento

            elif organism.organism_type == "Carnivore":
                herbivores = [org for org in self.organisms if org.organism_type == "Herbivore" and org.initial_energy > 0]
                if herbivores:
                    prey = random.choice(herbivores)
                    consumed_energy = min(prey.initial_energy, random.uniform(1.0, 3.0))
                    organism.initial_energy += consumed_energy
                    prey.initial_energy -= consumed_energy
                    if prey.initial_energy <= 0:
                        prey.quantity -= 1
                        self.log_lifecycle_event(prey, "death", f"{prey.name} ha muerto.")
                    self.log_lifecycle_event(organism, "consume", f"{organism.name} cazó y consumió {consumed_energy:.2f} de energía.")
                else:
                    self.log_lifecycle_event(organism, "energy_loss", f"{organism.name} no encontró presas y perdió energía.")
                    organism.reduce_energy(1.0)  # Pérdida de energía por falta de presas

            # Pérdida de energía por metabolismo
            energy_loss = random.uniform(0.1, 1.0)
            organism.initial_energy -= energy_loss
            self.log_lifecycle_event(organism, "energy_loss", f"{organism.name} perdió {energy_loss:.2f} de energía.")

            # Reproducción
            if self.check_reproduction_conditions(organism):
                offspring = self.reproduce(organism)
                self.log_lifecycle_event(organism, "reproduction", f"{organism.name} se ha reproducido. Nuevos individuos: {offspring}")

            # Muerte
            if organism.initial_energy <= 0 or random.random() < organism.death_rate:
                organism.quantity -= 1
                self.environment.resources += organism.initial_energy * 0.2  # Retorna energía al ambiente
                self.log_lifecycle_event(organism, "death", f"{organism.name} ha muerto.")
                if organism.quantity <= 0:
                    break

    def check_reproduction_conditions(self, organism):
        """Verifica si un organismo cumple las condiciones para reproducirse."""
        in_reproduction_season = organism.reproduction_season in ["all_year", self.get_current_season()]
        enough_energy = organism.initial_energy >= organism.reproduction_energy_threshold
        return in_reproduction_season and enough_energy

    def reproduce(self, organism):
        """Realiza la reproducción del organismo y devuelve el número de nuevos individuos."""
        birth_count = int(organism.quantity * organism.birth_rate)
        organism.quantity += birth_count
        organism.initial_energy -= organism.reproduction_energy_threshold  # El costo energético de la reproducción
        return birth_count

    def get_current_season(self):
        """Determina la estación actual en función del tiempo simulado."""
        month = datetime.fromtimestamp(self.env.now).month
        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "fall"
        else:
            return "winter"

    def log_lifecycle_event(self, organism, event_type, message):
        """Registra eventos importantes en la tabla Lifecycle."""
        print(f"[{event_type.upper()}] {message}")
        new_event = Lifecycle(
            organism_id=organism.id,
            event_type=event_type,
            description=message,
            timestamp=self.env.now,
            quantity=organism.quantity,
            energy=organism.initial_energy
        )
        self.db_session.add(new_event)
        self.db_session.commit()

    def run(self, simulation_time):
        """Inicia la simulación de manera asíncrona y registra la historia de la población periódicamente."""
        print("Iniciando simulación...")
        for organism in self.organisms:
            self.env.process(self.organism_lifecycle(organism))
        while self.env.now < simulation_time:
            # Pausa asíncrona para permitir que otras tareas se ejecuten
            asyncio.sleep(0.1)  # Pausa para no bloquear el bucle de eventos
            self.env.run(until=self.env.now + 1)  # Avanzamos la simulación 1 unidad de tiempo
            self.update_population_history()

    def update_population_history(self):
        """Actualiza la historia de la población."""
        print("Actualizando historia de la población...")
        try:
            plant_count = sum(org.quantity for org in self.organisms if org.organism_type == "Plant")
            herbivore_count = sum(org.quantity for org in self.organisms if org.organism_type == "Herbivore")
            predator_count = sum(org.quantity for org in self.organisms if org.organism_type == "Carnivore")
            timestamp = datetime.fromtimestamp(self.env.now)

            new_history = PopulationHistory(
                environment_id=self.environment_id,
                timestamp=timestamp,
                plant_population=plant_count,
                herbivore_population=herbivore_count,
                predator_population=predator_count
            )

            self.db_session.add(new_history)
            self.db_session.commit()
            print(f"Historia actualizada: Plantas={plant_count}, Herbívoros={herbivore_count}, Depredadores={predator_count}")
        except Exception as e:
            self.db_session.rollback()
            print(f"Error al actualizar historia: {e}")
            raise
