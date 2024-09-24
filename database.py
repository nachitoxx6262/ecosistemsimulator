from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a PostgreSQL
DATABASE_URL = "postgresql://postgres:admin@localhost/proyecto1"
# Crear el motor de conexión
engine = create_engine(DATABASE_URL)
# Crear una clase Base para los modelos
Base = declarative_base()
# Crear una fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Crear las tablas en la base de datos
try:
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")
except Exception as e:
    print(f"Error creando las tablas: {e}")
# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    print(db)
    try:
        yield db
    finally:
        db.close()
