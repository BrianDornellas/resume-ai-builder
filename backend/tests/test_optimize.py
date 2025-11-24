import pytest
import re
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import parse_keywords, analyze_alignment

def test_parse_keywords_handles_punctuation_and_casing():
    text = "Senior Python Developer! Python, python. THE best; developer?"
    result = parse_keywords(text)
    # Should be lowercased, deduped, no stopwords, no punctuation
    assert 'python' in result
    assert 'developer' in result
    assert 'the' not in result
    assert set(result) == {'python', 'developer', 'senior', 'best'}


def test_parse_keywords_dedupes_keywords():
    text = "Data data DATA science Science SCIENCE"
    result = parse_keywords(text)
    assert result == ['data', 'science']


def test_analyze_alignment_detects_missing_and_present():
    resume = "Experienced in Python, data science, and machine learning."
    job_keywords = ['python', 'data', 'science', 'sql']
    missing, strengths = analyze_alignment(resume, job_keywords)
    assert 'sql' in missing
    assert 'python' in strengths
    assert 'data' in strengths
    assert 'science' in strengths
    assert 'sql' not in strengths
    assert 'python' not in missing


def test_parse_keywords_removes_short_and_stopwords():
    text = "A an the is on at by to of in for as be do"
    result = parse_keywords(text)
    assert result == []


def test_analyze_alignment_case_insensitive():
    resume = "Expert in PYTHON and SQL."
    job_keywords = ['python', 'sql']
    missing, strengths = analyze_alignment(resume, job_keywords)
    assert not missing
    assert set(strengths) == {'python', 'sql'}
