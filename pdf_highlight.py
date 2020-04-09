#!/usr/bin/env python
"""
Assumes you have a trained extraction model. Given the path to a PDF document, 
OCRs that pdf document (w/ preset_config='ondocument') and then gets predicted
annotations. Next with the OCR and prediction results, highlights the 
annotations to a copy of the source PDF document.

Chang the specifications on the global variables to your paths/host/model. 
"""
from typing import List, Tuple
from pdf_annotate import PdfAnnotator, Location, Appearance 
from indico import IndicoClient, IndicoConfig
from indico.queries import (DocumentExtraction, JobStatus, 
                            ModelGroupPredict, RetrieveStorageObject)

# NOTE: CHANGE BELOW FOR YOUR SPECIFICATIONS
PDF_PATH = './new_pdf_example.pdf'
OUTPUT_PATH = './pdf_example_w_labels.pdf'
TOKEN_PATH = './indico_api_token.txt'
HOST = 'app.indico.io'
MODEL_ID = 24333


def collect_token_positions(predictions, ocr_result):
    doc_positions = []
    unique_labels = set()
    for page_num, pred_list in enumerate(predictions):
        page_positions = []
        pred_list = sorted(pred_list, key=lambda x: x["start"])
        page_tokens = ocr_result[page_num]['tokens']
        for pred in pred_list:
            start, end = pred['start'], pred['end'] + 1 # account for punctuation incl. w/ token
            for token in page_tokens:
                if token['page_offset']['start'] >= start and token['page_offset']['end'] <= end:
                    position_data = token['position']
                    position_data['label'] = pred['label']
                    unique_labels.add(pred['label'])
                    page_positions.append(position_data)
        doc_positions.append(page_positions)
    return doc_positions, unique_labels



def highlight_pdf(pdf_path, output_path, doc_positions):
    my_pdf = PdfAnnotator(pdf_path, scale=72/300)

    for page_num, page in enumerate(doc_positions):
        for loc in page:
            my_pdf.add_annotation(
                'square',
                Location(
                    x1=loc['bbLeft'], 
                    y1=3300-loc['bbTop'], 
                    x2=loc['bbRight'], 
                    y2=3300-loc['bbBot'], 
                    page=page_num
                ),
                Appearance(stroke_color=(1, 1, 0), 
                        stroke_width=.1, 
                        fill=(1, 1, 0), 
                        fill_transparency=0.4),
            )

    my_pdf.write(output_path)


def get_client(host=HOST, api_token_path=TOKEN_PATH):
    config = IndicoConfig(
            host=HOST,
            api_token_path=TOKEN_PATH
        )
    return IndicoClient(config=config)


def ocr_pdf_document(client, pdf_path):
    files_to_extract = client.call(
        DocumentExtraction(
            files=[pdf_path], 
            json_config=dict(preset_config='ondocument')
        )
    )
    extracted_file = client.call(JobStatus(id=files_to_extract[0].id, wait=True))
    if extracted_file.status != 'SUCCESS':
        raise ValueError('OCR Failed- make sure your doc/token path is correct.')
    full_result = client.call(RetrieveStorageObject(extracted_file.result))
    page_text = get_page_text_to_ocr(full_result)
    return full_result, page_text


def get_predictions(client: IndicoClient, page_texts: List[str], model_id: int):
    job = client.call(
        ModelGroupPredict(
            model_id=model_id,
            data=page_texts,
            )
        )
    prediction = client.call(
        JobStatus(id=job.id, wait=True)
        )
    return prediction.result


def get_page_text_to_ocr(ocr_result):
    page_text = list()
    for page in ocr_result:
        page_text.append(page['pages'][0]['text'])
    print(page_text)
    return page_text


if __name__ == "__main__":
    print('Starting predictions and PDF highlighting')
    client = get_client()
    ocr_result, page_texts = ocr_pdf_document(client, pdf_path=PDF_PATH)
    predictions = get_predictions(client, page_texts, model_id=MODEL_ID)
    doc_positions, unique_labels = collect_token_positions(predictions, ocr_result)
    highlight_pdf(PDF_PATH, OUTPUT_PATH, doc_positions)
    print('Finished')
