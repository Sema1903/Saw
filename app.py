import telebot
from telebot import types
import random
import sqlite3 as sl
bot = telebot.TeleBot('6479575609:AAEqAk_1aCCCd6exW72YwUwkmyDDVjvXz3Y')
con = sl.connect('game.db', check_same_thread = False)
cursor = con.cursor()
#cursor.execute('DROP TABLE users')
#cursor.execute('CREATE TABLE users (id TEXT, status TEXT, basns INT, word TEXT, letters TEXT, raund INT)')
#cursor.execute('CREATE TABLE words (id INT, word TEXT, losers INT)')
#cursor.execute('INSERT INTO words (id, word, losers) VALUES (?, ?, ?)', (0, 'пила', 0))
#con.commit()
def new_word():
    cursor.execute('SELECT  * FROM words')
    records = cursor.fetchall()    
    words = []
    for row in records:
        words.append(row[1])    
    return random.choice(words)
@bot.message_handler(commands = ['start'])
def start(message):
    menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
    button1 = types.KeyboardButton('Начинаем 🩸')
    button2 = types.KeyboardButton('Добавить слово 📒')
    button3 = types.KeyboardButton('Наш канал 🌐')
    menu.add(button1, button2, button3)
    name = message.from_user.first_name
    f = open('images/start_game/start_game' + random.choice(['1', '2', '3', '4', '5']) + '.gif', 'rb')
    bot.send_message(message.chat.id, 'Здравствуй, ' + name + '. За всю свою жизь, ты совершил слишком много грехов. Пора платить по счетам 🩸 Сыграем в игру? Правила просты. Я загадал слово. Ты можешь узнать, есть ли некая буква в этом слове, или проверить это слово. Но имей ввиду, за каждую ошибку ты становишься на шаг ближе к смерти 🔪 Расходуй попытки с умом. Игра началась...', reply_markup = menu)
    bot.send_animation(message.chat.id, f)
    f.close()
    here = False
    cursor.execute('SELECT  * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[0] == str(message.chat.id):
            here = True
            if row[1] == 'in_game':
                bot.send_message(message.chat.id, 'Игра еще не окончена, ' + name)
            else:
                word = new_word()
                cursor.execute('UPDATE users SET word = ? AND letters = ? AND raund = ? WHERE id = ?', (word, '', 0, str(message.chat.id)))
                con.commit()
    if not here:
        word = new_word()
        cursor.execute('INSERT INTO users (id, status, basns, word, letters, raund) VALUES (?, ?, ?, ?, ?, ?)', (str(message.chat.id), 'in_game', 0, word, '', 0))
        con.commit()
@bot.message_handler(content_types = ['text'])
def message(message):
    name = message.from_user.first_name
    if message.text == 'Начинаем 🩸':
        cursor.execute('SELECT  * FROM users')
        records = cursor.fetchall()
        here = False
        for row in records:
            if row[0] == str(message.chat.id):
                if row[1] == 'in_game':
                    bot.send_message(message.chat.id, 'Игра еще не окончена, ' + name)
                    here = True
        if not here:
            word = new_word()
            cursor.execute('UPDATE users SET word = ? WHERE id = ?', (word, str(message.chat.id)))
            cursor.execute('UPDATE users SET letters = ? WHERE id = ?', ('', str(message.chat.id)))
            cursor.execute('UPDATE users SET raund = ? WHERE id = ?', (0, str(message.chat.id)))
            cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('in_game', str(message.chat.id)))
            con.commit()
            bot.send_message(message.chat.id, name + ', игра началась...')
            f = open('images/start_game/start_game' + random.choice(['1', '2', '3', '4', '5']) + '.gif', 'rb')
            bot.send_animation(message.chat.id, f)
            f.close()
            f = open('images/scores/0.jpg', 'rb')
            bot.send_photo(message.chat.id, f)
            result = ''
            for i in range(len(word)):
                result += '_ '
            bot.send_message(message.chat.id, result)
    elif message.text == 'Добавить слово 📒':
        here = False
        cursor.execute('SELECT * FROM users')
        records = cursor.fetchall()
        for row in records:
            if row[0] == str(message.chat.id):
                if row[1] == 'in_game':
                    here = True
                    bot.send_message(message.chat.id, name + ', игра еще не окончена')
        if not here:
            bot.send_message(message.chat.id, 'Добро пожаловть в команду Джона Крамера, ' + name + '🔪 Напиши слово, мы его рассмотрим')
            cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('new_word', str(message.chat.id)))
            f = open('images/new_word/' + random.choice(['1', '2', '3', '4', '5']) + '.gif', 'rb')
            bot.send_animation(message.chat.id, f)
            f.close()
    elif message.text == 'Наш канал 🌐':
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Зайти в Убежище Крамера', url='https://web.telegram.org/k/#-4724815779')
        markup.add(button1)
        bot.send_message(message.chat.id, 'Заходи к нам с сообщество'.format(message.from_user), reply_markup=markup) 
    else:
        cursor.execute('SELECT * FROM users')
        records = cursor.fetchall()
        for row in records:
            if row[0] == str(message.chat.id):
                if row[1] == 'new_word':
                    cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('free', str(message.chat.id)))
                    con.commit()
                    bot.send_message(1733954589, 'Джон Крамер, ' + name + ' предложил Вам новое слово: ' + message.text)
                    bot.send_message(message.chat.id, 'Отличная работа, ' + name + ', твое слово отправлено на модерацию')
                elif row[1] == 'free':
                    bot.send_message(message.chat.id, 'Чтобы сыграть нужно начать игру')
                else:
                    word = row[3]
                    raund = row[5]
                    letters = row[4]
                    if len(message.text) > 1:
                        if message.text.lower() == word:
                            bot.send_message(message.chat.id, 'Ты выиграл, ' + name + '. Поздравляю с победой. Это было слово: ' + word + '. Надеюсь, что впредь ты будешь больше ценить свою жизнь')
                            f = open('images/win/' + random.choice(['1', '2', '3', '4', '5']) + '.gif', 'rb')
                            bot.send_animation(message.chat.id, f)
                            cursor.execute('UPDATE users SET raund = ? WHERE id = ?', (0, str(message.chat.id)))
                            cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('free', str(message.chat.id)))
                            cursor.execute('UPDATE users SET letters = ? WHERE id = ?', ('', str(message.chat.id)))                            
                            f.close()     
                        else:
                            raund += 1
                            if raund != 10:
                                bot.send_message(message.chat.id, 'Неверно. Будь аккуратнее, если хочешь выжить')
                                f = open('images/scores/' + str(raund) + '.jpg', 'rb')
                                bot.send_photo(message.chat.id, f)
                                f.close()
                                cursor.execute('UPDATE users SET raund = ? WHERE id = ?', (raund, str(message.chat.id)))
                            else:
                                bot.send_message(message.chat.id, 'Ты проиграл, ' + name + ' и погиб. Это было слово: ' + word + '. Игра окончена...')
                                cursor.execute('UPDATE users SET raund = ? WHERE id = ?', (0, str(message.chat.id)))
                                cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('free', str(message.chat.id)))
                                cursor.execute('UPDATE users SET letters = ? WHERE id = ?', ('', str(message.chat.id)))
                                f = open('images/game_over/' + random.choice(['1', '2', '3', '4', '5']) + '.gif', 'rb')
                                bot.send_animation(message.chat.id, f)
                                f.close()
                                cursor.execute('UPDATE users SET raund = ? WHERE id = ?', (0, str(message.chat.id)))
                                cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('free', str(message.chat.id)))
                                cursor.execute('UPDATE users SET letters = ? WHERE id = ?', ('', str(message.chat.id)))
                    else:
                        if message.text.lower() in letters.split():
                            bot.send_message(message.chat.id, name + ', эта буква уже использована')
                        else: 
                            if message.text.lower() in word:
                                letters += message.text.lower() + ' '
                                here = True
                                for i in word:
                                    if i not in letters.split():
                                        here = False
                                if here:
                                    bot.send_message(message.chat.id, 'Ты выиграл, ' + name + '. Поздравляю с победой. Это было слово: ' + word + '. Надеюсь, что впредь ты будешь больше ценить свою жизнь')
                                    cursor.execute('UPDATE users SET raund = ? WHERE id = ?', (0, str(message.chat.id)))
                                    cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('free', str(message.chat.id)))
                                    cursor.execute('UPDATE users SET letters = ? WHERE id = ?', ('', str(message.chat.id)))
                                    f = open('images/win/' + random.choice(['1', '2', '3', '4', '5']) + '.gif', 'rb')
                                    bot.send_animation(message.chat.id, f)
                                    f.close() 
                                else:
                                    bot.send_message(message.chat.id, 'Правильно. Так держать')
                                    cursor.execute('UPDATE users SET letters = ? WHERE id = ?', (letters, str(message.chat.id)))
                                    result = ''
                                    for i in word:
                                        if i in letters.split():
                                            result += i + ' '
                                        else:
                                            result += '_ ' 
                                    bot.send_message(message.chat.id, result)
                            else:
                                raund += 1
                                if raund != 10:
                                    bot.send_message(message.chat.id, 'Неверно. Будь аккуратнее, если хочешь выжить')
                                    f = open('images/scores/' + str(raund) + '.jpg', 'rb')
                                    bot.send_photo(message.chat.id, f)
                                    f.close()
                                    cursor.execute('UPDATE users SET raund = ? WHERE id = ?', (raund, str(message.chat.id)))
                                    result = ''
                                    for i in word:
                                        if i in letters.split():
                                            result += i + ' '
                                        else:
                                            result += '_ ' 
                                    bot.send_message(message.chat.id, result)                                    
                                else:
                                    bot.send_message(message.chat.id, 'Ты проиграл, ' + name + ' и погиб. Это было слово: ' + word + '. Игра окончена...')
                                    f = open('images/game_over/' + random.choice(['1', '2', '3', '4', '5']) + '.gif', 'rb')
                                    bot.send_animation(message.chat.id, f)
                                    f.close()
                                    cursor.execute('UPDATE users SET raund = ? WHERE id = ?', (0, str(message.chat.id)))
                                    cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('free', str(message.chat.id)))
                                    cursor.execute('UPDATE users SET letters = ? WHERE id = ?', ('', str(message.chat.id)))
                    con.commit()
bot.polling(non_stop = True)