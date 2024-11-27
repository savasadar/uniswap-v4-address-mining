from web3 import Web3

def calculate_score(address):
    # 1. Başındaki Sıfır Nibble'ları Say ve Puanla
    score = 0
    hex_address = address[2:]  # "0x" kısmını kaldırıyoruz
    leading_zeros = 0
    for nibble in hex_address:
        if nibble == '0':
            leading_zeros += 1
        else:
            break
    score += leading_zeros * 10

    # 2. İlk 4'ten İtibaren Ardışık Dört 4 Varsa Puan Ver
    first_four_index = hex_address.find('4')
    if first_four_index != -1 and hex_address[first_four_index:first_four_index + 4] == '4444':
        score += 40
        
        # 3. Dört '4'ten Sonraki İlk Nibble '4' Değilse Ekstra Puan Ver
        if len(hex_address) > first_four_index + 4 and hex_address[first_four_index + 4] != '4':
            score += 20

    # 4. Son Dört Nibble 4 ise Ekstra Puan Ver
    if hex_address[-4:] == '4444':
        score += 20

    # 5. Adreste Bulunan Tüm '4'leri Say ve Puanla
    total_fours_count = hex_address.count('4')
    score += total_fours_count

    return score

# Test adresi
address = "0x000000000044449b4B19c2B8477Dbc403Cc4DA4e"
score = calculate_score(address)
print(f"Adres: {address}, Puan: {score}")
