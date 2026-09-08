from targets.text_stats import (
    word_count,
    char_frequency,
    most_common_word,
    unique_words,
)


def test_word_count_empty():
    assert word_count("") == 0


def test_word_count_single():
    assert word_count("hello") == 1


def test_word_count_multiple():
    assert word_count("the quick brown fox") == 4


def test_word_count_extra_spaces():
    assert word_count("  hello   world  ") == 2


def test_char_frequency_empty():
    assert char_frequency("") == {}


def test_char_frequency_single():
    assert char_frequency("a") == {"a": 1}


def test_char_frequency_ignores_non_alpha():
    assert char_frequency("a1b!c") == {"a": 1, "b": 1, "c": 1}


def test_char_frequency_case_insensitive():
    assert char_frequency("AaBb") == {"a": 2, "b": 2}


def test_char_frequency_repeated():
    result = char_frequency("hello")
    assert result["l"] == 2


def test_most_common_word_empty():
    assert most_common_word("") == ""


def test_most_common_word_single():
    assert most_common_word("python") == "python"


def test_most_common_word_repeated():
    assert most_common_word("the cat and the dog and the bird") == "the"


def test_most_common_word_lowercased():
    assert most_common_word("go go go") == "go"


def test_unique_words_empty():
    assert unique_words("") == set()


def test_unique_words_single():
    assert unique_words("hello") == {"hello"}


def test_unique_words_deduplication():
    assert unique_words("cat dog cat bird dog") == {"cat", "dog", "bird"}


def test_unique_words_case_normalized():
    assert unique_words("Python python PYTHON") == {"python"}
