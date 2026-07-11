#!/usr/bin/env python3

import os
import sys
import time
import itertools
import hashlib
import threading
import queue
import argparse

ASCII_ART = r"""
=====================================
██╗  ██╗ █████╗ ███████╗██╗  ██╗ ██████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██║  ██║██╔══██╗██╔════╝██║  ██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████║███████║███████╗███████║██║     ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██║██╔══██║╚════██║██╔══██║██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║██║  ██║███████║██║  ██║╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
   By jsnulled (https://github.com/jsnulled)
=====================================
"""

# Extended character sets
CHARSETS = {
    "1": "abcdefghijklmnopqrstuvwxyz0123456789",
    "2": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#",
    "3": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:'\",.<>?/",
    "4": "0123456789",  # Numeric only
    "5": "abcdefghijklmnopqrstuvwxyz",  # Lowercase only
    "6": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # Uppercase only
    "7": "0123456789abcdef",  # Hex characters
}

# All supported hash types with their lengths
HASH_TYPES = {
    32: "MD5",
    40: "SHA-1",
    56: "SHA-224",
    64: "SHA-256",
    96: "SHA-384",
    128: "SHA-512",
}

# Hash function mapping
HASH_FUNCTIONS = {
    "MD5": lambda x: hashlib.md5(x).hexdigest(),
    "SHA-1": lambda x: hashlib.sha1(x).hexdigest(),
    "SHA-224": lambda x: hashlib.sha224(x).hexdigest(),
    "SHA-256": lambda x: hashlib.sha256(x).hexdigest(),
    "SHA-384": lambda x: hashlib.sha384(x).hexdigest(),
    "SHA-512": lambda x: hashlib.sha512(x).hexdigest(),
}

# Thread-safe counter
class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()
    
    def increment(self, amount=1):
        with self.lock:
            self.value += amount
    
    def get(self):
        with self.lock:
            return self.value


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def loading_bar(message, duration=1.5, steps=20):
    print(f"\n{message}")
    for i in range(steps):
        time.sleep(duration / steps)
        bar = '#' * (i + 1) + '-' * (steps - i - 1)
        sys.stdout.write(f"\r[{bar}]")
        sys.stdout.flush()
    print("\n")


def is_valid_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def detect_hash_type(hash_str):
    if not is_valid_hex(hash_str):
        return None
    
    return HASH_TYPES.get(len(hash_str))


def hash_word(word, hash_type):
    encoded = word.encode()
    return HASH_FUNCTIONS.get(hash_type, lambda x: None)(encoded)


def brute_force(target_hash, prefix, max_len, charset, hash_type, counter=None, stop_event=None):
    """Single-threaded brute force for comparison"""
    start_time = time.time()
    attempts = 0
    prefix_len = len(prefix)
    
    for length in range(prefix_len, max_len + 1):
        if stop_event and stop_event.is_set():
            return None, time.time() - start_time
        
        for combo in itertools.product(charset, repeat=length - prefix_len):
            if stop_event and stop_event.is_set():
                return None, time.time() - start_time
            
            word = prefix + ''.join(combo)
            attempts += 1
            
            if counter:
                counter.increment()
            
            if attempts % 100000 == 0:
                elapsed = time.time() - start_time
                rate = attempts / elapsed if elapsed > 0 else 0
                sys.stdout.write(f"\rTried: {attempts:,} | {rate:.0f}/sec")
                sys.stdout.flush()
            
            if hash_word(word, hash_type) == target_hash:
                print()
                return word, time.time() - start_time
    
    return None, time.time() - start_time


def multi_threaded_brute_force(target_hash, prefix, max_len, charset, hash_type, num_threads=4):
    """Multi-threaded brute force for better performance"""
    start_time = time.time()
    counter = Counter()
    stop_event = threading.Event()
    result_holder = {'result': None, 'elapsed': 0}
    
    def worker():
        while not stop_event.is_set():
            # Get current length to process
            try:
                length = length_queue.get_nowait()
            except queue.Empty:
                break
            
            for combo in itertools.product(charset, repeat=length - len(prefix)):
                if stop_event.is_set():
                    break
                word = prefix + ''.join(combo)
                counter.increment()
                
                if hash_word(word, hash_type) == target_hash:
                    stop_event.set()
                    result_holder['result'] = word
                    result_holder['elapsed'] = time.time() - start_time
            
            length_queue.task_done()
    
    # Create queue of lengths to process
    length_queue = queue.Queue()
    prefix_len = len(prefix)
    for length in range(prefix_len, max_len + 1):
        length_queue.put(length)
    
    # Start threads
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    
    # Progress display
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        rate = counter.get() / elapsed if elapsed > 0 else 0
        sys.stdout.write(f"\rTried: {counter.get():,} | {rate:.0f}/sec")
        sys.stdout.flush()
        time.sleep(0.1)
    
    # Wait for threads
    for t in threads:
        t.join(timeout=0.1)
    
    return result_holder['result'], result_holder['elapsed']


def wordlist_attack(target_hash, wordlist_path, hash_type):
    """Try to crack hash using a wordlist file"""
    start_time = time.time()
    attempts = 0
    
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                word = line.strip()
                if not word:
                    continue
                
                attempts += 1
                if attempts % 10000 == 0:
                    elapsed = time.time() - start_time
                    rate = attempts / elapsed if elapsed > 0 else 0
                    sys.stdout.write(f"\rTried: {attempts:,} | {rate:.0f}/sec")
                    sys.stdout.flush()
                
                if hash_word(word, hash_type) == target_hash:
                    print()
                    return word, time.time() - start_time
    except FileNotFoundError:
        print(f"\nWordlist file not found: {wordlist_path}")
        return None, 0
    
    return None, time.time() - start_time


def rainbow_table_lookup(target_hash, hash_type):
    """Check common passwords (built-in rainbow table)"""
    common_passwords = [
        # Top 100 most common passwords
        "password", "123456", "12345678", "12345", "qwerty",
        "123456789", "1234567", "1234567890", "111111", "000000",
        "admin", "letmein", "welcome", "monkey", "dragon",
        "master", "login", "abc123", "password1", "iloveyou",
        "trustno1", "sunshine", "hello", "charlie", "donald",
        "test", "guest", "root", "pass", "passwd", "admin123",
        "toor", "changeme", "default", "passw0rd", "p@ssw0rd",
        "password123", "123qwe", "qwerty123", "1q2w3e4r", "qwe123",
        "123456a", "123456abc", "123abc", "abc1234", "password!",
        "qwerty1", "admin1234", "welcome1", "letmein1", "123456789a",
        "password12", "password1234", "1234567890a", "123456789ab",
        "qwertyuiop", "asdfghjkl", "zxcv123", "123zxc", "qazwsx",
        "qazwsx123", "123qaz", "qaz123", "wsx123", "wsx321",
        "asd123", "asd1234", "asdf1234", "asdf123", "asdf",
        "asdfgh", "asdfgh123", "asdfgh1234", "1234qwer", "qwer1234",
        "qwer123", "qwerty12", "qwerty1234", "qwerty12345", "qwerty123456",
    ]
    
    for word in common_passwords:
        if hash_word(word, hash_type) == target_hash:
            return word
    
    return None


def show_hash_info():
    """Display information about supported hash types"""
    print("\nSupported Hash Types:")
    print("-" * 40)
    for length, name in sorted(HASH_TYPES.items()):
        print(f"  {name}: {length} characters (hex)")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Hash Cracker - A tool for cracking various hash types",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hashcracker.py -H 5f4dcc3b5aa765d61d8327deb882cf99
  python hashcracker.py -H 5f4dcc3b5aa765d61d8327deb882cf99 -c 1 -m 8
  python hashcracker.py -H 5f4dcc3b5aa765d61d8327deb882cf99 -w wordlist.txt
  python hashcracker.py --info
        """
    )
    
    parser.add_argument('-H', '--hash', help='Target hash to crack')
    parser.add_argument('-p', '--prefix', default='', help='Prefix for brute force')
    parser.add_argument('-m', '--max-length', type=int, default=6, help='Maximum password length')
    parser.add_argument('-c', '--charset', choices=CHARSETS.keys(), default='2', 
                        help='Character set to use (1-7)')
    parser.add_argument('-t', '--threads', type=int, default=1, 
                        help='Number of threads for brute force')
    parser.add_argument('-w', '--wordlist', help='Path to wordlist file')
    parser.add_argument('-r', '--rainbow', action='store_true', 
                        help='Try built-in rainbow table first')
    parser.add_argument('-i', '--info', action='store_true', 
                        help='Show supported hash types')
    parser.add_argument('-l', '--list-charsets', action='store_true',
                        help='List available character sets')
    
    args = parser.parse_args()
    
    if args.info:
        show_hash_info()
        return
    
    if args.list_charsets:
        print("\nAvailable Character Sets:")
        print("-" * 40)
        for key, charset in CHARSETS.items():
            print(f"  {key}. {charset[:30]}..." if len(charset) > 30 else f"  {key}. {charset}")
        return
    
    # Interactive mode if no hash provided
    if not args.hash:
        clear()
        print(ASCII_ART)
        
        try:
            target_hash = input("Paste hash: ").strip().lower()
            prefix = input("Prefix (optional): ").strip()
            
            length_input = input("Max length (default 6): ").strip()
            max_len = int(length_input) if length_input.isdigit() else 6
            
            if max_len <= 0:
                print("Length must be greater than 0.")
                return
            
            print("\nSelect charset:")
            for key, charset in CHARSETS.items():
                print(f"  {key}. {charset[:30]}..." if len(charset) > 30 else f"  {key}. {charset}")
            
            charset_choice = input("> ").strip()
            if charset_choice not in CHARSETS:
                print("Invalid option.")
                return
            
            charset = CHARSETS[charset_choice]
            
            threads_input = input("Threads (default 1): ").strip()
            num_threads = int(threads_input) if threads_input.isdigit() else 1
            
            rainbow = input("Try rainbow table first? (y/n): ").strip().lower() == 'y'
            
        except KeyboardInterrupt:
            print("\nExiting...")
            return
    else:
        target_hash = args.hash.strip().lower()
        prefix = args.prefix
        max_len = args.max_length
        charset = CHARSETS[args.charset]
        num_threads = args.threads
        rainbow = args.rainbow
    
    hash_type = detect_hash_type(target_hash)
    if not hash_type:
        print("Invalid or unsupported hash.")
        print("Use --info to see supported hash types.")
        return
    
    print(f"\nDetected: {hash_type}")
    
    # Try rainbow table first
    if rainbow:
        loading_bar("Checking rainbow table...")
        result = rainbow_table_lookup(target_hash, hash_type)
        if result:
            print(f"\n========== RESULT ==========")
            print(f"Hash: {target_hash}")
            print(f"Result: {result}")
            print(f"Method: Rainbow table")
            return
    
    # Try wordlist if provided
    if args.wordlist:
        loading_bar(f"Loading wordlist: {args.wordlist}...")
        result, elapsed = wordlist_attack(target_hash, args.wordlist, hash_type)
        
        print("\n========== RESULT ==========")
        print(f"Hash: {target_hash}")
        print(f"Result: {result if result else 'Not found'}")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Method: Wordlist")
        return
    
    # Brute force
    loading_bar("Starting brute force...")
    
    if num_threads > 1:
        result, elapsed = multi_threaded_brute_force(target_hash, prefix, max_len, charset, hash_type, num_threads)
    else:
        result, elapsed = brute_force(target_hash, prefix, max_len, charset, hash_type)
    
    print("\n========== RESULT ==========")
    print(f"Hash: {target_hash}")
    print(f"Result: {result if result else 'Not found'}")
    print(f"Time: {elapsed:.2f} seconds")
    print(f"Method: Brute force")


if __name__ == "__main__":
    main()
