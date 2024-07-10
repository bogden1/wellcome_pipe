#!/usr/bin/env python3
#Applying HaToRI's approach (serv/src/wordcloud/__init__.py)

import sys
from wordcloud import WordCloud

def draw(freqs, fnam, colorize = False, dark = 0.5):
  #color stuff
  if colorize:
    if dark != 0.5:
      print('"colorize" set: ignoring meaningless "dark"', file = sys.stderr)
  else:
    if dark < 0 or dark > 1:
      raise
  if not colorize:
    def scale(m, M): return int((M - m) * (1 - dark) + m)
    r = scale(70, 130)
    g = scale(130, 220)
    b = scale(150, 255)

    kwargs = {
      'width': 1000,
      'height': 1000,
      'stopwords': {},
      'background_color': None,
      'relative_scaling': 1.0,
      'min_font_size': 15, #nb this effectively sets a 'minimum importance' threshold -- but word/phrase/term length is also a factor
      'normalize_plurals': False,
      'mode': 'RGBA',
    }
    if not colorize:
      kwargs['color_func'] = lambda *kwds, **args: (r, g, b, 255)
    wc = WordCloud(**kwargs).generate_from_frequencies(freqs)
    wc.to_image().save(fnam + '.png')
    with open(fnam + '.svg', 'w') as f:
      print(wc.to_svg(), file = f)

