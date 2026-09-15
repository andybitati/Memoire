"""Agents Logminer de haut niveau."""

from .contract_net import CNP_MESSAGE_TYPES, ContractNetCoordinator, NegotiationResult
from .idempotency import IdempotencyRecord, RedisIdempotencyStore, SQLiteIdempotencyStore
from .intelligent_runtime import (
    AgentCapability,
    AgentPerception,
    AgentPolicyWeights,
    AgentTask,
    BidEvaluation,
    MultiTaskIntelligentAgent,
    TaskResult,
)
from .redis_contract_net import RedisContractNetCoordinator, RedisContractNetTransport


def run_supervisor_cycle(*args, **kwargs):
    """Charge le superviseur historique uniquement lorsqu'il est demandé.

    Le chargement différé garde le noyau CNP déployable sur des agents légers
    qui ne disposent pas de toute la pile scientifique du superviseur.
    """

    from .supervisor_agent import run_supervisor_cycle as _run_supervisor_cycle

    return _run_supervisor_cycle(*args, **kwargs)

__all__ = [
    "AgentCapability",
    "AgentPerception",
    "AgentPolicyWeights",
    "AgentTask",
    "BidEvaluation",
    "CNP_MESSAGE_TYPES",
    "ContractNetCoordinator",
    "IdempotencyRecord",
    "MultiTaskIntelligentAgent",
    "NegotiationResult",
    "RedisContractNetCoordinator",
    "RedisContractNetTransport",
    "RedisIdempotencyStore",
    "SQLiteIdempotencyStore",
    "TaskResult",
    "run_supervisor_cycle",
]
