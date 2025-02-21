import os
import hashlib
import subprocess
import argparse

def encrypt_keys_file(input_file, encrypt_key):
    """Encrypt keys file with hash-based integrity check."""
    # Generate output filename
    input_basename = os.path.basename(input_file).split('.')[0]
    output_file = input_basename + '.enc'
    
    # Calculate hash of input file
    sha256_hash = hashlib.sha256()
    with open(input_file, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    file_hash = sha256_hash.hexdigest()
    
    # Create temporary file with hash
    temp_in = f"{input_file}.tmp"
    with open(temp_in, 'w') as f:
        f.write(f"{file_hash}\n")
        with open(input_file, 'r') as src:
            f.write(src.read())
    
    # Encrypt the combined file
    cmd = [
        'openssl', 'enc', '-e',
        '-aes-256-cbc',
        '-pbkdf2',
        '-iter', '10000',
        '-md', 'sha256',
        '-salt',
        '-in', temp_in,
        '-out', output_file,
        '-pass', f'pass:{encrypt_key}'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Successfully encrypted {input_file} to \n\t {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Encryption failed: {e.stderr}")
        if os.path.exists(output_file):
            os.remove(output_file)
        raise
    finally:
        if os.path.exists(temp_in):
            os.remove(temp_in)

def decrypt_keys_file(input_file, decrypt_key, output_file):
    """Decrypt encrypted keys file and verify integrity."""
    # Create temporary file for decrypted content
    temp_out = f"{input_file}.tmp"
    
    # Decrypt the file
    cmd = [
        'openssl', 'enc', '-d',
        '-aes-256-cbc',
        '-pbkdf2',
        '-iter', '10000',
        '-md', 'sha256',
        '-salt',
        '-in', input_file,
        '-out', temp_out,
        '-pass', f'pass:{decrypt_key}'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Read decrypted content and verify hash
        with open(temp_out, 'r') as f:
            stored_hash = f.readline().strip()
            content = f.read()
            
        # Calculate hash of decrypted content
        sha256_hash = hashlib.sha256()
        sha256_hash.update(content.encode())
        content_hash = sha256_hash.hexdigest()
        
        # Verify integrity
        if stored_hash != content_hash:
            raise ValueError("Integrity check failed: File may be corrupted or tampered")
        
        # Write verified content to output file
        with open(output_file, 'w') as f:
            f.write(content)
            
        print(f"Successfully decrypted {input_file} to \n\t {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Decryption failed: {e.stderr}")
        if os.path.exists(output_file):
            os.remove(output_file)
        raise
    finally:
        if os.path.exists(temp_out):
            os.remove(temp_out)

def main():
    parser = argparse.ArgumentParser(
        description='Encrypt/Decrypt YAML keys file with integrity check'
    )
    parser.add_argument(
        '-f', '--file',
        required=True,
        help='Path to the input file'
    )
    parser.add_argument(
        '-p', '--password',
        required=True,
        help='Encryption/Decryption password'
    )
    parser.add_argument(
        '-d', '--decrypt',
        action='store_true',
        help='Decrypt mode (default is encrypt)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file name (required for decryption)',
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.file):
        print(f"Error: Input file not found: {args.file}")
        return 1
    
    try:
        if args.decrypt:
            if not args.output:
                print("Error: Output file (-o/--output) is required for decryption")
                return 1
            decrypt_keys_file(args.file, args.password, args.output)
        else:
            encrypt_keys_file(args.file, args.password)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())
