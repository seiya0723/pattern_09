from django.db import models
from django.utils import timezone

#Djangoのもともとあったユーザーモデルと1対多を結ぶのではなく、カスタムしたユーザーモデルと1対多を結ぶ
#from django.contrib.auth.models import User
from django.conf import settings

from django.core.mail import send_mail

from django.core.validators import MinValueValidator,MaxValueValidator,RegexValidator


class Pattern(models.Model):

    class Meta:
        db_table = "pattern"

    title   = models.CharField(verbose_name="タイトル",max_length=30)
    dt      = models.DateTimeField(verbose_name="投稿日時",default=timezone.now)
    img     = models.ImageField(verbose_name="画像",upload_to="shop/pattern/")

    #ここに糸の太さを指定するフィールドを追加。糸の太さは1つしかないからPatternModelに記録。
    size    = models.IntegerField(verbose_name="糸の太さ",default=1,validators=[MinValueValidator(1),MaxValueValidator(10)])


    #userモデルと紐づくフィールド(nullはサンプルの模様を格納)
    #user    = models.ForeignKey(User, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)

    #カスタムユーザーモデルと1対多を結ぶ
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)

    def __str__(self):
        return self.title



class PatternRecipe(models.Model):

    #Patternモデルクラスと1対多のリレーションを作る。
    target      = models.ForeignKey(Pattern,verbose_name="対象の模様",on_delete=models.CASCADE)

    #colorフィールドは16進数カラーコードの正規表現を指定し、それのみ受け付ける
    #参照:https://noauto-nolife.com/post/django-models-regex-validate/
    color_regex = RegexValidator(regex=r'^#(?:[0-9a-fA-F]{6})$')
    color       = models.CharField(verbose_name="色",max_length=7,validators=[color_regex],default="#000000")

    number      = models.IntegerField(verbose_name="本数",default=1,validators=[MinValueValidator(1),MaxValueValidator(10)])

    #ここにコントローラの順番を記録するため、dtを記録する
    dt      = models.DateTimeField(verbose_name="投稿日時",default=timezone.now)


    #userモデルと紐づくフィールド(nullはサンプルの模様を格納)
    #user    = models.ForeignKey(User, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)

    #カスタムユーザーモデルと1対多を結ぶ
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)

class Contact(models.Model):

    dt      = models.DateTimeField(verbose_name="お問い合わせ日時",default=timezone.now)
    subject = models.CharField(verbose_name="お問い合わせ件名",max_length=100)
    content = models.CharField(verbose_name="お問い合わせ内容",max_length=1000)
    
    #TODO:お問い合わせしてきた人のIPアドレスを記録する。
    #参照元:https://noauto-nolife.com/post/django-show-ip-ua-gateway/
    #参照元:https://noauto-nolife.com/post/django-same-user-operate-prevent/
    ip      = models.GenericIPAddressField(verbose_name="お問い合わせした人のIPアドレス")

    email   = models.EmailField(verbose_name="お問い合わせ送信先Email")
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)


    def __str__(self):
        return self.subject


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print("お問い合わせ承りました。")

        #TODO:ここにメール送信をする。

        subject = "お問い合わせ承りました"
        message = "お問い合わせ承りました\n\n" + "件名:" + self.subject + "\n本文:" + self.content 

        #運営からのメールであれば、このようにsettings.pyに書いてあるDEFAULT_FROM_EMAILを読み取り、セットする。
        #ユーザー間の送信であれば、ユーザーモデルからメールアドレスを参照する。
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [ self.email ]

        send_mail(subject, message, from_email, recipient_list)


#TODO:全員に送信するメールの件名、本文を格納するモデルを作る。




#TODO:次回、ここにカートモデル、注文モデル、配送モデルを作りカートに入れて決済し、配送されるまでの一連の流れを作る。Stripeの仕組みの解説。
#TODO:allauthのメールの雛形を編集して、アカウント作成時のメールの内容を書き換える。


class Cart(models.Model):

    dt      = models.DateTimeField(verbose_name="カートに追加された日時",default=timezone.now)
    #TODO:後の決済のため、カートの機能はユーザーが誰であるか特定する必要が有るため、未入力は禁止する
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="カートに入れた人", on_delete=models.CASCADE)

    #TODO:ここで商品モデルとも1対多のリレーションを組んだフィールドを追加する。
    #product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)

    pattern = models.ForeignKey(Pattern, verbose_name="商品に貼り付ける模様", on_delete=models.CASCADE)
    
    #顧客はカートを見るを選び、支払い方法を入力して注文をする。その時、サーバーはカートの中身の商品を全て注文済みへ書き換える。
    #そしてその時、saveメソッドが働き、注文済みがTrueであれば、注文モデルへ複写する(ただし、書き込みにはフォームクラスが必要。フォームクラスを使用した書き込み系のsaveメソッドオーバーライドはforms.pyにて書く)
    ordered = models.BooleanField(verbose_name="注文済み",default=False)
    

class Order(models.Model):

    dt      = models.DateTimeField(verbose_name="注文日時",default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="カートに入れた人", on_delete=models.CASCADE)

    #TODO:ここの2つは1対多で繋がっていると後から値が変わった時、問題が起こる。
    #例えば、顧客がカートに入れて、決済した時100円だったとする。管理者が支払い済みかどうかチェックする時、商品の値段が120円になっていると、決済されていないと誤認されかねない。
    #そのため、流動性のある情報(商品の価格、配送先の住所、貼り付ける模様など)は必ず、1対多で紐付かないフィールドに個別に格納しておいたほうがよい。
    #product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)
    pattern = models.ForeignKey(Pattern, verbose_name="商品に貼り付ける模様", on_delete=models.CASCADE)
    
    #この支払い済みの編集処理は、必ず管理サイトにて、管理者が入金を確認した上で、チェックを入れる。
    #こちらも同様にsaveメソッドが働いて、配送モデルに複写される。
    paid    = models.BooleanField(verbose_name="支払い確認済み",default=False)


class Delivery(models.Model):

    dt      = models.DateTimeField(verbose_name="注文日時",default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="カートに入れた人", on_delete=models.CASCADE)

    #product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)
    pattern = models.ForeignKey(Pattern, verbose_name="商品に貼り付ける模様", on_delete=models.CASCADE)
    
    delivered   = models.BooleanField(verbose_name="配送済み",default=False)


