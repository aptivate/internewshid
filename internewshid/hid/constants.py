# Define the categorization taxonomy associated with
# each item type. The front end currently supports a
# single item-type specific categorization taxonomy.
# (eg. all questions are categorized using the Ebola Questions
# taxonomy)
ITEM_TYPE_CATEGORY = {
    'question': 'ebola-questions'
}

# The default item type used when editing a item. Currently
# nothing prevents creating an item without an item type
# from the API, this is used by the edit form.
DEFAULT_ITEM_TYPE = {
    'taxonomy': 'item-types',
    'name': 'question',
    'long_name': 'Question'
}
