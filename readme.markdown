# Internews HID

A Humanitarian Dashboard.


## API Documentation


URL

### /items/

#### POST

- create an item. Should return the object, including its unique ID  and the
  system allocated  creation time.

    { 
        "body": "blah", 
        "timestamp": "..." 
    }  


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

#### GET 

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

## '/taxonomies/'

### GET

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

### POST

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

Adds a taxonomy including terms. If the slug is calculated we have to return
it.

## '/taxonomies/<taxonomy-slug>/'

### GET
- details of the taxonomy

E.g.: `/taxonomies/ebola-questions/`.

- Taxonomy details URL should use the taxonomy's sluggified name

## '/terms/'

Get list of all terms

### GET


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



### POST

- Update the details of a Taxonomy.

- Use the slug as unique id (i.e. don't deal with the internal numeric id)

## '/taxonomies/'


## Taxonomies as Item metadata:

These categories and tags will be used to store all the variable metadata
for the `Item`s. So when we get items, we want to also get their metadata.
And also to allow Item POST requests to add metadata terms.

### To create items with metadata

TODO

### /item/<item-id>/<taxonomy-id>/

e.g.:

    '/items/2314/ebola-questions/'

#### GET on this would give the same list of term objects.

- Returns a subset of the terms for the given taxo' that apply to the
  specified item. 

    [ { "name": "...",
        "long-name", "...",
      }
    ]

PUT { "name": "term" } updates a category

If the taxonomy has cardinality `optional` this sets its value, irrespective of
what it was before. If it has `multiple` this could either:

- cause an exception (you expect a list), or
- set the list to the given singleton (I don't like this)


POST { "name": "term" } adds a term

Adds it to the item so long as the cardinality constraint is not violated.

PUT [ { "name": "term" }, ... ]

- sets the values to those given, for cardinality `multiple`
- throws error for `optional` 






















/items/

        { body="kljlik" }


/items/67/

    POST  { long_name="new name!" }

    POST  { terms: [
                { "taxonomy": "ebola-questions",
                  "name": "vaccine",
                },
                ...
            ]
    }

/items/67/metadata/ebola-questions/

    POST { "name": "health" }
    POST [ { "name": "health" }]
    POST []






    GET /items/67/

        { id:87, 
          body:"lsdfkljasd",  
          meta: {
             "ebola-questions": "vaccine",
             ...
          }
        }


        { id:87, 
          body:"lsdfkljasd",  
          meta: [
             { "taxonomy": "ebola-questions",
               "name": "vaccine",
               "long_name": "when will there be a vaccine"
             },
             ...
          ]
        }


Removing a tag from an item

/items/65/ebola-questions/vaccine

        DELETE

/taxonomies/ebola-questions/vaccine/65 
        DELETE
