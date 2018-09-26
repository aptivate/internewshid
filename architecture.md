# Humanitarian Information Dashboard Architecture

## Adding a new spreadsheet format

Create a new `SheetProfile` object with a `profile`, for example:
```
    {
        "name":"Geopoll",
        "format":"excel",
        "label":"geopoll",
        "skip_header":1,
        "taxonomies":{
            "contexts":"Ebola-Liberia",
            "countries":"Liberia",
            "data-origins":"Geopoll Spreadsheet",
            "item-types":"question"
        },
        "columns":[
            {
                "field":"terms",
                "type":"taxonomy",
                "name":"Province",
                "taxonomy":"tags"
            },
            {
                "field":"timestamp",
                "type":"date",
                "name":"CreatedDate",
                "date_format":"%m/%d/%y"
            },
            {
                "field":"ignore",
                "type":"ignore",
                "name":"AgeGroup"
            },
            {
                "field":"body",
                "type":"text",
                "name":"QuestIO"
            }
        ]
  }
```

`name`
: A human-readable name for this profile

`format`
: File format (currently must be `excel`)

`label`
: Unique identifier (not currently used???)

`skip_header`
: If `0` or absent use the profile's order of columns. Otherwise use the header to define the order

`columns`
: An array of columns to be imported from the spreadsheet. See [Column keys](#column-keys)

### Column keys

`field`
: See [Fields](#fields)

`type`
: Supported types are `date`, `text`, `integer`, `number` (decimal), `taxonomy`. This can also be set to `ignore` for ignored fields.

`name`
: The column heading in the spreadsheet

`date_format`
: String used to import the cells of `date` type (as used by [strptime](https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior))

`taxonomy`
: Taxonomy to use when importing terms

### Fields

`ignore`
: This column is not imported

`body`
: The main body of the message. Stored as `body` on the `Item` object

`timestamp`
: Date when reported. Stored as `timestamp` on the `Item` object

`terms`
: Import field as taxonomy terms (eg tags)

## Creating a new Tabbed Page

A tabbed page has a `name` and one or more tab instances. These determine the pages of the View & Edit screen.

The `Settings` are specified in a blob of JSON with the following format:
```
{
  "source":"kobo",
  "columns":[
    "select_item",
    "created",
    "timestamp",
    "body",
    "category"
  ],
  "categories":[
    "ebola-questions"
  ],
  "filters":{
    "terms":[
      "item-types:question"
    ]
  },
  "label":"Questions"
}
```

`source`
: Matches the `SheetProfile` `label` above

`columns`
: Which columns to display in the table

`categories`
: ???

`filters`
: Which filters to apply when listing items in this tab

`label`
: ???

## Importing a spreadsheet

Importing a spreadsheet will create ``Item`` objects (see `data_layer/models.py` via the ``transport`` app).
