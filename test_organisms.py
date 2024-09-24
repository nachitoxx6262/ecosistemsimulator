# test_organisms.py

from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

# Datos realistas de los organismos
organism_data = [
    {
        "name": "Ciervo",
        "organism_type": "Herbivore",
        "birth_rate": 0.3,
        "death_rate": 0.1,
        "initial_energy": 100.0,
        "quantity": 50,
        "environment_id": 4,
        "growth_rate": 1.05,  # Tasa de crecimiento en función de los recursos
        "energy_consumption_rate": 10.0,  # Energía consumida por día
        "reproduction_season": "Primavera",  # Temporada de reproducción
        "lifespan": 15.0,  # Esperanza de vida en años
        "reproduction_energy_threshold": 20.0,  # Umbral de energía necesario para la reproducción
        "min_energy_for_health": 15.0  # Umbral mínimo de energía para mantenerse sano
    },
    {
        "name": "Lobo",
        "organism_type": "Carnivore",
        "birth_rate": 0.1,
        "death_rate": 0.05,
        "initial_energy": 200.0,
        "quantity": 15,
        "environment_id": 4,
        "growth_rate": 1.02,  # Tasa de crecimiento en función de los recursos
        "energy_consumption_rate": 20.0,  # Energía consumida por día
        "reproduction_season": "Invierno",  # Temporada de reproducción
        "lifespan": 12.0,  # Esperanza de vida en años
        "reproduction_energy_threshold": 30.0,  # Umbral de energía necesario para la reproducción
        "min_energy_for_health": 25.0  # Umbral mínimo de energía para mantenerse sano
    },
    {
        "name": "Helecho",
        "organism_type": "Plant",
        "birth_rate": 1.0,
        "death_rate": 0.2,
        "initial_energy": 50.0,
        "quantity": 100,
        "environment_id": 4,
        "growth_rate": 1.10,  # Tasa de crecimiento en función de los recursos
        "energy_consumption_rate": 5.0,  # Energía consumida por día
        "reproduction_season": "Verano",  # Temporada de reproducción
        "lifespan": 5.0,  # Esperanza de vida en años
        "reproduction_energy_threshold": 10.0,  # Umbral de energía necesario para la reproducción
        "min_energy_for_health": 10.0  # Umbral mínimo de energía para mantenerse sano
    }
]


def test_create_organisms():
    # Test para crear los organismos con POST
    for organism in organism_data:
        response = client.post("/organisms/", json=organism)
        assert response.status_code == 200  # Comprobar si el código de respuesta es 201 (Creado)
        response_data = response.json()
        for key in organism:
            assert response_data[key] == organism[key]

def test_update_organism():
    # Actualiza un organismo existente con PUT
    updated_organism = organism_data[0].copy()
    updated_organism['quantity'] = 60  # Cambia la cantidad del ciervo
    
    # PUT para actualizar el organismo con id=1
    response = client.put("/organisms/1", json=updated_organism)
    assert response.status_code == 200  # Comprobar si el código de respuesta es 200 (OK)
    response_data = response.json()
    assert response_data['quantity'] == updated_organism['quantity']
