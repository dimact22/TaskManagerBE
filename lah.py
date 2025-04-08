import pandas as pd  

 

  

 

# Ваш шифр  

 

cipher_map = {   

 

    "А": "К", "Б": "Ь", "В": "І", "Г": "Є", "Ґ": "Н",   

 

    "Д": "М", "Е": "Ш", "Є": "Х", "Ж": "Ї", "З": "Т",   

 

    "И": "О", "І": "Я", "Ї": "Р", "Й": "С", "К": "З",   

 

    "Л": "У", "М": "Л", "Н": "Б", "О": "В", "П": "Ю",   

 

    "Р": "А", "С": "Д", "Т": "Г", "У": "Ф", "Ф": "Ч",   

 

    "Х": "Й", "Ц": "Е", "Ч": "Ц", "Ш": "П", "Щ": "Ж",   

 

    "Ь": "Ґ", "Ю": "З", "Я": "И"   

 

}  

 

  

 

original_text = '''Звичайний ранок у маленькому містечку збирав на своїх вулицях краплі долі, кожна з яких несла в собі свою історію.'''  

 

  

 

cipher_text = """ Дируоетре лотан к посятчнапк півзяунк дбрлои то виахм иксржгм нлошсі юасі, наїто д гнрм тявсо и вабі виан івзалін."""  

 

  

 

  

 

def decrypt_text(cipher_text, cipher_map):  

 

    decrypted_text = []  

 

      

 

      

 

    for char in cipher_text:  

 

        if char.upper() in cipher_map:  

 

            decrypted_char = cipher_map[char.upper()]  

 

             

 

            if char.isupper():  

 

                decrypted_text.append(decrypted_char.upper())  

 

            else:  

 

                decrypted_text.append(decrypted_char.lower())  

 

        else:  

 

              

 

            decrypted_text.append(char)  

 

      

 

    return ''.join(decrypted_text)  

 

  

 

  

 

def calculate_accuracy(original_text, decrypted_text, cipher_map):  

 

    correct = 0  

 

    incorrect = 0  

 

  

 

      

 

    for original_char, decrypted_char in zip(original_text, decrypted_text):  

 

         

 

        if original_char.upper() in cipher_map:  

 

            correct_char = cipher_map[original_char.upper()]  

 

              

 

            if decrypted_char.upper() == correct_char.upper():  

 

                correct += 1  

 

            else:  

 

                incorrect += 1  

 

  

 

    total = correct + incorrect  

 

    if total == 0:  

 

        return 0, 0   

 

  

 

    correct_percentage = (correct / total) * 100  

 

    incorrect_percentage = (incorrect / total) * 100  

 

  

 

    return correct_percentage, incorrect_percentage  

 

  

 

  

 

decrypted_text = decrypt_text(cipher_text, cipher_map)  

 

  

 

  

 

correct_percentage, incorrect_percentage = calculate_accuracy(original_text, decrypted_text, cipher_map)  

 

  

 

  

 

print(f"Відсоток правильних замін: {correct_percentage:.2f}%")  

 

print(f"Відсоток неправильних замін: {incorrect_percentage:.2f}%") 