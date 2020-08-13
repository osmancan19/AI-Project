import requests
import re
from bs4 import BeautifulSoup
from nltk.util import ngrams

# Title : The Adventures of Sherlock Holmes, by Arthur Conan Doyle
# This book is free to use. Therefore, it will not cause any legal trouble (Free license)
link = 'https://www.gutenberg.org/files/1661/1661-h/1661-h.htm'
html = requests.get(link).text
b_soup = BeautifulSoup(html, 'html.parser')

# Create a text file to write
text_file_1 = open("prob_one_gram.txt","w+")
text_file_2 = open("prob_two_gram.txt","w+")

# This link includes some information about the provider, but we are only looking for what is written in the book
# Therefore, we are extracting unnecessary stuff
text = ''
for chapters in b_soup.find_all('div', {'class' : 'chapter'}):
  text = text + chapters.text

# 1-Gram
# Tokenize each word to count later
# [a-z][a-z]?[a-z]?[a-z]?[a-z]? = Word with at most 5 letters surrounded by spaces
words_1 = re.findall(' [a-z][a-z]?[a-z]?[a-z]?[a-z]? ', text.lower())
words_1 = [word[1:-1] for word in words_1] # Remove empty spaces around tokens

# Calculate frequency of each word
freqs_1 = [words_1.count(x) for x in words_1]
freq_dict_1 = dict(list(zip(words_1, freqs_1)))
sorted_freq_list_1 = sorted(freq_dict_1.items(), reverse=True, key = lambda x: x[1])

# Create a probability distribution using frequency
sorted_freq_list_1 = [[word, freq / len(words_1)] for (word, freq) in sorted_freq_list_1]

# Write and close text file
for word in sorted_freq_list_1:
  text_file_1.write(str(word[0]) + " " + str(word[1]) + '\n')
text_file_1.close()

# 2-Grams
# Tokenize each two words to count later
# A phrase can be at most 5 char (excluding space)
words_2 = re.findall(' [a-z] [a-z] ', text.lower()) # Case 1 : " _ _ " (_ indicates char)
words_2.extend(re.findall(' [a-z][a-z] [a-z] ', text.lower())) # Case 2 : "__ _"
words_2.extend(re.findall(' [a-z] [a-z][a-z] ', text.lower())) # Case 3 : "_ __"
words_2.extend(re.findall(' [a-z][a-z] [a-z][a-z] ', text.lower())) # Case 4 : "__ __"
words_2.extend(re.findall(' [a-z][a-z][a-z] [a-z][a-z] ', text.lower())) # Case 5 : "___ __"
words_2.extend(re.findall(' [a-z][a-z] [a-z][a-z][a-z] ', text.lower())) # Case 6 : "__ ___"
words_2 = [phrase[1:-1] for phrase in words_2] # Remove empty spaces around tokens

# Calculate frequency of each word
freqs_2 = [words_2.count(x) for x in words_2]
freq_dict_2 = dict(list(zip(words_2, freqs_2)))
sorted_freq_list_2 = sorted(freq_dict_2.items(), reverse=True, key = lambda x: x[1])

# Create a probability distribution using frequency
sorted_freq_list_2 = [[word, freq / len(words_2)] for (word, freq) in sorted_freq_list_2]

# Write and close text file
for word in sorted_freq_list_2:
  text_file_2.write(str(word[0]) + " " + str(word[1]) + '\n')
text_file_2.close()