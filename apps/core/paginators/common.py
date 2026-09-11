from rest_framework.pagination import LimitOffsetPagination


class CommonPaginator(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 25

    limit_query_description = 'Number of results to return per page.'
    offset_query_description = 'The initial index from which to return the results.'

