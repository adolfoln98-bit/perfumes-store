from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, ForeignKey, Numeric, Text, String
from enum import Enum
from sqlalchemy import Enum as sqlEnum

from decimal import Decimal

class Base(DeclarativeBase):
    pass

class Marca(Base):
    
    __tablename__ = "marcas"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False
        )
    
    perfumes: Mapped[list["Perfume"]] = relationship(back_populates="marca")
    
    def __repr__(self):
        return( 
            f"Id={self.id}, "
            f"nombre={self.nombre}"
            )    
    
class Perfume(Base):
    
    __tablename__ = "perfumes"
    
    __table_args__ = (
        CheckConstraint("precio > 0", name="ck_perfumes_precio_positivo"),
        CheckConstraint("stock >=0", name="ck_stock_no_negativo"),
    )
        
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(
        Text,
        nullable=False
        )
    
    volumen_ml: Mapped[int] = mapped_column(nullable=False)
    precio: Mapped[Decimal] = mapped_column(
        Numeric(10,2),
        nullable=False
    )
    stock: Mapped[int] = mapped_column(
        default=0,
        server_default="0",
        nullable=False
    )
    
    marca_id: Mapped[int | None] = mapped_column(ForeignKey("marcas.id", ondelete="SET NULL"), nullable=True) 
    
    marca: Mapped["Marca | None"] = relationship(back_populates="perfumes")
    

    
    def __repr__(self):
        return( 
            f"Id={self.id}, "
            f"nombre={self.nombre}, "
            f"volumen_ml={self.volumen_ml}, " 
            f"precio={self.precio}, "
            f"stock={self.stock}, "
            f"marca_id={self.marca_id}"
            )
        
class RolUsuario(Enum):
    USER = "user"
    ADMIN = "admin"
    
class Usuario(Base):
    
    __tablename__ = "usuarios"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    ) 
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    rol: Mapped[RolUsuario] = mapped_column(
        sqlEnum(
            RolUsuario,
            name="rol_usuario",
            values_callable= lambda enum: [
                miembro.value for miembro in enum
            ]
        ),
        server_default="user",
        default=RolUsuario.USER
    )
    
    def __repr__(self):
        return (
            f"Id={self.id}, "
            f"email={self.email}, "
            f"rol={self.rol.value}"
        )