import pandas as pd
import telebot
import unicodedata

# Veri çerçevesini yükle
df = pd.read_excel('ankara mamak (2).xlsx')

# Telegram botunu oluştur
bot = telebot.TeleBot("6058174867:AAGSdPL4V9mHb4zmr_W3I8_kNa4jmcHLdqU")

# Türkçe ve ingilizce karakterlerin dönüşümünü sağlayan metot
def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

# Mesajları işleme fonksiyonu
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    search_text = normalize_text(message.text).casefold()  # Arama Türkçe karakter ve büyük-küçük harf bağımsız 'normalize' eder

    # Başında 0 kontrolü
    if search_text[:1] == "0":
        # Başında 0 olan ve 11 haneli numara için 0'ı kaldır
        if len(search_text) == 11:
            search_text = search_text[1:]
        else:
            # Başında 0 olan ve 10 haneli numara için başına 0 ekle
            search_text = "0" + search_text
            
    # Ad, Soyad, Adres, gsmtel_no, ikinci_adi, muhtarlik_adi sütunlarını içeren verileri filtrele
    filtered_df = df[(normalize_text(df['adi']).casefold() == search_text) |
                    (normalize_text(df['soyadi']).casefold() == search_text) |
                    ((df['gsmtel_no'].astype(str).str[-10:] == search_text[-10:]) | (df['gsmtel_no'].astype(str).str[-9:] == search_text[-10:])) |
                    (normalize_text((df['adi'] + ' ' + df['soyadi'])).casefold() == search_text) |
                    (normalize_text(df['ikinci_adi']).casefold() == search_text) |
                    (normalize_text(df['muhtarlik_adi']).casefold() == search_text)]

    if not filtered_df.empty:
        # Sonuçları soyisim (soyadi) sütununa göre alfabetik sıraya göre sırala
        filtered_df = filtered_df.sort_values(by='soyadi')

        response = "Sonuçlar:\n"
        for index, row in filtered_df.iterrows():
            response += f"Adı: {row['adi']}\n"
            if pd.notnull(row['ikinci_adi']):  # ikinci_adi boş değilse ekle
                response += f"İkinci Adı: {row['ikinci_adi']}\n"
            response += f"Soyadı: {row['soyadi']}\n"
            response += f"Adres: {row['adres']}\n"
                # Yeni eklenen veriler
            response += f"Anne Adı: {row['ana_adi']}\n"
            response += f"Baba Adı: {row['baba_adi']}\n"
            response += f"Doğum Tarihi: {row['dogum_tarih']}\n"
            response += f"Doğduğu İl: {row['dogum_il_adi']}\n"
            response += "-----------\n"
            gsmtel_no = str(row['gsmtel_no'])
            if len(gsmtel_no) == 11:  # Başında 0 kontrolü
                gsmtel_no = gsmtel_no[1:]  # Başındaki 0'ı kaldır
            gsmtel_no = gsmtel_no[-10:]  # Son 10 hane alınacak
            response += f"Cep Tel: {gsmtel_no}\n"

            response += f"Muhtarlık Adı: {row['muhtarlik_adi']}\n"
            response += "-----------\n"
    else:
        response = "Sonuç bulunamadı."

    # Yanıtı birden fazla mesaj olarak gönderme
    MAX_MESSAGE_LENGTH = 4096  # Maksimum mesaj uzunluğu
    while len(response) > MAX_MESSAGE_LENGTH:
        try:
            bot.reply_to(message, response[:MAX_MESSAGE_LENGTH])  # Uzun mesajı bölümlere ayırarak gönder
        except telebot.apihelper.ApiTelegramException as e:
            if hasattr(e.result, 'retry_after'):
                wait_time = e.result.retry_after
            else: 
                wait_time = 2
            time.sleep(wait_time)  # Retry bekleme süresi
        response = response[MAX_MESSAGE_LENGTH:]

    bot.reply_to(message, response)  # Kalan kısmı gönder

# Botu çalıştır
bot.polling()  
