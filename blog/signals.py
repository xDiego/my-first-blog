from django.dispatch import Signal

update_num_post = Signal(providing_args=['blog'])
