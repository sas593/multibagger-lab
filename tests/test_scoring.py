from investment_engine.data_provider import DummyDataProvider
from investment_engine.scoring import score_company
def test_dodla_de():
    assert DummyDataProvider().fundamentals("DODLA").debt_to_equity==.03
def test_score_range():
    for t in DummyDataProvider().companies:
        assert 0<=score_company(DummyDataProvider().fundamentals(t)).total<=100
