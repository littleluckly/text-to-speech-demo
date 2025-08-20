# debug_edge_tts.py
from edge_tts import Communicate
import inspect

# 查看 Communicate 的构造函数参数
sig = inspect.signature(Communicate.__init__)
print("🔍 Communicate.__init__ 支持的参数：")
for name, param in sig.parameters.items():
    print(f"  {name} = {param.default}")

# 打印模块位置（确认来源）
print(f"\n📦 edge-tts 来自：{Communicate.__module__}")
print(f"📄 模块文件：{inspect.getfile(Communicate)}")

# 打印版本
import edge_tts
print(f"\n🏷️  edge-tts 版本：{edge_tts.__version__}")