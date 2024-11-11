from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Post, File, Comment
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立所有表
Base.metadata.create_all(engine)

def get_db_session():
    """返回資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_to_database(all_posts_comments):
    """將資料儲存到資料庫"""
    with get_db_session() as db:
        for timestamp, post_data in all_posts_comments.items():
            post = Post(
                timestamp=timestamp,
                link=post_data["link"],
                author=post_data["author"],
                content=post_data["content"],
                post_time=post_data["post_time"]
            )
            db.add(post)
            
            for file_link in post_data["file_links"]:
                file = File(
                    post=post,
                    file_name=os.path.basename(file_link),
                    link=file_link
                )
                db.add(file)
            
            for comment_data in post_data["comments"]:
                comment = Comment(
                    post=post,
                    comment_author=comment_data["author"],
                    comment_text=comment_data["content"]
                )
                db.add(comment)
        
        db.commit()
        print("Data saved to database.")