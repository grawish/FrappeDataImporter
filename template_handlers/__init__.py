
from abc import ABC, abstractmethod
import pandas as pd

class TemplateHandler(ABC):
    """Base class for doctype-specific template handlers"""
    
    def get_fields(self, selected_fields=None) -> list:
        """Return list of fields to include in the template
        
        Args:
            selected_fields: List of fields selected from the frontend
            
        Returns:
            list: List of field definitions in format "fieldname [type] [options]"
        """
        return selected_fields if selected_fields else []

    @abstractmethod
    def process_template(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process the template dataframe before saving
        
        Args:
            df: Template dataframe with columns from get_fields()
            
        Returns:
            DataFrame: Processed template dataframe
        """
        pass
