from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    CheckConstraint,
    UniqueConstraint,
    ForeignKey,
    Numeric,
    Text,
    String,
    Integer,
    DateTime,
    func
)
from enum import Enum
from sqlalchemy import Enum as sqlEnum

from decimal import Decimal
from datetime import datetime

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
        CheckConstraint("stock >=0", name="ck_perfumes_stock_no_negativo"),
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
    
    marca_id: Mapped[int] = mapped_column(ForeignKey("marcas.id"),nullable=False) 
    
    marca: Mapped["Marca"] = relationship(back_populates="perfumes")
    lineas_carrito: Mapped[list["LineaCarrito"]] = relationship(back_populates="perfume", passive_deletes=True)
    lineas_pedido: Mapped[list["LineaPedido"]] = relationship(back_populates="perfume")

    
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
    carrito: Mapped[Carrito | None] = relationship(back_populates="usuario", uselist=False, passive_deletes=True)
    pedidos: Mapped[list[Pedido]] = relationship(back_populates="usuario")
    
    def __repr__(self):
        return (
            f"Id={self.id}, "
            f"email={self.email}, "
            f"rol={self.rol.value}"
        )
        

class Carrito(Base):
    
    __tablename__ = "carritos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        )
    
    usuario: Mapped["Usuario"] = relationship(back_populates="carrito")
    lineas_carrito: Mapped[list["LineaCarrito"]] = relationship(back_populates="carrito", passive_deletes=True)
    
    def __repr__(self):
        return(
            f"Id={self.id}, "
            f"usuario_id={self.usuario_id}"
        )

class LineaCarrito(Base):
    
    __tablename__ = "lineas_carrito"
    
    __table_args__ = (
            CheckConstraint("cantidad > 0", name="ck_linea_carrito_cantidad_positiva"),
            UniqueConstraint("carrito_id", "perfume_id", name="uq_lineas_carrito_carrito_perfume")
        )
    id: Mapped[int] = mapped_column(primary_key=True)

    carrito_id: Mapped[int] = mapped_column(
        ForeignKey("carritos.id", ondelete="CASCADE"),
        nullable=False
    )
    perfume_id: Mapped[int] = mapped_column(
        ForeignKey("perfumes.id", ondelete="CASCADE"),
        nullable=False
    )
    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    carrito: Mapped["Carrito"] = relationship(back_populates="lineas_carrito")
    perfume: Mapped["Perfume"] = relationship(back_populates="lineas_carrito")
    
    def __repr__(self):
        return (
            f"Id={self.id}, "
            f"carrito_id={self.carrito_id}, "
            f"perfume_id={self.perfume_id}, "
            f"cantidad={self.cantidad}"
        )

class Pedido(Base):
    
    __tablename__ = "pedidos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), 
        nullable=False
        )
    
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
        )
    
    usuario: Mapped["Usuario"] = relationship(back_populates="pedidos")
    lineas_pedido: Mapped[list["LineaPedido"]] = relationship(back_populates="pedido")
    
    def __repr__(self):
        return(
            f"Id={self.id}, "
            f"usuario_id={self.usuario_id}, "
            f"fecha_creacion={self.fecha_creacion}"
        )

class LineaPedido(Base):
    
    __tablename__ = "lineas_pedido"

    __table_args__ = (
            CheckConstraint("cantidad > 0", name="ck_linea_pedido_cantidad_positiva"),
            CheckConstraint("precio_unidad > 0", name="ck_linea_pedido_precio_unidad_positiva")
        )

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        nullable=False
    )
    perfume_id: Mapped[int] = mapped_column(
        ForeignKey("perfumes.id"),
        nullable=False
    )
    nombre_perfume: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    precio_unidad: Mapped[Decimal] = mapped_column(
        Numeric(10,2),
        nullable=False
    )
    
    pedido: Mapped["Pedido"] = relationship(back_populates="lineas_pedido")
    perfume: Mapped["Perfume"] = relationship(back_populates="lineas_pedido")
    
    def __repr__(self):
        return(
            f"Id={self.id}, "
            f"pedido_id={self.pedido_id}, "
            f"perfume_id={self.perfume_id}, "
            f"cantidad={self.cantidad}, "
            f"precio_unidad={self.precio_unidad}"
        )