from typing import List, Tuple
import numpy as np


class OnDoc:
    """
    OnDoc is a helper class for the raw ondocument OCR result. Enables easy extraction
    of common datapoints into usable objects. 
    """

    def __init__(self, ondoc: List[dict]):
        """
        ondoc {List[dict]}: ondocument result object from indico.queries.DocumentExtraction
        """
        self.ondoc = ondoc

    @property
    def full_text(self) -> str:
        """
        Return full document text as string
        """
        return "\n".join(page["pages"][0]["text"] for page in self.ondoc)

    @property
    def page_text(self) -> List[str]:
        """
        Return list of page-level text
        """
        return [page["pages"][0]["text"] for page in self.ondoc]

    @property
    def page_results(self) -> List[dict]:
        """
        Return list of page-level dictionary result objects
        """
        return [page["pages"][0] for page in self.ondoc]

    @property
    def block_text(self) -> List[str]:
        """
        Return list of block-level text
        """
        return [block["text"] for page in self.ondoc for block in page["blocks"]]

    def ocr_confidence(self, metric="mean") -> float:
        """
        Return the average OCR confidence (scale: 0 - 100) for all characters in the document

        metric {str}: options are "mean" or "median"
        """
        if metric not in ("mean", "median"):
            raise Exception(
                f"Metric value must be either mean or median, not '{metric}'"
            )

        if "confidence" not in self.ondoc[0]["chars"][0].keys():
            raise Exception("You are using an old SDK version, confidence is not included")
        
        confidence = [
            character["confidence"]
            for page in self.ondoc
            for character in page["chars"]
        ]
        if metric == "mean":
            return np.mean(confidence)
        return np.median(confidence)
