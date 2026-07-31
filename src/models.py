from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

class Base(DeclarativeBase):
    pass

class Marca(Base):
    
    __tablename__ = "marcas"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    perfumes: Mapped[list["Perfume"]] = relationship(back_populates="marca")
    
    def __repr__(self):
        return( 
            f"Id={self.id}, "
            f"nombre={self.nombre}"
            )    
    
class Perfume(Base):
    
    __tablename__ = "perfumes"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(nullable=False)
    volumen_ml: Mapped[int] = mapped_column(nullable=False)
    marca_id: Mapped[int | None] = mapped_column(ForeignKey("marcas.id", ondelete="SET NULL"), nullable=True) 
    
    marca: Mapped["Marca | None"] = relationship(back_populates="perfumes")
    
    def __repr__(self):
        return( 
            f"Id={self.id}, "
            f"nombre={self.nombre}, "
            f"volumen_ml={self.volumen_ml}, " 
            f"marca_id={self.marca_id}"
            )