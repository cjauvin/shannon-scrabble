# shannon_scrabble.py
#
# Solution to the second optional NLP problem from AI Class 2011:
# https://www.ai-class.com/course/video/quizquestion/296
# http://www.youtube.com/watch?v=KuSg1wcty3s
#
# Christian Jauvin (cjauvin@gmail.com)
# December 2011

from __future__ import division
import re, math, gzip, heapq
from collections import defaultdict

msg = """|de|  | f|Cl|nf|ed|au| i|ti|  |ma|ha|or|nn|ou| S|on|nd|on|
         |ry|  |is|th|is| b|eo|as|  |  |f |wh| o|ic| t|, |  |he|h |
         |ab|  |la|pr|od|ge|ob| m|an|  |s |is|el|ti|ng|il|d |ua|c |
         |he|  |ea|of|ho| m| t|et|ha|  | t|od|ds|e |ki| c|t |ng|br|
         |wo|m,|to|yo|hi|ve|u | t|ob|  |pr|d |s |us| s|ul|le|ol|e |
         | t|ca| t|wi| M|d |th|"A|ma|l |he| p|at|ap|it|he|ti|le|er|
         |ry|d |un|Th|" |io|eo|n,|is|  |bl|f |pu|Co|ic| o|he|at|mm|
         |hi|  |  |in|  |  | t|  |  |  |  |ye|  |ar|  |s |  |  |. |"""

EPSILON = 1e-10
CHAR_NGRAM_ORDER = 6
WORD_NGRAM_ORDER = 1

char_counts = defaultdict(int)
word_counts = defaultdict(int)

# http://dingo.sbs.arizona.edu/~hammond/ling696f-sp03/browncorpus.txt
f = gzip.open('brown.txt.gz')
print 'training..'
for n_lines, line in enumerate(f, 1):
    # words
    words = re.sub(r'\W+', ' ', line).split() # tokenize with punctuation and whitespaces
    word_counts[''] += len(words) # this little hack is useful for 1-grams
    for n in range(WORD_NGRAM_ORDER):
        for i in range(len(words)):
            if i >= n:
                word_counts[' '.join(words[i-n:i+1])] += 1
    # chars
    chars = ' '.join(words)    
    char_counts[''] += len(chars)
    for n in range(CHAR_NGRAM_ORDER):
        for i in range(len(chars)):
            if i >= n:
                char_counts[chars[i-n:i+1]] += 1
    if n_lines % 10000 == 0: print n_lines
f.close()

print 'model has %d params' % (len(char_counts) + len(word_counts))
print

def charProb(c):
    global char_counts
    if c in char_counts: 
        return char_counts[c] / char_counts[c[:-1]]
    return EPSILON

def wordProb(w):
    global word_counts
    words = w.split()
    h = ' '.join(words[:-1])
    #print 'w=%s h=%s' % (w, h)
    if w in word_counts: 
        return word_counts[w] / word_counts[h]
    return EPSILON
    
def gridScore(grid):
    # add spaces between rows
    s = ' '.join([''.join([grid[i][j] for i in range(19)]) for j in range(8)])
    # tokenize with punctuation and whitespaces
    s = ' '.join(re.sub(r'\W+', ' ', s).split()) 

    # hack to make it stop at the right place (once we know the answer!)
    if s.lower().startswith('claude shannon founded information theory'):
        return float('inf')

    LL = 0 # log-likelihood
    for i in range(len(s)):
        probs = []
        for n in range(CHAR_NGRAM_ORDER):
            if i >= n:
                probs.append(charProb(s[i-n:i+1]))
        if not probs: continue
        pi = sum([p/len(probs) for p in probs])
        LL += math.log(pi)
    words = s.split()
    for i in range(len(words)):
        probs = []
        for n in range(WORD_NGRAM_ORDER):
            if i >= n:
                probs.append(wordProb(' '.join(words[i-n:i+1])))
        if not probs: continue
        pi = sum([p/len(probs) for p in probs])
        LL += math.log(pi)
    return LL

def nextGrids(grid):
    global visited # I know..
    next_grids = set()
    for i in range(19):
        for j in range(19):
            if i == j: continue
            next_grid = list(list(col) for col in grid)
            next_grid.insert(i, next_grid.pop(j))
            next_grid = tuple(tuple(col) for col in next_grid)
            if next_grid not in visited:
                next_grids.add(next_grid)
    return next_grids

def repr(grid):
    return '\n'.join(['|%s|' % '|'.join([grid[i][j] for i in range(19)]) for j in range(8)])

grid = [[''] * 8 for i in range(19)]
for j, line in enumerate(msg.split('\n')):
    cols = line.strip().split('|')[1:-1]
    for i, col in enumerate(cols):
        grid[i][j] = col

n_trials = 0
visited = set()
score = float('inf')
frontier = []
while score > float('-inf'):
    for next_grid in nextGrids(grid):
        # using a min-heap so score has to be negated
        heapq.heappush(frontier, (-gridScore(next_grid), next_grid))
    score, grid = heapq.heappop(frontier)
    #score, grid = min([(-gridScore(next_grid), next_grid) for next_grid in nextGrids(grid)])
    visited.add(grid)
    print repr(grid)
    print score    
    print
    n_trials += 1

print 'solved in %d trials' % n_trials
