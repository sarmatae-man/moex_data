import sys
import os
from decimal import Decimal, ROUND_DOWN
from quotes_folder import FOLDER_NAME, FILE_EXT

def truncate_and_format(value_str, decimals):
    """Обрезает число до заданного числа знаков после запятой (без округления)"""
    d = Decimal(value_str)
    step = Decimal(1).scaleb(-decimals)   # 10 ** (-decimals)
    q = d.quantize(step, rounding=ROUND_DOWN)
    s = str(q)
    # убираем лишние нули в конце: 251.0 -> 251, 253.50 -> 253.5
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s


def main():
    if len(sys.argv) != 3:
       sys.exit(1)

    name = sys.argv[1]
    decimals = int(sys.argv[2])
    path = os.path.join(FOLDER_NAME, name + FILE_EXT)
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        sys.exit(1)

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Первая строка — заголовок, не трогаем; данные правим со второй строки
    new_lines = [lines[0].rstrip('\n')]
    for line in lines[1:]:
        parts = line.strip().split(',')
        date = parts[0]
        values = parts[1:]
        corrected = [truncate_and_format(v, decimals) for v in values]
        new_lines.append(date + ',' + ','.join(corrected))

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')

    print(f"Done: {path}")

if __name__ == '__main__':
    main()