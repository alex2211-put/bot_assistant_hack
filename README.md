# bot assistant
Telegram robot-assistant for the [hackathon](https://tfalliance.ru/)

Link to the bot - [AssistantHack](https://t.me/mango_humans_assistant_bot)

Link to the board - [Mango_bot](https://trello.com/b/wxsCduHL/mangobot)

Team **Mango humans**
1) Alexander Putin: [telegram](https://t.me/alik_put)
2) Potapov Anton: [telegram](https://t.me/JustAnt)


Database is used in this project: MongoDB.
Reasons: 
1. Speed. In our project speed of DB's responce more valuable advantage than relations between columns.
2. Simpleness. BD should has about 10 atributs and our requests are going to be sort by 2 arguments as a maximum.
3. Comfortable. Mongo has convenient and simple integration with python.   


BD atributs : {
    "user_id":"xxx", 
    "user_name" : "yyy", 
    "chat_id" : "xxx", 
    "date" : "00.00.0000",
    "color" : ["red", "green", "blue"], 
    "text" : "Issue reported."
}

