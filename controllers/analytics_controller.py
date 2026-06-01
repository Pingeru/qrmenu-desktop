"""Controller for business analytics actions."""

from models.analytics_model import AnalyticsModel


class AnalyticsController:
    def __init__(self, analytics_model: AnalyticsModel | None = None):
        self.analytics_model = analytics_model or AnalyticsModel()

    def load_summary(self, from_date: str | None = None, to_date: str | None = None):
        return self.analytics_model.get_business_analytics(from_date=from_date, to_date=to_date)
