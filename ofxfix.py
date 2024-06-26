import sys
import re
import logging
import click
import click_log

from ofxtools.Parser import OFXTree
import xml.etree.ElementTree as ET

log = logging.getLogger(__name__)
click_log.basic_config(log)

dt_pattern = re.compile(r"""
  (?P<month>  \d{2}) / # slash
  (?P<day>    \d{2}) \ # space
  (?P<hour>   \d{2}) : # colon
  (?P<minute> \d{2})
""", re.VERBOSE)

exclude_patterns = {
  'String is entirely digits': re.compile('^\d+$'),
  'Phone number': re.compile('^\d{0,3}-?\d{3}-?\d{4}$'),
  'Store number': re.compile('^#\d+'),
  'Store number alpha prefixed': re.compile('^\w{2,3}\d{3}'),
  'Store number like Target': re.compile('\w-\d+'),
  'Store number like Caseys': re.compile('\d{4}T\d{3}', re.IGNORECASE),
  '2 or more X': re.compile('X{2,}', re.IGNORECASE)
}

exclude_keywords = [
  'PMT', 'PYMNTS', 'ONLINE', 'UTIL', 'BILL',
  'MN', 'MINNEAPOLIS', 'BLOOMINGTON', 'RICHFIELD',
  'TST*', 'DOWNTOWN'
]

minlength = 2

def fix_date(olddate, memo):
  match = re.findall(dt_pattern, memo)

  if match:
    return olddate[:4] + ''.join(list(match[0])) + '00'
  else:
    return olddate

def fix_text(oldtext, filter_functions):
  newtext = oldtext
  
  log.debug("Before {}".format(newtext))
  
  # Amazon order number
  newtext = re.sub("\*\w{9}( SEATTLE)?$", '', newtext)
  # Square
  newtext = re.sub("^SQ \*", '', newtext)
  # Toast
  newtext = re.sub("^TST\* ", '', newtext)
  # AMAZON
  newtext = re.sub("AMZN MKTP US", "AMAZON", newtext, flags=re.IGNORECASE)
  # Prime Video
  newtext = re.sub("PRIME VIDEO \*\w{9} SEATTLE", "Prime Video", newtext)
  # Google Fi
  newtext = re.sub("\*FI \w{6}", "Fi", newtext)
  # Whole Foods
  newtext = re.sub("WHOLEFDS", "Whole Foods", newtext)
  # Patreon
  newtext = re.sub("Patreon\* Membership Internet CA", "Patreon", newtext)
  
  pieces = re.split('\s', newtext)
  #log.debug("Parsing: {}".format(pieces))
  if pieces:
    newp = []
    for p in pieces[::-1]:
      passes = True
      for fn in filter_functions:
        if not fn(p):
          passes = False
          break
      if passes:
        #log.debug("Keeping chunk: {}".format(p))
        newp.append(p)
      else:
        pass
        #log.debug("Rejecting chunk: {}".format(p))

    newp.reverse()
    #log.debug("Final list for the item: {}".format(newp))
    newtext = " ".join(newp)

  log.debug("Keyword{}".format(newtext))
  
  newtext = re.sub("&amp;amp;amp;", "&amp;", newtext)

  newtext = newtext.title()
  
  newtext = re.sub("&Amp;", "&amp;", newtext)
  newtext = re.sub("Rei", "REI", newtext)
  log.debug("After  {}".format(newtext))
  
  return newtext

def filter_patterns(p):
  #log.debug("Running filter_patterns on {}...".format(p))
  for name, pattern in exclude_patterns.items():
    #log.debug("\tRunning pattern {}".format(name))

    if re.match(pattern, p):
      #log.debug("\tDiscarded {}: Matches pattern {}.".format(p, name))
      return False
  return True

def filter_minlength(p):
  if len(p) < minlength:
    #log.debug("Running filter_minlength on {}... FAIL: Length {} < minlength {}.".format(p, len(p), minlength))
    return False
  else:
    #log.debug("Running filter_minlength on {}... ok".format(p))
    return True

def filter_keywords(p):
  if p in exclude_keywords:
    #log.debug("Running filter_keywords on {}... FAIL: Matches an excluded keyword.".format(p))
    return False
  else:
    #log.debug("Running filter_keywords on {}... ok".format(p))
    return True

@click.command()
@click_log.simple_verbosity_option(log)
@click.argument('input',
                required=True,
                type=click.Path(exists=True,
                                dir_okay=False,
                                readable=True,
                                resolve_path=True))
@click.option('--patterns/--no-patterns', default=True,
              help="Enable/disable regexp-based pattern exclusion")
@click.option('--keywords/--no-keywords', default=True,
              help="Enable/disable keyword-based pattern exclusion")
@click.option('--silent', is_flag=True,
              help="Disable all output to stdout (for scripting)")
def cli(input, patterns=True, keywords=True, silent=False):
  if silent:
    while log.hasHandlers():
      log.removeHandler(log.handlers[0])
    log.addHandler(logging.NullHandler())

  filename = click.format_filename(input)
  log.info("Preparing to parse and fix {}".format(filename))

  parser = OFXTree()
  parser.parse(filename)

  for e in parser.getroot().findall(".//STMTTRN"):
    node_name = e.find('./NAME')
    node_memo = e.find('./MEMO')
    
    node_dtposted = e.find('./DTPOSTED')
    log.debug("Date {}".format(node_dtposted.text))
    #node_dtposted.text = fix_date(node_dtposted.text, node_memo.text)

    filter_functions = []
    # filter_functions.append(filter_minlength)
    if keywords: filter_functions.append(filter_keywords)
    if patterns: filter_functions.append(filter_patterns)

    if node_name != None:
        node_name.text = fix_text(node_name.text, filter_functions)
    
    if node_memo != None:
        # Just remove the Memo field. We don't care.
        e.remove(node_memo)

  parser.write(sys.stdout, encoding="unicode")

def __main__():
  cli()

if __name__ == '__main__':
  cli()

