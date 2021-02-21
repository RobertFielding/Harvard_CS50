import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""
# 1. Holmes sat.
# 2. Holmes lit a pipe.
# 3. We arrived the day before Thursday.
# 4. Holmes sat in the red armchair and he chuckled.
# 5. My companion smiled an enigmatical smile.
# 6. Holmes chuckled to himself.
# 7. She never said a word until we were at the door here.
# 8. Holmes sat down and lit his pipe.
# 9. I had a country walk on Thursday and came home in a dreadful mess.
# 10. I had a little moist red paint in the palm of my hand.
NONTERMINALS = """  
S -> NP VP | NP VP NP | S Conj S 
NP -> N | NP NP | Det NP | P NP | NP AP | AP NP | NP Adv
VP -> V | VP P | VP Adv | Adv VP
AP -> Adj | Adj AP
"""


grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    tokenised_sentence = nltk.word_tokenize(sentence)
    lc_tokenised = [word.lower() for word in tokenised_sentence]
    sentence_words = []
    for word in lc_tokenised:
        num_alpha_char = sum(char in 'abcdefghjijlmnopqrstuvwxyz' for char in word)
        if num_alpha_char < 1:
            continue
        sentence_words.append(word)
    return sentence_words

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    subtrees = tree.subtrees()
    np_chunks = []
    for subtree in subtrees:
        if subtree.label() == "NP" and sum(sec_subtree.label() == "NP" for sec_subtree in subtree.subtrees()) == 1:
            np_chunks.append(subtree)
    return np_chunks


if __name__ == "__main__":
    main()
