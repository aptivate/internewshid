from django_tables2.data import TableListData


class PreSortedTableListData(TableListData):

    # We don't want the table to do any ordering, so we have the order_by
    # method do nothing.
    def order_by(self, _):
        pass
