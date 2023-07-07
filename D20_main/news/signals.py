# from django.core.mail import EmailMultiAlternatives
# from django.db.models.signals import m2m_changed
# from django.dispatch import receiver
# from django.template.loader import render_to_string
# from .models import PostCategory, Comment
# from NewsPaper import settings
# from django.db.models.signals import post_save
# from django.core.mail import send_mail
# from django.contrib.auth import get_user_model
#
#
# def send_notifications(preview, pk, title, subscribers):
#     html_contect = render_to_string(
#         'post_add_email.html',
#         {
#             'text': preview,
#             'link': f'{settings.SITE_URL}/news/{pk}'
#         }
#     )
#
#     msg = EmailMultiAlternatives(
#         subject=title,
#         body='',
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=['aleksTest13@yandex.ru'],    # тут пишем to=subscribe для отправки на почту подписчикам, для теста моя
#     )
#     # print(settings.DEFAULT_FROM_EMAIL)
#     msg.attach_alternative(html_contect, 'text/html')
#     msg.send()
#
#
# @receiver(m2m_changed, sender=PostCategory)
# def notify_about_new_post(sender, instance, **kwargs):
#     if kwargs['action'] == 'post_add':
#         categories = instance.category.all()
#         subscribers_emails = []
#
#         for cat in categories:
#             subscribers = cat.subscribers.all()
#             subscribers_emails += [s.email for s in subscribers]
#
#         send_notifications(instance.preview(), instance.pk, instance.title, subscribers_emails)
#

# @receiver(post_save, sender=Comment)     # сигнал на добавление коментария к посту
# def send_comment_notification(sender, instance, created, **kwargs):
#     if created:
#         # Получаем автора поста
#         post_author = instance.post.author
#         # Получаем пользователей, которые подписаны на уведомления
#         subscribed_users = get_user_model().objects.filter(subscriptions__post=instance.post)
#         # Получаем список адресов электронной почты для уведомления
#         recipients = [post_author.email] + list(subscribed_users.values_list('email', flat=True))
#         # Отправляем электронное письмо
#         send_mail(
#             f'Новый комментарий к посту "{instance.post.title}"',
#             f'Пользователь {instance.user.username} оставил комментарий к вашему посту "{instance.post.title}":\n\n{instance.content}',
#             settings.DEFAULT_FROM_EMAIL,
#             recipients,
#             fail_silently=False,
#         )
#
#
# @receiver(post_save, sender=Comment)    #  сигнал на одобрение коментария к посту автора
# def send_comment_reply_notification(sender, instance, created, **kwargs):
#     if created and instance.reply_to:
#         reply_to_author = instance.reply_to.user
#         if reply_to_author != instance.user and reply_to_author.email:
#             send_mail(
#                 f'Вам ответили на комментарий к посту "{instance.post.title}"',
#                 f'Пользователь {instance.user.username} ответил на ваш комментарий к посту "{instance.post.title}":\n\n{instance.content}',
#                 settings.DEFAULT_FROM_EMAIL,
#                 [reply_to_author.email],
#                 fail_silently=False,
#             )
#
