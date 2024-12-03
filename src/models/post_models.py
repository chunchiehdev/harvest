from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, unique=True, nullable=False)
    link = Column(Text, nullable=False)
    author = Column(String(255))
    content = Column(Text)
    post_time = Column(String(255))

    # 關聯到 File 和 Comment
    files = relationship("File", back_populates="post", cascade="all, delete")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"))
    file_name = Column(String(255))
    link = Column(Text)
    

    # 關聯到 Post
    post = relationship("Post", back_populates="files")
    
    __table_args__ = (
        UniqueConstraint('post_id', 'file_name', name='uq_post_file_name'),
    )

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"))
    comment_author = Column(String(255))
    comment_text = Column(Text)

    # 關聯到 Post
    post = relationship("Post", back_populates="comments")
    
    __table_args__ = (
        UniqueConstraint('post_id', 'comment_author', 'comment_text', name='uq_post_comment'),
    )