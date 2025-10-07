from api.shared.domain.exceptions import NotFoundException
from api.company.infrastructure.company_repo import CompanyRepo
from api.end_users.infrastructure.end_user_repo import EndUserRepo


class ChatServices:
    def __init__(self):
        pass

    def verify_company(self, company: id):
        company = CompanyRepo().get_company_by_id(company)
        if not company:
            raise NotFoundException("Company not found")

    def verify_user(self, user: id):
        user = EndUserRepo().get_user_by_id(user)
        if not user:
            raise NotFoundException("User not found")
