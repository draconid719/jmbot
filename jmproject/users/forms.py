from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailInput, Widget

from .models import Profile, Binance, Poloniex, Bitz, Ftx, Bittrex, Kraken, Kucoin, Digifinex, Bw, Huobipro
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label=_("email"), required=True)
    username = forms.CharField(label=_("username"), max_length=15, required=True,
                               help_text=_("Username limited to 15 characters"))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(label=_("username"), max_length=15, required=True, help_text=_("Username limited to 15 "
                                                                                              "characters"))

    class Meta:
        model = User
        fields = ['username']


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class ProfileUpdateForm(forms.ModelForm):
    # telegram = forms.CharField(max_length=100, required=False)
    # image = forms.ImageField(required=False)
    email = forms.EmailField(label=_("email"), max_length=100, required=False, disabled=True)

    class Meta:
        model = Profile
        fields = ['email']


class ProfileRegisterForm(forms.ModelForm):
    # telegram = forms.CharField(max_length=100, required=False)
    # image = forms.ImageField(required=False)
    email = forms.EmailField(label=_("email"), max_length=100, required=False)

    class Meta:
        model = Profile
        fields = ['email']


class ChangeEmail(forms.Form):
    email1 = forms.EmailField(label=_(u'Type new Email'))
    email2 = forms.EmailField(label=_(u'Type Email again'))


class BinanceUpdateForm(forms.ModelForm):
    binance_apikey = forms.CharField(label="Binance API Key", max_length=200, required=False)
    binance_secret = forms.CharField(label="Binance Secret", max_length=200, required=False)

    class Meta:
        model = Binance
        fields = ['binance_apikey', 'binance_secret']


class PoloniexUpdateForm(forms.ModelForm):
    poloniex_apikey = forms.CharField(label="Poloniex API Key", max_length=200, required=False)
    poloniex_secret = forms.CharField(label="Poloniex Secret", max_length=200, required=False)

    class Meta:
        model = Poloniex
        fields = ['poloniex_apikey', 'poloniex_secret']


class BitzUpdateForm(forms.ModelForm):
    bitz_apikey = forms.CharField(label="BitZ API Key", max_length=200, required=False)
    bitz_secret = forms.CharField(label="BitZ Secret", max_length=200, required=False)

    class Meta:
        model = Bitz
        fields = ['bitz_apikey', 'bitz_secret']


class KrakenUpdateForm(forms.ModelForm):
    kraken_apikey = forms.CharField(label="Kraken API Key", max_length=200, required=False)
    kraken_secret = forms.CharField(label="Kraken Secret", max_length=200, required=False)

    class Meta:
        model = Kraken
        fields = ['kraken_apikey', 'kraken_secret']


class BittrexUpdateForm(forms.ModelForm):
    bittrex_apikey = forms.CharField(label="Bittrex API Key", max_length=200, required=False)
    bittrex_secret = forms.CharField(label="Bittrex Secret", max_length=200, required=False)

    class Meta:
        model = Bittrex
        fields = ['bittrex_apikey', 'bittrex_secret']


class KucoinUpdateForm(forms.ModelForm):
    kucoin_apikey = forms.CharField(label="KuCoin API Key", max_length=200, required=False)
    kucoin_secret = forms.CharField(label="KuCoin Secret", max_length=200, required=False)
    kucoin_password = forms.CharField(label="KuCoin Password", max_length=200, required=False)

    class Meta:
        model = Kucoin
        fields = ['kucoin_apikey', 'kucoin_secret', 'kucoin_password']


class DigifinexUpdateForm(forms.ModelForm):
    digifinex_apikey = forms.CharField(label="DigiFinex API Key", max_length=200, required=False)
    digifinex_secret = forms.CharField(label="DigiFinex Secret", max_length=200, required=False)

    class Meta:
        model = Digifinex
        fields = ['digifinex_apikey', 'digifinex_secret']


class BwUpdateForm(forms.ModelForm):
    bw_apikey = forms.CharField(label="BW API Key", max_length=200, required=False)
    bw_secret = forms.CharField(label="BW Secret", max_length=200, required=False)

    class Meta:
        model = Bw
        fields = ['bw_apikey', 'bw_secret']


class HuobiproUpdateForm(forms.ModelForm):
    huobipro_apikey = forms.CharField(label="Huobi Pro API Key", max_length=200, required=False)
    huobipro_secret = forms.CharField(label="Huobi Pro Secret", max_length=200, required=False)

    class Meta:
        model = Huobipro
        fields = ['huobipro_apikey', 'huobipro_secret']


class FtxUpdateForm(forms.ModelForm):
    ftx_apikey = forms.CharField(label="FTX API Key", max_length=200, required=False)
    ftx_secret = forms.CharField(label="FTX Secret", max_length=200, required=False)

    class Meta:
        model = Ftx
        fields = ['ftx_apikey', 'ftx_secret']
