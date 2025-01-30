
from abc import ABC, abstractmethod
import pandas as pd

class TemplateHandler(ABC):
    """Base class for doctype-specific template handlers"""
    
    @abstractmethod
    def get_fields(self) -> list:
        """Return list of fields to include in the template
        
        Returns:
            list: List of field definitions in format "fieldname [type] [options]"
        """
        pass

    @abstractmethod
    def process_template(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process the template dataframe before saving
        
        Args:
            df: Template dataframe with columns from get_fields()
            
        Returns:
            DataFrame: Processed template dataframe
        """
        pass
