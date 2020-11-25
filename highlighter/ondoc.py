from typing import List, Tuple


class OnDoc:
    """
    OnDoc is a helper class for the raw ondocument OCR result. Enables easy extraction
    of common datapoints into usable objects. 
    """
    def __init__(self, ondoc: List[dict]):
        self.ondoc = ondoc

    @property
    def full_text(self) -> str:
        """
        Return full document text
        """
        return '\n'.join(page['pages'][0]['text'] for page in self.ondoc)
    
    @property
    def page_text(self) -> List[str]:
        """
        Return list of page-level text
        """
        return list(page['pages'][0]['text'] for page in self.ondoc)

    @property
    def page_results(self)-> List[dict]:
        """
        Return list of page-level dictionary result objects
        """
        return list(page['pages'][0] for page in self.ondoc)

    @property
    def block_text(self) -> List[str]:
        pass

