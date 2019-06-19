from django.urls import path
from authentication import views

app_name = 'authentication'

urlpatterns = [
    path('login_user/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout'),
    path('show_messages/<str:tname>/', views.show_messages, name='show_messages'),
    path('register_student/', views.register_student, name='register_student'),
    path('register_teacher/', views.register_teacher, name='register_teacher'),
    path('home/', views.home_page, name='publish_message'),
    path('publish_message/<int:t_id>/', views.publish_message, name='message_content'),
    path('publish_encrypt_key/', views.publish_encrypt_key, name='publish_encrypt_key'),
    path('publish_encrypt_message/<str:key>/', views.publish_encrypted_message, name='publish_encrypt_message'),
    path('receive_file/', views.receive_file, name='receive_file'),
    path('start_send_msg_enc/', views.start_key_message, name='start_key_msg'),
    path('receive_key/', views.receive_key, name='receive_key'),
    path('send_file/', views.send_file, name='send_file'),
    path('start_send_file/', views.start_file_send, name='send_actual_file'),
    path('snd_file/<str:fname>/', views.snd_file, name='snd_file'),
    path('publish_options/<int:t_id>/', views.publish_options, name='publish_options'),
    path('subscribe_options/', views.subscribe_options, name='subscribe_options'),
    path('subscribe_file/', views.subscribe_file, name='subscribe_file'),
    path('subscribe/<int:t_id>/', views.subs, name='subscribe'),
    path('new_topic/', views.tpc, name='create_topic'),
]
