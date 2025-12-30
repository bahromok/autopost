"""Quick script to fix .env file with correct API credentials."""

# Read the current .env file
with open('.env', 'r') as f:
    lines = f.readlines()

# Fix the API credentials
new_lines = []
for line in lines:
    if line.startswith('API_ID='):
        new_lines.append('API_ID=28739061\n')
    elif line.startswith('API_HASH='):
        new_lines.append('API_HASH=c90fc951dfdace987eb56e2c467175599\n')
    else:
        new_lines.append(line)

# Write back
with open('.env', 'w') as f:
    f.writelines(new_lines)

print("✓ .env file updated with correct API credentials")
print("API_ID: 28739061")
print("API_HASH: c90fc951dfdace987eb56e2c467175599")
