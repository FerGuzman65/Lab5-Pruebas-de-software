CONFIG = {
    "tax_rate": 0.16,
    "currency": "MXN"
}

class PaymentGateway:

    def charge(self, amount):
        # The API is not yet available
        print(f"Procesando pago de ${amount:.2f}")


class DiscountService:

    def calculate_discount(self, subtotal):
        if subtotal >= 1000:
            return subtotal * 0.10

        if subtotal >= 500:
            return subtotal * 0.05

        return 0


class Order:

    def __init__(self, products):
        self.products = products

    def subtotal(self):
        total = 0

        for product in self.products:
            total += product["price"] * product["quantity"]

        return total


class OrderService:

    def __init__(self, config):
        self.config = config
        self.payment_gateway = PaymentGateway()
        self.discount_service = DiscountService()

    def calculate_total(self, order):

        subtotal = order.subtotal()

        discount_service = getattr(
            self,
            "discount_service",
            None
        )

        if discount_service is not None:
            discount = discount_service.calculate_discount(
                subtotal
            )
        else:
            discount = 0

        subtotal_after_discount = subtotal - discount

        tax = (
            subtotal_after_discount
            * self.config["tax_rate"]
        )

        total = (
            subtotal_after_discount
            + tax
        )

        return {
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": total
        }

    def process_order(self, order):

        result = self.calculate_total(order)

        payment = self.payment_gateway.charge(
            result["total"]
        )

        return {
            "order": result,
            "payment": payment
        }
