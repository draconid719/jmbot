from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ChangeEmail, ProfileUpdateForm, ProfileRegisterForm, \
    UserLoginForm, BinanceUpdateForm, PoloniexUpdateForm, BitzUpdateForm, FtxUpdateForm, BittrexUpdateForm, \
    KrakenUpdateForm, KucoinUpdateForm, DigifinexUpdateForm, BwUpdateForm, HuobiproUpdateForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from users.models import Profile
from django.contrib.auth.models import User
from django.views import View
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            form = ProfileRegisterForm(request.POST, instance=user.profile)
            form.save()
            current_site = get_current_site(request)
            mail_subject = _('Activate your wide-bot account.')
            message = render_to_string('users/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            try:
                email.send()
            except Exception as e:
                messages.error(request, _('Can not send you an email. Please contact with admin'))
                return render(request, 'users/register.html', {'form': form})
            messages.info(request, mark_safe((
                str(_('Please confirm your email address to complete the registration.')) + ' <a href="resend/{}/">' +
                str(_('Resend activation link')) + '</a>').format(user.pk)))
            return render(request, 'users/waiting_confirmation.html')
        else:
            messages.info(request, _('Invalid Registration Field'))
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def resend(request, pk):
    current_site = get_current_site(request)
    mail_subject = _('Activate your wide-bot account.')
    user = User.objects.filter(pk=pk).first()
    message = render_to_string('users/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()
    messages.info(request, mark_safe(
        (str(_('Email sent! Please confirm your email address  to complete the registration.')) + ' <a href="resend/{}/">'
         + str(_('Resend activation link')) + '</a> ').format(user.pk)))
    return render(request, 'users/waiting_confirmation.html')


def logout_view(request, *args, **kwargs):
    logout(request)
    return HttpResponseRedirect(reverse('intro-page'))


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('bots-page')
        else:
            return render(request, 'users/login.html', {'form': UserLoginForm})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('bots-page')
            else:
                messages.error(request, 'Error')
                return redirect('login')
        elif User.objects.filter(username=username).first():
            if User.objects.filter(username=username).first().profile.registration_status != "Complete":
                userpk = User.objects.filter(username=username).first().pk
                messages.error(request, mark_safe(
                    (str(_('Account not activated, Please complete registration.')) + '<a href="resend/{}/">' +
                     str(_('Resend activation link')) + '</a> ').format(userpk)))
                return redirect('login')
            else:
                messages.error(request, _('Invalid Password or Username, Please try again'))
                return redirect('login')

        else:
            messages.error(request, _('Invalid Password or Username, Please try again'))
            return redirect('login')


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        binance_form = BinanceUpdateForm(request.POST, instance=request.user.binance)
        poloniex_form = PoloniexUpdateForm(request.POST, instance=request.user.poloniex)
        bitz_form = BitzUpdateForm(request.POST, instance=request.user.bitz)
        kraken_form = KrakenUpdateForm(request.POST, instance=request.user.kraken)
        bittrex_form = BittrexUpdateForm(request.POST, instance=request.user.bittrex)
        kucoin_form = KucoinUpdateForm(request.POST, instance=request.user.kucoin)
        digifinex_form = DigifinexUpdateForm(request.POST, instance=request.user.digifinex)
        bw_form = BwUpdateForm(request.POST, instance=request.user.bw)
        huobipro_form = HuobiproUpdateForm(request.POST, instance=request.user.huobipro)
        ftx_form = FtxUpdateForm(request.POST, instance=request.user.ftx)

        if u_form.is_valid() and p_form.is_valid() and binance_form.is_valid() and poloniex_form.is_valid() and bitz_form.is_valid() and kraken_form.is_valid() and bittrex_form.is_valid() and kucoin_form.is_valid() and digifinex_form.is_valid() and bw_form.is_valid() and huobipro_form.is_valid() and ftx_form.is_valid():
            u_form.save()
            p_form.save()
            binance_form.save()
            poloniex_form.save()
            bitz_form.save()
            kraken_form.save()
            bittrex_form.save()
            kucoin_form.save()
            digifinex_form.save()
            bw_form.save()
            huobipro_form.save()
            ftx_form.save()

            messages.success(request, _('Successfully changed account information'))
            return redirect('profile-page')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        binance_form = BinanceUpdateForm(instance=request.user.binance)
        poloniex_form = PoloniexUpdateForm(instance=request.user.poloniex)
        bitz_form = BitzUpdateForm(instance=request.user.bitz)
        kraken_form = KrakenUpdateForm(instance=request.user.kraken)
        bittrex_form = BittrexUpdateForm(instance=request.user.bittrex)
        kucoin_form = KucoinUpdateForm(instance=request.user.kucoin)
        digifinex_form = DigifinexUpdateForm(instance=request.user.digifinex)
        bw_form = BwUpdateForm(instance=request.user.bw)
        huobipro_form = HuobiproUpdateForm(instance=request.user.huobipro)
        ftx_form = FtxUpdateForm(instance=request.user.ftx)

    context = {'u_form': u_form, 'p_form': p_form, 'binance_form': binance_form,
               'poloniex_form': poloniex_form, 'bitz_form': bitz_form, 'kraken_form': kraken_form,
               'bittrex_form': bittrex_form, 'kucoin_form': kucoin_form, 'digifinex_form': digifinex_form,
               'bw_form': bw_form, 'huobipro_form': huobipro_form, 'ftx_form': ftx_form,
               'home': "", 'backtest': "", 'live': "", 'paper': "", 'arbitrage': "", 'profile': "active", 'mybots': ""}
    return render(request, 'users/profile.html', context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.filter(pk=uid).first()
    except Exception as err:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.profile.registration_status = "Complete"
        user.save()
        messages.success(request, _('Your email has been confirmed. Now you can log in to your account.'))
        return redirect('login')
    else:
        messages.error(request, _('Link invalid'))
        return redirect('login')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, _('Your password was successfully updated!'))
            return redirect('change_password')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


def change_email(request):
    # a common django idiom for forms
    if request.method == 'POST':
        form = ChangeEmail(request.POST)
        user = User.objects.get(username=request.user)
        if form.is_valid():
            # check that emails are the same
            if form.cleaned_data['email1'] == form.cleaned_data['email2']:
                user.profile.email_change = form.cleaned_data['email1']
                # Save the user object here, since we're not dealing with a ModelForm
                user.save()
                current_site = get_current_site(request)
                mail_subject = _('Email change request.')
                message = render_to_string('users/confirmemailchange.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = form.cleaned_data.get('email1')
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                return render(request, 'users/email_waiting_for_confirmation.html')
    # We're presenting them with the empty form if something went wrong
    # and re-displaying. The form's field errors should be printed out in
    # the template
    else:
        form = ChangeEmail()
    return render(request, 'users/email_change.html', {'form': form})


def confirm_email_change(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.profile.email = user.profile.email_change
        user.save()
        messages.success(request, _('Your email has been successfully changed.'))
        return redirect('profile-page')
    else:
        return messages.error(request, _('Link invalid'))


def handler404(request, exception):
    return render(request, 'users/404.html', status=404)


def handler500(request, *args, **argv):
    return render(request, 'users/500.html', status=500)
