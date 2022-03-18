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


```
DB attributes : {
    'message_id' = 7,
    'chat_id' : 8,
    'user_id': 25,
    'first_name' = 'xxx',
    'last_name' ='xxx', 
    'user_name' : '@xxx',  
    'date' : 0123456789,
    'importance_marker' : 'xxx' # ['red', 'yello', 'green'] - choices, 
    'message_text' : 'Issue reported.',
    'media_group_id' : 123,
    'message_type' : 'type',
    'content_type' : 'xxx',
    'content_id' : 28,
    'archived' : 'xxx' # ['True', 'False'] - choices
}
```
