from abc import ABC, abstractmethod


class CRMStrategyInterface(ABC):

    @abstractmethod
    def _get_access_token(self):
        pass

    @abstractmethod
    def create_or_update_contact(self, email, properties):
        pass

    @abstractmethod
    def create_or_update_deal(self, contact_id, deal_data, deal_pipeline_id):
        pass

    @abstractmethod
    def create_support_ticket(self, contact_id, deal_id, properties):
        pass
