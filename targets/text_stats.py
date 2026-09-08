def word_count(text):
    return len(text.split())


def char_frequency(text):
    frequency = {}
    for char in text.lower():
        if char.isalpha():
            frequency[char] = frequency.get(char, 0) + 1
    return frequency


def most_common_word(text):
    words = text.lower().split()
    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1
    if not frequency:
        return ""
    return max(frequency, key=frequency.get)


def unique_words(text):
    return set(text.lower().split())
