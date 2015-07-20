# Internews HID

A Humanitarian Dashboard.


## API Documentation


### Items

Base URL '/items/'

#### Create Items

'/items/' POST 

    { 
        "body": "blah", 
        "timestamp": "..." 
    }  

- create an item. Should return the object, including its unique ID  and the
  system allocated  creation time.


#### Create item with tags and categories

    {
        "body": "blah", 
        "timestamp": "...",
        "metadata": [
            { "slug": "<taxonomy-slug>",  // slug OR: name
              "name": "<taxonomy name>"
              "tems": [
                "<tem-name>", // multiple values for tags
                "<tem-name>",
                "<tem-name>",
              ]
            }
            { "slug": "<taxonomy-slug>",  // slug OR: name
              "name": "<taxonomy name>"
              "tems": ["<tem-name>"] // single for category
            }
        ]
    }

We need either the `slug` or the `name` (from which the slug can be derived),
and a list of relevant terms. If the name and slug don't match, obviously there
should be an exception.

#### List items

'/items/' GET

- returns a list of Items

    [ { "id": nn, 
        "body": "...",
        "created": ...
        "timestamp": ...
        },
        { ... },
        ...
    ]

- When we do categories it should return those the same way as post above,
  e.g.:
          
    [ { 
        "id": nn, 
        "body": "...",
        "created": ...
        "timestamp": ...
        "metadata": [
            {"name": ... },
        ]
      },
        { ... },
        ...
    ]


## Categories and Tags (Taxonomies)

They need their own list and details urls, and we should include them in
the expanded `Item` JSON somehow too.

### List all Taxonomies

'/taxonomies/' GET

- Return list of taxonomies

    [
      { "name": "Ebola Question Type",
        "slug": "ebola-question-type",
        "long_name": "Question Type",  
        "cardinality": "optional",
        "vocabulary": "closed",
        "terms": [
            {"name": "Is Ebola Real", 
             "long name": ...
            },
            ...
        ]
      },
      { "name": "Reliability", 
        ...
      },
      ...
    ]

  Here `long name` is shorter than the `name` because I'm thinking that
  long name is the one that gets used as a column heading, whereas `name`
  is the unique name for making the unique slug.

NOTE: It is the slug not the name that has has to be unique. What do we do
when someone tries to create "Ebola Questions" and "ebola-questions" as
taxonomies? Do they map onto the same slug? How do we handle that since
the unique field is derived from the given one?


### Add a new Taxonomy

'/taxonomies/' POST

      { "name": "Ebola Question Type",
        "slug": "ebola-question-type", // do we supply this or is it calculated?
        "long_name": "Question Type",  
        "cardinality": "optional",
        "vocabulary": "closed",
        "terms": [
            {"name": "Is Ebola Real", 
             "long name": ...
            },
            ...
        ]
      },

Adds a taxonomy (optionally including terms). The slug is calculated it should
be returned by the call.

### Taxonomy details

'/taxonomies/<taxonomy-slug>/' GET

      { "name": "Ebola Question Type",
        "slug": "ebola-question-type", // calculated from name
        "long_name": "Question Type",  
        "cardinality": "optional",
        "vocabulary": "closed",
        "terms": [
            {"name": "Is Ebola Real", 
             "long name": ...
            },
            ...
        ]
      },

e.g. `/taxonomies/ebola-questions/`  

- Taxonomy details URL should use the taxonomy's sluggified name

### Update Taxonomy Details 

`/taxonomies/ebola-questions/`  POST

      { 
        "long_name": "Question Type",  
        "cardinality": "optional",
        "vocabulary": "closed",
      },

- Use the slug as unique id (i.e. don't deal with the internal numeric id)

### List terms per taxonomy

`/taxonomies/<taxonomy-slug>/terms/ GET

- returns list of terms

### Add a term to a taxonomy

We could do 
`/taxonomies/ebola-questions/terms/`  POST { 'name': 'vaccine' }

But for the moment we;re doing

`/terms/` POST { 'name': 'vaccine', 'taxonomy': 'ebola-questions' }


### List all Terms (all taxonomies)

'/terms/' GET

Get list of all terms (from all taxonomies).
Could add query params to limit to a certain Taxonomy

'/terms/?taxonomy=ebola-questions' GET

Or item

'/terms/?item=416' GET

Or both

'/terms/?taxonomy=ebola-questions&item=416' GET

Returns a list of terms:

    [ { "name": "Ebola Real?",
        "long_name": "Is Ebola Real?",
        "taxonomy": "ebola-questions",
      },
      { "name": "Timescale",
        "long_name": "When will Liberia be free of Ebola?"
        "taxonomy": "ebola-questions",
      },
      ...
    ]



## Taxonomies as Item metadata:

These categories and tags will be used to store all the variable metadata
for the `Item`s. So when we get items, we want to also get their metadata.
And also to allow Item POST requests to add metadata terms.

### To create items with metadata

See above Create Items with tags and categories

### List terms for an item

/item/<item-id>/<taxonomy-id>/ GET

e.g.:

    '/items/2314/taxonomies/ebola-questions/' GET

- Return list of ebola questions for item 2314

OR

    '/items/2314/taxonomies/terms/' GET

- list all terms for 2314.

- Add qyery parameters to select for a given taxonomy

    '/items/2314/taxonomies/terms/?taxonomy=ebola-questions' GET

- To delete a single term

    '/items/2314/taxonomies/terms/<term-slug>/'  DELETE

- Where term slug is the unique slug for the term. 
e.g.
    '/items/2314/taxonomies/terms/ebola-questions-


In which case you can add a term to an object like this

    '/items/2314/ebola-questions/' POST { 'name': 'Duration' }

And you can remove one like this

    '/items/2314/ebola-questions/duration' DELETE


## Dependencies

To run all the tests, you need [phantomjs](http://phantomjs.org/) installed.

With node/npm

    npm install -g phantomjs

Or, on ubuntu

    apt-get install phantomjs
