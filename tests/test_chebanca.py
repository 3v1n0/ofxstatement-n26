import os

from ofxstatement.ui import UI

from ofxstatement.plugins.n26 import N26Plugin


def test_n26() -> None:
    plugin = N26Plugin(UI(), {})
    here = os.path.dirname(__file__)
    sample_filename = os.path.join(here, "sample-statement.csv")

    parser = plugin.get_parser(sample_filename)
    statement = parser.parse()

    assert statement is not None
