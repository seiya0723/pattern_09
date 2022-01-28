from django.contrib import admin
from django.utils.html import format_html

from .models import Pattern,PatternRecipe,Contact,Cart,Order,Delivery

class PatternAdmin(admin.ModelAdmin):

    list_display    = [ "title","dt","size","format_img","user" ]

    def format_img(self,obj):
        if obj.img:
            return format_html('<img src="{}" alt="画像" style="width:15rem">', obj.img.url)

    format_img.short_description    = Pattern.img.field.verbose_name
    format_img.empty_value_display  = "画像なし"



class PatternRecipeAdmin(admin.ModelAdmin):

    #一覧に表示させる内容
    list_display    = [ "target","color","number","dt","user" ]

class ContactAdmin(admin.ModelAdmin):

    #一覧に表示させる内容
    list_display    = [ "dt","subject","content","ip","user" ]


class CartAdmin(admin.ModelAdmin):
    pass


class OrderAdmin(admin.ModelAdmin):

    #管理者が支払い確認を入力するとき、配送モデルへ追加する。
    #https://stackoverflow.com/questions/36443245/override-save-method-of-django-admin

    
    def save_model(self, request, obj, form, change):
        print("支払い確認しました")
        super(OrderAdmin, self).save_model(request, obj, form, change)


class DeliveryAdmin(admin.ModelAdmin):

    #管理者が配送完了を入力する
    def save_model(self, request, obj, form, change):
        print("配送開始しました")
        super(OrderAdmin, self).save_model(request, obj, form, change)


admin.site.register(Pattern,PatternAdmin)
admin.site.register(PatternRecipe,PatternRecipeAdmin)
admin.site.register(Contact,ContactAdmin)

admin.site.register(Cart,CartAdmin)
admin.site.register(Order,OrderAdmin)


admin.site.register(Delivery,DeliveryAdmin)


