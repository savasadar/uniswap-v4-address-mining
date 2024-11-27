from web3 import Web3
from eth_utils import to_checksum_address
import multiprocessing
import time
import os

# Sabit veriler
deployer_address = "0x48E516B34A1274f49457b9C6182097796D0498Cb"
initcode_hash = "0x94d114296a5af85c1fd2dc039cdaa32f1ed4b0fe0868f02d888bfc91feb645d9"
offset_file = "suffix_offset.txt"

# CREATE2 adresini hesaplayan fonksiyon
def compute_create2_address(deployer, salt, initcode_hash):
    deployer_bytes = bytes.fromhex(deployer[2:])
    salt_bytes = bytes.fromhex(salt[2:])
    initcode_bytes = bytes.fromhex(initcode_hash[2:])
    address_bytes = Web3.keccak(b'\xff' + deployer_bytes + salt_bytes + initcode_bytes)
    return to_checksum_address(address_bytes[-20:])

# Frontrunning önlemi uygulanmış salt oluşturma fonksiyonu
def generate_salt(address, suffix):
    salt = address[2:] + suffix
    return "0x" + salt

# Puan hesaplama fonksiyonu
def calculate_score(address):
    score = 0
    hex_address = address[2:]
    leading_zeros = len(hex_address) - len(hex_address.lstrip('0'))
    score += leading_zeros * 10

    first_four_index = hex_address.find('4')
    if first_four_index != -1 and hex_address[first_four_index:first_four_index + 4] == '4444':
        score += 40
        if len(hex_address) > first_four_index + 4 and hex_address[first_four_index + 4] != '4':
            score += 20
    if hex_address[-4:] == '4444':
        score += 20
    total_fours_count = hex_address.count('4')
    score += total_fours_count
    return score

# Çoklu işlemle brute force yapacak fonksiyon
def brute_force_create2(start, end, address, suffix_offset):
    results = []
    for i in range(start, end):
        suffix = f"{i + suffix_offset:012x}"
        salt = generate_salt(address, suffix)
        create2_address = compute_create2_address(deployer_address, salt, initcode_hash)
        score = calculate_score(create2_address)
        if score >= 140:
            results.append((create2_address, salt, score))
    return results

# Offset değerini dosyadan yükleyen veya dosya yoksa sıfırdan başlatan fonksiyon
def load_suffix_offset():
    if os.path.exists(offset_file):
        with open(offset_file, 'r') as f:
            return int(f.read().strip())
    return 0

# Offset değerini dosyaya kaydeden fonksiyon
def save_suffix_offset(suffix_offset):
    with open(offset_file, 'w') as f:
        f.write(str(suffix_offset))

# Çoklu işlemi başlatma fonksiyonu
def parallel_brute_force(address):
    num_processes = 4
    range_size = 100000
    pool = multiprocessing.Pool(processes=num_processes)
    suffix_offset = load_suffix_offset()
    
    while True:
        ranges = [(i * range_size, (i + 1) * range_size, address, suffix_offset) for i in range(num_processes)]
        results = pool.starmap(brute_force_create2, ranges)
        all_results = [item for sublist in results for item in sublist]
        sorted_results = sorted(all_results, key=lambda x: x[2], reverse=True)
        for addr, salt, score in sorted_results:
            print(f"CREATE2 Adresi: {addr} | Salt: {salt} | Puan: {score}")
        
        suffix_offset += num_processes * range_size
        save_suffix_offset(suffix_offset)
        time.sleep(1)

# Brute force işlemini başlatma
if __name__ == '__main__':
    address = "0x81D1F44E3dDB7Df9c16aC8268b079C87ea86Ef6E"
    parallel_brute_force(address)
