from django.urls import include, path
from . import views
from .views import BotCreateView, BotUpdateView, BotDeleteView, ArbitrageBotCreateView, ArbitrageBotUpdateView, \
    ArbitrageBotDeleteView
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n'))
]

urlpatterns += [
    path('', views.intro, name='intro-page'),
    path('account/', views.account, name='account-page'),
    path('contactus/', views.contactus, name='contactus-page'),
    path('return/', views.returnview, name='return'),
    path('manual/<slug:slug>/', views.manual_page, name='manual-page'),
    path('mybots/<int:pk>/trade/', views.do_trade, name='trade-page'),
    path('myarbitragebots/<int:pk>/trade', views.arbtrade, name='arbtrade-page'),
    path('aboutus/', views.about_us, name='aboutus-page'),
    path('chat/', views.chat, name='chat-page'),
    path('mybots/<slug:slug>/', views.my_bots, name='mybots-page'),
    path('mybots/filter/<slug:slug>/', views.filter, name='mybots-filter-page'),
    path('bots/', views.get_bots, name='bots-page'),
    path('bots/mine', views.get_bots, name='my-bots-page'),
    path('bots/<int:pk>/detail/', views.bot_detail, name='detail-bot-page'),
    path('bots/<int:pk>/copy/', views.copy_bot, name='copy_bot'),
    path('activity/', views.activity, name='activity'),
    path('activity/bots/<int:pk>', views.activity, name='bot-activity'),
    path('botrank/', views.ranking, name='ranking-page'),
    path('bots/create', BotCreateView.as_view(), name='create-bot-page'),
    # path('faq/', views.faq, name='faq-page'),
    path('bots/<int:pk>/edit/', BotUpdateView.as_view(), name='edit-bot-page'),
    path('bots/<int:pk>/delete/', BotDeleteView.as_view(), name='delete-bot-page'),
    path('mybots/<int:pk>/detail/', views.bot_detail, name='detailbot-page'),
    path('newarbitragebot/', ArbitrageBotCreateView.as_view(), name='createarbit-page'),
    path('myarbitragebots/', views.myarbitragebots, name='myarbitbots-page'),
    path('myarbitragebots/filter/<slug:slug>/', views.arbfilter, name='myarbitbots-filter-page'),
    path('myarbitragebots/<int:pk>/detail', views.arbbotdetail, name='myarbitbotsdetail-page'),
    path('myarbitragebots/<int:pk>/modifybot/', ArbitrageBotUpdateView.as_view(), name='modifyarbitbot-page'),
    path('myarbitragebots/<int:pk>/deletebot/', ArbitrageBotDeleteView.as_view(), name='deletearbitbot-page'),
    path('price/currentPrice', views.get_current_price, name='currentPrice'),
    # path('bot_test', views.test_page, name='bot-test'),
    url(r'^deletetrade/$', views.delete_trade),
    url(r'^buy/$', views.exchange_buy),
    url(r'^sell/$', views.exchange_sell),
    url(r'^backtest/startback/$', views.createbacktest),
    url(r'^live/startlive/$', views.create_live),
    url(r'^live/countidata/$', views.live_tornado),
    url(r'^live/elapsed/$', views.elapsed),
    url(r'^live/manual/countidata/$', views.manualtornado),
    url(r'^paper/stoplive/$', views.deactivate_live),
    url(r'^paper/getlivestatus/$', views.get_live_status),
    url(r'^paper/getarblivestatus/$', views.getarblivestatus),
    url(r'^paper/stoplivearbitrage/$', views.deactivatelivearb),
    url(r'^arbitrage/startlivearbitrage/$', views.createlivearbitrage),
    url(r'^arbitrage/countidata/$', views.arbitragetornado),
    url(r'^arbitrage/exchangeslive/$', views.arbitrageExchangelive),
    url(r'^shout/publish/$', views.publish),
    url(r'^shout/load/$', views.load),
    url(r'^shout/newmessage/$', views.ping, name='newmessage'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
