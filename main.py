from database import engine
from models import Base

Base.metadata.create_all(engine)
print("Base de datos creada correctamente.")