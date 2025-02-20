import json
import queue
from collections import namedtuple

MenuItemTuple = namedtuple("MenuItemTuple", ["name", "price", "type", "extra"])

class MenuItem:
    def __init__(self, name, price):
        self._name = name
        self._price = price

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_price(self):
        return self._price

    def set_price(self, price):
        self._price = price

    def calculate_total_price(self):
        return self._price

class Beverage(MenuItem):
    def __init__(self, name, price, size):
        super().__init__(name, price)
        self._size = size

    def get_size(self):
        return self._size

    def set_size(self, size):
        self._size = size

class Appetizer(MenuItem):
    def __init__(self, name, price, portion):
        super().__init__(name, price)
        self._portion = portion

    def get_portion(self):
        return self._portion

    def set_portion(self, portion):
        self._portion = portion

class MainCourse(MenuItem):
    def __init__(self, name, price, cooking_level):
        super().__init__(name, price)
        self._cooking_level = cooking_level

    def get_cooking_level(self):
        return self._cooking_level

    def set_cooking_level(self, cooking_level):
        self._cooking_level = cooking_level

class Order:
    def __init__(self):
        self.items = []
        self.has_main_course = False

    def add_item(self, item):
        self.items.append(item)
        if isinstance(item, MainCourse):
            self.has_main_course = True

    def calculate_total_bill(self):
        total = 0
        for item in self.items:
            if isinstance(item, Beverage) and self.has_main_course:
                total += item.calculate_total_price() * 0.9  # Aplicar descuento del 10%
            else:
                total += item.calculate_total_price()
        return total

    def apply_discount(self, discount_percentage):
        total = 0
        for item in self.items:
            discount = discount_percentage / 100
            total += item.calculate_total_price() * (1 - discount)
        return total

    def create_menu(self, menu_name):
        menu = {}
        with open(f"{menu_name}.json", "w") as file:
            json.dump(menu, file, indent=4)

    def add_menu_item(self, menu_name, item):
        try:
            with open(f"{menu_name}.json", "r") as file:
                menu = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            menu = {}
        
        menu[item.get_name()] = {
            "price": item.get_price(),
            "type": type(item).__name__,
            "extra": getattr(item, '_size', getattr(item, '_portion', getattr(item, '_cooking_level', None)))
        }
        with open(f"{menu_name}.json", "w") as file:
            json.dump(menu, file, indent=4)

    def update_menu_item(self, menu_name, item_name, new_item):
        with open(f"{menu_name}.json", "r") as file:
            menu = json.load(file)
        if item_name in menu:
            menu[item_name] = {
                "price": new_item.get_price(),
                "type": type(new_item).__name__,
                "extra": getattr(new_item, '_size', getattr(new_item, '_portion', getattr(new_item, '_cooking_level', None)))
            }
        with open(f"{menu_name}.json", "w") as file:
            json.dump(menu, file, indent=4)

    def delete_menu_item(self, menu_name, item_name):
        with open(f"{menu_name}.json", "r") as file:
            menu = json.load(file)
        if item_name in menu:
            del menu[item_name]
        with open(f"{menu_name}.json", "w") as file:
            json.dump(menu, file, indent=4)

class MedioPago:
    def __init__(self):
        pass

    def pagar(self, monto):
        raise NotImplementedError("Subclases deben implementar pagar()")

class Tarjeta(MedioPago):
    def __init__(self, numero, cvv):
        super().__init__()
        self.numero = numero
        self.cvv = cvv

    def pagar(self, monto):
        print(f"Pagando {monto:.2f} con tarjeta {self.numero[-4:]}")

class Efectivo(MedioPago):
    def __init__(self, monto_entregado):
        super().__init__()
        self.monto_entregado = monto_entregado

    def pagar(self, monto):
        if self.monto_entregado >= monto:
            print(f"Pago realizado en efectivo. Cambio: {self.monto_entregado - monto:.2f}")
        else:
            print(f"Fondos insuficientes. Faltan {monto - self.monto_entregado:.2f} para completar el pago.")

class Payment:
    def __init__(self, order, payment_method):
        self.order = order
        self.payment_method = payment_method

    def calculate_final_amount(self, discount_percentage=0):
        if discount_percentage > 0:
            return self.order.apply_discount(discount_percentage)
        return self.order.calculate_total_bill()

    def process_payment(self, discount_percentage=0, amount_paid=None):
        total = self.calculate_final_amount(discount_percentage)
        if isinstance(self.payment_method, Efectivo):
            self.payment_method.monto_entregado = amount_paid
        self.payment_method.pagar(total)

class OrderManager:
    def __init__(self):
        self.order_queue = queue.Queue()

    def add_order(self, order):
        self.order_queue.put(order)

    def get_next_order(self):
        if not self.order_queue.empty():
            return self.order_queue.get()
        return None

# Crear un menú JSON
menu_name = "menu_principal"
order = Order()
order.create_menu(menu_name)

item1 = Beverage(name="Coca Cola", price=1.5, size="500ml")
item2 = Appetizer(name="Papas Fritas", price=3.0, portion="grande")
order.add_menu_item(menu_name, item1)
order.add_menu_item(menu_name, item2)

print(f"Menú {menu_name}.json creado con éxito.")
