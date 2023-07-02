from fastapi import FastAPI, Response, status, HTTPException  # FastAPI framework

from pydantic import BaseModel   # pydanctic model for request validation

import psycopg2                            # postgres driver
from psycopg2.extras import RealDictCursor

app = FastAPI()

class Tweet(BaseModel):
    title: str
    content: str

try:
    conn = psycopg2.connect(host='localhost',
                            database='tweetbase',
                            user='postgres',
                            password='postgres',
                            cursor_factory=RealDictCursor)

    cursor = conn.cursor()
    print("Database connection was successful")

except Exception as error:
    print("Connecting to database failed")
    print("The error was :", error)


@app.get("/tweets")                                         # get all tweets 
def get_tweets():
    cursor.execute(""" SELECT * from tweets """)
    tweets = cursor.fetchall()
    return {"data": tweets}


@app.post("/tweets", status_code=status.HTTP_201_CREATED)        # create a post
def create_tweets(tweet: Tweet):
    cursor.execute(
        """INSERT INTO tweets(title, content) VALUES (%s, %s) RETURNING * """, (tweet.title, tweet.content))
    new_tweet = cursor.fetchone()
    conn.commit()
    return {"data": new_tweet}

 
@app.get("/tweets/{id}")                                         # get a post by id
def get_tweet(id: int):
    cursor.execute("SELECT * FROM tweets WHERE id = %s", (str(id), ))
    tweet = cursor.fetchone()
    if not tweet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"tweet with id: {id} does not exists")
    return {"data": tweet}


@app.delete("/tweets/{id}", status_code=status.HTTP_204_NO_CONTENT)            # delete a post
def delete_tweet(id: int):
    cursor.execute("DELETE FROM tweets where id = %s RETURNING *", (str(id), ))
    deleted_tweet = cursor.fetchone()
    conn.commit()
    if not deleted_tweet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"tweet with id: {id} does not exists")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/tweets/{id}")                                               # update a post
def update_tweet(id: int, tweet: Tweet):
    cursor.execute("UPDATE tweets SET title = %s, content = %s WHERE id = %s RETURNING *",
                   (tweet.title, tweet.content, str(id), ))
    updated_tweet = cursor.fetchone()
    conn.commit()
    if not updated_tweet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"tweet with id: {id} does not exists")
    return {"data": updated_tweet}
