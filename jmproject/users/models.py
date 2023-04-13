from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import json


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # image = models.ImageField(default= 'default.png', upload_to='profile_pics')
    telegram = models.CharField(max_length=100)
    email = models.EmailField()
    # api = models.OneToOneField(API, on_delete=models.CASCADE, null=True)
    registration_status = models.TextField(null=True)
    sorting_preference = models.CharField(null=False, max_length=100, default='-profit')
    chat_visit = models.DateTimeField(null=True)
    received_notification = models.DateTimeField(null=True)
    received_new_bot_notification = models.CharField(null=True, max_length=100)
    email_change = models.EmailField(null=True)

    def __str__(self):
        return '{} Profile'.format(self.user.username)

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

    # img = Image.open(self.image.path)

    # if img.height > 300 or img.width > 300:
    # 	output_size = (300, 300)
    # 	img.thumbnail(output_size)
    # 	img.save(self.image.path)


class Binance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    binance_apikey = models.TextField()
    binance_secret = models.TextField()
    fees = models.TextField(null=True)

    def __str__(self):
        return str(self.binance_apikey) + '*******'

    def save(self, *args, **kwargs):
        super(Binance, self).save(*args, **kwargs)


class Poloniex(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    poloniex_apikey = models.TextField()
    poloniex_secret = models.TextField()
    fees = models.TextField(null=True)

    def __str__(self):
        return str(self.poloniex_apikey) + '*******'

    def save(self, *args, **kwargs):
        super(Poloniex, self).save(*args, **kwargs)


class Bitz(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    bitz_apikey = models.TextField()
    bitz_secret = models.TextField()

    def __str__(self):
        return str(self.bitz_apikey) + '*******'

    def save(self, *args, **kwargs):
        super(Bitz, self).save(*args, **kwargs)


class Ftx(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    ftx_apikey = models.TextField()
    ftx_secret = models.TextField()

    def __str__(self):
        return str(self.ftx_apikey) + '*******'

    def save(self, *args, **kwargs):
        super(Ftx, self).save(*args, **kwargs)


class Kraken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    kraken_apikey = models.TextField()
    kraken_secret = models.TextField()

    def __str__(self):
        return str(self.kraken_apikey) + '*******'

    def save(self, *args, **kwargs):
        super(Kraken, self).save(*args, **kwargs)


class Bittrex(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    bittrex_apikey = models.TextField()
    bittrex_secret = models.TextField()

    def __str__(self):
        return str(self.bittrex_apikey[:4]) + '*******'

    def save(self, *args, **kwargs):
        super(Bittrex, self).save(*args, **kwargs)


class Kucoin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    kucoin_apikey = models.TextField()
    kucoin_secret = models.TextField()
    kucoin_password = models.TextField(default='')

    def __str__(self):
        return str(self.kucoin_apikey[:4]) + '*******'

    def save(self, *args, **kwargs):
        super(Kucoin, self).save(*args, **kwargs)


class Digifinex(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    digifinex_apikey = models.TextField()
    digifinex_secret = models.TextField()

    def __str__(self):
        return str(self.digifinex_apikey[:4]) + '*******'

    def save(self, *args, **kwargs):
        super(Digifinex, self).save(*args, **kwargs)


class Bw(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    bw_apikey = models.TextField()
    bw_secret = models.TextField()

    def __str__(self):
        return str(self.bw_apikey[:4]) + '*******'

    def save(self, *args, **kwargs):
        super(Bw, self).save(*args, **kwargs)


class Huobipro(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    huobipro_apikey = models.TextField()
    huobipro_secret = models.TextField()

    def __str__(self):
        return str(self.huobipro_apikey[:4]) + '******'

    def save(self, *args, **kwargs):
        super(Huobipro, self).save(*args, **kwargs)
