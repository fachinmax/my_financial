from django import forms


class MetamaskLocal(forms.Form):
    """login form. User must insert address and private key of his account"""
    address = forms.CharField(max_length=42, required=True, widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'off', 'size': 50}))
    private_key = forms.CharField(max_length=66, required=True, widget=forms.TextInput(attrs={'autocomplete': 'off', 'size': 72}))