from typing import List
from collections import defaultdict
import fitz
from fitz.utils import getColor
from faker import Faker
import copy
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
        self.prediction_positions: List[dict] = None

    @staticmethod
    def _match_page_predict(
        predictions: List[dict],
        page_ocr: dict,
        include_pred_text: bool = False,
        offset_text: str = "doc_offset",
    ) -> dict:
        """
        Use doc_offset or page_offset to get bounding boxes for each token of page's predictions
        """
        result = defaultdict(list)
        meta = page_ocr["pages"][0]
        result["dimensions"].extend([meta["size"]["width"], meta["size"]["height"]])
        result["page_num"] = meta["page_num"]
        result["labels"] = defaultdict(int)
        for pred in predictions:
            result["labels"][pred["label"]] += 1
            start, end = (
                pred["start"] - 1,
                pred["end"] + 1,
            )
            new_prediction = True
            position = dict()
            for token in page_ocr["tokens"]:
                if (
                    token[offset_text]["start"] >= start
                    and token[offset_text]["end"] <= end
                ):
                    if new_prediction:
                        position = copy.deepcopy(token["position"])
                        if include_pred_text:
                            position["full_text"] = pred["text"]
                        position["label"] = (
                            pred["label"],
                            len(pred["text"]),
                        )  # length for spoofing
                        new_prediction = False
                    elif token["position"]["bbTop"] > position["bbBot"]:
                        result["positions"].append(position)
                        position = copy.deepcopy(token["position"])
                        position["label"] = (
                            pred["label"],
                            len(pred["text"]),
                        )
                    else:
                        position["bbRight"] = token["position"]["bbRight"]
            if position:
                result["positions"].append(position)
        return result

    def collect_positions(
        self,
        predictions: List[List[dict]],
        inplace: bool = True,
        include_pred_text: bool = False,
    ) -> List[dict]:
        """
        Gets the predicted tokens positions from a full document prediction output json
        
        Arguments:
            predictions {List[List[dict]]} -- prediction output from ModelGroupPredict
            include_pred_text {bool} -- whether to include the text of the prediction with the positional data
        
        Returns:
            List[dict] -- locations of predictions
        """
        prediction_positions = []
        sorted_preds = sorted(predictions[0], key=lambda x: x["start"])

        for page_ocr in self.ocr_result.ondoc:
            max_page_offset = page_ocr["tokens"][-1]["doc_offset"]["end"]
            if max_page_offset < sorted_preds[0]["start"]:
                continue
            page_preds = []
            for i, pred in enumerate(sorted_preds):
                if pred["start"] > max_page_offset:
                    sorted_preds = sorted_preds[i:]
                    break
                else:
                    page_preds.append(pred)
            if not page_preds:
                continue
            result = self._match_page_predict(page_preds, page_ocr, include_pred_text)
            prediction_positions.append(result)

        if not inplace:
            return prediction_positions
        self.prediction_positions = prediction_positions

    def collect_page_wise_positions(
        self,
        predictions: List[List[dict]],
        inplace: bool = True,
        include_pred_text: bool = False,
    ) -> List[dict]:
        """
        Gets the predicted tokens positions given page-wise prediection results 
        (i.e. a document's pages separated and individually sent to the model)
        
        Arguments:
            predictions {List[List[dict]]} -- prediction output from ModelGroupPredict
            include_pred_text {bool} -- whether to include the text of the prediction with the positional data
        
        Returns:
            List[dict] -- locations of predictions
        """
        prediction_positions = []
        for page_ocr, page_preds in zip(self.ocr_result.ondoc, predictions):
            page_preds = sorted(page_preds, key=lambda x: x["start"])
            result = self._match_page_predict(
                page_preds, page_ocr, include_pred_text, "page_offset"
            )
            prediction_positions.append(result)
        if not inplace:
            return prediction_positions
        self.prediction_positions = prediction_positions

    def highlight_pdf(
        self, pdf_path: str, output_path: str, include_toc: bool = False, color_map=None
    ):
        """
        Highlights predictions onto a copy of source PDF with the option to include a table of contents
        
        Arguments:
            pdf_path {str} -- path to source PDF
            output_path {str} -- path of labeled PDF copy to create (set to same as pdf_path to overwrite)
            include_toc {bool} -- if True, insert a table of contents of what annotations were made and on what page
        """
        if not color_map:
            color_map = defaultdict(lambda: "yellow")
        doc = fitz.open(pdf_path)
        for preds in self.prediction_positions:
            page = doc[preds["page_num"]]
            xnorm = page.rect[2] / preds["dimensions"][0]
            ynorm = page.rect[3] / preds["dimensions"][1]
            for token in preds["positions"]:
                annotation = fitz.Rect(
                    token["bbLeft"] * xnorm,
                    token["bbTop"] * ynorm,
                    token["bbRight"] * xnorm,
                    token["bbBot"] * ynorm,
                )
                if not "label" in token:
                    raise AssertionError("All tokens must have a label attribute")
                color = color_map[token["label"][0]]
                ann = page.addHighlightAnnot(annotation)
                ann.setOpacity(0.5)
                ann.setColors(stroke=getColor(color))
                ann.update()

        if include_toc:
            toc_text = self.get_toc_text(pdf_path)
            doc.insertPage(0, text=toc_text, fontsize=13)
        doc.save(output_path)

    def redact_pdf(self, pdf_path: str, output_path: str, color_black: bool = True):
        """
        Redact predicted text from a copy of a source PDF. Currently, you still need to convert 
        your PDF to image files afterward to ensure PI is fully removed from the underlying data.
        
        Arguments:
            pdf_path {str} -- path to source PDF
            output_path {str} -- path of labeled PDF copy to create (set to same as pdf_path to overwrite)
            color_black {bool} -- if True, redactions are made with a black mark, else they are made with a white mark
        """
        if color_black:
            color = (0, 0, 0)
        else:
            color = (1, 1, 1)
        doc = fitz.open(pdf_path)
        for preds in self.prediction_positions:
            page = doc[preds["page_num"]]
            xnorm = page.rect[2] / preds["dimensions"][0]
            ynorm = page.rect[3] / preds["dimensions"][1]
            for token in preds["positions"]:
                annotation = fitz.Rect(
                    token["bbLeft"] * xnorm,
                    token["bbTop"] * ynorm,
                    token["bbRight"] * xnorm,
                    token["bbBot"] * ynorm,
                )
                inflater = annotation.height * 0.1
                annotation.x0, annotation.y0 = (
                    annotation.x0 - inflater,
                    annotation.y0 - inflater,
                )
                annotation.x1, annotation.y1 = (
                    annotation.x1 + inflater,
                    annotation.y1 + inflater,
                )
                page.addRedactAnnot(annotation, fill=color)
            page.apply_redactions()
        doc.save(output_path)
        print(
            f"*Important* to ensure that underlying data can't be recovered, convert {output_path} to a png, tif, or scanned pdf file"
        )

    def redact_and_replace(self, pdf_path: str, output_path: str, fill_text: dict):
        """
        Redact predicted text from a copy of a source PDF and replace if with fake values based on 
        label keys. For a full list of fake data options, see: https://github.com/joke2k/faker). 
        
        Arguments:
            pdf_path {str} -- path to source PDF
            output_path {str} -- path of labeled PDF copy to create (set to same as pdf_path to overwrite)
            fill_text {dict} -- a dictionary where the keys are your labels and the val is an option from the 
                                faker library. Possible options include 'text', 'company', 'currency', 'numerify', 
                                'address', 'name', 'company_email', 'date' and many more. With 'numerify' and 
                                'text', fake data will match the length of the redacted data.

        Example:
            # add a key to fill_text for each label in your extraction task w/ allowed fake data method
            fill_text = dict(member='name', birthday='date', invoice_number='numerify')
            highlight.redact_and_replace('source.pdf', 'redacted.pdf', fill_text=fill_text)
        """
        fake = Faker()
        doc = fitz.open(pdf_path)
        for preds in self.prediction_positions:
            page = doc[preds["page_num"]]
            xnorm = page.rect[2] / preds["dimensions"][0]
            ynorm = page.rect[3] / preds["dimensions"][1]
            for token in preds["positions"]:
                annotation = fitz.Rect(
                    token["bbLeft"] * xnorm,
                    token["bbTop"] * ynorm,
                    token["bbRight"] * xnorm,
                    token["bbBot"] * ynorm,
                )
                inflater = annotation.height * 0.1
                annotation.x0, annotation.y0 = (
                    annotation.x0 - inflater,
                    annotation.y0 - inflater,
                )
                annotation.x1, annotation.y1 = (
                    annotation.x1 + inflater,
                    annotation.y1 + inflater,
                )
                if "label" in token:
                    label_type = fill_text[token["label"][0]]
                    if label_type == "numerify":
                        text = getattr(fake, label_type)(token["label"][1] * "#")
                    elif label_type == "text":
                        text = getattr(fake, label_type)(token["label"][1])
                    else:
                        text = getattr(fake, label_type)()
                    page.addRedactAnnot(
                        annotation, text=text, fill=(1, 1, 1), fontsize=15
                    )
                else:
                    # second line of single prediction redacted
                    page.addRedactAnnot(annotation, fill=(1, 1, 1))
                page.apply_redactions()
        doc.save(output_path)
        print(
            f"*Important* to ensure that underlying data can't be recovered, convert {output_path} to a png, tif, or scanned pdf file"
        )

    def get_toc_text(self, filename: str):
        """
        If a table of contents is requested, formats and returns the page text
        
        Arguments:
            filename {str} -- name of the pdf file
        Returns:
            {str} -- page text for the table of contents
        """
        base_text = f"File: {filename}\n\nPages w/ Extractions found:\n\n"
        page_strings = list()
        for page in self.prediction_positions:
            if page["labels"]:
                start = f"Page {page['page_num'] + 1}: "
                content = ", ".join(
                    f"{key} ({val})" for key, val in page["labels"].items()
                )
                page_strings.append(start + content)
        return base_text + "\n".join(page_strings)
