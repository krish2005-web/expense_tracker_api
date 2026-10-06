from pydantic import BaseModel,ConfigDict,Field,field_validator
from datetime import datetime,date

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=2, max_length=50)
    description: str | None = Field(
        default=None,
        max_length=200
    )
    expense_date: date

    @field_validator("category")
    @classmethod
    def validate_category(cls, value):
        allowed_categories = {
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Other"
        }

        value = value.strip().title()

        if value not in allowed_categories:
            raise ValueError("Invalid category")

        return value

class ExpenseResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    title:str
    amount:float
    category:str
    description:str
    expense_date:date
    created_at:datetime
    user_id:int
    receipt_path: str | None = None

class ExpenseUpdate(BaseModel):
    title:str | None = None
    amount:float | None = None
    description:str | None = None
    expense_date:date | None = None