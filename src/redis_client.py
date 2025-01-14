import redis
import logging
from typing import Union, Dict, List, Any
import base64

class RedisClient:
    """Redis客户端连接工具类"""
    
    def __init__(self):
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.binary_client = None
    
    def connect(self, host: str = 'localhost', 
                port: int = 6379,
                password: str = None,
                db: int = 0) -> bool:
        """
        连接Redis服务器
        """
        try:
            # 如果已经存在连接，先关闭
            if self.client:
                self.client.close()
            
            # 创建两个客户端连接
            # 一个用于二进制数据（不自动解码）
            self.binary_client = redis.Redis(
                host=host,
                port=port,
                password=password if password else None,
                db=db,
                decode_responses=False,  # 不自动解码
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # 一个用于文本数据（自动解码）
            self.client = redis.Redis(
                host=host,
                port=port,
                password=password if password else None,
                db=db,
                decode_responses=True,  # 自动解码
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # 测试连接
            self.client.ping()
            self.logger.info(f"Successfully connected to Redis at {host}:{port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            self.client = None
            self.binary_client = None
            return False

    def select_db(self, db: int) -> bool:
        """选择数据库"""
        try:
            if not self.client:
                self.logger.error("No Redis connection available")
                return False
            self.client.select(db)
            return True
        except Exception as e:
            self.logger.error(f"Error selecting database {db}: {str(e)}")
            return False

    def get_all_keys(self, pattern: str = '*') -> List[str]:
        """获取所有键"""
        try:
            if not self.client:
                self.logger.error("No Redis connection available")
                return []
            return [key for key in self.client.keys(pattern)]
        except Exception as e:
            self.logger.error(f"Error getting keys: {str(e)}")
            return []

    def get_string(self, key: str) -> str:
        """获取字符串值"""
        try:
            if not self.client or not self.binary_client:
                self.logger.error("No Redis connection available")
                return None
                
            # 首先尝试使用二进制客户端获取数据
            binary_value = self.binary_client.get(key)
            if binary_value is None:
                return None
                
            try:
                # 尝试 UTF-8 解码
                return binary_value.decode('utf-8')
            except UnicodeDecodeError:
                # 如果解码失败，返回 Base64 编码的字符串
                return f"[Binary Data (Base64)]: {base64.b64encode(binary_value).decode('ascii')}"
                
        except Exception as e:
            self.logger.error(f"Error getting key {key}: {str(e)}")
            return None

    def get_hash_field(self, key: str, field: str) -> str:
        """获取哈希字段值"""
        try:
            if not self.binary_client:
                return None
                
            binary_value = self.binary_client.hget(key, field)
            if binary_value is None:
                return None
                
            try:
                return binary_value.decode('utf-8')
            except UnicodeDecodeError:
                return f"[Binary Data (Base64)]: {base64.b64encode(binary_value).decode('ascii')}"
        except Exception as e:
            self.logger.error(f"Error getting hash field {field} for key {key}: {str(e)}")
            return None

    def get_value(self, key: str) -> Any:
        """根据类型获取值"""
        try:
            if not self.client or not self.binary_client:
                self.logger.error("No Redis connection available")
                return None
                
            key_type = self.get_type(key)
            if not key_type:
                return None
                
            if key_type == 'string':
                return self.get_string(key)
            elif key_type == 'hash':
                # 获取所有哈希字段
                binary_hash = self.binary_client.hgetall(key)
                result = {}
                for field, value in binary_hash.items():
                    try:
                        field_str = field.decode('utf-8')
                        try:
                            value_str = value.decode('utf-8')
                        except UnicodeDecodeError:
                            value_str = f"[Binary Data (Base64)]: {base64.b64encode(value).decode('ascii')}"
                        result[field_str] = value_str
                    except UnicodeDecodeError:
                        # 如果字段名也无法解码，使用其Base64编码
                        field_str = f"[Binary Field (Base64)]: {base64.b64encode(field).decode('ascii')}"
                        value_str = f"[Binary Data (Base64)]: {base64.b64encode(value).decode('ascii')}"
                        result[field_str] = value_str
                return result
            elif key_type == 'list':
                # 获取列表数据
                binary_list = self.binary_client.lrange(key, 0, -1)
                return [self._decode_value(item) for item in binary_list]
            elif key_type == 'set':
                # 获取集合数据
                binary_set = self.binary_client.smembers(key)
                return [self._decode_value(item) for item in binary_set]
            elif key_type == 'zset':
                # 获取有序集合数据
                binary_zset = self.binary_client.zrange(key, 0, -1, withscores=True)
                return [(self._decode_value(item[0]), item[1]) for item in binary_zset]
            else:
                self.logger.warning(f"Unsupported Redis type: {key_type} for key: {key}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting value for key {key}: {str(e)}")
            return None

    def _decode_value(self, value: bytes) -> str:
        """解码二进制值"""
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return f"[Binary Data (Base64)]: {base64.b64encode(value).decode('ascii')}"

    def set_string(self, key: str, value: str, ttl: int = None) -> bool:
        """设置字符串值"""
        try:
            if not self.client:
                return False
            self.client.set(key, value, ex=ttl)
            return True
        except Exception as e:
            self.logger.error(f"Error setting string key {key}: {str(e)}")
            return False

    def get_type(self, key: str) -> str:
        """获取键的类型"""
        try:
            if not self.client:
                self.logger.error("No Redis connection available")
                return None
            
            # 直接返回字符串类型，不需要decode
            # 因为我们在创建连接时已经设置了 decode_responses=True
            return self.client.type(key)
        except Exception as e:
            self.logger.error(f"Error getting type for key {key}: {str(e)}")
            return None

    def delete_key(self, key: str) -> bool:
        """删除指定的键"""
        try:
            if not self.client:
                self.logger.error("No Redis connection available")
                return False
            return bool(self.client.delete(key))
        except Exception as e:
            self.logger.error(f"Error deleting key {key}: {str(e)}")
            return False

    def flush_db(self) -> bool:
        """清空当前数据库"""
        try:
            if not self.client:
                self.logger.error("No Redis connection available")
                return False
            self.client.flushdb()
            return True
        except Exception as e:
            self.logger.error(f"Error flushing current database: {str(e)}")
            return False

    def flush_all(self) -> bool:
        """清空所有数据库"""
        try:
            if not self.client:
                self.logger.error("No Redis connection available")
                return False
            self.client.flushall()
            return True
        except Exception as e:
            self.logger.error(f"Error flushing all databases: {str(e)}")
            return False 

    def get_ttl(self, key: str) -> int:
        """获取键的TTL"""
        try:
            if not self.client:
                return None
            return self.client.ttl(key)
        except Exception as e:
            self.logger.error(f"Error getting TTL for key {key}: {str(e)}")
            return None

    def set_ttl(self, key: str, ttl: int) -> bool:
        """设置键的TTL"""
        try:
            if not self.client:
                return False
            if ttl < 0:
                self.client.persist(key)  # 移除过期时间
            else:
                self.client.expire(key, ttl)
            return True
        except Exception as e:
            self.logger.error(f"Error setting TTL for key {key}: {str(e)}")
            return False

    def set_hash(self, key: str, mapping: dict) -> bool:
        """设置哈希值"""
        try:
            if not self.client:
                return False
            self.client.delete(key)  # 先删除旧值
            if mapping:
                self.client.hset(key, mapping=mapping)
            return True
        except Exception as e:
            self.logger.error(f"Error setting hash key {key}: {str(e)}")
            return False

    def set_list(self, key: str, items: list) -> bool:
        """设置列表值"""
        try:
            if not self.client:
                return False
            self.client.delete(key)  # 先删除旧值
            if items:
                self.client.rpush(key, *items)
            return True
        except Exception as e:
            self.logger.error(f"Error setting list key {key}: {str(e)}")
            return False

    def set_set(self, key: str, items: list) -> bool:
        """设置集合值"""
        try:
            if not self.client:
                return False
            self.client.delete(key)  # 先删除旧值
            if items:
                self.client.sadd(key, *items)
            return True
        except Exception as e:
            self.logger.error(f"Error setting set key {key}: {str(e)}")
            return False

    def set_zset(self, key: str, items: list) -> bool:
        """设置有序集合值"""
        try:
            if not self.client:
                return False
            self.client.delete(key)  # 先删除旧值
            if items:
                self.client.zadd(key, {member: score for member, score in items})
            return True
        except Exception as e:
            self.logger.error(f"Error setting sorted set key {key}: {str(e)}")
            return False 