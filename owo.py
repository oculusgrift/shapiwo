#!/usr/bin/env python3
""" owo is a godawful module for making meme tweets """
from random import choice
from re import search
from typing import List, Dict

# Prefixes to apply to tweets
PREFIXES: List[str] = [
  '<3 ',
  'H-hewwo?? ',
  'HIIII! ',
  'Haiiii! ',
  'Huohhhh. ',
  'OWO ',
  'OwO ',
  'UwU '
]

# Suffixes to appy to tweets
SUFFIXES: List[str] = [
  ' :3',
  ' UwU',
  ' ʕʘ‿ʘʔ',
  ' >_>',
  ' ^_^',
  '..',
  ' Huoh.',
  ' ^-^',
  ' ;_;',
  ' ;-;',
  ' xD',
  ' x3',
  ' :D',
  ' :P',
  ' ;3',
  ' XDDD',
  ', fwendo',
  ' ㅇㅅㅇ',
  ' (人◕ω◕)',
  '（＾ｖ＾）',
  ' Sigh.',
  ' ._.',
  ' >_<'
]

# All substitutions to perform on the provided text to "owo" it
SUBSTITUTIONS: Dict[str, str] = {
  'r': 'w',
  'l': 'w',
  'R': 'W',
  'L': 'W',
  'no': 'nu',
  'has': 'haz',
  'have': 'haz',
  'you': 'uu',
  'the ': 'da ',
  'The ': 'Da '
}

def whats_this(string: str, affixes: bool = True) -> str:
  """ whats_this takes a given string and owos it, adding prefixes """

  # Get a random prefix
  prefix = choice(PREFIXES)

  # Search for a link and then strip it if there is one
  link = search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
  if link is not None:
    string = string[:link.start()-1]

  # owo the provided text
  owo = replace(string)

  # Get a random suffix
  suffix = choice(SUFFIXES)

  if affixes and len(f'{prefix}{owo}') <= 280:
    # If we can fit the prefix, add it
    owo = f'{prefix}{owo}'

  if affixes and len(f'{owo}{suffix}') <= 280:
    # If we can fit the suffix, add it
    owo = f'{owo}{suffix}'

  # Return the meme text
  return owo

def replace(string: str) -> str:
  """ replace takes a given string and owos it """
  for key, value in SUBSTITUTIONS.items():
    # Perform all substitutions on the string
    string = string.replace(key, value)
  
  # Return the owo'd string
  return string
