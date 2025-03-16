import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel
import torch.distributed.rpc as rpc
from torch.distributed.optim import DistributedOptimizer
from torch.distributed.rpc import RRef, remote
from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import asyncio
import ray
from mpi4py import MPI
import horovod.torch as hvd

@dataclass
class TensorShard:
    data: torch.Tensor
    indices: torch.LongTensor
    dimension: int

class DistributedTensorManager:
    def __init__(self, 
                 world_size: int,
                 device: Optional[torch.device] = None):
        self.world_size = world_size
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.tensor_store = {}
        self.shard_map = {}
        
    def distribute_tensor(self, 
                         tensor: torch.Tensor,
                         strategy: str = 'block') -> str:
        tensor_id = self._generate_id()
        
        if strategy == 'block':
            shards = self._block_partition(tensor)
        elif strategy == 'cyclic':
            shards = self._cyclic_partition(tensor)
        else:
            raise ValueError(f"Unknown distribution strategy: {strategy}")
            
        # Store local shard
        self.tensor_store[tensor_id] = shards[self.rank]
        
        # Create shard mapping
        self.shard_map[tensor_id] = {
            i: self._get_shard_metadata(shard)
            for i, shard in enumerate(shards)
        }
        
        return tensor_id
        
    def _block_partition(self, tensor: torch.Tensor) -> List[TensorShard]:
        n_dims = tensor.dim()
        dim_sizes = tensor.size()
        
        # Choose dimension to split
        split_dim = max(range(n_dims), key=lambda i: dim_sizes[i])
        split_size = dim_sizes[split_dim] // self.world_size
        
        shards = []
        for i in range(self.world_size):
            start_idx = i * split_size
            end_idx = start_idx + split_size if i < self.world_size - 1 else dim_sizes[split_dim]
            
            # Create slice for this shard
            slices = [slice(None)] * n_dims
            slices[split_dim] = slice(start_idx, end_idx)
            
            shard_data = tensor[slices].clone().to(self.device)
            shard_indices = torch.arange(start_idx, end_idx)
            
            shards.append(TensorShard(
                data=shard_data,
                indices=shard_indices,
                dimension=split_dim
            ))
            
        return shards
        
    def _cyclic_partition(self, tensor: torch.Tensor) -> List[TensorShard]:
        n_dims = tensor.dim()
        dim_sizes = tensor.size()
        
        # Choose dimension to split
        split_dim = max(range(n_dims), key=lambda i: dim_sizes[i])
        
        shards = [[] for _ in range(self.world_size)]
        for i in range(dim_sizes[split_dim]):
            rank = i % self.world_size
            
            # Create slice for this element
            slices = [slice(None)] * n_dims
            slices[split_dim] = i
            
            shards[rank].append((tensor[slices], i))
            
        # Combine elements for each shard
        result_shards = []
        for rank, elements in enumerate(shards):
            if elements:
                shard_data, indices = zip(*elements)
                result_shards.append(TensorShard(
                    data=torch.stack(shard_data).to(self.device),
                    indices=torch.tensor(indices),
                    dimension=split_dim
                ))
            else:
                result_shards.append(TensorShard(
                    data=torch.tensor([]).to(self.device),
                    indices=torch.tensor([]),
                    dimension=split_dim
                ))
                
        return result_shards
        
    def _get_shard_metadata(self, shard: TensorShard) -> Dict:
        return {
            'shape': list(shard.data.shape),
            'indices': shard.indices.tolist(),
            'dimension': shard.dimension
        }
        
    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
        
    @ray.remote
    def gather_tensor(self, tensor_id: str) -> torch.Tensor:
        # Get metadata for all shards
        all_metadata = self.comm.allgather(
            self.shard_map[tensor_id][self.rank]
        )
        
        # Determine final tensor shape
        max_dim = max(meta['dimension'] for meta in all_metadata)
        shape = list(all_metadata[0