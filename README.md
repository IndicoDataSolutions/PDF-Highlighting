# PDF Highlighting

The executable script 'pdf_highlight.py' demonstrates how to apply highlighting to 
a PDF w/ Indico's OCR/Prediction positional data. 

Assumes you have a trained extraction model and have installed the packages 
in 'requirements.txt' into a virtual env (tested w/ python 3.7.4- should work for 3.6+). 

Given the path to a PDF document, OCRs that pdf document and then gets predicted
annotations. Next with the OCR and prediction results, highlights the 
annotations to a copy of the source PDF document.

Chang the specifications on the global variables in 'pdf_highlight.py' to your pdf paths/ your indico host/ your extraction model ID.
