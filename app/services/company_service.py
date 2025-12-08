from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.company_model import CompanyModel
from app.schemas.company_schema import CompanyUpdate,CompanyResponse,CompanyCreate

class CompanyService:
    def __init__(self,db_session:AsyncSession):
        self.db = db_session
    
    async def create_company(self,company_data: CompanyCreate) -> CompanyModel:
        company = CompanyModel(**company_data.model_dump())
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def get_company(self,company_id:int)->CompanyModel:
        query = select(CompanyModel).where(CompanyModel.id == company_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_companies(self) -> list[CompanyModel]:
        query = select(CompanyModel)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_company(self,company_id:int,company_data:CompanyUpdate)->CompanyModel:
        company = await self.get_company(company_id)
        if not company:
            return None
        for field,value in company_data.model_dump(exclude_unset=True).items():
            setattr(company,field,value)
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def delete_company(self,company_id:int)->bool:
        company = await self.get_company(company_id)
        if not company:
            return False
        await self.db.delete(company)
        await self.db.commit()
        return True


