# PDF Highlighter

The class Highlighter uses ondocument OCR output from the Indico API and predicted 
annotation results to apply highlights to (default: a copy) of a source PDF document.  

## Example Usage
Assumes you know how to obtain ocr_result object 'ondoc_ocr_result' and 
'model_predictions'. If you're not sure, see the example in 'example_pipeline.py' or 
check out [the documentation](https://indicodatasolutions.github.io/indico-client-python/)
```
from highlighter import Highlighter

highlight = Highlighter(ondoc_ocr_result)

# map predictions to PDF location
highlight.collect_positions(model_predictions)

# highlight the positions onto a PDF
highlight.highlight_pdf('./source_doc.pdf', './highlighted_source_doc.pdf')
```


## Demo Script

The executable script 'example_pipeline.py' demonstrates how to apply highlighting to 
a PDF w/ Indico's OCR/Prediction positional data. 

Assumes you have a trained extraction model and have installed the packages 
in 'requirements.txt' into a virtual env (tested w/ python 3.7.4- should work for 3.6+.
Change the specifications of the global variables to your pdf paths, your indico host,
and your extraction model ID.
