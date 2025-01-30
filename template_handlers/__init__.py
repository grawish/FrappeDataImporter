
from abc import ABC, abstractmethod

class TemplateHandler(ABC):
    @abstractmethod
    def get_fields(self):
        """Return list of fields for the template"""
        pass

    @abstractmethod
    def process_template(self, df):
        """Process the template dataframe before saving"""
        pass
