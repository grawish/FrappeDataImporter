
from abc import ABC, abstractmethod
from numpy import void
import pandas as pd
from typing import Tuple, Optional

class TemplateHandler(ABC):

    connection_id: str
    
    """Base class for doctype-specific template handlers"""
    
    def get_fields(self, selected_fields=None) -> list:
        """Return list of fields to include in the template
        
        Args:
            selected_fields: List of fields selected from the frontend
            
        Returns:
            list: List of field definitions
        """
        if not selected_fields:
            return []
            
        # Get base selected fields
        return selected_fields.copy()

    @abstractmethod
    def process_template(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """Process the template dataframe before saving
        
        Args:
            df: Template dataframe with columns from get_fields()
            
        Returns:
            Tuple[DataFrame, Optional[DataFrame]]: 
                - First DataFrame: Main processed template dataframe
                - Second DataFrame: Optional filtered dataframe for child tables/special handling
        """
        return df, None

