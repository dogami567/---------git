import os
import shutil
import git
import logging
from typing import List, Dict, Optional, Union
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.exceptions import RepositoryException
from backend.app.core.logging import logger

class RepositoryService:
    """
    零件仓库管理服务
    负责与Git仓库交互，管理代码组件
    """
    
    def __init__(self):
        """
        初始化仓库服务
        """
        self.repo_url = settings.COMPONENTS_REPO_URL
        self.repo_branch = settings.COMPONENTS_REPO_BRANCH
        self.local_path = Path(settings.COMPONENTS_REPO_LOCAL_PATH)
        self.repo = None
        
    def setup_repository(self) -> bool:
        """
        设置组件仓库
        如果本地路径不存在，则克隆远程仓库
        如果本地路径存在，则拉取最新更改
        
        Returns:
            bool: 设置是否成功
        """
        try:
            if not os.path.exists(self.local_path):
                # 创建目录
                os.makedirs(self.local_path, exist_ok=True)
                
                # 克隆仓库
                if self.repo_url:
                    logger.info(f"克隆仓库: {self.repo_url}")
                    self.repo = git.Repo.clone_from(
                        self.repo_url,
                        self.local_path,
                        branch=self.repo_branch
                    )
                else:
                    # 如果没有提供URL，则初始化一个新的本地仓库
                    logger.info("初始化新的本地仓库")
                    self.repo = git.Repo.init(self.local_path)
                    
                    # 创建初始结构
                    self._create_initial_structure()
                    
                    # 初始提交
                    self.commit_changes("初始化仓库")
            else:
                # 打开现有仓库
                self.repo = git.Repo(self.local_path)
                
                # 如果有远程仓库，则拉取最新更改
                if self.repo_url and "origin" in [remote.name for remote in self.repo.remotes]:
                    logger.info("拉取最新更改")
                    origin = self.repo.remotes.origin
                    origin.fetch()
                    origin.pull()
                    
            return True
        except git.GitCommandError as e:
            logger.error(f"Git命令错误: {str(e)}")
            raise RepositoryException(f"设置仓库时出错: {str(e)}")
        except Exception as e:
            logger.error(f"设置仓库时出错: {str(e)}")
            raise RepositoryException(f"设置仓库时出错: {str(e)}")
            
    def commit_changes(self, message: str) -> str:
        """
        提交更改到仓库
        
        Args:
            message: 提交消息
            
        Returns:
            str: 提交ID
            
        Raises:
            RepositoryException: 提交失败
        """
        try:
            if not self.repo:
                self.setup_repository()
                
            # 添加所有更改
            self.repo.git.add(all=True)
            
            # 检查是否有更改
            if not self.repo.is_dirty() and not self.repo.untracked_files:
                logger.info("没有更改需要提交")
                # 返回最新提交的ID
                return self.repo.head.commit.hexsha
                
            # 提交更改
            commit = self.repo.index.commit(message)
            logger.info(f"提交更改: {commit.hexsha}")
            
            # 如果有远程仓库，则推送更改
            if self.repo_url and "origin" in [remote.name for remote in self.repo.remotes]:
                logger.info("推送更改到远程仓库")
                origin = self.repo.remotes.origin
                origin.push()
                
            return commit.hexsha
        except git.GitCommandError as e:
            logger.error(f"Git命令错误: {str(e)}")
            raise RepositoryException(f"提交更改时出错: {str(e)}")
        except Exception as e:
            logger.error(f"提交更改时出错: {str(e)}")
            raise RepositoryException(f"提交更改时出错: {str(e)}")
            
    def reset_changes(self) -> bool:
        """
        重置所有未提交的更改
        
        Returns:
            bool: 重置是否成功
            
        Raises:
            RepositoryException: 重置失败
        """
        try:
            if not self.repo:
                self.setup_repository()
                
            # 重置所有更改
            self.repo.git.reset('--hard')
            
            # 清理未跟踪的文件
            self.repo.git.clean('-fd')
            
            logger.info("已重置所有未提交的更改")
            return True
        except git.GitCommandError as e:
            logger.error(f"Git命令错误: {str(e)}")
            raise RepositoryException(f"重置更改时出错: {str(e)}")
        except Exception as e:
            logger.error(f"重置更改时出错: {str(e)}")
            raise RepositoryException(f"重置更改时出错: {str(e)}")
            
    def get_file_content(self, file_path: str) -> str:
        """
        获取文件内容
        
        Args:
            file_path: 文件路径（相对于仓库根目录）
            
        Returns:
            str: 文件内容
            
        Raises:
            RepositoryException: 获取文件内容失败
        """
        try:
            if not self.repo:
                self.setup_repository()
                
            full_path = os.path.join(self.local_path, file_path)
            
            if not os.path.exists(full_path):
                raise RepositoryException(f"文件不存在: {file_path}")
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return content
        except Exception as e:
            logger.error(f"获取文件内容时出错: {str(e)}")
            raise RepositoryException(f"获取文件内容时出错: {str(e)}")
            
    def get_file_history(self, file_path: str, max_count: int = 10) -> List[Dict[str, str]]:
        """
        获取文件的提交历史
        
        Args:
            file_path: 文件路径（相对于仓库根目录）
            max_count: 最大提交数
            
        Returns:
            List[Dict[str, str]]: 提交历史
            
        Raises:
            RepositoryException: 获取历史失败
        """
        try:
            if not self.repo:
                self.setup_repository()
                
            full_path = os.path.join(self.local_path, file_path)
            
            if not os.path.exists(full_path):
                raise RepositoryException(f"文件不存在: {file_path}")
                
            # 获取文件的提交历史
            commits = list(self.repo.iter_commits(paths=file_path, max_count=max_count))
            
            history = []
            for commit in commits:
                history.append({
                    'commit_id': commit.hexsha,
                    'author': f"{commit.author.name} <{commit.author.email}>",
                    'date': commit.committed_datetime.isoformat(),
                    'message': commit.message,
                })
                
            return history
        except git.GitCommandError as e:
            logger.error(f"Git命令错误: {str(e)}")
            raise RepositoryException(f"获取文件历史时出错: {str(e)}")
        except Exception as e:
            logger.error(f"获取文件历史时出错: {str(e)}")
            raise RepositoryException(f"获取文件历史时出错: {str(e)}")
            
    def _create_initial_structure(self) -> None:
        """
        创建初始仓库结构
        """
        # 创建组件目录
        components_dir = os.path.join(self.local_path, "components")
        os.makedirs(components_dir, exist_ok=True)
        
        # 创建README文件
        readme_path = os.path.join(self.local_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("# 组件仓库\n\n")
            f.write("这是一个用于存储和管理代码组件的仓库。\n\n")
            f.write("## 目录结构\n\n")
            f.write("- `components/`: 组件目录\n")
            f.write("  - `<类别>/`: 按类别组织的组件\n")
            f.write("    - `<组件名>/`: 具体组件\n")
            f.write("      - `metadata.json`: 组件元数据\n")
            f.write("      - `README.md`: 组件文档\n")
            f.write("      - 其他组件文件\n")
            
        # 创建.gitignore文件
        gitignore_path = os.path.join(self.local_path, ".gitignore")
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write("# Python\n")
            f.write("__pycache__/\n")
            f.write("*.py[cod]\n")
            f.write("*$py.class\n")
            f.write("*.so\n")
            f.write(".Python\n")
            f.write("env/\n")
            f.write("build/\n")
            f.write("develop-eggs/\n")
            f.write("dist/\n")
            f.write("downloads/\n")
            f.write("eggs/\n")
            f.write(".eggs/\n")
            f.write("lib/\n")
            f.write("lib64/\n")
            f.write("parts/\n")
            f.write("sdist/\n")
            f.write("var/\n")
            f.write("*.egg-info/\n")
            f.write(".installed.cfg\n")
            f.write("*.egg\n\n")
            f.write("# IDE\n")
            f.write(".idea/\n")
            f.write(".vscode/\n")
            f.write("*.swp\n")
            f.write("*.swo\n") 