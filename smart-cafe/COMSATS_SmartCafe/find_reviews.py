try:
    with open('backend/app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if 'get_reviews' in line:
                print(f"{i+1}: {line.strip()}")
except FileNotFoundError:
    print("File not found")
