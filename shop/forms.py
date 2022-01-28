from django import forms 
from .models import Pattern,PatternRecipe,Contact,Cart,Order,Delivery

class PatternForm(forms.ModelForm):

    class Meta:
        model   = Pattern
        fields  = [ "title","img","size","user" ]

class PatternRecipeForm(forms.ModelForm):

    class Meta:
        model   = PatternRecipe
        fields  = [ "target","color","number","user" ]

class ContactForm(forms.ModelForm):
    class Meta:
        model   = Contact
        fields  = [ "subject","content","ip","user","email" ]


#顧客がカートに追加した時に使うフォーム
class CartAddForm(forms.ModelForm):
    class Meta:
        model   = Cart
        fields  = [ "user","pattern" ]

#顧客が注文した時に格納するフォーム(注文済みにチェックを入れる。)
class CartOrderForm(forms.ModelForm):
    class Meta:
        model   = Cart
        fields  = [ "user","pattern","ordered" ]


    #注文した時、注文モデルへ複写する。
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
