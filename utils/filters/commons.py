from utils.filters.parser import parse_search


class FilterListMixin:
    filter_fields = {}

    def get_search_filters(self):
        search_expr = self.request.GET.get('search', None)
        if not search_expr:
            return None

        return parse_search(search_expr, self.filter_fields)
