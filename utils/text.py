""" text : A useful collection of tools for handling text data
"""

import re
import pandas as pd
from jellyfish import damerau_levenshtein_distance as dl_distance
from itertools import combinations
from nltk import word_tokenize 
from nltk.util import ngrams

def get_ngrams(sentence, n=2):
    return ['_'.join(gram) for gram in ngrams(word_tokenize(sentence), n)]

def multi_remove(s, remove_list=[]):
    for remove in remove_list:
        s = s.replace(remove, '').strip()
    return s

def num_words(string, list_words=False):
    # Number of words in a string
    string = str(string) if type(string) != str else string
    words = re.findall(r'\w+', string)
    nwords = len(words)
    data1 = (nwords, words) if list_words else nwords
    return data1

def score_token(token, lex): 
    return lex[token] if token in lex else pd.np.nan

def score_tokens(tokens, lex):
    return {t:score_token(t, lex=lex) for t in tokens if t in lex}

def score_sentence(sent, lex, return_mean=True):
    
    # Get all bigrams in lexicon
    bigrams = get_ngrams(sent, n=2)
    score_dict = score_tokens(bigrams, lex=lex)

    # Remove scored bigrams
    bigrams_to_remove = [bigram.replace('_', ' ') for bigram in score_dict]
    new_sent = multi_remove(sent, bigrams_to_remove)
    
    # Score remaining unigrams
    unigrams = get_ngrams(new_sent, n=1)
    unigram_scores = score_tokens(unigrams, lex=lex)

    score_dict.update(unigram_scores)
    if return_mean:
        scores = list(score_dict.values())
        return pd.np.mean(scores) if scores else None
    else:
        return score_dict

def score_bigrams(sent, lex):
    # Get all bigrams in lexicon
    bigrams = get_ngrams(sent, n=2)
    scores = score_tokens(bigrams, lex=lex)
    return pd.np.mean(list(scores.values()))

def get_score_direction(s, thresh=0):
    if s is None: return None
    elif s < thresh:      return 'left'
    elif s > thresh:      return 'right'
    elif s == thresh:     return 'center'

def get_dl_variance(str_list):
    """Get average Damerau-Levenshtein Distance
    """
    all_pairs = [(s1, s2) for s1, s2 in combinations(str_list, 2) if str_list.any()]
    return pd.np.mean([dl_distance(s1, s2) for s1, s2 in all_pairs])

def get_email_address(s):
    # https://zapier.com/blog/extract-links-email-phone-regex/
    regex = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    return re.search(regex, s).group(1)

def get_phone_number(s):
    regex = """(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?"""
    return re.search(regex, s).group(1)