from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt

from database import SessionLocal, get_db
from models import User
from core.security import ALGORITHM, SECRET_KEY, oauth2_scheme


async def get_db_session():
   """Dependency to get async database session."""
   async with SessionLocal() as session:
      yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
   credentials_exception = HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Invalid token",
         header={"WWW-Authenticate": "Bearer"},
   )
   """
   Dependency to get current authenticated user from JWT token.
    
   """
   try:
      # decode token and extract user_id from "sub" claim
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      user_id: str = payload.get("sub")

      # no user_id in token payload
      if user_id is None:
         raise credentials_exception
   except JWTError:
      # Catches expired, bad signature, malformed, etc.
      raise credentials_exception

   # Query the database for the user
   result = await db.execute(select(User).where(User.id == int(user_id)))
   user = result.scalar().first()

   # If user was deleted after token was issued
   if user is None:
      raise credentials_exception
   
   return user
