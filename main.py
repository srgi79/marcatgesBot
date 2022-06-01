import logging, os, json
from datetime import datetime
from math import floor
import pandas as pd

from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, RegexHandler, TypeHandler, DispatcherHandlerStop

# Global variables
TOKEN = '1111111111:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
fitxades = []
horesNormals = [7*60+20, 8*60+40, 12*60+40, 14*60+40, 14*60+41, 16*60+20, 16*60+29, 18*60+40]

last_month = int(datetime.now().strftime("%m"))

# Restore auth users
users_file = "users_auth.json"
if os.path.isfile(users_file):
    with open(users_file, "r") as f:
        users_auth = json.load(f)
        print('USUARIS AUTORITZATS RECUPERATS', users_auth)
        f.close()
else:
    users_auth = [1234567, 12345678] # My first
    print('USUARIS AUTORITZATS PER DEFECTE', users_auth)
f = open(users_file, "w+")
json.dump(users_auth, f)
f.close()

# Restore database
db_name = str(last_month)+".csv"
if os.path.isfile(db_name):
    df = pd.read_csv(db_name)
    df.set_index(['DIA', 'USER'], inplace=True)
    print('RESTORED DB:')
    print(df.to_markdown(tablefmt="grid"))
else:
    df = pd.DataFrame([], columns=['DIA', 'USER', 'EM', 'SM', 'ET', 'ST','SF','EF'])
    df.set_index(['DIA', 'USER'], inplace=True)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def pretty(all_in_minutes):
    if all_in_minutes > 0:
        h = floor(all_in_minutes/60)
        m = all_in_minutes-h*60
        if m < 10:
            return str(h)+':0'+str(m)
        else:
            return str(h)+':'+str(m)

    else:
        return ''

def sortida(mEM, mSM, mET, mPiti):
    if mET - mSM <= 60:
        # 1h o menys per dinar
        mSortida = mEM + 9*60
    else:
        minutsMati = mSM - mEM
        mSortida = mET + 8*60 - minutsMati
    if mPiti > 0:
        mSortida = mSortida + mPiti
    print(mSortida)
    return pretty(mSortida)

def hores(mEM, mSM, mET, mST):
    minutsMati = mSM - mEM
    minutsTarda = mST - mET
    return pretty(minutsMati + minutsTarda)

def check(no_check, userid):
    global df, last_month, horesNormals
    new_month = int(datetime.now().strftime("%m"))
    new_year = int(datetime.now().strftime("%y"))
    if (last_month != new_month):
        print('New month')
        last_month = new_month
        df = pd.DataFrame([], columns=['DIA', 'USER', 'EM', 'SM', 'ET', 'ST','SF','EF'])
        df.set_index(['DIA', 'USER'], inplace=True)
        if (last_year != new_year):
            print('Happy new year')
            last_year = new_year
            listOfFiles = [f for f in os.listdir() if os.path.isfile(f) if f.endswith(".csv")]
            for file in listOfFiles:
                os.remove(file)


    int_today = int(datetime.now().strftime("%d"))
    if not (int_today, userid) in df.index:
        print('New user_day '+str(userid)+'_'+str(int_today))
        df.loc[(int_today,userid),:] = (0,0,0,0,0,0)


    print('ARA: ', datetime.now().strftime("%H:%M"))
    h = int(datetime.now().strftime("%H"))
    m = int(datetime.now().strftime("%M"))
    txt = 'All done'
    keyboard = False
    minutes = h*60+m
    if df.loc[(int_today,userid), 'EM'] == 0: # df.at[int_today, 'EM']
        if no_check or ((minutes >= horesNormals[0]) and (minutes <= horesNormals[1])):
            df.loc[(int_today,userid), 'EM'] = h*60+m
            df.to_csv(db_name)
            txt = 'EM: '+pretty(h*60+m)
        else:
            txt = 'Segur EM a les '+datetime.now().strftime("%H:%M")+'?'
            keyboard = True
    elif df.loc[(int_today,userid), 'SM'] == 0:
        if (no_check or (minutes >= horesNormals[2]) and (minutes <= horesNormals[3])):
            df.loc[(int_today,userid), 'SM'] = h*60+m
            df.to_csv(db_name)
            txt = 'SM: '+pretty(h*60+m)
        else:
            txt = 'Segur SM a les '+datetime.now().strftime("%H:%M")+'?'
            keyboard = True
    elif df.loc[(int_today,userid), 'ET'] == 0:
        if no_check or ((minutes >= horesNormals[4]) and (minutes <= horesNormals[5])) or ((minutes >= df.loc[(int_today,userid), 'SM']+60) and (minutes <= df.loc[(int_today,userid), 'SM']+125)):
            df.loc[(int_today,userid), 'ET'] = h*60+m
            df.to_csv(db_name)
            if df.loc[(int_today,userid), 'SF'] > 0 and df.loc[(int_today,userid), 'EF'] > 0:
                mPiti = df.loc[(int_today,userid), 'EF'] - df.loc[(int_today,userid), 'SF']
                if mPiti > 0:
                    txt = 'ET: '+pretty(h*60+m)+', Surt a les '+sortida(df.loc[(int_today,userid), 'EM'], df.loc[(int_today,userid), 'SM'], df.loc[(int_today,userid), 'ET'], mPiti)
                else:
                    txt = 'ET: '+pretty(h*60+m)+', Error en piti'
            else:
                txt = 'ET: '+pretty(h*60+m)+', Surt a les '+sortida(df.loc[(int_today,userid), 'EM'], df.loc[(int_today,userid), 'SM'], df.loc[(int_today,userid), 'ET'], 0)
        else:
            txt = 'Segur ET a les '+datetime.now().strftime("%H:%M")+'?'
            keyboard = True

    elif df.loc[(int_today,userid), 'ST'] == 0:
        if no_check or ((minutes >= horesNormals[6]) and (minutes <= horesNormals[7])):
            df.loc[(int_today,userid), 'ST'] = h*60+m
            df.to_csv(db_name)
            mPiti = df.loc[(int_today,userid), 'EF'] - df.loc[(int_today,userid), 'SF']
            if mPiti > 0:
                txt = 'ST: '+pretty(h*60+m)+', Has fet '+hores(df.loc[(int_today,userid), 'EM'], df.loc[(int_today,userid), 'SM'], df.loc[(int_today,userid), 'ET']+mPiti, df.loc[(int_today,userid), 'ST'])
            else:
                txt = 'ST: '+pretty(h*60+m)+', Has fet '+hores(df.loc[(int_today,userid), 'EM'], df.loc[(int_today,userid), 'SM'], df.loc[(int_today,userid), 'ET'], df.loc[(int_today,userid), 'ST'])
        else:
            txt = 'Segur ST a les '+datetime.now().strftime("%H:%M")+'?'
            keyboard = True
    print(df.to_markdown(tablefmt="grid"))
    return str(txt), keyboard


def start(update: Update, context: CallbackContext) -> None:
    global df, users_auth
    userid = update.effective_user['id']
    username = update.effective_user['first_name']
    print(str(username)+':'+str(userid))
    int_today = int(datetime.now().strftime("%d"))
    if userid in users_auth:
        if not (int_today, userid) in df.index:
            reply_text = 'Hola '+str(username)+' ['+str(userid)+']\n'
            reply_text += 'Sense fitxades avui ' + str(int_today)
        else:
            serie = df.loc[(int_today,userid),:]
            reply_text = 'Hola '+str(username)+' ['+str(userid)+'], avui dia '+str(int_today)+'\n'
            reply_text += serie.to_string()
    else:
        reply_text = 'Hola '+str(username)+' ['+str(userid)+']\n'
        reply_text += 'No estas autoritzat'
    update.message.reply_text(reply_text)

def reco_command(update: Update, context: CallbackContext) -> None:
    global df, users_auth
    txt = 'Ja has sortit'
    userid = update.effective_user['id']
    int_today = int(datetime.now().strftime("%d"))
    h = int(datetime.now().strftime("%H"))
    m = int(datetime.now().strftime("%M"))
    sortida_obj = 17*60
    if userid in users_auth:
        if not (int_today, userid) in df.index:
            txt = 'Sense fitxades'
        elif df.loc[(int_today,userid), 'EM'] == 0:
            txt = 'Sense EM'
        elif df.loc[(int_today,userid), 'SM'] == 0:
            txt = 'Sense SM'
        else:
            minMati = (df.loc[(int_today,userid), 'SM'] - (df.loc[(int_today,userid), 'EM'] - (df.loc[(int_today,userid), 'SF']-df.loc[(int_today,userid), 'EF'])))
            proposta = sortida_obj - (8*60 - minMati)
            if proposta > (df.loc[(int_today,userid), 'SM'] + 60):
                if h*60+m + 9 > proposta:
                    txt = "Fas tard, hauries d'entrar a les "+pretty(proposta)
                else:
                    txt = "Hauries d'entrar a les "+pretty(proposta)
            else:
                txt = 'No pots sortir a les 5pm, entra a les '+pretty(df.loc[(int_today,userid), 'SM']+60)
    else:
        txt = 'No estas autoritzat'
    update.message.reply_text(txt)

def help_command(update: Update, context: CallbackContext) -> None:
    reply_txt = '/start Per veure les fitxades \
        \n/checkin Per fitxar \
        \n/del Per esborrar-ho tot \
        \n/pitipausa Per fitxar piti \
        \n/mod EM XX:YY per modificar alguna fitxada \
        \n/reco Per solicitar recomenacio ET \
        \n/sortida Per saber a quina hora sortir \
        \n/auth UserID per afegir un usuari autoritzat'
    update.message.reply_text(reply_txt)

def pitipausa_command(update: Update, context: CallbackContext) -> None:
    global df, users_auth
    txt = 'Unknown'
    userid = update.effective_user['id']
    int_today = int(datetime.now().strftime("%d"))
    h = int(datetime.now().strftime("%H"))
    m = int(datetime.now().strftime("%M"))

    if userid in users_auth:
        if not (int_today, userid) in df.index:
            txt = 'Sense fitxades'
        elif df.loc[(int_today,userid), 'EM'] == 0:
            txt = 'Sense EM'
        elif df.loc[(int_today,userid), 'SF'] == 0:
            df.loc[(int_today,userid), 'SF'] = h*60+m
            df.to_csv(db_name)
            txt = 'SF: '+pretty(h*60+m)
        elif df.loc[(int_today,userid), 'EF'] == 0:
            df.loc[(int_today,userid), 'EF'] = h*60+m
            df.to_csv(db_name)
            txt = str(h*60+m - df.loc[(int_today,userid), 'SF']) + ' minuts de break'
    else:
        txt = 'No estas autoritzat'

    update.message.reply_text(txt)

def checkin_command(update: Update, context: CallbackContext) -> None:
    global df, users_auth
    h = int(datetime.now().strftime("%H"))
    m = int(datetime.now().strftime("%M"))
    int_today = int(datetime.now().strftime("%d"))
    userid = update.effective_user['id']

    if userid in users_auth:
        if not (int_today, userid) in df.index:
            print('New user_day '+str(update.effective_user['id'])+'_'+str(int_today))
            df.loc[(int_today,update.effective_user['id']),:] = (0,0,0,0,0,0)
            df.to_csv(db_name)

        reply, keyboard = check(False, update.effective_user['id'])
        print(reply)
        if keyboard:
            keyboardObj = [
        [
            InlineKeyboardButton("OK", callback_data='OK'),
            InlineKeyboardButton("NO", callback_data='NO'),
        ]
        ]
        else:
            keyboardObj = []

    else:
        keyboardObj = []
        reply = 'No estas autoritzat'
    reply_markup = InlineKeyboardMarkup(keyboardObj)
    update.message.reply_text(reply, reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    reply_text = ''
    userid = update.effective_user['id']
    if userid in users_auth:
        if query.data == 'OK':
            reply_text, keyboard = check(True, update.effective_user['id'])
            print(reply_text)
        elif query.data == 'NO':
            reply_text = 'OK'
            print('NO')
    else:
        reply_text = 'No estas autoritzat'
    query.edit_message_text(text=reply_text)

def del_command(update: Update, context: CallbackContext) -> None:
    global df, users_auth
    userid = update.effective_user['id']
    if userid in users_auth:
        df = pd.DataFrame([], columns=['DIA', 'USER', 'EM', 'SM', 'ET', 'ST','SF','EF'])
        df.set_index(['DIA', 'USER'], inplace=True)
        txt = 'Done'
    else:
        txt = 'No estas autoritzat'
    update.message.reply_text(txt)

def auth_command(update: Update, context: CallbackContext) -> None:
    global users_auth
    userid = update.effective_user['id']
    if userid in users_auth:
        user_proposed = update.message.text.replace(" ", "")
        new_user = user_proposed[5:]
        try:
            new_id = int(new_user)
            if new_id in users_auth:
               txt = 'Usuari ja existent'
            else:
                txt = 'Nou usuari autoritzat: '+str(new_id)
                print('new_user', str(new_id))
                users_auth.append(new_id)
                f = open(users_file, "w+")
                json.dump(users_auth, f)
                f.close()
        except:
            txt = 'Error en la conversio'
    else:
        txt = 'Tu qui et penses que ets?'
    update.message.reply_text(txt)

def mod_command(update: Update, context: CallbackContext) -> None:
    global users_auth
    text = update.message.text.replace(" ", "")
    print(text)
    fixaje_list = ['EM', 'SM', 'ET', 'ST']
    fixaje = fixaje_list.index(text[4:6])
    reply_text = 'Error'
    userid = update.effective_user['id']
    if userid in users_auth:
        if not(fixaje == ValueError):
            restu = text.replace('/mod'+fixaje_list[fixaje], '')
            time_list = restu.split(":")
            time_list_int = [int(x) for x in time_list]
            print(time_list_int)
            if time_list_int[0] >= 0 and time_list_int[0] <= 23:
                if time_list_int[1] >= 0 and time_list_int[1] <= 59:
                    int_today = int(datetime.now().strftime("%d"))
                    if not (int_today, userid) in df.index:
                        df.loc[(int_today,update.effective_user['id']),:] = (0,0,0,0,0,0)
                    df.loc[(int_today,userid), fixaje_list[fixaje]] = time_list_int[0]*60+time_list_int[1]
                    df.to_csv(db_name)
                    if time_list_int[1] < 10:
                        reply_text = fixaje_list[fixaje]+' a les '+str(time_list_int[0])+':0'+str(time_list_int[1])
                    else:
                        reply_text = fixaje_list[fixaje]+' a les '+str(time_list_int[0])+':'+str(time_list_int[1])
    else:
        reply_text = 'No estas autoritzat'

    update.message.reply_text(reply_text)
    raise DispatcherHandlerStop # Only if you DON'T want other handlers to handle this update

def sortida_command(update: Update, context: CallbackContext) -> None:
    global df, users_auth
    txt = 'Unknown'
    userid = update.effective_user['id']
    int_today = int(datetime.now().strftime("%d"))

    if userid in users_auth:
        if not (int_today, userid) in df.index:
            txt = 'Sense fitxades'
        elif df.loc[(int_today,userid), 'EM'] == 0:
            txt = 'Sense EM'
        elif df.loc[(int_today,userid), 'SM'] == 0:
            txt = 'Sense SM'
        elif df.loc[(int_today,userid), 'ET'] == 0:
            txt = 'Sense ET'
        else:
            if df.loc[(int_today,userid), 'SF'] > 0 and df.loc[(int_today,userid), 'EF'] > 0:
                mPiti = df.loc[(int_today,userid), 'EF'] - df.loc[(int_today,userid), 'SF']
                if mPiti > 0:
                    txt = 'Surt a les '+sortida(df.loc[(int_today,userid), 'EM'], df.loc[(int_today,userid), 'SM'], df.loc[(int_today,userid), 'ET'], mPiti)
                else:
                    txt = 'Error en piti'
            else:
                txt = 'Surt a les '+sortida(df.loc[(int_today,userid), 'EM'], df.loc[(int_today,userid), 'SM'], df.loc[(int_today,userid), 'ET'], 0)
    else:
        txt = 'No estas autoritzat'
    update.message.reply_text(txt)


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("checkin", checkin_command))
    dispatcher.add_handler(CommandHandler("pitipausa", pitipausa_command))
    dispatcher.add_handler(CommandHandler("reco", reco_command))
    dispatcher.add_handler(CommandHandler("del", del_command))
    dispatcher.add_handler(CommandHandler("mod", mod_command))
    dispatcher.add_handler(CommandHandler("sortida", sortida_command))
    dispatcher.add_handler(CommandHandler("auth", auth_command))

    dispatcher.add_handler(CallbackQueryHandler(button))

    # on non command i.e message - echo the message on Telegram
    #dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
