#!/usr/bin/env python3
"""
Script để sửa lỗi cú pháp trong chrome_manager.py
"""

import re

def fix_syntax_errors():
    with open('chrome_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Sửa lỗi except: không có Exception
    content = re.sub(r'except:\s*pass', 'except Exception:\n                pass', content)
    
    # Sửa lỗi try block không có except
    # Tìm và sửa các try block bị thiếu except
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # Nếu gặp try: và không có except tương ứng
        if line.strip().startswith('try:') and i < len(lines) - 1:
            # Kiểm tra xem có except tương ứng không
            has_except = False
            indent_level = len(line) - len(line.lstrip())
            
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                if next_line.strip() == '':
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                
                if next_indent <= indent_level:
                    if next_line.strip().startswith('except') or next_line.strip().startswith('finally'):
                        has_except = True
                    break
            
            if not has_except:
                # Thêm except block
                fixed_lines.append(' ' * (indent_level + 4) + 'except Exception as e:')
                fixed_lines.append(' ' * (indent_level + 8) + 'print(f"Error: {str(e)}")')
                fixed_lines.append(' ' * (indent_level + 8) + 'pass')
        
        i += 1
    
    # Ghi lại file
    with open('chrome_manager.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Đã sửa lỗi cú pháp trong chrome_manager.py")

if __name__ == "__main__":
    fix_syntax_errors()
