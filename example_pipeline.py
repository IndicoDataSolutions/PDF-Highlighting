#!/usr/bin/env python
"""
Assumes you have a trained extraction model. Given the path to a PDF document, 
OCRs that pdf document (w/ preset_config='ondocument') and then gets predicted
annotations. Next with the OCR and prediction results, highlights the 
annotations to a copy of the source PDF document.

Chang the specifications on the global variables to your paths/host/model. 
"""
from highlighter import Highlighter, OnDoc
from typing import List, Tuple
from pdf_annotate import PdfAnnotator, Location, Appearance 
from indico import IndicoClient, IndicoConfig
from indico.queries import (DocumentExtraction, JobStatus, 
                            ModelGroupPredict, RetrieveStorageObject)

# NOTE: CHANGE BELOW FOR YOUR SPECIFICATIONS
PDF_PATH = './pdf_example.pdf'
OUTPUT_PATH = './pdf_example_w_labels.pdf'
TOKEN_PATH = './indico_api_token.txt'
HOST = 'app.indico.io'
MODEL_ID = 27018


def get_client(host: str, api_token_path: str) -> IndicoClient:
    config = IndicoConfig(
            host=HOST,
            api_token_path=TOKEN_PATH
        )
    return IndicoClient(config=config)


def ocr_pdf_document(client: IndicoClient, pdf_path: str) -> Tuple[List[dict], List[str]]:
    """
    OCRs a PDF document and prepares page-level text for predictions
    
    Arguments:
        client {IndicoClient} -- client for your account
        pdf_path {str} -- path to the PDF you want to OCR
    
    Returns:
        Tuple[List[dict], List[str]] -- Raw OCR result and list of page texts
    """
    files_to_extract = client.call(
        DocumentExtraction(
            files=[pdf_path], 
            json_config=dict(preset_config='ondocument')
        )
    )
    extracted_file = client.call(JobStatus(id=files_to_extract[0].id, wait=True))
    if extracted_file.status != 'SUCCESS':
        raise ValueError('OCR Failed- make sure your doc/token path is correct.')
    ocr_result = client.call(RetrieveStorageObject(extracted_file.result))
    return ocr_result


def get_predictions(client: IndicoClient, page_texts: List[str], model_id: int) -> List[List[dict]]:
    """
    Get predicted annotations for PDF pages
    
    Arguments:
        client {IndicoClient} -- your account client
        page_texts {List[str]} -- list of page texts
        model_id {int} -- model ID for your trained extraction model
    
    Returns:
        List[List[dict]] -- For each page, a list of predicted annotations
    """
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


def main():
    print('Starting...')
    client = get_client(host=HOST, api_token_path=TOKEN_PATH)
    ocr_result = ocr_pdf_document(client, pdf_path=PDF_PATH)
    page_level_text = OnDoc(ocr_result).page_text
    predictions = get_predictions(client, page_level_text, model_id=MODEL_ID)
    highlight = Highlighter(ocr_result)
    highlight.collect_positions(predictions)
    highlight.highlight_pdf(PDF_PATH, OUTPUT_PATH, include_toc=True)
    print('Finished..')


if __name__ == "__main__":
    main()
