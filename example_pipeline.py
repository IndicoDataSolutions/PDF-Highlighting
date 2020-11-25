#!/usr/bin/env python
"""
Assumes you have a trained extraction model. Given the path to a PDF document, 
OCRs that pdf document (w/ preset_config='ondocument') and then gets predicted
annotations. Next with the OCR and prediction results, highlights the 
annotations to a copy of the source PDF document.
"""
from highlighter import Highlighter, OnDoc
from typing import List, Tuple 
from indico import IndicoClient, IndicoConfig
from indico.queries import (DocumentExtraction, JobStatus, 
                            ModelGroupPredict, RetrieveStorageObject)

# NOTE: CHANGE BELOW FOR YOUR ENVIRONMENT, MODEL, AND INDICO INSTANCE
PDF_PATH = '../datasets/test.pdf'
OUTPUT_PATH = './pdf_example_w_labels.pdf'
TOKEN_PATH = '../api_keys/indico_api_token.txt'
HOST = 'app.indico.io'
MODEL_ID = 30242


def get_client(host: str, api_token_path: str) -> IndicoClient:
    config = IndicoConfig(
            host=host,
            api_token_path=api_token_path
        )
    return IndicoClient(config=config)


def ocr_pdf_document(client: IndicoClient, pdf_path: str) -> Tuple[List[dict], List[str]]:
    """
    OCRs a PDF or Tiff document
    """
    files_to_extract = client.call(
        DocumentExtraction(
            files=[pdf_path], 
            json_config=dict(preset_config='ondocument')
        )
    )
    extracted_file = client.call(JobStatus(id=files_to_extract[0].id, wait=True))
    if extracted_file.status != 'SUCCESS':
        print(f"ERROR: {extracted_file.result}")
        raise Exception('OCR Failed- make sure your doc/token path is correct.')
    return client.call(RetrieveStorageObject(extracted_file.result))

def get_predictions(client: IndicoClient, doc_text: List[str], model_id: int) -> List[List[dict]]:
    """
    Get predicted annotations for PDF pages
    
    Arguments:
        client {IndicoClient} -- your account client
        page_texts {List[str]} -- list of full doc_text
        model_id {int} -- model ID for your trained extraction model
    
    Returns:
        List[List[dict]] -- prediction results
    """
    job = client.call(
        ModelGroupPredict(
            model_id=model_id,
            data=doc_text,
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
    highlight = Highlighter(ocr_result)
    predictions = get_predictions(client, [highlight.ocr_result.full_text], model_id=MODEL_ID)
    highlight.collect_positions(predictions)
    highlight.highlight_pdf(PDF_PATH, OUTPUT_PATH, include_toc=True)
    print('Finished..')


if __name__ == "__main__":
    main()
