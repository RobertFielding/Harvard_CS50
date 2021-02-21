import os
import re
import sys
from collections import defaultdict
from math import inf

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob_dist = defaultdict(float)
    corpus_len = len(corpus)
    if not corpus[page]:
        for corpus_page in corpus:
            prob_dist[corpus_page] += 1/corpus_len
        return prob_dist

    len_linked_pages = len(corpus[page])
    for linked_page in corpus[page]:
        prob_dist[linked_page] += damping_factor * 1/len_linked_pages
    for corpus_page in corpus:
        prob_dist[corpus_page] += (1 - damping_factor) * 1/corpus_len

    assert abs(sum(prob_dist.values()) - 1) < 10**-2
    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    corpus_length = len(corpus)
    # First sample
    previous_page_rank = defaultdict(lambda: 1/corpus_length)

    # All remaining samples
    # Choose a previous page, then add transition probabilities
    # Loop over remaining previous pages
    for sample in range(1, n):
        next_page_rank = defaultdict(float)
        for prev_page in corpus:
            transitions = transition_model(corpus, prev_page, damping_factor)
            assert abs(sum(transitions.values())-1) < 10**-2
            for next_page in transitions:
                next_page_rank[next_page] += previous_page_rank[prev_page] * transitions[next_page]
        previous_page_rank = next_page_rank.copy()
        assert abs(sum(previous_page_rank.values()) - 1) < 10**-2
    return previous_page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Set initial values to choosing a page randomly
    corpus_length = len(corpus)
    prev_iterated_page_rank = defaultdict(lambda: 1/corpus_length)
    max_abs_difference = inf
    while max_abs_difference > 0.001:
        max_iter_diff = -inf
        next_iterated_page_rank = defaultdict(lambda: (1 - damping_factor) / corpus_length)
        for prev_page in corpus:
            if not corpus[prev_page]:
                print("hi")
                for next_page in corpus:
                    next_iterated_page_rank[next_page] += prev_iterated_page_rank[prev_page] * 1/len(corpus)
            else:
                print("hi2")
                for next_page in corpus[prev_page]:
                    next_iterated_page_rank[next_page] += damping_factor * prev_iterated_page_rank[prev_page]/len(corpus[prev_page])

        for prev_prob, next_prob in zip(prev_iterated_page_rank.values(), next_iterated_page_rank.values()):
            max_iter_diff = max(max_iter_diff, abs(next_prob-prev_prob))
        max_abs_difference = min(max_abs_difference, max_iter_diff)

        prev_iterated_page_rank = next_iterated_page_rank.copy()
        assert abs(sum(prev_iterated_page_rank.values())-1) < 10**-2
    assert abs(sum(next_iterated_page_rank.values()) - 1) < 10**-2
    return prev_iterated_page_rank

if __name__ == "__main__":
    main()
