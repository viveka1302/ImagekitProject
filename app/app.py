from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from sqlalchemy import select
from .schemas import PostCreate
from .db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app= FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_file(
    file: UploadFile= File(...),
    caption: str= Form(""),
    session: AsyncSession= Depends(get_async_session)
    ):
    
    post= Post(
        caption=caption,
        url="dummy url",
        file_type="photo",
        filename="dummy name" 
    )
    session.add(post) #staging into db
    await session.commit() #saved in db
    await session.refresh(post) #populates extra data like id, created_at
    return post

@app.get("/feed")
async def get_feed(
    session: AsyncSession= Depends(get_async_session)
):
    result= await session.execute(statement=select(Post).order_by(Post.created_at.desc()))
    posts= [row[0] for row in result.all()]
    posts_data=[]
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "created_at": post.created_at.isoformat()
            }
        )
        return {"posts": posts_data}