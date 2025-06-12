import sqlite3
import queue
import threading
from contextlib import contextmanager
import time
from utils.logger import Logger

class SQLiteConnectionPool:
    """SQLite数据库连接池实现
    
    这个类实现了一个简单的SQLite连接池，用于管理和重用数据库连接，
    避免频繁创建和关闭连接带来的性能开销。
    """
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, db_path, max_connections=5):
        """获取连接池单例
        
        Args:
            db_path: 数据库文件路径
            max_connections: 连接池最大连接数
            
        Returns:
            SQLiteConnectionPool: 连接池实例
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(db_path, max_connections)
            return cls._instance
    
    def __init__(self, db_path, max_connections=5):
        """初始化连接池
        
        Args:
            db_path: 数据库文件路径
            max_connections: 连接池最大连接数
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        self.logger = Logger("SQLiteConnectionPool")
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池，预创建一些连接"""
        # 预创建一半的连接
        initial_connections = max(1, self.max_connections // 2)
        for _ in range(initial_connections):
            self._create_connection()
    
    def _create_connection(self):
        """创建一个新的数据库连接并添加到池中"""
        try:
            # 修改：将check_same_thread设置为False，但添加线程锁来确保线程安全
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            # 设置一些连接属性以提高性能
            conn.execute("PRAGMA journal_mode=WAL")  # 使用WAL模式提高并发性能
            conn.execute("PRAGMA cache_size=-5000")  # 增加缓存大小（约5MB）
            conn.execute("PRAGMA synchronous=NORMAL")  # 降低同步级别，提高性能
            conn.execute("PRAGMA temp_store=MEMORY")  # 临时表存储在内存中
            
            with self.lock:
                self.active_connections += 1
            
            self.pool.put(conn)
            return True
        except Exception as e:
            self.logger.error(f"创建数据库连接失败", {"error": str(e), "db_path": self.db_path})
            return False
    
    def get_connection(self, timeout=5):
        """从连接池获取一个连接
        
        Args:
            timeout: 获取连接的超时时间（秒）
            
        Returns:
            sqlite3.Connection: 数据库连接对象
            
        Raises:
            Exception: 如果无法获取连接则抛出异常
        """
        start_time = time.time()
        
        while True:
            try:
                # 尝试从池中获取连接
                return self.pool.get(block=True, timeout=0.5)
            except queue.Empty:
                # 如果池为空且未达到最大连接数，则创建新连接
                with self.lock:
                    if self.active_connections < self.max_connections:
                        if self._create_connection():
                            continue
                
                # 检查是否超时
                if time.time() - start_time > timeout:
                    raise Exception(f"获取数据库连接超时（{timeout}秒）")
                
                # 短暂等待后重试
                time.sleep(0.1)
    
    def return_connection(self, conn):
        """将连接归还到连接池
        
        Args:
            conn: 要归还的数据库连接
        """
        try:
            # 如果连接有问题，关闭它并创建一个新的
            if conn is None:
                with self.lock:
                    self.active_connections -= 1
                self._create_connection()
                return
            
            # 检查连接是否有效
            try:
                conn.execute("SELECT 1").fetchone()
                # 连接有效，归还到池中
                self.pool.put(conn)
            except sqlite3.Error:
                # 连接无效，关闭并创建新连接
                try:
                    conn.close()
                except:
                    pass
                
                with self.lock:
                    self.active_connections -= 1
                
                self._create_connection()
        except Exception as e:
            self.logger.error(f"归还连接到池中失败", {"error": str(e)})
            try:
                conn.close()
            except:
                pass
            
            with self.lock:
                self.active_connections -= 1
    
    @contextmanager
    def connection(self):
        """使用上下文管理器获取和释放连接
        
        用法:
            with pool.connection() as conn:
                # 使用conn进行数据库操作
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn is not None:
                self.return_connection(conn)
    
    def close_all(self):
        """关闭所有连接并清空连接池
        
        通常在应用程序关闭时调用
        """
        while not self.pool.empty():
            try:
                conn = self.pool.get(block=False)
                conn.close()
            except:
                pass
        
        with self.lock:
            self.active_connections = 0