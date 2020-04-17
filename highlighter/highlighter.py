from typing import List, Tuple
from pdf_annotate import PdfAnnotator, Location, Appearance
from collections import defaultdict
import fitz
from .ondoc import OnDoc


class Highlighter:
    def __init__(self, ocr_result: List[dict]):
        """
        Map annotation predictions to pdf token positions from 'ondocument' OCR and highlight onto 
        the source pdf.
        
        Arguments:
            ondoc {List[dict]} -- ocr output from DocumentExtraction w/ ondocument preset
        """
        if isinstance(ocr_result, OnDoc):
            self.ocr_result = ocr_result
        else:
            self.ocr_result = OnDoc(ocr_result)
        self.prediction_positions = None

    def collect_positions(
        self, predictions: List[List[dict]], inplace: bool = True
    ) -> List[dict]:
        """
        Gets the predicted tokens positions on the PDF
        
        Arguments:
            predictions {List[List[dict]]} -- prediction output from ModelGroupPredict
        
        Returns:
            List[dict] -- locations of predictions
        """
        prediction_positions = []
        for page_ocr, page_preds in zip(self.ocr_result.ondoc, predictions):
            result = defaultdict(list)
            meta = page_ocr["pages"][0]
            result["dimensions"].extend([meta["size"]["width"], meta["size"]["height"]])
            result["page_num"] = meta["page_num"]
            page_preds = sorted(page_preds, key=lambda x: x["start"])
            for pred in page_preds:
                start, end = (
                    pred["start"] - 1,
                    pred["end"] + 1,
                )  # account for punctuation incl. w/ token
                for token in page_ocr["tokens"]:
                    if (
                        token["page_offset"]["start"] >= start
                        and token["page_offset"]["end"] <= end
                    ):
                        result["positions"].append(token["position"])
            prediction_positions.append(result)
        if not inplace:
            return prediction_positions
        self.prediction_positions = prediction_positions

    def highlight_pdf(
        self,
        pdf_path: str,
        output_path: str,
        highlight_rgb: List[int] = [255, 255, 0],
        transparency: float = 0.4,
    ) -> None:
        """
        Highlights predictions onto a copy of source PDF
        
        Arguments:
            pdf_path {str} -- path to source PDF
            output_path {str} -- path of labeled PDF copy to create (set to same as pdf_path to overwrite)
            highlight_rgb {List[int]} -- rgb color for highlight (default: yellow)
            transparency {float} -- highlight transparency (default: 0.4)
        """
        my_pdf = PdfAnnotator(pdf_path, scale=72 / 300)
        highlight_rgb = tuple(rgb / 255 for rgb in highlight_rgb)
        for page in self.prediction_positions:
            if not page["positions"]:
                print(f"No predicted annotations on page {page['page_num']}")
                continue
            for loc in page["positions"]:
                my_pdf.add_annotation(
                    "square",
                    Location(
                        x1=loc["bbLeft"],
                        y1=page["dimensions"][1] - loc["bbTop"],
                        x2=loc["bbRight"],
                        y2=page["dimensions"][1] - loc["bbBot"],
                        page=page["page_num"],
                    ),
                    Appearance(
                        stroke_color=highlight_rgb,
                        stroke_width=0.1,
                        fill=highlight_rgb,
                        fill_transparency=transparency,
                    ),
                )
        my_pdf.write(output_path)


    def pymudf_highlight(self, pdf_path, output_path):
        """
        Highlights predictions onto a copy of source PDF. 
        Implementation w/ pymudf
        
        Arguments:
            pdf_path {str} -- path to source PDF
            output_path {str} -- path of labeled PDF copy to create (set to same as pdf_path to overwrite)
        """
        doc = fitz.open(pdf_path)
        for preds in self.prediction_positions:
            page = doc[preds['page_num']]
            xnorm = page.rect[2] / preds['dimensions'][0]
            ynorm = page.rect[3] / preds['dimensions'][1]
            for token in preds['positions']:
                annotation = fitz.Rect(
                    token['bbLeft'] * xnorm, 
                    token['bbTop'] * ynorm,
                    token['bbRight'] * xnorm,
                    token['bbBot'] * ynorm,
                )
                page.addHighlightAnnot(annotation)
        doc.save(output_path)
