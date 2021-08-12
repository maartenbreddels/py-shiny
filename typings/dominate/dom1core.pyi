"""
This type stub file was generated by pyright.
"""

__license__ = ...
class dom1core:
  '''
  Implements the Document Object Model (Core) Level 1

  http://www.w3.org/TR/1998/REC-DOM-Level-1-19981001/
  http://www.w3.org/TR/1998/REC-DOM-Level-1-19981001/level-one-core.html
  '''
  @property
  def parentNode(self):
    '''
    DOM API: Returns the parent tag of the current element.
    '''
    ...
  
  def getElementById(self, id): # -> None:
    '''
    DOM API: Returns single element with matching id value.
    '''
    ...
  
  def getElementsByTagName(self, name): # -> None:
    '''
    DOM API: Returns all tags that match name.
    '''
    ...
  
  def appendChild(self, obj): # -> dom1core:
    '''
    DOM API: Add an item to the end of the children list.
    '''
    ...
  


