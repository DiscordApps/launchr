from django import forms

class ChangePlanForm(forms.Form):

    plan_id = forms.CharField(max_length=50)
