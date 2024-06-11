from utility_functions import *
import pyperclip

jsonObj = json.loads(pyperclip.paste())
csv_string = ','.join(f'{value}' if isinstance(value, (int, float)) else value for value in jsonObj.values())
print(csv_string)
pyperclip.copy(csv_string)