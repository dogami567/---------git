import os
import platform

# 在pytest收集测试之前执行的钩子
def pytest_configure(config):
    """
    允许插件和conftest文件在测试收集之前执行初始化代码。
    """
    # 临时解决Windows环境下虚拟环境PATH不更新的问题
    # 在导入weasyprint之前，手动将GTK的dll路径添加到环境变量中
    if platform.system() == "Windows":
        gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"
        if os.path.exists(gtk_path) and gtk_path not in os.environ['PATH']:
            print(f"ROOT conftest.py: 临时添加GTK路径到PATH: {gtk_path}")
            os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH'] 