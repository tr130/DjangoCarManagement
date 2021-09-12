from django.db import models

# Create your models here.
class Part(models.Model):
    name = models.CharField(max_length=200)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    customer_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_level = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.stock_level} in stock)"

    def get_total_on_order(self):
        total = 0
        for order in self.partsorderunit_set.all():
            if not order.checked_in:
                total += order.quantity
        return total

class PartsOrder(models.Model): 
    placed = models.DateTimeField(auto_now_add=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    editable = models.BooleanField(default=True)

    def save(self):
        if self.editable:
            for unit in self.partsorderunit_set.all():
                self.sub_total += unit.total_cost
            self.vat = float(self.sub_total) * 0.2
            self.grand_total = float(self.sub_total) + self.vat
        return super().save()

    def __str__(self):
        return f"Order for {self.grand_total} placed on {self.placed}. Is Editable? {self.editable}"

    def get_delivery_status(self):
        checked_in = 0
        for unit in self.partsorderunit_set.all():
            if unit.checked_in:
                checked_in += 1
        if checked_in == 0:
            return 'awaiting'
        elif checked_in == self.partsorderunit_set.count():
            return 'delivered'
        else:
            return 'part'

class PartsOrderUnit(models.Model):
    order = models.ForeignKey(PartsOrder, on_delete=models.PROTECT)
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    cost_each = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    checked_in = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.part.name} x {self.quantity}"

    def save(self):
        self.cost_each = self.part.cost_price
        self.total_cost = self.cost_each * self.quantity
        return super().save()

