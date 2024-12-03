from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.post_models import File, Post, Comment
from fastapi import Depends

from datetime import datetime, timezone
import configuration as cf
from db.init_db import get_db


def save_to_database( all_posts_comments, db: Session = Depends(get_db)):
    """
    將貼文存入資料庫
    
    :param db: database
    :param all_posts_comments: 爬取的帖子数据字典
    """

    try:
        for timestamp, post_data in all_posts_comments.items():

            timestamp_datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            post = db.query(Post).filter_by(timestamp=timestamp_datetime).first()

            if not post:
                post = Post(
                    timestamp=timestamp_datetime,
                    link=post_data["link"],
                    author=post_data["author"],
                    content=post_data["content"],
                    post_time=post_data["post_time"]
                )
                db.add(post)
                db.flush() 
            
            
            if post_data["file_links"]:  
                for file_link in post_data["file_links"]:
                    file_name = file_link.get("file_name", "") if isinstance(file_link, dict) else ""
                    file_url = file_link.get("link", "") if isinstance(file_link, dict) else file_link

                    file = db.query(File).filter_by(post_id=post.id, file_name=file_name).first()
                    
                    if file:
                        file.link = file_url  # 更新連結
                    else:
                        new_file = File(
                            post_id=post.id,
                            file_name=file_name,
                            link=file_url
                        )
                        db.add(new_file)

            for comment_data in post_data["comments"]:
                comment_author = comment_data["author"]
                comment_text = comment_data["content"]

                
                comment = db.query(Comment).filter_by(
                    post_id=post.id,
                    comment_author=comment_author,
                    comment_text=comment_text
                ).first()
                if not comment:
                    
                    new_comment = Comment(
                        post_id=post.id,
                        comment_author=comment_author,
                        comment_text=comment_text
                    )
                    db.add(new_comment)
        
            db.commit()
            print("Data saved to database.")
    except Exception as e:
        db.rollback()  
        print(f"Error saving data to database: {e}")
        

def get_valid_pdf_links(db: Session):
    """
    從資料庫中提取需要處理的有效 PDF 連結
    """
    valid_pdf_links = []

    files = db.query(File).filter(File.link.like('%facebook.com%')).all()

    for file in files:
        original_url = file.link
        
        actual_url = cf.extract_actual_url(original_url)

        if actual_url and cf.is_pdf_url(actual_url):
            valid_pdf_links.append((file.id, actual_url))
        else:
            print(f"無效或非 PDF 連結: {original_url}")

    return valid_pdf_links