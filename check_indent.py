with open('venue_admin/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(380, 400):
        if i < len(lines):
            indent = len(lines[i]) - len(lines[i].lstrip())
            print(f'{i+1:4}: {" " * indent}{lines[i].rstrip()}')