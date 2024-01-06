from telebot import TeleBot, types
import db

TOKEN = '6731823293:AAGIFP2NIM-o-JnduwOhu4V3lBO10ttuHIE'

bot = TeleBot(TOKEN)


game = False 
night = False

def game_loop(message):
    global game, night
    bot.send_message(
        message.chat.id, "Добро пожаловась в игру! На знакомство 1 минута.")
    sleep(60)
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id, msg)
        
        if not night:
            gif = open("day_santa.mp4", 'rb')
            bot.send_video(message.chat.id, gif)
            gif.close()
            bot.send_message(message.chat.chat_id,
                             "Город засыпает, просыпается мафия. Наступила ночь...")
        else:
            gif = open("night_santa.mp4, 'rb")
            bot.send_message(message.chat.id, 
                             "Город просыпается, чтобы узнать о новый жертвах. Наступил день.")
            gif.close()
        winner = db.check_winner()
        if winner != None:
            game = False
            bot.send_message(message.chat.id,
                             text = f"Игра окончена! Победили: {winner}")
            return
        db.clear(dead=False)
        night = not night
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(mmesage.chat.id, text = f"В игре:\n{alive}")
        sleep(60)

@bot.message_handler(func=lambda m: m.text.lower() == 'готов играть' and m.chat.type == 'private')
def send_text(message):
    bot.send_message(message.chat.id, f"{message.from_user.first_name} присоединился к игре")
    bot.send_message(message.from_user.id, "Вы добавлены в игру!")
    db.insert_player(player_id = message.from_user.id, username = message.from_user.first_name)

@bot.message_handler(commands=['play'])
def game_on(message):
    if not game:
        bot.send_message(message.chat.id, text = "Есди хотите играть, напишите 'готов играть' в лс")

@bot.message_handler(commands=['game'])
def game(message):
    global game
    players = db.players_amount()
    if players >= 1 and not game:
        db.set_roles(players)
        players_roles = db.get_players_roles()
        mafia_usernames = db.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(player.id, text = role)
            if role == 'mafia':
                bot.send_message(player_id, 
                                 text = f"Все члены мафии:\n{mafia_usernames}")
        game = True
        bot.send_message(message.chat.id, text = 'Игра начинается!')
        return

    bot.send_message(message.chat.id, text = 'Недостаточно людей для игры!')

@bot.message_handler(commands=['kick'])
def kick(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, text = "Такого имени нет!")
            return
        voted = db.vote("citizen_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, text = "Ваш голос учитан!")
            return
        bot.send_message(message.chat.id, text = "У вас больше нет права голосовать!")
        return
    bot.send_message(message.chat.id, "Ночью голосование невозможно!")

@bot.message_handler(commands=['kill'])
def kill(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_alive()
    if night:
        if not username in usernames:
            bot.send_message(message.chat.id, text = "Такого имени нет!")
            return
        if message.from_user.first_name in db.get_mafia_usernames():
            voted = db.vote("mafia_vote", username, message.from_user.id)
            if voted:
                bot.send_message(message.chat.id, text = "Вы проголосовали за следующую жертву.")
                return
            bot.send_message(message.chat.id, "У вас больше нет права голосовать")
            return
        bot.send_message(message.chat.id, text = "Голосовать может только мафия!")
        return
    bot.send_message(message.chat.id, text = "Днем голосование невозможно!")

def get_killed(night):
    if not night:
        username_killed = db.citizens_kill()
        return f"Горожане линчевали {username_killed}"
    username_killed = db.mafia_kill()
    return f"Сегодня ночью убили {username_killed}"

    
if __name__ in '__main__':
    bot.infinity_polling()
