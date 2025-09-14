from __future__ import annotations
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Table, Column
from typing import List, Optional


# Creating our Base Model
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)


class Customers(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(30), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(db.String(100), unique=True)
    password: Mapped[Optional[str]] = mapped_column(db.String(100))
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)

    service_tickets: Mapped[List["ServiceTickets"]] = db.relationship(
        back_populates="customer"
    )


# Association Table
ServiceMechanics = Table(
    "service_mechanics",
    Base.metadata,
    Column("service_ticket_id", db.ForeignKey("service_tickets.id"), primary_key=True),
    Column("mechanic_id", db.ForeignKey("mechanics.id"), primary_key=True),
)


class ServiceTickets(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    VIN: Mapped[str] = mapped_column(db.String(100), unique=True)
    service_date: Mapped[date] = mapped_column(db.Date)
    service_desc: Mapped[str] = mapped_column(db.String(30), nullable=False)

    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"))
    customer: Mapped["Customers"] = db.relationship(back_populates="service_tickets")

    mechanics: Mapped[List["Mechanics"]] = db.relationship(
        secondary=ServiceMechanics, back_populates="service_tickets"
    )

    inventory_tickets: Mapped[List["InventoryServiceTicket"]] = db.relationship(
        back_populates="service_ticket"
    )


class Mechanics(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(30), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(db.String(100), unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False, unique=True)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_tickets: Mapped[List["ServiceTickets"]] = db.relationship(
        secondary=ServiceMechanics, back_populates="mechanics"
    )


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(30), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    inventory_tickets: Mapped[List["InventoryServiceTicket"]] = db.relationship(
        back_populates="inventory"
    )


class InventoryServiceTicket(Base):
    __tablename__ = "inventory_service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inventory_id: Mapped[int] = mapped_column(
        db.ForeignKey("inventory.id"), nullable=False
    )
    service_ticket_id: Mapped[int] = mapped_column(
        db.ForeignKey("service_tickets.id"), nullable=False
    )
    quantity: Mapped[Optional[float]] = mapped_column(db.Float, nullable=True)

    inventory: Mapped["Inventory"] = db.relationship(back_populates="inventory_tickets")
    service_ticket: Mapped["ServiceTickets"] = db.relationship(
        back_populates="inventory_tickets"
    )


# Models
# class Customers(Base):
#     __tablename__ = "customers"
#     id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
#     name: Mapped[str] = mapped_column(db.String(30), nullable=False)
#     email: Mapped[Optional[str]] = mapped_column(db.String(100), unique=True)
#     password: Mapped[Optional[str]] = mapped_column(db.String(100))
#     phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
#     serviceTickets: Mapped[List['ServiceTickets']] = db.relationship(back_populates='customer')

# # Association Table
# ServiceMechanics = Table(
#     "service_mechanics",
#     Base.metadata,
#     Column("service_ticket_id", db.ForeignKey("serviceTickets.id")),
#     Column("mechanic_id", db.ForeignKey("mechanics.id"))
# )

# class ServiceTickets(Base):
#     __tablename__ = "service_tickets"
#     id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
#     VIN: Mapped[str] = mapped_column(db.String(100), unique=True)
#     service_date: Mapped[date] = mapped_column(db.Date)
#     service_desc: Mapped[str] = mapped_column(db.String(30), nullable=False)
#     customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))
#     customer: Mapped["Customers"] = db.relationship(back_populates='serviceTickets')
#     mechanics: Mapped[List["Mechanics"]] = db.relationship(secondary=ServiceMechanics, back_populates='serviceTickets')

#     inventory_tickets :  Mapped[List["InventoryServiceTicket"]] = db.relationship(back_populates="service_ticket")

# class Mechanics(Base):
#     __tablename__ = "mechanics"
#     id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
#     name: Mapped[str] = mapped_column(db.String(30), nullable=False)
#     email: Mapped[Optional[str]] = mapped_column(db.String(100), unique=True)
#     phone: Mapped[str] = mapped_column(db.String(20), nullable=False, unique=True)
#     salary: Mapped[float] = mapped_column(db.Float, nullable=False)
#     serviceTickets: Mapped[List["ServiceTickets"]] = db.relationship(secondary=ServiceMechanics, back_populates="mechanics")

# class Inventory(Base):
#     __tablename__ = "inventory"
#     id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
#     name: Mapped[str] = mapped_column(db.String(30), nullable=False)
#     price: Mapped[float] = mapped_column(db.Float, nullable=False)

#     inventory_tickets :  Mapped[List["InventoryServiceTicket"]] = db.relationship(back_populates="inventory")


# class InventoryServiceTicket(Base):
#     __tablename__ = "InventoryServiceTicket"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     Inventory_id: Mapped[int] = mapped_column(db.ForeignKey("inventory.id"), nullable=False)
#     service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"), nullable=False)
#     quantity: Mapped[Optional[float]] = mapped_column(db.Float, nullable=True)


#     inventory:  Mapped["Inventory"] = db.relationship(back_populates="inventory_tickets")
#     service_ticket:  Mapped["ServiceTickets"] = db.relationship(back_populates="inventory_tickets")


