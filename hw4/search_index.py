import re

class SearchIndex:
    def __init__(self):
        self._index = {}
        self._documents = {}
        self._word_counts = {}

    @staticmethod
    def _tokenize(text):
        return re.findall(r'\w+', text.lower())

    def add(self, doc_id, text):
        if doc_id in self._documents:
            self._remove(doc_id)
        counts = {}
        for word in self._tokenize(text):
            counts[word] = counts.get(word, 0) + 1
        self._documents[doc_id] = counts
        for word, count in counts.items():
            self._index.setdefault(word, set()).add(doc_id)
            self._word_counts[word] = self._word_counts.get(word, 0) + count

    def _remove(self, doc_id):
        counts = self._documents.pop(doc_id)
        for word, count in counts.items():
            docs = self._index.get(word)
            if docs is not None:
                docs.discard(doc_id)
                if not docs:
                    del self._index[word]
            new_count = self._word_counts.get(word, 0) - count
            if new_count > 0:
                self._word_counts[word] = new_count
            else:
                self._word_counts.pop(word, None)

    def remove(self, doc_id):
        if doc_id not in self._documents:
            raise KeyError(doc_id)
        self._remove(doc_id)

    def _query_words(self, words):
        query = []
        seen = set()
        for word in words:
            for token in self._tokenize(word):
                if token not in seen:
                    seen.add(token)
                    query.append(token)
        return query

    def search_all(self, *words):
        query = self._query_words(words)
        if not query:
            return set()
        sets = []
        for word in query:
            docs = self._index.get(word)
            if docs is None:
                return set()
            sets.append(docs)
        sets.sort(key=len)
        result = set(sets[0])
        for docs in sets[1:]:
            result.intersection_update(docs)
            if not result:
                break
        return result

    def search_any(self, *words):
        result = set()
        for word in self._query_words(words):
            docs = self._index.get(word)
            if docs is not None:
                result.update(docs)
        return result

    def top_words(self, n):
        if n <= 0:
            return []
        items = sorted(self._word_counts.items(), key=lambda item: item[1], reverse=True)
        return items[:n]


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]
    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}

    assert idx.search_all('python,') == set()
    assert idx.search_all('PYTHON', 'dict') == set()
    assert idx.search_any('LANGUAGE', 'language') == set()
    assert idx.search_any('new', 'text') == {3}
    assert idx.search_all('new', 'new', 'text') == {3}
    assert idx.search_any() == set()
    assert idx.search_all() == set()

    idx.add(4, 'python python set')
    assert idx.search_all('python') == {4}
    assert idx.search_all('set') == {2, 4}
    assert idx.search_any('python', 'fast') == {4}
    assert idx._word_counts['python'] == 2
    assert idx.top_words(1) == [('a', 4)]
    assert idx.top_words(0) == []
    assert idx.top_words(-1) == []
    assert len(idx.top_words(100)) == len(idx._word_counts)

    idx.add(4, 'only python')
    assert idx.search_all('set') == {2}
    assert idx._word_counts['python'] == 1
    assert 4 in idx._index['python']
    idx.add(4, 'only python')
    assert idx._word_counts['python'] == 1
    assert len(idx.search_all('only', 'python')) == 1

    idx.remove(4)
    assert idx.search_all('python') == set()
    assert 'python' not in idx._index
    assert 'python' not in idx._word_counts
    assert 'only' not in idx._index
    assert idx.search_any('python', 'only') == set()

    idx.add(5, '... !!! ???')
    assert idx.search_all('anything') == set()
    idx.remove(5)
    assert 5 not in idx._documents

    try:
        idx.remove(999)
        assert False, 'ожидали KeyError'
    except KeyError:
        pass

    idx.add('doc', 'Hello, WORLD! hello')
    assert idx.search_all('hello') == {'doc'}
    assert idx.search_any('world') == {'doc'}
    assert idx._word_counts['hello'] == 2
    assert ('hello', 2) in idx.top_words(100)
    idx.remove('doc')
    assert idx.search_any('hello', 'world') == set()
    assert 'hello' not in idx._index and 'world' not in idx._index

    top = SearchIndex()
    top.add(10, 'b a c b a')
    assert top.top_words(3) == [('b', 2), ('a', 2), ('c', 1)]
    top.add(11, 'c c c')
    assert top.top_words(2) == [('c', 4), ('b', 2)]
    top.remove(11)
    assert top.top_words(2) == [('b', 2), ('a', 2)]
    assert top.top_words(10) == [('b', 2), ('a', 2), ('c', 1)]
