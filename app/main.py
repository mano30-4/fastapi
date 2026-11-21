
from fastapi import FastAPI,Response,status,HTTPException,Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine,Sessionlocal,get_db
from sqlalchemy.orm import Session

#engine -> it triggers to create tables from models.py
models.Base.metadata.create_all(bind=engine)

class Post(BaseModel):
    title : str
    content :str
    published : bool = True # default value

while True :
        try :
            conn = psycopg2.connect(host = 'localhost',database = 'fastapi',user = 'manohargajula' ,password ='',cursor_factory = RealDictCursor)
            cursor = conn.cursor()
            print("Database connection was successful !!!")
            break
        except Exception as error :
            print("connecting to database failed")
            print("Error:", error)
            time.sleep(2)

app = FastAPI()


@app.get("/")
def root():
    return {"message" : "hello world"}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts""")
    #posts = cursor.fetchall()
    posts=db.query(models.Post).all()
    return {"data": posts}

# once we send request to fastapi server, it will look for path in list of paths, we ever it founds the first path it stops running code


@app.post("/posts")
def create_posts(post : Post,db: Session = Depends(get_db) ):
     # cursor.execute("""INSERT INTO posts(title,content,published) VAlUES (%s,%s,%s) RETURNING * """,(post.title,post.content,post.published))
     # new_post = cursor.fetchone()  ## fetches result by above sql
     # conn.commit() ## without commit it won't save data in database table
     #new_post = models.Post(title=post.title,content=post.content,published=post.published)
     new_post = models.Post(**post.model_dump())
     db.add(new_post)
     db.commit()
     db.refresh(new_post)
     return {"data":new_post}

@app.get("/posts/{id}") ## always gets collected as str, convert before use it
def get_post(id : int,db: Session = Depends(get_db)): ## bc of fastapi it automatically converts it into int and validates it else its just a type annotation
    # cursor.execute("""SELECT * FROM posts WHERE posts.id = %s""",(str(id)))
    # post=cursor.fetchone()

    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=404,detail=f"post with {id} was not found")
    return {"detail":post}

@app.delete("/posts/{id}")
def delete_post(id :int,db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts where posts.id = %s RETURNING *""",(str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post :
        raise HTTPException(status_code= 404 , detail = "post not found")
    db.delete(post)
    db.commit()
    return post


@app.put("/posts/{id}")
def update_post(id :int, post : Post,db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title =%s, content = %s, published = %s WHERE id = %s RETURNING *""",(post.title,post.content,post.published,str(id)))
    # updated_post=cursor.fetchone()
    # conn.commit()

    post_query=db.query(models.Post).filter(models.Post.id==id)
    existing_post=post_query.first()
    if not existing_post:
        raise HTTPException(status_code= 404 , detail = "post not found")

    post_query.update(post.model_dump(), synchronize_session=False)

    db.commit()

    return post_query.first()
