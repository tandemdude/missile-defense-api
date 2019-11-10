#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import quart
from quart import request
import aiosqlite
import json

app = quart.Quart(__name__)

DATABASE_NAME = "highscores.db"


@app.route("/api/addscore/", methods=["POST"])
async def handle_new_score():
    data = json.loads((await request.get_data()).decode())
    try:
        name = data["name"]
        score = data["score"]
    except KeyError:
        return "Bad Request", 400
    if isinstance(name, str) and isinstance(score, int):
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute(
                "INSERT INTO scores(name, score) VALUES(?, ?)", [name, score]
            )
            await db.commit()
            return "OK", 200
    else:
        return "Bad Request", 400


@app.route("/api/highscores/", methods=["GET"])
async def handle_highscores():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        async with db.execute(
            "SELECT name, score FROM scores ORDER BY score DESC LIMIT 10;"
        ) as cursor:
            rows = await cursor.fetchall()
            response = {
                "scores": [{"name": name, "score": score} for name, score in rows]
            }
            return response


@app.before_serving
async def create_database_if_required():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute(
            """
			CREATE TABLE IF NOT EXISTS scores(
				name text NOT NULL,
				score integer NOT NULL
			);
		"""
        )
        await db.commit()
        return


if __name__ == "__main__":
    app.run()
