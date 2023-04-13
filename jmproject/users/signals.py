from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Binance, Poloniex, Bitz, Ftx, Bittrex, Kraken, Kucoin, Digifinex, Bw, Huobipro


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Binance.objects.create(user=instance)
        Poloniex.objects.create(user=instance)
        Bitz.objects.create(user=instance)
        Ftx.objects.create(user=instance)
        Kraken.objects.create(user=instance)
        Bittrex.objects.create(user=instance)
        Kucoin.objects.create(user=instance)
        Digifinex.objects.create(user=instance)
        Bw.objects.create(user=instance)
        Huobipro.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
    instance.binance.save()
    instance.poloniex.save()
    instance.bitz.save()
    instance.ftx.save()
    instance.kraken.save()
    instance.bittrex.save()
    instance.kucoin.save()
    instance.digifinex.save()
    instance.bw.save()
    instance.huobipro.save()
