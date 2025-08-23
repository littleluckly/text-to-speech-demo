import re
import uuid
import os

# 读取文件内容
file_path = '/Users/xiongweiliu/workspaces/text-to-speech/vue_questions-md-format copy.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 定义正则表达式来匹配id行
id_pattern = r'id: (\d+)'

# 替换所有id为UUID
def replace_id(match):
    # 生成新的UUID
    new_uuid = str(uuid.uuid4())
    print(f'替换id: {match.group(1)} -> {new_uuid}')
    return f'id: {new_uuid}'

# 执行替换
new_content = re.sub(id_pattern, replace_id, content)

# 保存修改后的内容到新文件
output_file_path = '/Users/xiongweiliu/workspaces/text-to-speech/vue_questions-md-format_uuid.md'
with open(output_file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'\n替换完成！已生成新文件：{output_file_path}')
print(f'总共替换了 {len(re.findall(id_pattern, content))} 个ID')