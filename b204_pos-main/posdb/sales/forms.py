# sales/forms.py

from django import forms
from .models import OrderItem, Discount


class OrderItemForm(forms.ModelForm):
    """One line item to add to an order."""
    class Meta:
        model  = OrderItem
        fields = ['product', 'quantity']

    def clean_quantity(self):
        """Validation: quantity must be at least 1."""
        qty = self.cleaned_data['quantity']
        if qty < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return qty
    def clean_product(self):
        """Validation: product must be in stock."""
        product = self.cleaned_data.get('product')
        if product and product.stock == 0:
            raise forms.ValidationError("This product is out of stock.")
        return product


class DiscountForm(forms.ModelForm):
    """Form to add or edit a discount on an order."""
    class Meta:
        model = Discount
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Staff discount, Loyalty, Promotion...',
                'maxlength': '200',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
        }

    def clean_amount(self):
        """Validation: discount amount must be positive."""
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount < 0:
            raise forms.ValidationError("Discount amount cannot be negative.")
        return amount

