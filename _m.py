# TO DO
# При апдейте всех файлов, в случае ошибки выдать тикер ошибочного файла.
from MoexCandlePeriods import MoexCandlePeriods   
from MoexImporter import MoexImporter
from MoexSecurity import MoexSecurity
import sys
from os import stat, walk,path
from os.path import join, splitext
from pathlib import Path
from datetime import datetime
from quotes_folder import FOLDER_NAME, FILE_EXT

global  symbols_path, mi, timeframe
timeframe = MoexCandlePeriods.Period1Day

def load_first(path_user_data, sec, item_s, _timeframe):      
   csv_out = []   
   csv_out.append('Date,Open,High,Low,Close' + '\n') # ,Volume' 
   # get sec.mainboard data   
   sec_d = sec.boards[sec.mainboard]      
   dttill_d = sec_d['dttill']
   dtfrom_d = sec_d['dtfrom']
   count = 1
   print('[', end='', flush=True)
   while True:         
       first_df = sec.getCandleQuotesAsArray(dtfrom_d, dttill_d, interval = _timeframe) #, interval = MoexCandlePeriods.Period1Min         
       if len(first_df) == 0:
          print("Requests error, symbol: " + item_s)          
          return       
       for item in first_df:
          csv_out.append(item['begin'].date().strftime("%Y-%m-%d") + ',' + str(item ['open']) + ',' + str(item ['high']) + ',' + str(item ['low']) + ',' + str(item ['close']) + '\n') #  + ',' + str(item ['quantity'])   
          #check date
       if dtfrom_d == dttill_d:
          break              
       # check date last loading date vs. get sec (ex. TRNFP)
       last_d = first_df[-1]['begin'].date()
       if dtfrom_d == last_d:
          print("Warning! Last date: " + str(last_d) + " is not equivalent get sec data: " +  str(dttill_d)  + ", symbol: " + item_s)
          break
       dtfrom_d = first_df[-1]['begin'].date()      
       csv_out.pop(-1) 
       count += 1
       # что-то пошло не так
       if (count > 40):
          print("Error, count upload: " +  item_s + ": " + str(count))
          return
       print('#', end='', flush=True)     
   name_f = path.join(symbols_path, item_s + FILE_EXT)     
   with open(name_f ,"w+", encoding="utf-8") as fl:
         for item in csv_out:
           fl.write(item) 
   print(']')
  
def load_data(path_file, _sec):       
   lines = []
   # проверяем если был какой-то ранее сбой и файл пустой заново качаем его и копируем юзеру
   if stat(path_file).st_size == 0:
         print("File destroyed: " + path_file)
         return
   with open(path_file, 'r') as file:
     lines = file.readlines()
   # upload last 5 date
   if len(lines) > 6:
     last_line = lines[-5]       
   else:       
     return      
   str_sp = last_line.split(',')
   begin = datetime.strptime(str_sp[0], "%Y-%m-%d")
   sec_d = _sec.boards[_sec.mainboard]
   first_df = _sec.getCandleQuotesAsArray(begin.date(), sec_d['dttill'], interval = timeframe)      
   # if not internet or bad symbol name
   if len(first_df) == 0:
         print("Requests error, symbol: " + _sec)                 
         return    

   with open(path_file, "w+", encoding="utf-8") as fl:
            for item in lines[:-5]:
              fl.write(item)
            _str = ''
            for item in first_df:
              _str = item['begin'].date().strftime("%Y-%m-%d") + ',' + str(item ['open']) + ',' + str(item ['high']) + ',' + str(item ['low']) + ',' + str(item ['close']) + '\n' 
              try:
                 _ = item['close'] * 1.1
              except:
                 print(path_file + ' | bad close write to file')                 
                 return
              else:
                fl.write(_str) 
   print('#', end='', flush=True)      
                
def upload_all():    
  # рекурсивно обходим symbols_path, включая вложенные папки
    print('[', end='', flush=True)
    for root, dirs, files in walk(symbols_path):
        for file in files:
            if not file.endswith(FILE_EXT):
                continue

            full_path = join(root, file)
            _sec = MoexSecurity(Path(full_path).stem, mi)

            if _sec.mainboard is None:
                print("Symbol not found: " + Path(full_path).stem)
                continue

            load_data(full_path, _sec)
    print(']')
    
if __name__ == "__main__":    
    base_dir = Path(__file__).resolve().parent
    symbols_path = base_dir / FOLDER_NAME
    # Создаём каталог, если его нет
    symbols_path.mkdir(exist_ok=True)   
    mi = MoexImporter()    
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        sec = MoexSecurity(symbol, mi)         
        if sec.mainboard == None:
            print("Symbol not found: " + symbol)
            exit()
        load_first(symbols_path, sec, symbol, timeframe)
    else:                                                                                           
        upload_all()