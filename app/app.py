from fastapi import FastAPI, HTTPException
from schemas import PostCreate

app= FastAPI()

# @app.get("/hello-world")
# def hello_world():
#     return {
#             "message": "hello world"
#             }
text_posts = {
    1: {"title": "New POst", "content": "cool post1"},
    2: {"title": "Tech Trends", "content": "AI is transforming industries rapidly."},
    3: {"title": "Travel Diaries", "content": "Exploring the mountains was unforgettable."},
    4: {"title": "Healthy Living", "content": "Daily exercise improves both body and mind."},
    5: {"title": "Coding Tips", "content": "Practice consistently to become a better developer."},
    6: {"title": "Book Review", "content": "This novel had an inspiring and emotional story."}
}

@app.get("/posts")
def get_all_posts(limit: int= None):
    if limit:
        return list(text_posts.values())[:limit]
    return text_posts

@app.get("/posts/{id}")
def get_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="post-id Not Found")
    return text_posts.get(id)