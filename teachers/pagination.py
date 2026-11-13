from rest_framework.pagination import PageNumberPagination

class TeacherPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"  # 允许前端 ?page_size=50
    max_page_size = 100