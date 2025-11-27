from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user_model import UserModel
from app.models.company_model import CompanyModel
from app.models.review_model import ReviewModel
from app.models.salary_model import SalaryModel

