from flask import Blueprint, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import math

# Init Blueprint
puzzle = Blueprint('puzzle', __name__)

# Init Selenium
def open_browser():
  try:
    global driver
    driver = webdriver.Firefox(executable_path="/Users/cagataykupeli/Desktop/CS 461/Project/Puzzle/back-end/geckodriver")
  except:
    pass

# Helper Functions
def redirect_puzzle_page():
  try:
    driver.get("https://www.nytimes.com/crosswords/game/mini")
    #driver.get("https://www.nytimes.com/crosswords/game/mini/2016/06/01") # Use it during Saturdays for testing
  except:
    pass


def inspect_old_clues():
  old_clues_across = {} # Empty dictionary
  old_clues_down = {} # Empty dictionary
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  for i, (old_clue_label, old_clue) in enumerate(zip(b_soup.find_all('span', {'class' : 'Clue-label--2IdMY'}), b_soup.find_all('span', {'class' : 'Clue-text--3lZl7'}))):
    if(i < 5):
      old_clues_across[old_clue_label.text] = old_clue.text
    else:
      old_clues_down[old_clue_label.text] = old_clue.text
  return old_clues_across, old_clues_down

def inspect_puzzle_layout():
  blocked_cells = []
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  for blocked_cell in b_soup.find_all('rect', {'class' : 'Cell-block--1oNaD'}):
    blocked_cells.append(int(blocked_cell.get('id')[8:]))
  return blocked_cells

def inspect_cell_numbers():
  cell_numbers = []
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  for cell_text_anchor in b_soup.find_all('text', {'text-anchor' : 'start'}):
    cell_number = cell_text_anchor.find_previous_sibling('rect').get('id')[8:]
    cell_numbers.append(int(cell_number))
  return cell_numbers

def reveal_solutions():
  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/main/div[2]/div/div[2]/div[3]/div/article/div[2]/button'))
    ).click()
  except:
    pass
  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/div[1]/li/button'))
    ).click()
  except:
    pass
  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/li[2]/button'))
    ).click()
  except:
    pass
  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/li[2]/ul/li[3]/a'))
    ).click()
  except:
    pass
  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/article/div[2]/button[2]'))
    ).click()
  except:
    pass
  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/span'))
    ).click()
  except:
    pass

def inspect_solutions():
  solutions = []
  for _ in range(0, 25):
    solutions.append('')
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  for letter in b_soup.find_all('text', {'text-anchor' : 'middle'}):
    # For some reason at 26, Nov, NY Times changed their html structure. As a result, this monstrosity occured. I could just use the script in if statement. However, I fear that they might change the structure again.
    if(len(letter.text) > 1):
      solutions[int(letter.find_previous_sibling('rect').get('id')[8:])] = letter.text[0]
    elif(len(letter.text) == 1):
      solutions[int(letter.find_previous_sibling('rect').get('id')[8:])] = letter.text
  return solutions

def convert_solutions(solution_list):
  solutions_dict = {}
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  for i in b_soup.find_all('text', {'text-anchor' : 'start'}):
    index = int(i.find_previous_sibling('rect').get('id')[8:])
    # Down
    if(index < 5):
      solutions_dict[i.text + 'D'] = ''.join([solution_list[index], solution_list[5 + index], solution_list[10 + index], solution_list[15 + index], solution_list[20 + index]])
    elif((index >= 5) & (solution_list[index - 5] == '')):
      solutions_dict[i.text + 'D'] = ''.join([solution_list[index % 5], solution_list[5 + (index % 5)], solution_list[10 + (index % 5)], solution_list[15 + (index % 5)], solution_list[20 + (index % 5)]])
    # Across
    if((index % 5 != 0) & (solution_list[index - 1] == '')):
      solutions_dict[i.text + 'A'] = ''.join(solution_list[(index // 5) * 5:((index // 5) * 5 + 5)])
    elif((index % 5 == 0) & (solution_list[index] != '')):
      solutions_dict[i.text + 'A'] = ''.join(solution_list[(index // 5) * 5:((index // 5) * 5 + 5)])
  return solutions_dict

def search_famous_person(solution):
  driver.get('https://www.famousbirthdays.com/names/' + solution.lower() + '.html')
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  if(b_soup.find(text = 'Oops!') == None):
    href = b_soup.find('a', {'class' : 'face person-item'}).get('href')
    driver.get(href)
    b_soup = BeautifulSoup(driver.page_source, 'html.parser')
    [x.replace_with(x.text) for x in b_soup.find_all('a')]
    # Replace nonbreak space with regular space
    new_clue = b_soup.find('p').text[:-1].replace('\xa0', ' ') # \xa0 is unicode of nonbreak space
    # If clue is more than 2 sentences, use only the 1st one
    for i, l in enumerate(new_clue):
      if(l == '.'):
        new_clue = new_clue[:i]
    # Clue supposed to be 1 sentence long. However, it is still longer than 120 chars
    if(len(new_clue) > 120):
      end_sentence = re.search('" [A-Z]', new_clue)
      if(end_sentence != None):
        end_index = re.search('" [A-Z]', new_clue).end()
        new_clue = new_clue[:end_index - 2]
    # If the word is mentioned in clue, return nothing
    '''
    if(new_clue.lower().find(solution.lower()) == -1):
      return new_clue
    else:
      return ''
    '''
    return new_clue
  else:
    return ''

def search_wordnet(solution):
  driver.get('http://wordnetweb.princeton.edu/perl/webwn?s=' + solution.lower())
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  [x.extract() for x in b_soup.find_all('a')]
  [x.extract() for x in b_soup.find_all('b')]
  [x.extract() for x in b_soup.find_all('i')]
  html = b_soup.find('li')
  if(html != None):
    new_clue = html.text
    new_clue = new_clue[:-2]
    for i, l in enumerate(new_clue):
      if(l == '('):
        new_clue = new_clue[i + 1:]
        break
    new_clue_list = new_clue.split(';')
    #print(new_clue_list)
    for i, clue in enumerate(new_clue_list):
      # If word is not the 1st clue in the list, it starts with ' '. Thus, we eliminate that by removing that ' '.
      if(i != 0):
        clue = clue[1:]
      if((clue.lower().find(solution.lower()) == -1) & (len(clue) < 90)):
        # Check if it is an abbreviation
        extended_abb = clue
        clue = clue.replace('-', ' ') # PTSD might be written as post-traumatic stress disorder
        abb_list = clue.split(' ')
        abb_checker = ''
        for abb in abb_list:
          abb_checker = abb_checker + abb[0]
        if(abb_checker.lower() != solution.lower()):
          clue = clue[0].upper() + clue[1:]
          return clue
        else:
          return find_abbreviation_meaning(extended_abb)
    return ''
  else:
    return ''

def search_urban(solution):
  driver.get('https://www.urbandictionary.com/define.php?term=' + solution.lower())
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  if(b_soup.find('div', {'class' : 'shrug space'}) == None):
    new_clue = b_soup.find('div', {'class' : 'meaning'}).text
    # Remove '.' at the end if exists
    if(new_clue[-1] == '.'):
      new_clue = new_clue[:-1]
    # If the length of clue is more than 120 (4 Lines) chars, return nothing
    if(len(new_clue) > 120):
      return ''
    else:
      new_clue = new_clue[0].upper() + new_clue[1:]
      # If a word is mentioned in clue, return nothing
      if(new_clue.lower().find(solution.lower()) == -1):
        return new_clue
      else:
        return ''
  else:
    return ''

def search_merriam_webster(solution):
  driver.get('https://www.merriam-webster.com/dictionary/' + solution.lower())
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  # There is two ways this site represents its data
  if(b_soup.find('h1', {'class' : 'mispelled-word'}) == None):
    if(b_soup.find('span', {'class' : 'dtText'}) != None):
      new_clue = b_soup.find('span', {'class' : 'dtText'}).text
      new_clue = new_clue.replace(':', '') # For some reason, some descriptions starts with ':'
      extended_abb = new_clue # Store this information just in case if found solution is abb
      # If word starts with ':', it continues with a ' '
      new_clue = new_clue.replace('-', ' ')
      # Merriam webster is a strange website. There are so many ways to display definition.
      # One includes example as well, following section aims to deal with that particular case
      for i, l in enumerate(new_clue):
        if(l == '\n'):
          new_clue = new_clue[:i - 1]
          break
      while(new_clue[-1] == ' '):
        new_clue = new_clue[:-1]
      if(new_clue[0] == ' '):
        new_clue = new_clue[1:]
      # Check if it is an abbreviation
      abb_list = new_clue.split(' ')
      abb_checker = ''
      for abb in abb_list:
        abb_checker = abb_checker + abb[0]
      if(abb_checker.lower() != solution.lower()):
        new_clue = new_clue[0].upper() + new_clue[1:]
        if(len(new_clue) < 80):
          return new_clue
        else:
          return ''
      else:
        return find_abbreviation_meaning(extended_abb)
    else:
      if(b_soup.find('span', {'class' : 'mw_t_sp'}) != None): # If the word is an abb, check for an example sentence
        new_clue = b_soup.find('span', {'class' : 'mw_t_sp'}).text
        new_clue = new_clue.lower()
        placeholder = ''.join(['_' for _ in range(0, len(solution))])
        new_clue = new_clue.replace(solution.lower(), placeholder)
        new_clue = new_clue[0].upper() + new_clue[1:]
        new_clue = '"' + new_clue + '"'
        if(new_clue[-1] == '.'):
          new_clue = new_clue[:-1]
        if(len(new_clue) < 80):
          return new_clue
        else:
          return ''
      else:
        if(b_soup.find('span', {'class' : 'unText'}) != None):
          new_clue = b_soup.find('span', {'class' : 'unText'}).text
          new_clue = new_clue[0].upper() + new_clue[1:]
          return new_clue
    return ''
  else:
    return ''

def search_cambridge(solution): # Default value of spacing is false
  driver.get('https://dictionary.cambridge.org/dictionary/english/' + solution)
  b_soup = BeautifulSoup(driver.page_source, 'html.parser')
  new_clue_obj = b_soup.find('div', {'class' : 'def ddef_d db'})
  if(new_clue_obj != None):
    new_clue = new_clue_obj.text
    # Some of the abbreviation states that it is and abbreviation at the start of sentence
    # If abbreviation word stated, it is in form of "abbreviation for sth (=definition)"
    if(re.search('abbreviation', new_clue) != None):
      for i, l in enumerate(new_clue):
        if(l == '='):
          if(new_clue[i - 1] == '('):
            new_clue = new_clue[i + 2:-1]
    else:
      # If no abbreviation word appears, it sometimes still have the form "definition 1 (=definition 2)",
      # but definition 1 is always better
      for i, l in enumerate(new_clue):
        if(l == '='): # If it has the form definition 1 only. It will not enter this if statement and use definition 1 only
          if(new_clue[i - 1] == '('):
            new_clue = new_clue[:i - 1]
    # If the word is short form of another word, it has the form "short form of long form"
    # However, they usually provide an example
    if(re.search('short form', new_clue) != None):
      new_clue = b_soup.find('div', {'class' : 'examp dexamp'}).text
      new_clue = new_clue.lower()
      new_clue = new_clue.replace(solution.lower(), '_____')
    new_clue = new_clue[0].upper() + new_clue[1:]
    return new_clue
  else:
    return ''


# Takes an extended version of abbreviation and tries to find an suitable solution
# It is used when algorithm detects possibility of abbreviation
# For example, when you search PTSD, it gives post-traumatic stress disorder. We know that this is extended version of PTSD because
# Post
# Traumatic
# Stress
# Disorder
def find_abbreviation_meaning(expanded_solution):
  # Use cambridge for finding abbreviation meaning
  expanded_solution = expanded_solution.lower()
  return search_cambridge(expanded_solution)

# Split a string into possible word pairs
def split_string(string):
  return [(string[:i], string[i:]) for i in range(1, min(len(string), 5))] # Excluding the word itself

# Return the probability of one word if it exists in our text file
# P(A)
def prob_1(word):
  prob = 0
  with open('./prob_one_gram.txt','r') as text_file:
    for line in text_file:
      line_list = line.split()
      if(line_list[0] == word):
        prob = line_list[1]
  return float(prob)

# Returns the probability of two word phrases if it exists in our text file
# P(A, B)
def prob_2(words):
  prob = 0
  with open('./prob_two_gram.txt','r') as text_file:
    for line in text_file:
      line_list = line.split()
      if(line_list[0] + ' ' + line_list[1] == words):
        prob = line_list[2]
  return float(prob)

# Returns the probability of two words phrases given previous word
# P(A | B) = P(A, B) / P(B)
def cond_prob(word, prev_word):
  prob_union = prob_2(word + ' ' + prev_word) # P(word, prev_word)
  prob_prev = prob_1(prev_word) # P(prev_word)
  if((prob_union > 0) & (prob_prev > 0)):
    return prob_union / prob_prev
  else:
    # Probability cannot be less than 0
    # If phrase (word + ' ' + word) does not exits, there is no point of calculating probability
    # If previous word does not exits, there is no point of calculating probability 
    # (If previous word is missing, there should not be a combination)
    return 0

# Both find_best_segmentation_ind and find_best_segmentation_cond requires a word such as "weare" not "we are". Thus, directly insert gathered solution without spliting
# Find the most possible word pair for independent words (Unused)
def find_best_segmentation_ind(string):
  candidates = split_string(string)
  probs = []
  for first, second in candidates:
    prob_first = prob_1(first)
    prob_second = prob_1(second)
    if((prob_first == 0) & (prob_second == 0)):
      probs.append(0)
    elif((prob_first != 0) & (prob_second != 0)):
      probs.append(prob_first * prob_second)
    elif((prob_first != 0) & (prob_second == 0) & (len(second) == 0)):
      probs.append(prob_first)
    elif((prob_first == 0) & (prob_second != 0) & (len(first) == 0)):
      probs.append(prob_first)
    else:
      probs.append(0)
  sorted_candidates = [x for _, x in sorted(zip(probs, candidates))]
  sorted_candidates.reverse()
  return sorted_candidates

# Find the most possible word pair using conditional probability
def find_best_segmentation_cond(string):
  candidates = split_string(string)
  probs = []
  for first, second in candidates:
    prob_first = prob_1(first)
    prob_second = cond_prob(second, first)
    if((prob_first == 0) & (prob_second == 0)):
      probs.append(0)
    elif((prob_first != 0) & (prob_second != 0)):
      probs.append(prob_first * prob_second)
    elif((prob_first != 0) & (prob_second == 0) & (len(second) == 0)):
      probs.append(prob_first)
    elif((prob_first == 0) & (prob_second != 0) & (len(first) == 0)):
      probs.append(prob_first)
    else:
      probs.append(0)
  sorted_candidates = [x for _, x in sorted(zip(probs, candidates))]
  sorted_candidates.reverse()
  return sorted_candidates

def find_alt_clue(solution):
  solution = solution.lower()
  try:
    new_clue = ''
    # Search a famous person
    new_clue = search_famous_person(solution)
    # If there is no famous person, search at wordnet dict
    if(new_clue == ''):
      new_clue = search_wordnet(solution)
      # If there is no regular dict description for that solution, search at urban dict
      if(new_clue == ''):
        new_clue = search_merriam_webster(solution)
        if(new_clue == ''):
          new_clue = search_cambridge(solution)
          if(new_clue == ''):
            new_clue = search_urban(solution)
            if(new_clue == ''):
              solution_segmentation_list = find_best_segmentation_cond(solution)
              for segmentation in solution_segmentation_list:
                # Check meriam webster
                if(new_clue == ''):
                  new_solution = ' '.join(segmentation)
                  new_clue = search_merriam_webster(new_solution)
                  if(new_clue == ''):
                    new_solution = '%27'.join(segmentation) # Depends on the site's structure
                    new_clue = search_merriam_webster(new_solution)
                    if(new_clue == ''):
                      new_solution = '+'.join(segmentation)
                      new_solution = '?q=' + new_solution
                      new_clue = search_cambridge(new_solution)
                      if(new_clue == ''):
                        new_solution = '-'.join(segmentation)
                        new_solution = new_solution + '?q='
                        new_solution = new_solution + '%27'.join(segmentation)
                        new_clue = search_cambridge(new_solution)
    return new_clue
  except:
    print('There is a problem related to ' + solution)

# API Calls
@puzzle.route('/get_old_clues_across')
def get_old_clues_across():
  redirect_puzzle_page()
  across, _ = inspect_old_clues()
  return jsonify(across)

@puzzle.route('/get_old_clues_down')
def get_old_clues_down():
  redirect_puzzle_page()
  _, down = inspect_old_clues()
  return jsonify(down)

@puzzle.route('/get_puzzle_layout')
def get_puzzle_layout():
  cell_types = dict(enumerate(['regular'] * 25))
  redirect_puzzle_page()
  for i in inspect_puzzle_layout():
    cell_types[i] = 'block'
  return jsonify(cell_types)

@puzzle.route('/get_cell_numbers')
def get_cell_numbers():
  redirect_puzzle_page()
  cell_numbers = inspect_cell_numbers()
  return jsonify(cell_numbers)

@puzzle.route('/get_solutions')
def get_solutions():
  redirect_puzzle_page()
  reveal_solutions()
  solution_dict = {}
  solution_list = inspect_solutions()
  for i in range(0, 25):
    solution_dict[str(i)] = solution_list[i]
  return jsonify(solution_dict)

@puzzle.route('/generate_new_clues')
def generate_new_clues():
  redirect_puzzle_page()
  reveal_solutions()
  solution_dict = convert_solutions(inspect_solutions())
  new_clues = {}
  for i in solution_dict:
    new_clues[i] = find_alt_clue(solution_dict[i])
  return jsonify(new_clues)

# Unused API
@puzzle.route('/get_solutions_dict')
def get_solutions_dict():
  redirect_puzzle_page()
  reveal_solutions()
  solution_dict = convert_solutions(inspect_solutions())
  return jsonify(solution_dict)

open_browser()