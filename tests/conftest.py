import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def test_dir():
    return Path(__file__).parent.absolute()

SAMPLE_OCR = [
    {
        "pages": [{"page_num": 0, "size": {"height": 3300, "width": 2550},}],
        "tokens": [
            {
                "block_offset": {"start": 0, "end": 6},
                "page_num": 0,
                "doc_offset": {"start": 125, "end": 131},
                "text": "Amazon",
                "position": {
                    "bbBot": 342,
                    "bbTop": 282,
                    "bbLeft": 1070,
                    "bbRight": 1310,
                },
                "page_offset": {"start": 125, "end": 131},
            },
            {
                "block_offset": {"start": 7, "end": 10},
                "page_num": 0,
                "doc_offset": {"start": 132, "end": 135},
                "text": "Web",
                "position": {
                    "bbBot": 342,
                    "bbTop": 282,
                    "bbLeft": 1332,
                    "bbRight": 1463,
                },
                "page_offset": {"start": 132, "end": 135},
            },
            {
                "block_offset": {"start": 11, "end": 20},
                "page_num": 0,
                "doc_offset": {"start": 136, "end": 145},
                "text": "Services,",
                "position": {
                    "bbBot": 342,
                    "bbTop": 282,
                    "bbLeft": 1486,
                    "bbRight": 1752,
                },
                "page_offset": {"start": 136, "end": 145},
            },
            {
                "block_offset": {"start": 21, "end": 25},
                "page_num": 0,
                "doc_offset": {"start": 146, "end": 150},
                "text": "Inc.",
                "position": {
                    "bbBot": 342,
                    "bbTop": 282,
                    "bbLeft": 1781,
                    "bbRight": 1878,
                },
                "page_offset": {"start": 146, "end": 150},
            },
        ],
    }
]

SAMPLE_PREDICTION = [
    [
        {
            "end": 150,
            "label": "Vendor",
            "start": 125,
            "text": "Amazon Web Services, Inc.",
        }
    ]
]
