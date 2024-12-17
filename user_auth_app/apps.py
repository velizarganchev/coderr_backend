import os
from django.apps import AppConfig
import logging


class UserAuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_auth_app'

    def ready(self):
        import user_auth_app.signals
        self.check_and_create_users()

    def check_and_create_users(self):
        """Prüft, ob die Benutzer existieren, und erstellt sie, falls nicht."""
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token

        flag_file = os.path.join(os.path.dirname(__file__), 'initialized.flag')

        if not os.path.exists(flag_file):
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
