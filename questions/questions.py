import nltk
import sys
import os
from collections import defaultdict
import string
import numpy as np
# nltk.download('stopwords')

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)
    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    result_dict = dict()
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), encoding='utf8') as f:
            next(f)
            # Read article excluding hyperlink
            result_dict[filename] = f.read()
    return result_dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by converting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokenised_doc = nltk.word_tokenize(document.lower())
    formatted_doc = [token for token in tokenised_doc if token not in string.punctuation and token not in
                    nltk.corpus.stopwords.words("English")]
    return formatted_doc


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    num_docs = len(documents)
    num_docs_with_word = defaultdict(int)
    for document in documents.values():
        words_in_document = set(document)
        for word in words_in_document:
            num_docs_with_word[word] += 1
    inv_doc_freq = dict()
    for word in num_docs_with_word:
        inv_doc_freq[word] = np.log(num_docs / num_docs_with_word[word])
    return inv_doc_freq


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    file_scores = []
    for file, document in files.items():
        word_freq = defaultdict(int)
        for word in document:
            word_freq[word] += 1
        file_tf_idf = sum(word_freq[shared_word] * idfs[shared_word] for shared_word in query & set(document))
        file_scores.append((file, file_tf_idf))
    file_scores.sort(key=lambda x: x[1], reverse=True)
    return [file for file, _ in file_scores[:n]]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    top_n_sentences = []
    for sentence, words in sentences.items():
        sentence_words = set(words)
        sentence_score = sum(idfs[word] for word in query & sentence_words)
        query_density = len(query & sentence_words) / len(sentence)
        top_n_sentences.append((sentence, sentence_score, query_density))
    top_n_sentences.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return [sentence for sentence, _, _ in top_n_sentences[:n]]


if __name__ == "__main__":
    main()
