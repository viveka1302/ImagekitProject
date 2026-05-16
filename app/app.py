from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from sqlalchemy import select
from .schemas import PostCreate
from .db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.images import imagekit
from pathlib import Path
import uuid

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
    try:
        response = imagekit.files.upload(
            file=file.file,
            file_name=file.filename
        )
        print(f"File ID: {response.file_id}")
        print(f"URL: {response.url}")
        if response.url:
            post= Post(
                caption=caption,
                url=response.url,
                file_type=response.file_type,
                filename=file.filename 
            )
            session.add(post) #staging into db
            await session.commit() #saved in db
            await session.refresh(post) #populates extra data like id, created_at
            return post
    except Exception as e:
        raise HTTPException(status_code=500, detail= str(e))

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
    
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession= Depends(get_async_session)):
    try:
        post_uuid= uuid.UUID(post_id)
        result= await session.execute(select(Post).where(Post.id==post_uuid))
        post= result.scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail="not found")
        await session.delete(post)
        await session.commit()
        return {"success": True, "message": "post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))