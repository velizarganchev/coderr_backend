import os
import logging
from django.apps import AppConfig


class UserAuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_auth_app'

    def ready(self):
        import user_auth_app.signals

        from django.db.models.signals import post_migrate
        from django.contrib.auth.models import User
        from django.db import connection

        def create_default_users(sender, **kwargs):
            """
            Create default users after migrations are applied.
            """
            flag_file = os.path.join(
                os.path.dirname(__file__), 'initialized.flag')

            if not os.path.exists(flag_file) and 'auth_user' in connection.introspection.table_names():
                from rest_framework.authtoken.models import Token
                users_to_create = [
                    {"username": "andrey", "password": "asdasd",
                        'type': 'customer', "is_staff": False},
                    {"username": "kevin", "password": "asdasd24",
                        'type': 'business', "is_staff": True},
                ]

                for user_data in users_to_create:
                    if not User.objects.filter(username=user_data["username"]).exists():
                        user = User.objects.create_user(
                            username=user_data["username"],
                            password=user_data["password"],
                            is_staff=user_data.get("is_staff", False),
                        )
                        user.userprofile.type = user_data["type"]
                        user.userprofile.save()
                        Token.objects.create(user=user)
                        logging.info(f"User {user_data['username']} created.")
                    else:
                        logging.info(
                            f"User {user_data['username']} already exists.")

                with open(flag_file, 'w') as f:
                    f.write('initialized')

        post_migrate.connect(create_default_users, sender=self)
