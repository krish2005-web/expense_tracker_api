from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.orm import Session
from app.schemas.expense import ExpenseCreate,ExpenseResponse,ExpenseUpdate
from app.database import get_db
from app.models.expense import Expense
from app.models.user import User
from app.dependencies import get_current_user
from sqlalchemy import func
from app.exceptions import ExpenseNotFoundException
from fastapi import BackgroundTasks
from fastapi import UploadFile, File
from pathlib import Path
import shutil
import uuid

router=APIRouter(prefix="/expense",
                 tags=["Expenses"])

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

def log_expense_created(expense_id: int):
    print(f"Expense {expense_id} was created")

@router.post("/",response_model=ExpenseResponse,status_code=201)
def create_expense(expense:ExpenseCreate,
                   background_task:BackgroundTasks,
                   db:Session=Depends(get_db),
                   current_user:User=Depends(get_current_user)
                  ):
    new_expense=Expense(
      title=expense.title,
      amount=expense.amount,
      category=expense.category,
      description=expense.description,
      expense_date=expense.expense_date,
      user_id=current_user.id
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    background_task.add_task(
    log_expense_created,
    new_expense.id
)
   
    return new_expense

@router.get("/",response_model=list[ExpenseResponse])
def get_expenses(category:str | None = Query(None),
                 min_amount:float | None = Query(None,ge=0),
                 max_amount:float | None = Query(None,ge=0),
                 page:int=Query(1,ge=1),
                 limit:int=Query(10,ge=1,le=100),
                db:Session=Depends(get_db),
                current_user:User=Depends(get_current_user)):
    query=db.query(Expense).filter(Expense.user_id==current_user.id)
    
    if category is not None:
      query = query.filter(
        Expense.category == category
    )

    if min_amount is not None:
       query = query.filter(
        Expense.amount >= min_amount
    )

    if max_amount is not None:
      query = query.filter(
        Expense.amount <= max_amount
    )

    offset = (page - 1) * limit

    query = query.offset(offset).limit(limit)

    return query.all()

@router.get("/summary")
def expense_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = (
        db.query(
            func.sum(Expense.amount),
            func.count(Expense.id),
            func.avg(Expense.amount)
        )
        .filter(Expense.user_id == current_user.id)
        .first()
    )

    return {
        "total_expense": result[0] or 0,
        "total_count": result[1] or 0,
        "average_expense": result[2] or 0
    }

@router.get("/summary/categories")
def category_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = (
        db.query(
            Expense.category,
            func.sum(Expense.amount)
        )
        .filter(Expense.user_id == current_user.id)
        .group_by(Expense.category)
        .all()
    )

    return {
        category: total
        for category, total in result
    }

@router.get("/{expense_id}")
def get_expense(expense_id:int,
                db:Session=Depends(get_db),
                current_user:User=Depends(get_current_user)):
   expense=db.query(Expense).filter(Expense.id==expense_id , Expense.user_id==current_user.id).first()
   if not expense:
    raise ExpenseNotFoundException("Expense not found")
   return expense

@router.patch("/{expense_id}",response_model=ExpenseResponse)
def partial_update(expense_id:int,
                   exp_update:ExpenseUpdate,
                   db:Session=Depends(get_db),
                   current_user:User=Depends(get_current_user)):
   expense=db.query(Expense).filter(Expense.id==expense_id,Expense.user_id==current_user.id).first()
   if not expense:
     raise ExpenseNotFoundException("Expense not found")
   updates=exp_update.model_dump(exclude_unset=True)

   for field, values in updates.items():
      setattr(expense,field,values)

   db.commit()
   db.refresh(expense)

   return expense

@router.delete("/{expense_id}")
def delete(expense_id:int,
                   db:Session=Depends(get_db),
                   current_user:User=Depends(get_current_user)):
   expense=db.query(Expense).filter(Expense.id==expense_id,Expense.user_id==current_user.id).first()
   if not expense:
    raise ExpenseNotFoundException("Expense not found")
   db.delete(expense)
   db.commit()
   return{
      "message":"expense deleted successfully"
   }

@router.post("/{expense_id}/receipt")
def upload_receipt(
    expense_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = (
        db.query(Expense)
        .filter(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        )
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WEBP files are allowed"
        )
   
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    original_name = Path(file.filename or "receipt").name
    filename = f"{uuid.uuid4()}_{original_name}"
    file_path = upload_dir / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    expense.receipt_path = str(file_path)

    db.commit()
    db.refresh(expense)

    return {
    "message": "Receipt uploaded successfully",
    "filename": filename,
    "receipt_path": expense.receipt_path
}

