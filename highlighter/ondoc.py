from typing import List, Tuple


class OnDoc:
    """
    OnDoc is a helper class for the raw ondocument OCR result. Enables easy extraction
    of common datapoints into usable objects. 
    """
    def __init__(self, ondoc: List[dict]):
        self.ondoc = ondoc

    @property
    def page_text(self) -> List[str]:
        page_text = list()
        for page in self.ondoc:
            page_text.append(page['pages'][0]['text'])
        return page_text

    @property
    def page_results(self)-> List[dict]:
        page_results = list()
        for page in self.ondoc:
            page_results.append(page['pages'][0])
        return page_results

    @property
    def block_text(self) -> List[str]:
        pass

