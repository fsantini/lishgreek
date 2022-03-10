#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Greeklish to greek converter. This implementation follows an approach similar
to "All Greek to me! An automatic Greeklish to Greek transliteration system"
by Chalamandaris et al. 2006

The greeklish word, following a number of possible Greeklish conventions,
is tokenized and transformed into a pseudophonetic version (called uglish -
"unified greeklish"). This pseudophonetic version is then used as a key to a
uglish/Greek dictionary to find a number of possible Greek equivalences.

Simple orthographic and probability rules are applied to select the most probable
Greek equivalent word.

Copyright 2022 Francesco Santini <francesco.santini@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

uglish-dict.json is derived from "Hermit Dave" word list for Greek
available here: https://github.com/hermitdave/FrequencyWords/tree/master/content/2018/el
And it is redistributable under a CC-BY-SA-4.0 license.

"""

import json
import gzip

greek_accented   = 'ά έ ή ί ΐ ό ύ ΰ ώ'
greek_unaccented = 'α ε η ι ϊ ο υ ϋ ω'

lat_accented   = 'à è ì ò ù ẁ á é í ó ú ẃ'
lat_unaccented = 'a e i o u w a e i o u w'

def make_dictionary_from_strings(original_string, replace_string):
    orig_list = original_string.split()
    replace_list = replace_string.split()
    output_dict = {}
    
    for i,l in enumerate(orig_list):
        output_dict[l] = replace_list[i]
    return output_dict

def replace_old(string, replace_dict):
    if isinstance(string, list):
        s_out = []
        for s in string:
            s_out.extend(replace(s, replace_dict))
        return s_out
    s_in = string
    s_out = ['']
    for pos in range(len(s_in)):
        replace_made = False
        for original_graph in replace_dict.keys():
            char = s_in[pos:pos+len(original_graph)]
            if char == original_graph:
                replace_made = True
                s_in = s_in[:pos] + '_'*len(original_graph) + s_in[pos+len(original_graph):]
                new_s_out = []
                for alternative in replace_dict[original_graph]:
                    for string in s_out:
                        new_s_out.append(string + alternative)
                s_out = new_s_out
        if not replace_made and s_in[pos] != '_':
            new_s_out = []
            for string in s_out:
                new_s_out.append(string + s_in[pos])
            s_out = new_s_out
    return s_out

def replace(string, replace_dict):
    if isinstance(string, list):
        s_out = []
        for s in string:
            s_out.extend(replace(s, replace_dict))
        return s_out
    s_in = string
    s_out = ['']
    while len(s_in) > 0:
        replace_made = False
        for original_graph in replace_dict.keys():
            #print(original_graph, s_in)
            if s_in.startswith(original_graph):
                replace_made = True
                s_in = s_in[len(original_graph):] # shift input
                new_s_out = []
                for alternative in replace_dict[original_graph]:
                    for string in s_out:
                        new_s_out.append(string + alternative)
                s_out = new_s_out
                break
        if not replace_made: # no graph matches the string
            new_s_out = []
            for string in s_out:
                new_s_out.append(string + s_in[0])
            s_out = new_s_out
            s_in = s_in[1:] # shift input
    return s_out


greek_digraph    = 'αβ αφ αυ αι γγ γκ εβ εφ ευ ει μπ μβ νδ ντ οι ου γχ '
g_uglish_digraph = 'A  A  A  e  G  G  E  Ε  E  i  b  V  d  d  i  u  H  '

greek_monograph    = 'α β γ δ ε ζ η θ ι ϊ κ λ μ ν ξ ο π ρ σ ς τ υ ϋ φ χ ψ ω '
g_uglish_monograph = 'a v g d e z i 8 i i k l m n 3 o p r s s t i i f x 4 o '

greek_accent_dictionary = make_dictionary_from_strings(greek_accented, greek_unaccented)
g2u_dict = make_dictionary_from_strings(greek_digraph + greek_monograph, g_uglish_digraph + g_uglish_monograph)

lish_trigraph     = 'nch '
l_uglish_trigraph = 'H   '

lish_digraph     = 'ai au af av ay ch ei eu ef ev ey gg gk ks ng nk mp mb mv nt nd oi ou ps th '
l_uglish_digraph = 'e  A  A  A  A  x  i  E  E  E  E  G  G  3  G  G  b  bV V  d  d  i  u  4  8  '

lish_monograph     = 'a b  c d e f g h  i j k l m n o p q r s t u v w x  y z 3 8 9 4 '
l_uglish_monograph = 'a bv s d e f g xi i 3 k l m n o p q r s t i v o 3x i z 3 8 8 4 '

tiebreaker_tokens_lish  = 'y u h ai au ay ei eu ey oi ou mv'
tiebreaker_tokens_greek = 'υ υ η αι αυ αυ ει ευ ευ οι ου μβ'

tiebreaker_dict = {}
for tok_lish,tok_greek in zip(tiebreaker_tokens_lish.split(), tiebreaker_tokens_greek.split()):
    tiebreaker_dict[tok_lish] = tok_greek

lat_accent_dictionary = make_dictionary_from_strings(lat_accented, lat_unaccented)
l2u_dict = make_dictionary_from_strings(lish_trigraph + lish_digraph + lish_monograph, l_uglish_trigraph + l_uglish_digraph + l_uglish_monograph)

def is_greek_letter(char):
    alphabet = greek_monograph + ' ' + greek_accented
    if char in alphabet and char != ' ':
        return True
    else:
        return False

def is_latin_letter(char):
    alphabet = lish_monograph + ' ' + lat_accented
    if char in alphabet and char != ' ':
        return True
    else:
        return False

def is_greek(string):
    string = replace(string.lower(), greek_accent_dictionary)[0]
    for letter in string:
        if not is_greek_letter(letter):
            return False
    return True

def is_latin(string):
    string = replace(string.lower(), greek_accent_dictionary)[0]
    for letter in string:
        if not is_latin_letter(letter):
            return False
    return True

def greek_to_uglish(string):
    s = string.lower()
    s = replace(s, greek_accent_dictionary)
    s = replace(s, g2u_dict)
    return s

def tokenize_graphs(word, graph_string_or_dict):
    if isinstance(graph_string_or_dict, dict):
        graph_list = list(graph_string_or_dict.keys())
    else:
        graph_list = graph_string_or_dict.split()
    token_list = []
    while len(word) > 0:
        graph_found = False
        for graph in graph_list:
            if word.startswith(graph):
                token_list.append(graph)
                word = word[len(graph):]
                graph_found = True
                break
        if not graph_found:
            # assume graph has length 1
            token_list.append(word[0])
            word = word[1:]
    return token_list

def count_graphs(word, graph_string_or_dict):
    return len(tokenize_graphs(word, graph_string_or_dict))

def find_accent(string):
    positions = []
    for pos,l in enumerate(string):
        if l in greek_accented or l in lat_accented:
            positions.append(pos)
    return positions

def find_accent_graph_position(word, graph_string):
    try:
        accent_pos = find_accent(word)[0]
    except IndexError: # there is no accent: return an arbitrary big number to insert into the metric
        return 100
    word = word[:accent_pos+1]
    word = replace(word, greek_accent_dictionary)[0]
    word = replace(word, lat_accent_dictionary)[0]
    return count_graphs(word, graph_string)
    
    
def build_g_uglish_dict():
    LIMIT = -1 # limit to this number of common words
    print('Building dictionary')
    uglish_dict = {}
    line_number=1
    # this is already a list in order of frequency. The corresponding dictionary is ordered
    #with open('el-utf8_reduced.wl', 'r', encoding='utf-8') as f:
    with open('el_full.txt', 'r', encoding='utf-8') as f:
        for line in f:
            word = line.split()[0]
            word = word.strip()
            if not is_greek(word):
                #print(word)
                continue
            line_number += 1
            if LIMIT > 0 and line_number > LIMIT:
                break
            if len(find_accent(word)) > 1:
                continue
            uglish = greek_to_uglish(word)
            for uglish_word in uglish:
                if uglish_word not in uglish_dict:
                    uglish_dict[uglish_word] = []
                uglish_dict[uglish_word].append(word)
    print('Done')
    with gzip.open('uglish-dict.json.gz', 'wt', encoding='utf-8') as f:
        json.dump(uglish_dict, f)
    return uglish_dict
            
def load_g_uglish_dict():
    with gzip.open('uglish-dict.json.gz', 'rt', encoding='utf-8') as f:
        uglish_dict = json.load(f)
    return uglish_dict
        
#uglish_dict = build_g_uglish_dict()
uglish_dict = load_g_uglish_dict()

def lish_to_uglish(string):
    s = string.lower()
    s = replace(s, lat_accent_dictionary)
    s = replace(s, l2u_dict)
    return s

def find_possibilities(lat_string):
    uglish = lish_to_uglish(lat_string)
    greek_alt = []
    for uglish_word in uglish:
        try:
            greek_alt.extend(uglish_dict[uglish_word])
        except KeyError:
            pass
    return greek_alt

def sort_possibilities_by(possibilities, metric_list):
    new_possibilities = []
    sorted_indices = [i[0] for i in sorted(enumerate(metric_list), key=lambda x:x[1])]
    for i in sorted_indices:
        new_possibilities.append(possibilities[i])
    return new_possibilities

def sort_possibilities_by_accent(lat_string, possibilities):
    if len(find_accent(lat_string)) == 0:
        # greeklish has no accent, return unchanged
        return possibilities
    lat_accent_position = find_accent_graph_position(lat_string, lish_trigraph + lish_digraph + lish_monograph)
    greek_accent_position_differences = []
    for greek_word in possibilities:
        greek_accent_position_differences.append( abs(
            find_accent_graph_position(greek_word, greek_digraph + greek_monograph) - 
            lat_accent_position) )

    return sort_possibilities_by(possibilities, greek_accent_position_differences)

def sort_possibilities_by_length(lat_string, possibilities):
    lat_len = len(lat_string)
    
    digraphs_to_monographs = 'ch th ps'.split() # digraphs that are always translated into a monograph
    for digraph in digraphs_to_monographs:
        lat_len -= lat_string.lower().count(digraph)
    greek_length_differences = []
    for greek_word in possibilities:
        greek_length_differences.append(abs(len(greek_word) - lat_len))
    
    return sort_possibilities_by(possibilities, greek_length_differences)

def sort_possibilities_by_tiebreakers(lat_string, possibilities):
    lat_string = replace(lat_string.lower(), lat_accent_dictionary)[0]
    tokenized_lat = tokenize_graphs(lat_string, l2u_dict)
    inverse_probabilities = [100]*len(possibilities)
    tokenized_possibilities = []
    for possibility in possibilities:
        tokenized_possibility = tokenize_graphs(replace(possibility.lower(), greek_accent_dictionary)[0], g2u_dict)
        tokenized_possibilities.append(tokenized_possibility)
    
    for i, tok in enumerate(tokenized_lat):
        try:
            target_greek_tok = tiebreaker_dict[tok]
        except KeyError:
            continue # the token is not a tiebreaker
        
        # search each possibility if it contains the target token at the proper location
        for j, tokenized_possibility in enumerate(tokenized_possibilities):
            if tokenized_possibility[i] == target_greek_tok:
                inverse_probabilities[j] -= 1 # if yes, reduce the inverse probability
    
    return sort_possibilities_by(possibilities, inverse_probabilities)
    
    
def sorted_possibilities(lat_string):
    possibilities = find_possibilities(lat_string)
    #print(possibilities)
    possibilities = sort_possibilities_by_length(lat_string, possibilities)
    #print(possibilities)
    possibilities = sort_possibilities_by_accent(lat_string, possibilities)
    #print(possibilities)
    possibilities = sort_possibilities_by_tiebreakers(lat_string, possibilities)
    #print(possibilities)
    return possibilities


def translate_text(text):
    def guess(word):
        if word[0].isupper():
            capitalize = True
        else:
            capitalize = False
        #print(word)
        guess_list = sorted_possibilities(word)
        try:
            translated_word = guess_list[0]
        except IndexError: # there are no corresponding greek possibilities
            translated_word = word
        
        if capitalize:
            translated_word = translated_word[0].upper() + translated_word[1:]
        
        return translated_word
    
    word = ''
    text_out = ''
    for char in text:
        if not is_latin_letter(char.lower()):
            if word:
                text_out += guess(word) + char
                word = ''
            else:
                text_out += char
        else:
            word += char
    if word:
        text_out += guess(word)
    return text_out
        
#text = 'Ta Greeklish (Gkriklis), apo tis lekseis greek (ellinika) kai english (anglika), gnwsta kai ws Grenglish, Latinoellinika i Frankolevantinika, einai i elliniki glwssa grammeni me to latiniko alfavito. Einai ena eidos metagrafis.'
#print(translate_text(text))

if __name__ == '__main__':
    import sys
    for line in sys.stdin:
        print(translate_text(line.strip()))
