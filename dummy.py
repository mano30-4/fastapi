from typing import Optional
from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
import random
import psycopg2
from psycopg2.extras import RealDictCursor
import time

class Post(BaseModel):
    title : str
    content :str
    published : bool = True # default value
    # rating : Optional[int] = None # default value is none and optional gives us ability to accept int or None, In general u can't directly accept None if we are using 'variable' : int
while True :
        try :
            conn = psycopg2.connect(host = 'localhost',database = 'fastapi',user = "manohargajula" ,password = '0463',cursor_factory = RealDictCursor)
            cursor = conn.cursor()
            print("Database connection was successful !!!")
            break
        except Exception as error :
            print("connecting to database failed")
            print("Error:", error)
            time.sleep(2)

app = FastAPI()

my_posts = [{"title" : " title of post 1", "content":"content of post 1", "id": 1},
            {"title" : "title of post 2", "content":"content of post 2","id": 2}]

def find_post(id):
    for p in my_posts:
        if p["id"]== id:
            return p
    return None

def find_post_index(id):
    for i,p in enumerate(my_posts):
         if p["id"] == id :
             return i
    return None

@app.get("/")
def root():
    return {"message" : "hello world"}

# don't use uvicorn main:app --reload in production
@app.get("/posts")
def get_posts():
    posts= cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data":posts}

# once we send request to fastapi server, it will look for path in list of paths, we ever it founds the first path it stops running code

"""
@app.post("/createposts")
def create_posts(payload: dict= Body(...) ): # we are getting body and converting it into dict and then saving it into variable named payload
    return {"newpost": f"title : {payload['title']} content : {payload['content']}"} 
"""

"""
@app.post("/posts")
def create_posts(new_post : Post ):
    new_post.model_dump()
    return {"data" : new_post } # if u don't convert it into dictionary using model_dump then it throws error
"""

"""
C R U D

Create : POST

Read : GET

Update : PUT/PATCH

Delete : DELETE
"""

@app.post("/posts")
def create_posts(new_post : Post ):
    post_dict = new_post.model_dump()
    post_dict["id"]= random.randrange(0,10000)
    my_posts.append(post_dict)
    return {"data":post_dict}

@app.get("/posts/{id}") ## always gets collected as str, convert before use it
def get_post(id : int, response : Response): ## bc of fastapi it automatically converts it into int and validates it else its just a type annotation
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=404,detail=f"post with {id} was not found")
        #response.status_code = 404
    return {"detail":post}

@app.delete("/posts/{id}",status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id :int):
    post_index = find_post_index(id)
    if post_index == None :
        raise HTTPException(status_code= 404 , detail = "post not found")
    my_posts.pop(post_index)
    return Response(status_code = status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id :int, post : Post):
    post_index = find_post_index(id)
    if post_index == None :
        raise HTTPException(status_code= 404 , detail = "post not found")
    post_dict= post.model_dump() ## converting pydantic object into dict as we did in POST posts
    my_posts[post_index] = post_dict
    return {"detail":  post_dict }
