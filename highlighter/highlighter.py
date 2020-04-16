from typing import List, Tuple
from pdf_annotate import PdfAnnotator, Location, Appearance 
from collections import defaultdict
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


    def collect_positions(self, predictions: List[List[dict]], inplace: bool = True) -> List[dict]:
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
            meta = page_ocr['pages'][0]
            result['dimensions'].extend([meta['size']['height'], meta['size']['width']])
            result['page_num'] = meta['page_num']
            page_preds = sorted(page_preds, key=lambda x: x["start"])            
            for pred in page_preds:
                start, end = pred['start'], pred['end'] + 1 # account for punctuation incl. w/ token
                for token in page_ocr['tokens']:
                    if token['page_offset']['start'] >= start and token['page_offset']['end'] <= end:
                        result['positions'].append(token['position'])
            prediction_positions.append(result)
        if not inplace:
            return prediction_positions
        self.prediction_positions = prediction_positions



    def highlight_pdf(self, pdf_path: str, output_path: str) -> None:
        """
        Highlights predictions onto a copy of source PDF
        
        Arguments:
            pdf_path {str} -- path to source PDF
            output_path {str} -- path of labeled PDF copy to create (set to same as pdf_path to overwrite)
        """
        my_pdf = PdfAnnotator(pdf_path, scale=72/300)
        for page in self.prediction_positions:
            if not page['positions']:
                print(f"No predicted annotations on page {page['page_num']}")
                continue
            for loc in page['positions']:
                my_pdf.add_annotation(
                    'square',
                    Location(
                        x1=loc['bbLeft'], 
                        y1=page['dimensions'][0] - loc['bbTop'], 
                        x2=loc['bbRight'], 
                        y2=page['dimensions'][0] - loc['bbBot'], 
                        page=page['page_num']
                    ),
                    Appearance(stroke_color=(1, 1, 0), 
                            stroke_width=.1, 
                            fill=(1, 1, 0), 
                            fill_transparency=0.4),
                )
        my_pdf.write(output_path)
