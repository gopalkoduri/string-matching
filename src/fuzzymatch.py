import lcs
import damerauLevenshtein as levenshtein


def _strip_chars(word, chars):
    """
    _strip_chars(word, chars)

    This functions removes all the occurrences of specified characters from
    a word. The arguments word and chars should be string and list
    respectively.
    """
    result = ""
    for char in word:
        if char not in chars:
            result = result + char
    return result


def similarity(x, y):
    """
    _similarity(x, y)

    This function measures string similarity between x and y.
    The function returns:
    0.8*(len(LongestCommonSubsequence(x, y))) +
    0.2*1/(DamerauLevenshteinDistance(x, y))

    LCS and Levenshtein are, by trial and error, found to be
    compensating for each others errors. Hence their combination
    in most cases seems to be one of the good solutions.

    Eg: For Abhogi and Behag, LCS gives a high similarity
    score of 3, which is balanced by the Levenshtein's distance
    of 4, thus penalizing it.
    """

    len_thresh = 0.75
    # beyond this difference of ratio between lengths, they are deemed different terms

    if len(y) == 0:
        return 0
    ratio = 1.0 * len(x) / len(y)
    if ratio > 1:
        ratio = 1 / ratio;
    if ratio < len_thresh:
        return 0

    subseq = lcs.lcs(x, y)
    dldist = levenshtein.dameraulevenshtein(x, y)
    if dldist == 0:
        dldist = 1

    w1 = 0.8
    w2 = 0.2
    return w1 * (1.0 * len(subseq) / max([len(x), len(y)])) + (w2 * 1.0 / dldist);


def lookup_single(term, pool, thresh=0.8, n=100, stripped=False, recursion=2):
    """
    Parameters:

    lookup(term, pool, thresh=0.8, n=100, stripped=False, recursion=2)

    term: A term which need to be lookedup for matches in 'pool'.

    pool: The list of all the terms to be matched against.

    thresh: Similarity threshold. Increasing it emphasizes that for
    two term names to be deemed similar, the constraints are higher.

    n: Max number of results.

    stripped: If True, all the terms are stripped off the vowels and 'h'
    before comparison.

    recursion: If it is 1, the immediate matches only are returned.
    If it is 2, The matches for the matched term names are also
    included, and so on.

    Return values: [match1, match2, ...]
    """
    pool = list(pool[:])
    unwanted_chars = ['a', 'e', 'i', 'o', 'u', 'h', ' ']
    stripped_pool = []
    if stripped:
        term = _strip_chars(term, unwanted_chars)
        for i in pool:
            stripped_pool.append(_strip_chars(i, unwanted_chars))
    else:
        stripped_pool = pool
    l = len(stripped_pool)

    similarities = [0] * l
    for i in xrange(0, l):
        similarities[i] = similarity(term, stripped_pool[i])

    matches = []
    if n > l:
        n = l
    for i in xrange(n):
        ind = similarities.index(max(similarities))
        s = similarities.pop(ind)
        term_match = pool.pop(ind)
        if s >= thresh:
            matches.append(term_match)
            if recursion > 1:
                next_nearest = lookup(term_match, pool, thresh, n, stripped, recursion-1)
                if next_nearest:
                    matches.extend(next_nearest)
                    del next_nearest
    return list(set(matches))


def lookup(terms, pool, thresh=0.8, n=10, stripped=False, recursion=2):
    """
    Parameters:

    lookup(term, pool, thresh=0.8, n=100, stripped=False, recursion=2)

    terms: A list of terms which need to be lookedup for duplicates in 'pool'.

    pool: The list of all the terms to be matched against.

    thresh: Similarity threshold. Increasing it emphasizes that for
    two term names to be deemed similar, the constraints are higher.

    n: Max number of results.

    stripped: If True, all the terms are stripped off the vowels and 'h'
    before comparison.

    recursion: If it is 1, the immediate matches only are returned.
    If it is 2, The matches for the matched term names are also
    included, and so on.

    Return values:
    A dictionary with of the format {"term": [match1, match2, ...]}
    """
    pool = list(pool)
    terms = list(terms)
    if recursion <= 0:
        return

    duplicates = {}
    analyzed = []
    for term in terms:
        if term not in analyzed:
            duplicates[term] = lookup_single(term, pool, thresh, n, stripped, recursion)
            analyzed.extend(duplicates[term])
            analyzed.extend([term])
            analyzed = list(set(analyzed))
        else:
            continue
    return duplicates
