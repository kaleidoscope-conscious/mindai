"""
Thread-safe wrapper utilities for MindAI consciousness system.
Provides context managers and decorators for safe concurrent access to shared state.
"""

import threading
from contextlib import contextmanager
from typing import Any, Callable, TypeVar, Dict, List, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ThreadSafeWrapper:
    """Wrapper class for thread-safe access to shared data structures."""
    
    def __init__(self, data: Any, lock: Optional[threading.RLock] = None):
        """
        Initialize thread-safe wrapper.
        
        Args:
            data: The data structure to protect
            lock: Optional RLock to use (creates new one if None)
        """
        self.data = data
        self.lock = lock or threading.RLock()
        self._access_count = 0
        self._access_lock = threading.Lock()
    
    @contextmanager
    def acquire(self, timeout: float = 5.0):
        """
        Context manager for acquiring lock with timeout.
        
        Args:
            timeout: Lock acquisition timeout in seconds
            
        Yields:
            The protected data
            
        Raises:
            TimeoutError: If lock cannot be acquired within timeout
        """
        acquired = self.lock.acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError(f"Could not acquire lock within {timeout} seconds")
        
        try:
            with self._access_lock:
                self._access_count += 1
            yield self.data
        finally:
            try:
                self.lock.release()
            except RuntimeError:
                logger.warning("Lock was not acquired by this thread")
            finally:
                with self._access_lock:
                    self._access_count -= 1
    
    def safe_operation(self, operation: Callable[[Any], T], timeout: float = 5.0) -> T:
        """
        Execute operation safely with lock.
        
        Args:
            operation: Callable that takes the data and returns a result
            timeout: Lock acquisition timeout
            
        Returns:
            Result of the operation
        """
        with self.acquire(timeout=timeout) as data:
            return operation(data)
    
    @property
    def active_access_count(self) -> int:
        """Get current number of active accesses."""
        with self._access_lock:
            return self._access_count


def thread_safe(timeout: float = 5.0):
    """
    Decorator to make a method thread-safe using instance lock.
    
    Assumes the instance has a `lock` attribute (threading.RLock).
    
    Args:
        timeout: Lock acquisition timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'lock'):
                raise AttributeError(f"{self.__class__.__name__} must have a 'lock' attribute")
            
            acquired = self.lock.acquire(timeout=timeout)
            if not acquired:
                raise TimeoutError(f"Could not acquire lock for {func.__name__} within {timeout} seconds")
            
            try:
                return func(self, *args, **kwargs)
            finally:
                try:
                    self.lock.release()
                except RuntimeError:
                    logger.warning(f"Lock was not acquired by this thread for {func.__name__}")
        
        return wrapper
    return decorator


class ReferenceManager:
    """
    Manages cross-references between data structures to prevent memory leaks.
    Tracks all references and helps with cleanup.
    """
    
    def __init__(self):
        """Initialize reference manager."""
        self.references: Dict[str, set] = {}  # id -> set of referencing ids
        self.reverse_references: Dict[str, set] = {}  # id -> set of ids it references
        self.lock = threading.RLock()
    
    def add_reference(self, source_id: str, target_id: str) -> None:
        """
        Register a reference from source to target.
        
        Args:
            source_id: ID of object that references
            target_id: ID of object being referenced
        """
        with self.lock:
            if source_id not in self.references:
                self.references[source_id] = set()
            self.references[source_id].add(target_id)
            
            if target_id not in self.reverse_references:
                self.reverse_references[target_id] = set()
            self.reverse_references[target_id].add(source_id)
    
    def remove_reference(self, source_id: str, target_id: str) -> None:
        """
        Unregister a reference.
        
        Args:
            source_id: ID of object that references
            target_id: ID of object being referenced
        """
        with self.lock:
            if source_id in self.references:
                self.references[source_id].discard(target_id)
                if not self.references[source_id]:
                    del self.references[source_id]
            
            if target_id in self.reverse_references:
                self.reverse_references[target_id].discard(source_id)
                if not self.reverse_references[target_id]:
                    del self.reverse_references[target_id]
    
    def get_all_references_to(self, target_id: str) -> List[str]:
        """
        Get all objects that reference the given target.
        
        Args:
            target_id: ID of target object
            
        Returns:
            List of source IDs that reference this target
        """
        with self.lock:
            return list(self.reverse_references.get(target_id, set()))
    
    def get_all_referenced_by(self, source_id: str) -> List[str]:
        """
        Get all objects referenced by the given source.
        
        Args:
            source_id: ID of source object
            
        Returns:
            List of target IDs referenced by this source
        """
        with self.lock:
            return list(self.references.get(source_id, set()))
    
    def cleanup_all_references(self, obj_id: str) -> tuple[List[str], List[str]]:
        """
        Remove all references to and from an object.
        Use this when deleting an object to prevent leaks.
        
        Args:
            obj_id: ID of object being removed
            
        Returns:
            Tuple of (objects_that_referenced_it, objects_it_referenced)
        """
        with self.lock:
            # Get references before removing
            referencing = self.get_all_references_to(obj_id)
            referenced = self.get_all_referenced_by(obj_id)
            
            # Remove all references involving this object
            for source_id in list(self.references.get(obj_id, set())):
                self.remove_reference(obj_id, source_id)
            
            for target_id in list(self.reverse_references.get(obj_id, set())):
                self.remove_reference(target_id, obj_id)
            
            # Clean up the dictionaries
            self.references.pop(obj_id, None)
            self.reverse_references.pop(obj_id, None)
            
            return referencing, referenced
    
    def get_orphaned_references(self, existing_ids: set) -> List[tuple[str, str]]:
        """
        Find references where target objects no longer exist.
        Useful for identifying leaked references.
        
        Args:
            existing_ids: Set of IDs that currently exist
            
        Returns:
            List of (source, target) tuples where target doesn't exist
        """
        with self.lock:
            orphaned = []
            for source_id, targets in self.references.items():
                for target_id in targets:
                    if target_id not in existing_ids:
                        orphaned.append((source_id, target_id))
            return orphaned
    
    def cleanup_orphaned_references(self, existing_ids: set) -> int:
        """
        Remove references to objects that no longer exist.
        
        Args:
            existing_ids: Set of IDs that currently exist
            
        Returns:
            Number of orphaned references cleaned up
        """
        orphaned = self.get_orphaned_references(existing_ids)
        for source_id, target_id in orphaned:
            self.remove_reference(source_id, target_id)
        
        logger.info(f"Cleaned up {len(orphaned)} orphaned references")
        return len(orphaned)


class ValidationHelper:
    """Helper class for common validation operations."""
    
    @staticmethod
    def validate_node_list(nodes: Optional[List[Any]], min_size: int = 0, 
                          allow_empty: bool = False) -> bool:
        """
        Validate a list of nodes.
        
        Args:
            nodes: List to validate
            min_size: Minimum required size
            allow_empty: Whether empty lists are valid
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValueError: If validation fails
        """
        if nodes is None:
            if not allow_empty:
                raise ValueError("Nodes list cannot be None")
            return True
        
        if not isinstance(nodes, list):
            raise TypeError(f"Expected list, got {type(nodes).__name__}")
        
        if len(nodes) == 0 and not allow_empty:
            raise ValueError("Nodes list cannot be empty")
        
        if len(nodes) < min_size:
            raise ValueError(f"Nodes list must have at least {min_size} elements, got {len(nodes)}")
        
        return True
    
    @staticmethod
    def validate_node_id(node_id: Optional[str]) -> bool:
        """
        Validate a node ID.
        
        Args:
            node_id: ID to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if node_id is None:
            raise ValueError("Node ID cannot be None")
        
        if not isinstance(node_id, str):
            raise TypeError(f"Expected str, got {type(node_id).__name__}")
        
        if len(node_id) == 0:
            raise ValueError("Node ID cannot be empty string")
        
        return True
    
    @staticmethod
    def validate_dict(data: Optional[Dict], required_keys: Optional[List[str]] = None) -> bool:
        """
        Validate a dictionary.
        
        Args:
            data: Dictionary to validate
            required_keys: List of required keys
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if data is None:
            raise ValueError("Dictionary cannot be None")
        
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")
        
        if required_keys:
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Required key '{key}' not found in dictionary")
        
        return True
    
    @staticmethod
    def validate_numeric_range(value: Optional[float], min_val: float = 0.0, 
                              max_val: float = 1.0, name: str = "value") -> bool:
        """
        Validate a numeric value is within range.
        
        Args:
            value: Value to validate
            min_val: Minimum acceptable value
            max_val: Maximum acceptable value
            name: Name of value (for error messages)
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if value is None:
            raise ValueError(f"{name} cannot be None")
        
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected numeric value for {name}, got {type(value).__name__}")
        
        if value < min_val or value > max_val:
            raise ValueError(f"{name} must be between {min_val} and {max_val}, got {value}")
        
        return True


class SafeNodeContainer:
    """
    Thread-safe container for nodes with automatic reference cleanup.
    """
    
    def __init__(self):
        """Initialize container."""
        self.nodes: Dict[str, Any] = {}
        self.lock = threading.RLock()
        self.reference_manager = ReferenceManager()
    
    @thread_safe(timeout=5.0)
    def add_node(self, node_id: str, node: Any) -> None:
        """
        Add a node to the container.
        
        Args:
            node_id: ID of the node
            node: The node object
            
        Raises:
            ValueError: If node_id is invalid or already exists
        """
        ValidationHelper.validate_node_id(node_id)
        
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists")
        
        self.nodes[node_id] = node
    
    @thread_safe(timeout=5.0)
    def remove_node(self, node_id: str) -> Any:
        """
        Remove a node and clean up all references.
        
        Args:
            node_id: ID of the node to remove
            
        Returns:
            The removed node
            
        Raises:
            KeyError: If node doesn't exist
        """
        ValidationHelper.validate_node_id(node_id)
        
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} not found")
        
        # Clean up all references
        referencing, referenced = self.reference_manager.cleanup_all_references(node_id)
        
        logger.debug(f"Removing node {node_id}: {len(referencing)} references to clean, "
                    f"{len(referenced)} references from clean")
        
        return self.nodes.pop(node_id)
    
    @thread_safe(timeout=5.0)
    def get_node(self, node_id: str) -> Any:
        """
        Get a node by ID.
        
        Args:
            node_id: ID of the node
            
        Returns:
            The node object
            
        Raises:
            KeyError: If node doesn't exist
        """
        ValidationHelper.validate_node_id(node_id)
        
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} not found")
        
        return self.nodes[node_id]
    
    @thread_safe(timeout=5.0)
    def get_all_nodes(self) -> Dict[str, Any]:
        """
        Get a copy of all nodes.
        
        Returns:
            Dictionary of all nodes
        """
        return dict(self.nodes)
    
    @thread_safe(timeout=5.0)
    def node_exists(self, node_id: str) -> bool:
        """
        Check if a node exists.
        
        Args:
            node_id: ID of the node
            
        Returns:
            True if node exists
        """
        try:
            ValidationHelper.validate_node_id(node_id)
            return node_id in self.nodes
        except (ValueError, TypeError):
            return False
    
    @thread_safe(timeout=5.0)
    def cleanup_orphaned_references(self) -> int:
        """
        Clean up references to nodes that no longer exist.
        
        Returns:
            Number of orphaned references cleaned up
        """
        return self.reference_manager.cleanup_orphaned_references(set(self.nodes.keys()))
    
    @property
    def node_count(self) -> int:
        """Get count of nodes (may be stale immediately after acquisition)."""
        with self.lock:
            return len(self.nodes)
