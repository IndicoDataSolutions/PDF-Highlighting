# PDF Highlighter

The class Highlighter uses ondocument OCR output and predicted 
annotation results rom the Indico API to apply highlights to a source 
PDF document (or creates a highlighted copy). Optionally, you can also insert a table of contents detailing the number and type of extractions on each page.   


## Example Usage
Assumes you know how to obtain the returned object from DocumentExtraction 
'ondoc_ocr_result' and prediction from ModelGroupPredict 'model_predictions'. 
If you're not sure, see the example in 'example_pipeline.py' or 
check out [the documentation](https://indicodatasolutions.github.io/indico-client-python/)
```
from highlighter import Highlighter

highlight = Highlighter(ondoc_ocr_result)

# map predictions to PDF location
highlight.collect_positions(model_predictions)

# highlight the positions onto a PDF
highlight.highlight_pdf('./source_doc.pdf', './highlighted_source_doc.pdf', include_toc=True)
```


## Demo Script

The executable script 'example_pipeline.py' demonstrates how to apply highlighting to 
a PDF w/ Indico's OCR/Prediction positional data. 

Assumes you have a trained extraction model and have installed the packages 
in 'requirements.txt' into a virtual env (tested w/ python 3.7.4- should work for 3.6+.
Change the specifications of the global variables to your pdf paths, your indico host,
and your extraction model ID.
