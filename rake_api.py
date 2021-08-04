import re
import operator

class Rake(object):
    def __init__(self, stop_words_path):
        self.stop_words_path = stop_words_path
        self.__stop_words_pattern = self._build_stop_word_regex(stop_words_path)

    def get_keywords(self, text):
        sentence_list = self._split_sentences(text)

        phrase_list = self._generate_candidate_keywords(sentence_list, self.__stop_words_pattern)

        word_scores = self._calculate_word_scores(phrase_list)

        keyword_candidates = self._generate_candidate_keyword_scores(phrase_list, word_scores)

        sorted_keywords = sorted(keyword_candidates.items(), key=operator.itemgetter(1), reverse=True)
        
        return sorted_keywords


    def _is_number(self, s):
        try:
            float(s) if '.' in s else int(s)
            return True
        except ValueError:
            return False


    def _load_stop_words(self, stop_word_file):
        stop_words = []
        for line in open(stop_word_file):
            if line.strip()[0:1] != "#":
                for word in line.split():
                    stop_words.append(word)
        return stop_words


    def _separate_words(self, text, min_word_return_size):
        splitter = re.compile('[^а-яА-ЯёЁ0-9_\\+\\-/]')
        words = []
        for single_word in splitter.split(text):
            current_word = single_word.strip().lower()
            if len(current_word) > min_word_return_size and current_word != '' and not self._is_number(current_word):
                words.append(current_word)
        return words


    def _split_sentences(self, text):
        sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
        sentences = sentence_delimiters.split(text)
        return sentences


    def _build_stop_word_regex(self, stop_word_file_path):
        stop_word_list = self._load_stop_words(stop_word_file_path)
        stop_word_regex_list = []
        for word in stop_word_list:
            word_regex = r'\b' + word + r'(?![\w-])'  # added look ahead for hyphen
            stop_word_regex_list.append(word_regex)
        stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
        return stop_word_pattern


    def _generate_candidate_keywords(self, sentence_list, stopword_pattern):
        phrase_list = []
        for s in sentence_list:
            tmp = re.sub(stopword_pattern, '|', s.strip())
            phrases = tmp.split("|")
            for phrase in phrases:
                phrase = phrase.strip().lower()
                if phrase != "":
                    phrase_list.append(phrase)
        return phrase_list


    def _calculate_word_scores(self, phraseList):
        word_frequency = {}
        word_degree = {}
        for phrase in phraseList:
            word_list = self._separate_words(phrase, 0)
            word_list_length = len(word_list)
            word_list_degree = word_list_length - 1
            for word in word_list:
                word_frequency.setdefault(word, 0)
                word_frequency[word] += 1
                word_degree.setdefault(word, 0)
                word_degree[word] += word_list_degree
        for item in word_frequency:
            word_degree[item] = word_degree[item] + word_frequency[item]

        word_score = {}
        for item in word_frequency:
            word_score.setdefault(item, 0)
            word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)
        return word_score


    def _generate_candidate_keyword_scores(self, phrase_list, word_score):
        keyword_candidates = {}
        for phrase in phrase_list:
            keyword_candidates.setdefault(phrase, 0)
            word_list = self._separate_words(phrase, 0)
            candidate_score = 0
            for word in word_list:
                candidate_score += word_score[word]
            keyword_candidates[phrase] = candidate_score
        return keyword_candidates
