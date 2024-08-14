import yfinance as yf
import pandas as pd
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram.ext import ContextTypes as CT

# Telegram bot token'ınızı buraya ekleyin
TELEGRAM_TOKEN = '7354053430:AAHOYB_cHDWksRPgFxyAI098gYLlZ2QBulc'
CHAT_ID = '-4233914882'  # Mesaj göndereceğiniz Telegram sohbet ID'si

# EMA hesaplama fonksiyonu
def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

# EMA çapraz strateji uygulama fonksiyonu
def apply_ema_strategy(df, short_period, long_period):
    df['EMA_Short'] = calculate_ema(df['Close'], short_period)
    df['EMA_Long'] = calculate_ema(df['Close'], long_period)

    df['Signal'] = 0
    df.loc[df['EMA_Short'] > df['EMA_Long'], 'Signal'] = 1
    df.loc[df['EMA_Short'] < df['EMA_Long'], 'Signal'] = -1

    df['Buy_Signal'] = (df['Signal'] == 1) & (df['Signal'].shift(1) != 1)
    df['Sell_Signal'] = (df['Signal'] == -1) & (df['Signal'].shift(1) != -1)

    return df

# Pivot noktalarına dayalı destek ve direnç hesaplama
def calculate_pivot_levels(df):
    high = df['High'].iloc[-2]  # Bir önceki günün yüksek değeri
    low = df['Low'].iloc[-2]    # Bir önceki günün düşük değeri
    close = df['Close'].iloc[-2]  # Bir önceki günün kapanış değeri

    pivot = (high + low + close) / 3
    resistance1 = (2 * pivot) - low
    support1 = (2 * pivot) - high
    resistance2 = pivot + (high - low)
    support2 = pivot - (high - low)

    return pivot, support1, resistance1, support2, resistance2

# Belirli bir hisseyi tarama fonksiyonu

def scan_stocks(stock_list, short_period, long_period):
    buy_signals = []
    sell_signals = []

    end_date = datetime.today().strftime('%Y-%m-%d')

    for symbol in stock_list:
        try:
            df = yf.download(symbol, start='2010-01-01', end=end_date)
            if df.empty:
                continue

            df = apply_ema_strategy(df, short_period, long_period)

            if not df['Buy_Signal'].dropna().empty and df['Buy_Signal'].iloc[-1]:
                buy_signals.append(symbol)
            if not df['Sell_Signal'].dropna().empty and df['Sell_Signal'].iloc[-1]:
                sell_signals.append(symbol)

        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            continue

    return buy_signals, sell_signals
def scan_single_stock(symbol, short_period, long_period):
    end_date = datetime.today().strftime('%Y-%m-%d')
    try:
        df = yf.download(symbol, start='2010-01-01', end=end_date)
        if df.empty:
            return f"No data found for {symbol}."

        df = apply_ema_strategy(df, short_period, long_period)

        last_row = df.iloc[-1]
        ema_short = last_row['EMA_Short']
        ema_long = last_row['EMA_Long']
        signal = 'Buy' if last_row['Signal'] == 1 else 'Sell' if last_row['Signal'] == -1 else 'Hold'

        pivot, support1, resistance1, support2, resistance2 = calculate_pivot_levels(df)
        stop_loss = support1  # Stop-loss seviyesini birinci destek seviyesine ayarlıyoruz

        message = (f"{symbol} - EMA Short: {ema_short:.2f}, EMA Long: {ema_long:.2f}, Signal: {signal}\n"
                   f"Pivot: {pivot:.2f}\n"
                   f"Support1: {support1:.2f}, Resistance1: {resistance1:.2f}\n"
                   f"Support2: {support2:.2f}, Resistance2: {resistance2:.2f}\n"
                   f"Stop-Loss: {stop_loss:.2f}")
        return message

    except Exception as e:
        return f"Error processing {symbol}: {str(e)}"

# Telegram botunu oluştur
async def start(update: Update, context: CT.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bot çalışıyor...")

async def scan(update: Update, context: CT.DEFAULT_TYPE) -> None:
    stock_list = ['A1CAP.IS', 'ACSEL.IS', 'ADEL.IS', 'ADESE.IS', 'ADGYO.IS','AEFES.IS','AFYON.IS', 'AGESA.IS','AGHOL.IS',
'AGROT.IS', 'AGYO.IS','AHGAZ.IS', 'AKBNK.IS','AKCNS.IS','AKENR.IS','AKFGY.IS','AKFYE.IS','AKGRT.IS', 'AKMGY.IS',
'AKSA.IS','AKSEN.IS','AKSGY.IS','AKSUE.IS','AKYHO.IS','ALARK.IS', 'ALBRK.IS','ALCAR.IS', 'ALCTL.IS','ALFAS.IS','ALGYO.IS','ALKA.IS','ALKIM.IS','ALKLC.IS','ALMAD.IS','ALTNY.IS','ALVES.IS','ANELE.IS','ANGEN.IS','ANHYT.IS','ANSGR.IS','ARASE.IS','ARCLK.IS','ARDYZ.IS','ARENA.IS','ARSAN.IS','ARTMS.IS','ARZUM.IS','ASELS.IS','ASGYO.IS','ASTOR.IS','ASUZU.IS','ATAGY.IS','ATAKP.IS','ATATP.IS','ATEKS.IS','ATLAS.IS','ATSYH.IS','AVGYO.IS','AVHOL.IS','AVOD.IS','AVPGY.IS','AVTUR.IS','AYCES.IS','AYDEM.IS','AYEN.IS','AYES.IS','AYGAZ.IS','AZTEK.IS','BAGFS.IS','BAKAB.IS','BALAT.IS','BANVT.IS','BARMA.IS','BASCM.IS','BASGZ.IS','BAYRK.IS','BEGYO.IS','BERA.IS','BEYAZ.IS','BFREN.IS','BIENY.IS','BIGCH.IS','BIMAS.IS','BINHO.IS','BIOEN.IS','BIZIM.IS','BJKAS.IS','BLCYT.IS','BMSCH.IS','BMSTL.IS','BNTAS.IS','BOBET.IS','BORLS.IS','BORSK.IS','BOSSA.IS','BRISA.IS','BRKO.IS','BRKSN.IS', 'BRKVY.IS', 'BRLSM.IS', 'BRMEN.IS', 'BRSAN.IS', 'BRYAT.IS', 'BSOKE.IS', 'BTCIM.IS', 'BUCIM.IS', 'BURCE.IS', 'BURVA.IS', 'BVSAN.IS', 'BYDNR.IS', 'CANTE.IS', 'CASA.IS', 'CATES.IS', 'CCOLA.IS', 'CELHA.IS', 'CEMAS.IS', 'CEMTS.IS', 'CEOEM.IS', 'CIMSA.IS', 'CLEBI.IS', 'CMBTN.IS', 'CMENT.IS', 'CONSE.IS', 'COSMO.IS', 'CRDFA.IS', 'CRFSA.IS', 'CUSAN.IS', 'CVKMD.IS', 'CWENE.IS', 'DAGHL.IS', 'DAGI.IS', 'DAPGM.IS', 'DARDL.IS', 'DENGE.IS', 'DERHL.IS', 'DERIM.IS', 'DESA.IS', 'DESPC.IS', 'DEVA.IS', 'DGATE.IS', 'DGGYO.IS', 'DGNMO.IS', 'DIRIT.IS', 'DITAS.IS', 'DMRGD.IS', 'DMSAS.IS', 'DNISI.IS', 'DOAS.IS', 'DOBUR.IS', 'DOCO.IS', 'DOFER.IS', 'DOGUB.IS', 'DOHOL.IS', 'DOKTA.IS', 'DURDO.IS', 'DYOBY.IS', 'DZGYO.IS', 'EBEBK.IS', 'ECILC.IS', 'ECZYT.IS', 'EDATA.IS', 'EDIP.IS', 'EFORC.IS', 'EGEEN.IS', 'EGEPO.IS', 'EGGUB.IS', 'EGPRO.IS', 'EGSER.IS', 'EKGYO.IS', 'EKIZ.IS', 'EKOS.IS', 'EKSUN.IS', 'ELITE.IS', 'EMKEL.IS', 'EMNIS.IS', 'ENERY.IS', 'ENJSA.IS', 'ENKAI.IS', 'ENSRI.IS', 'ENTRA.IS', 'EPLAS.IS', 'ERBOS.IS', 'ERCB.IS', 'EREGL.IS', 'ERSU.IS', 'ESCAR.IS', 'ESCOM.IS', 'ESEN.IS', 'ETILR.IS', 'ETYAT.IS', 'EUHOL.IS', 'EUKYO.IS', 'EUPWR.IS', 'EUREN.IS', 'EUYO.IS', 'EYGYO.IS', 'FADE.IS', 'FENER.IS', 'FLAP.IS', 'FMIZP.IS', 'FONET.IS', 'FORMT.IS', 'FORTE.IS', 'FRIGO.IS', 'FROTO.IS', 'FZLGY.IS', 'GARAN.IS', 'GARFA.IS', 'GEDIK.IS', 'GEDZA.IS', 'GENIL.IS', 'GENTS.IS', 'GEREL.IS', 'Menkul.IS', 'GESAN.IS', 'GIPTA.IS', 'GLBMD.IS', 'GLCVY.IS', 'GLDTR.IS', 'GLRYH.IS', 'GLYHO.IS', 'GMSTR.IS', 'GMTAS.IS', 'GOKNR.IS', 'GOLTS.IS', 'GOODY.IS', 'GOZDE.IS', 'GRNYO.IS', 'GRSEL.IS', 'GRTRK.IS', 'GSDDE.IS', 'GSDHO.IS', 'GSRAY.IS', 'GUBRF.IS', 'GWIND.IS', 'GZNMI.IS', 'HALKB.IS', 'HATEK.IS', 'HATSN.IS', 'HDFGS.IS', 'HEDEF.IS', 'HEKTS.IS', 'HKTM.IS', 'HLGYO.IS', 'HOROZ.IS', 'HRKET.IS', 'HTTBT.IS', 'HUBVC.IS', 'HUNER.IS', 'HURGZ.IS', 'ICBCT.IS', 'ICUGS.IS', 'IDGYO.IS', 'IEYHO.IS', 'IHAAS.IS', 'IHEVA.IS', 'IHGZT.IS', 'IHLAS.IS', 'IHLGM.IS', 'IHYAY.IS', 'IMASM.IS', 'INDES.IS', 'INFO.IS', 'INGRM.IS', 'INTEM.IS', 'INVEO.IS', 'INVES.IS', 'IPEKE.IS', 'ISATR.IS', 'ISBIR.IS', 'ISBTR.IS', 'ISCTR.IS', 'ISDMR.IS', 'ISFIN.IS', 'ISGLK.IS', 'ISGSY.IS', 'ISGYO.IS', 'ISIST.IS', 'ISKPL.IS', 'ISKUR.IS', 'ISMEN.IS', 'ISSEN.IS', 'ISYAT.IS', 'IZENR.IS', 'IZFAS.IS', 'IZINV.IS', 'IZMDC.IS', 'JANTS.IS', 'KAPLM.IS', 'KAREL.IS', 'KARSN.IS', 'KARTN.IS', 'KARYE.IS', 'KATMR.IS', 'KAYSE.IS', 'KBORU.IS', 'KCAER.IS', 'KCHOL.IS', 'KENT.IS', 'KERVN.IS', 'KERVT.IS', 'KFEIN.IS', 'KGYO.IS', 'KIMMR.IS', 'KLGYO.IS', 'KLKIM.IS', 'KLMSN.IS', 'KLNMA.IS', 'KLRHO.IS', 'KLSER.IS', 'KLSYN.IS', 'KMPUR.IS', 'KNFRT.IS', 'KOCMT.IS', 'KONKA.IS', 'KONTR.IS', 'KONYA.IS', 'KOPOL.IS', 'KORDS.IS', 'KOTON.IS', 'KOZAA.IS', 'KOZAL.IS', 'KRDMA.IS', 'KRDMB.IS', 'KRDMD.IS', 'KRGYO.IS', 'KRONT.IS', 'KRPLS.IS', 'KRSTL.IS', 'KRTEK.IS', 'KRVGD.IS', 'KSTUR.IS', 'KTLEV.IS', 'KTSKR.IS', 'KUTPO.IS', 'KUVVA.IS', 'KUYAS.IS', 'KZBGY.IS', 'KZGYO.IS', 'LIDER.IS', 'LIDFA.IS', 'LILAK.IS', 'LINK.IS', 'LKMNH.IS', 'LMKDC.IS', 'LOGO.IS', 'LRSHO.IS', 'LUKSK.IS', 'MAALT.IS', 'MACKO.IS', 'MAGEN.IS', 'MAKIM.IS', 'MAKTK.IS', 'MANAS.IS', 'MARBL.IS', 'MARKA.IS', 'MARTI.IS', 'MAVI.IS', 'MEDTR.IS', 'MEGAP.IS', 'MEGAP.IS', 'MEGMT.IS', 'MEKAG.IS', 'MEPET.IS', 'MERCN.IS', 'MERIT.IS', 'MERKO.IS', 'METRO.IS', 'METUR.IS', 'MGROS.IS', 'MHRGY.IS', 'MIATK.IS', 'MMCAS.IS', 'MNDRS.IS', 'MNDTR.IS', 'MOBTL.IS', 'MOGAN.IS', 'MPARK.IS', 'MRGYO.IS', 'MRSHL.IS', 'MSGYO.IS', 'MTRKS.IS', 'MTRYO.IS', 'MZHLD.IS', 'NATEN.IS', 'NETAS.IS', 'NIBAS.IS', 'NTGAZ.IS', 'NTHOL.IS', 'NUGYO.IS', 'NUHCM.IS', 'OBAMS.IS', 'OBASE.IS', 'ODAS.IS', 'ODINE.IS', 'OFSYM.IS', 'ONCSM.IS', 'ONRYT.IS', 'ORCAY.IS', 'ORGE.IS', 'ORMA.IS', 'OSMEN.IS', 'OSTIM.IS', 'OTKAR.IS', 'OTTO.IS', 'OYAKC.IS', 'OYAYO.IS', 'OYLUM.IS', 'OYYAT.IS', 'OZGYO.IS', 'OZKGY.IS', 'OZKGY.IS', 'OZRDN.IS', 'OZSUB.IS', 'OZYSR.IS', 'PAGYO.IS', 'PAMEL.IS', 'PAPIL.IS', 'PARSN.IS', 'PASEU.IS', 'PATEK.IS', 'PCILT.IS', 'PEHOL.IS', 'PEKGY.IS', 'PENGD.IS', 'PENTA.IS', 'PETKM.IS', 'Menkul.IS', 'PETUN.IS', 'PGSUS.IS', 'PINSU.IS', 'PKART.IS', 'PKENT.IS', 'PLTUR.IS', 'PNLSN.IS', 'PNSUT.IS', 'POLHO.IS', 'POLTK.IS', 'PRDGS.IS', 'PRKAB.IS', 'PRKME.IS', 'PRZMA.IS', 'PSDTC.IS', 'PSDTC.IS', 'PSDTC.IS', 'PSDTC.IS', 'PSGYO.IS', 'QNBFB.IS', 'QNBFL.IS', 'QUAGR.IS', 'RALYH.IS', 'RAYSG.IS', 'REEDR.IS', 'RGYAS.IS', 'RNPOL.IS', 'RODRG.IS', 'ROYAL.IS', 'RTALB.IS', 'RUBNS.IS', 'RYGYO.IS', 'RYSAS.IS', 'SAFKR.IS', 'SAHOL.IS', 'SAMAT.IS', 'SANEL.IS', 'SANFM.IS', 'SANKO.IS', 'SARKY.IS', 'SASA.IS', 'SAYAS.IS', 'SDTTR.IS', 'SEGMN.IS', 'SEGYO.IS', 'SEKFK.IS', 'SEKUR.IS', 'SELEC.IS', 'SELGD.IS', 'SELVA.IS', 'SEYKM.IS', 'SILVR.IS', 'SISE.IS', 'SKBNK.IS', 'SKTAS.IS', 'SKYLP.IS', 'SKYMD.IS', 'SMART.IS', 'SMRTG.IS', 'SNGYO.IS', 'SNICA.IS', 'SNKRN.IS', 'SNPAM.IS', 'SODSN.IS', 'SOKE.IS', 'SOKM.IS', 'SONME.IS', 'SRVGY.IS', 'SUMAS.IS', 'SUNTK.IS', 'SURGY.IS', 'SUWEN.IS', 'TABGD.IS', 'TARKM.IS', 'TATEN.IS', 'TATGD.IS', 'TAVHL.IS', 'TBORG.IS', 'TCELL.IS', 'TDGYO.IS', 'TEKTU.IS', 'TERA.IS', 'TETMT.IS', 'TEZOL.IS', 'TGSAS.IS', 'THYAO.IS', 'TKFEN.IS', 'TKNSA.IS', 'TLMAN.IS', 'TMPOL.IS', 'TMSN.IS', 'TNZTP.IS', 'TOASO.IS', 'TRCAS.IS', 'TRGYO.IS', 'TRILC.IS', 'TSGYO.IS', 'TSKB.IS', 'TSPOR.IS', 'TTKOM.IS', 'TTRAK.IS', 'TUCLK.IS', 'TUKAS.IS', 'TUPRS.IS', 'TUREX.IS', 'TURGG.IS', 'TURSG.IS', 'UFUK.IS', 'ULAS.IS', 'ULKER.IS', 'ULUFA.IS', 'ULUSE.IS', 'ULUUN.IS', 'UMPAS.IS', 'UNLU.IS', 'USAK.IS', 'USDTR.IS', 'VAKBN.IS', 'VAKFN.IS', 'VAKKO.IS', 'VANGD.IS', 'VBTYZ.IS', 'VERTU.IS', 'VERUS.IS', 'VESBE.IS','VESTL.IS','VKFYO.IS','VKGYO.IS','VKING.IS','VRGYO.IS','XU100.IS']  # Kısaltılmış liste
    short_period = 4
    long_period = 8

    buy_signals, sell_signals = scan_stocks(stock_list, short_period, long_period)

    message = "Stocks with buy signals:\n" + "\n".join(buy_signals) + "\n\nStocks with sell signals:\n" + "\n".join(sell_signals)
    await context.bot.send_message(chat_id=CHAT_ID, text=message)

    await update.message.reply_text("Scan completed. Results have been sent.")

async def tarama(update: Update, context: CT.DEFAULT_TYPE) -> None:
    args = context.args
    short_period = 4
    long_period = 8

    if args:
        symbol = args[0]
        message = scan_single_stock(symbol, short_period, long_period)
        await context.bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        await update.message.reply_text("Lütfen bir hisse senedi sembolü belirtin. Örneğin: /tarama ADEL.IS")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('scan', scan))
    application.add_handler(CommandHandler('tarama', tarama))

    application.run_polling()

if __name__ == "__main__":
    main()
