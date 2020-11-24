import pytest
import pickle
from highlighter import Highlighter
from .conftest import SAMPLE_OCR, SAMPLE_PREDICTION


def test_collect_positions():
    highlighter = Highlighter(SAMPLE_OCR)
    prediction_positions = highlighter.collect_positions(
        SAMPLE_PREDICTION, 
        inplace=False,
        include_pred_text=False,
    )
    assert len(prediction_positions) == 1
    assert "Vendor" in prediction_positions[0]["labels"]
    assert prediction_positions[0]["labels"]["Vendor"] == 1
    assert len(prediction_positions[0]["positions"]) == 1
    assert prediction_positions[0]["positions"][0]["bbRight"] == 1878
    assert prediction_positions[0]["positions"][0]["bbLeft"] == 1070
    assert "full_text" not in prediction_positions[0]["positions"][0].keys()


def test_collect_positions_multi_page(test_dir):
    ocr = pickle.load(open(test_dir / "invoice_ocr_result.p", "rb"))
    preds = pickle.load(open(test_dir / "invoice_predictions.p", "rb"))
    highlighter = Highlighter(ocr)
    prediction_positions = highlighter.collect_positions(
        preds, 
        inplace=False,
        include_pred_text=True,
    )
    assert len(prediction_positions) == 2
    assert len(prediction_positions[0]["positions"]) == 10
    assert prediction_positions[0]["positions"][1]["full_text"] == "Amazon Web Services, Inc"
