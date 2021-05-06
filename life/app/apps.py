from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LifeConfig(AppConfig):
    name = "app"
    verbose_name = _("Life Tools")

    def ready(self):
        try:
            import life.app.signals  # noqa F401
        except ImportError:
            pass
