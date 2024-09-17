import io

# 创建一个文本流
text_stream = io.StringIO()
# 写入内容
text_stream.write("Hello, World!\n")
text_stream.write("Hello, Python!\n")

# 将文本流的指针移动到开头
text_stream.seek(0)
# 读取所有内容
print(text_stream.read())


text_stream.seek(0)
text_stream.truncate(0)
# 将文本流的指针移动到开头
text_stream.write("WORI!\n")

# 读取一行内容
print(text_stream.getvalue())

# 关闭流
text_stream.close()
