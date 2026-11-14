import pytest
from app.validators import validate_query

@pytest.mark.parametrize('length,valid', [(0,False),(1,True),(2,True),(499,True),(500,True),(501,False)])
def test_question_boundaries(length, valid):
    assert (validate_query(question='x'*length)==[]) is valid

def test_trimmed_empty():
    assert validate_query(question='  ')[0]['code'] == 'INVALID_QUESTION'

@pytest.mark.parametrize('value', [1, [], True, 5.4])
def test_question_wrong_type(value):
    assert validate_query(question=value)[0]['code'] == 'INVALID_TYPE'

@pytest.mark.parametrize('code,valid', [
    ('714020',False),('7140209',True),('71402091',False),
    ('7140202SN',False),('７１４０２０９',False),('abcdefg',False),('0000000',True)])
def test_major_code_boundaries(code, valid):
    assert (validate_query(major_code=code)==[]) is valid

@pytest.mark.parametrize('value', [1234567, False, None if False else 71.2])
def test_major_wrong_type(value):
    assert validate_query(major_code=value)[0]['code'] == 'INVALID_TYPE'

@pytest.mark.parametrize('limit,valid', [(-1,False),(0,True),(1,True),(9,True),(10,True),(11,False)])
def test_history_boundaries(limit, valid):
    assert (validate_query(question='hi', history_limit=limit)==[]) is valid

@pytest.mark.parametrize('value', ['5', True, False, 5.0, None])
def test_history_wrong_type(value):
    assert validate_query(question='hi',history_limit=value)[0]['field'] == 'history_limit'

@pytest.mark.parametrize('year', [2025,2027,'2026',True,False,None])
def test_invalid_year(year):
    assert validate_query(question='hi', admission_year=year)[0]['field'] == 'admission_year'

def test_missing_both():
    assert validate_query()[0]['code'] == 'MISSING_INPUT'

def test_multiple_errors():
    e=validate_query(question='',major_code='X',admission_year='X',history_limit='X')
    assert len(e) == 4
