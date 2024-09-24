# Simulador de Ecosistemas Biológicos

## Descripción General

El sistema es un **simulador de ecosistemas biológicos** diseñado para modelar interacciones entre organismos (plantas, herbívoros y carnívoros) dentro de un entorno específico. Utiliza tecnologías como **FastAPI**, **SQLAlchemy**, **Postgres** y **SimPy** para manejar el backend y la lógica de simulación.

El objetivo del simulador es estudiar la dinámica de poblaciones y el equilibrio ecológico a través de procesos como la reproducción, depredación, consumo de energía, y la relación con factores ambientales como recursos y estaciones del año.

## Tecnologías Utilizadas

- **FastAPI**: Framework para construir APIs rápidas y eficientes.
- **SQLAlchemy**: ORM (Mapeo objeto-relacional) que permite manejar las interacciones con la base de datos Postgres.
- **Postgres**: Base de datos relacional para almacenar la información de los organismos, el entorno y la historia de la simulación.
- **SimPy**: Biblioteca para simular eventos discretos como la depredación y reproducción en el ecosistema.

## Modelos de Datos

### **Organisms**

El modelo de **organisms** representa a los organismos en el ecosistema. Cada organismo puede ser una planta, herbívoro o carnívoro, y tiene atributos relacionados con su crecimiento, reproducción y energía.

```python
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

    environment = relationship("Environment", back_populates="organisms")
    interactions_as_prey = relationship("Interactions", foreign_keys='Interactions.prey_id', back_populates="prey")
    interactions_as_predator = relationship("Interactions", foreign_keys='Interactions.predator_id', back_populates="predator")
    lifecycle_events = relationship("Lifecycle", back_populates="organism")
```

## Environment
El modelo environment representa las condiciones del entorno en el que los organismos viven y se desarrollan. Contiene información como la temperatura, humedad y la cantidad de recursos disponibles.

## Lifecycle
El modelo lifecycle registra eventos importantes en la vida de los organismos, como nacimiento, crecimiento, consumo de energía y muerte. Este registro permite un análisis detallado del comportamiento del ecosistema.

## PopulationHistory
El modelo population_history guarda información sobre la cantidad de organismos en el ecosistema en momentos específicos, permitiendo rastrear cambios a lo largo del tiempo.

## Lógica del Ecosistema
Simulación del Ciclo de Vida de los Organismos
La simulación utiliza SimPy para manejar eventos de tiempo como la reproducción y el consumo de energía. Cada organismo sigue un ciclo de vida basado en su tipo (planta, herbívoro o carnívoro) y las condiciones del entorno.


```python
def organism_lifecycle(self, organism):
    """Ciclo de vida individual de un organismo."""
    while organism.quantity > 0:
        # Simula el paso de días
        yield self.env.timeout(random.randint(1, 5))

        if organism.organism_type == "Plant":
            growth = self.environment.resources * 0.1 * organism.growth_factor
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
```

## Reproducción y Muerte
Cada organismo tiene un ciclo de reproducción basado en su energía disponible y la temporada de reproducción. La lógica también incluye la muerte de los organismos debido a factores como falta de energía o el envejecimiento natural.

```python
def reproduce(self, organism):
    """Realiza la reproducción del organismo y devuelve el número de nuevos individuos."""
    birth_count = int(organism.quantity * organism.birth_rate)
    organism.quantity += birth_count
    organism.initial_energy -= organism.reproduction_energy_threshold  # El costo energético de la reproducción
    return birth_count
```


## Pérdida de Energía
Los organismos consumen energía de acuerdo a su tasa de consumo diario y pierden energía si no encuentran presas o recursos suficientes. Cuando un organismo muere, parte de su energía residual retorna al ambiente.

## Registro de Eventos
Cada evento significativo en la vida de los organismos, como el crecimiento, consumo de energía, reproducción y muerte, se registra en la tabla lifecycle para su posterior análisis.
```python
def log_lifecycle_event(self, organism, event_type, message):
    """Registra eventos importantes en la tabla Lifecycle."""
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
```

## Actualización de la Historia de Población
Durante la simulación, se actualiza la historia de la población para reflejar el estado actual de plantas, herbívoros y carnívoros en el ecosistema.
```python
def update_population_history(self):
    """Actualiza la historia de la población."""
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
```