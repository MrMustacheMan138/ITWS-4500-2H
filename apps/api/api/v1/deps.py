from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from typing import Annotated

from database import get_db
from models import User
from core.auth import ALGORITHM, SECRET_KEY, oauth2_scheme


DbSession = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(token: TokenDep, db: DbSession) -> User:
   """
   Dependency to get current authenticated user from JWT token.
   """
   
   credentials_exception = HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Invalid token",
         headers={"WWW-Authenticate": "Bearer"},
   )
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
   user = result.scalars().first()

   # If user was deleted after token was issued
   if user is None:
      raise credentials_exception
   
   return user
