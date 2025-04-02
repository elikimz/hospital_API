# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app import model
# from app.database import get_db
# from app.schema import ContactCreate, ContactOut

# router = APIRouter()


# # Add a new contact
# @router.post("/", response_model=ContactOut)
# async def add_contact(contact: ContactCreate, db: Session = Depends(get_db)):
#     new_contact = model.Contact(
#         name=contact.name,
#         email=contact.email,
#         message=contact.message,
#     )
#     db.add(new_contact)
#     db.commit()
#     db.refresh(new_contact)
#     return new_contact


# # Retrieve all contacts
# @router.get("/", response_model=list[ContactOut])
# async def get_all_contacts(db: Session = Depends(get_db)):
#     contacts = db.query(model.Contact).all()
#     return contacts


# # Retrieve a single contact
# @router.get("/{id}", response_model=ContactOut)
# async def get_contact(id: int, db: Session = Depends(get_db)):
#     contact = db.query(model.Contact).filter(model.Contact.id == id).first()
#     if not contact:
#         raise HTTPException(status_code=404, detail="Contact not found.")
#     return contact


# # Delete a contact
# @router.delete("/{id}")
# async def delete_contact(id: int, db: Session = Depends(get_db)):
#     contact = db.query(model.Contact).filter(model.Contact.id == id).first()
#     if not contact:
#         raise HTTPException(status_code=404, detail="Contact not found.")
    
#     db.delete(contact)
#     db.commit()
#     return {"message": "Contact deleted successfully."}