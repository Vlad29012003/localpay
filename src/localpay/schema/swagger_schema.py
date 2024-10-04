from drf_yasg import openapi

search_param = openapi.Parameter(
    'search',
    openapi.IN_QUERY,
    description="Search by name, surname, or login",
    type=openapi.TYPE_STRING
)
