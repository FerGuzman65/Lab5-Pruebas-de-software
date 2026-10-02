from shop import Order
from shop import OrderService
from shop import CONFIG
import pytest


class FakePaymentGateway:
    """Doble de prueba que sustituye al servicio externo de pagos (RF-11).

    La API real no esta disponible, por lo que se aisla el componente y
    se registra el monto cobrado para poder verificarlo.
    """

    def __init__(self):
        self.charged_amount = None
        self.calls = 0

    def charge(self, amount):
        self.calls += 1
        self.charged_amount = amount

        return {
            "status": "approved",
            "amount": amount,
            "currency": CONFIG["currency"]
        }


@pytest.fixture
def order():
    products = [
        {
            "name": "Teclado",
            "price": 800,
            "quantity": 1
        },
        {
            "name": "Mouse",
            "price": 300,
            "quantity": 1
        }
    ]

    return Order(products)


# CP-01 | monkeypatch.setattr() | RF-10, RF-11, RF-14
# Sustituye la dependencia payment_gateway por un doble de prueba.
# Entradas: Teclado $800 x1, Mouse $300 x1 | tax_rate = 0.16
# Esperado: subtotal 1100, descuento 110, impuesto 158.4, total 1148.4
#           y pago aprobado por el monto total de la orden.
def test_order_normal(monkeypatch, order):

    service = OrderService(CONFIG)

    fake_gateway = FakePaymentGateway()

    monkeypatch.setattr(
        service,
        "payment_gateway",
        fake_gateway
    )

    order_processed = service.process_order(order)

    assert order_processed["payment"]["status"] == "approved"
    assert order_processed["order"]["subtotal"] == 1100
    assert order_processed["order"]["discount"] == 110
    assert order_processed["order"]["tax"] == 158.4
    assert order_processed["order"]["total"] == 1148.4

    assert fake_gateway.calls == 1
    assert fake_gateway.charged_amount == 1148.4


# CP-02 | monkeypatch.setitem() | RF-07, RF-08, RF-09
# Modifica temporalmente la configuracion global para probar el sistema
# con otra tasa de impuesto, sin alterar CONFIG para los demas casos.
# El doble de pagos solo sirve de apoyo: la tecnica que se prueba aqui es
# setitem, y se usa process_order para comprobar que la tasa modificada
# llega hasta el monto que se cobra.
# Entradas: Teclado $800 x1, Mouse $300 x1 | tax_rate = 0.08
# Esperado: subtotal 1100, descuento 110, impuesto 79.2, total 1069.2
def test_tax_rate_from_config(monkeypatch, order):

    monkeypatch.setitem(CONFIG, "tax_rate", 0.08)

    service = OrderService(CONFIG)

    fake_gateway = FakePaymentGateway()

    monkeypatch.setattr(
        service,
        "payment_gateway",
        fake_gateway
    )

    order_processed = service.process_order(order)

    result = order_processed["order"]

    assert result["subtotal"] == 1100
    assert result["discount"] == 110
    assert result["tax"] == 79.2
    assert result["total"] == 1069.2

    assert order_processed["payment"]["status"] == "approved"
    assert fake_gateway.charged_amount == 1069.2
